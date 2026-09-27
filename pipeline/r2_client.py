#!/usr/bin/env python3
"""Minimal SigV4 client for Cloudflare R2. Standard library only.

WHY NOT THE aws CLI. Measured 2026-09-25: the installed awscli 2.18.12 is broken
— its bundled interpreter cannot load _cffi_backend, so every invocation exits
255 before reaching the network. Repairing it is a brew reinstall, which is a
change to the user's machine and their decision, and it would leave the upload
path depending on a tool that has already failed once.

SigV4 over urllib is ~60 lines, has no dependencies, and is fully deterministic —
the same properties the rest of this layer is held to. R2 differences from S3:
region is always `auto`, addressing is path-style, and the host carries the
account id.

Read-only by default. put() is the only method that writes, and nothing here
creates a bucket or spends without an explicit call.
"""
import datetime, hashlib, hmac, pathlib, re, sys, urllib.parse, urllib.request, urllib.error

ALGO = "AWS4-HMAC-SHA256"
EMPTY_SHA = hashlib.sha256(b"").hexdigest()
UNSIGNED = "UNSIGNED-PAYLOAD"


def env(path=None):
    """Read .env without importing anything. Values never printed by this module.

    ASTRA_ENV_FILE overrides the location. This exists because a test that meant
    to withhold credentials could not: r2_sync reads .env directly, so unsetting
    ASTRA_R2_* changed nothing and the refusal test would have uploaded 1.46 GB
    for real. A test now points this at an empty file.
    """
    import os as _os
    p = pathlib.Path(path or _os.environ.get("ASTRA_ENV_FILE")
                     or pathlib.Path(__file__).resolve().parent.parent / ".env")
    out = {}
    if p.exists():
        for line in p.read_text().splitlines():
            m = re.match(r"\s*([A-Za-z0-9_]+)\s*=\s*(.*)\s*$", line)
            if m:
                out[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    return out


class R2:
    def __init__(self, account_id, access_key, secret_key, region="auto"):
        self.host = f"{account_id}.r2.cloudflarestorage.com"
        self.ak, self.sk, self.region = access_key, secret_key, region

    def _sign(self, method, path, query, payload_hash, extra=None, length=None):
        now = datetime.datetime.now(datetime.timezone.utc)
        amzdate = now.strftime("%Y%m%dT%H%M%SZ")
        datestamp = now.strftime("%Y%m%d")
        headers = {"host": self.host, "x-amz-content-sha256": payload_hash,
                   "x-amz-date": amzdate}
        if length is not None:
            headers["content-length"] = str(length)
        headers.update({k.lower(): v for k, v in (extra or {}).items()})
        signed = ";".join(sorted(headers))
        canon_headers = "".join(f"{k}:{headers[k].strip()}\n" for k in sorted(headers))
        # R2 uses path-style addressing; each segment is encoded, '/' preserved.
        canon_uri = "/" + "/".join(urllib.parse.quote(s, safe="~")
                                   for s in path.lstrip("/").split("/")) if path.strip("/") else "/"
        canon_query = "&".join(f"{urllib.parse.quote(k, safe='~')}="
                               f"{urllib.parse.quote(str(v), safe='~')}"
                               for k, v in sorted((query or {}).items()))
        creq = "\n".join([method, canon_uri, canon_query, canon_headers,
                          signed, payload_hash])
        scope = f"{datestamp}/{self.region}/s3/aws4_request"
        sts = "\n".join([ALGO, amzdate, scope,
                         hashlib.sha256(creq.encode()).hexdigest()])
        k = ("AWS4" + self.sk).encode()
        for part in (datestamp, self.region, "s3", "aws4_request"):
            k = hmac.new(k, part.encode(), hashlib.sha256).digest()
        sig = hmac.new(k, sts.encode(), hashlib.sha256).hexdigest()
        headers["authorization"] = (f"{ALGO} Credential={self.ak}/{scope}, "
                                    f"SignedHeaders={signed}, Signature={sig}")
        url = f"https://{self.host}{canon_uri}" + (f"?{canon_query}" if canon_query else "")
        return url, headers

    def _call(self, method, path, query=None, body=None, payload_hash=None,
              extra=None, timeout=120):
        ph = payload_hash or (hashlib.sha256(body).hexdigest() if body else EMPTY_SHA)
        url, headers = self._sign(method, path, query, ph, extra,
                                  length=(len(body) if body is not None else None))
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, r.read(), dict(r.headers)
        except urllib.error.HTTPError as e:
            return e.code, e.read(), dict(e.headers or {})

    # --- reads ---
    def list_buckets(self):
        code, body, _ = self._call("GET", "/")
        names = re.findall(rb"<Name>([^<]+)</Name>", body)
        return code, [n.decode() for n in names], body

    def head_bucket(self, bucket):
        code, body, _ = self._call("HEAD", f"/{bucket}")
        return code, body

    def list_objects(self, bucket, prefix="", token=None, limit=1000):
        q = {"list-type": "2", "max-keys": str(limit)}
        if prefix: q["prefix"] = prefix
        if token: q["continuation-token"] = token
        code, body, _ = self._call("GET", f"/{bucket}", q)
        # ONE <Contents> BLOCK AT A TIME, FIELDS BY NAME. The first version fixed
        # the order as Key, LastModified, ETag, Size — the AWS S3 ordering. R2
        # returns Key, Size, LastModified, ETag, so the regex matched nothing and
        # this reported an empty bucket while 557 uploads were succeeding. Worse,
        # main() uses this to skip objects already present, so a re-run would have
        # re-uploaded everything and paid for every write twice.
        keys = []
        for blk in re.findall(rb"<Contents>(.*?)</Contents>", body, re.S):
            k = re.search(rb"<Key>([^<]*)</Key>", blk)
            z = re.search(rb"<Size>(\d+)</Size>", blk)
            if k:
                keys.append((k.group(1).decode(), int(z.group(1)) if z else 0))
        nxt = re.search(rb"<NextContinuationToken>([^<]+)<", body)
        return code, keys, (nxt.group(1).decode() if nxt else None), body

    def create_bucket(self, bucket):
        """Provisioning, not storage. R2 bills stored bytes and operations, so an
        empty bucket costs nothing and deleting it is one call. Never called
        implicitly by a sync."""
        return self._call("PUT", f"/{bucket}")

    # --- the only write ---
    def put_file(self, bucket, key, local, content_type=None):
        data = pathlib.Path(local).read_bytes()
        extra = {"content-type": content_type} if content_type else None
        return self._call("PUT", f"/{bucket}/{key}", body=data, extra=extra)


def from_env():
    e = env()
    need = ("CLOUDFLARE_ACCOUNT_ID", "CLOUDFLARE_ACCESS_KEY",
            "CLOUDFLARE_SECRET_ACCESS_KEY")
    missing = [k for k in need if not e.get(k)]
    if missing:
        raise KeyError(f".env is missing {missing}")
    return R2(e["CLOUDFLARE_ACCOUNT_ID"], e["CLOUDFLARE_ACCESS_KEY"],
              e["CLOUDFLARE_SECRET_ACCESS_KEY"]), e


# FETCHING A PUBLIC OBJECT NEEDS A BROWSER USER-AGENT. The pub-*.r2.dev hostname
# sits behind Cloudflare's bot protection, which answers Python-urllib's default
# agent with HTTP 403 and "error code: 1010" — a fingerprint block, not a
# permissions error. Measured 2026-09-25: the same key returns 200 and 3,909,617
# bytes of image/png with a Chrome agent, and also with NO agent at all. Any build
# script that reads these URLs must set one, or it will read a 403 as "the bucket
# is not public" and go looking for the wrong bug.
BROWSER_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")


def public_url(base, key):
    return f"{str(base).rstrip('/')}/{str(key).lstrip('/')}"


def fetch_public(base, key, timeout=60):
    """GET a public object. Returns (status, bytes). Sends BROWSER_UA — see above."""
    req = urllib.request.Request(public_url(base, key),
                                 headers={"User-Agent": BROWSER_UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


CT = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
      ".webp": "image/webp", ".gif": "image/gif", ".mp4": "video/mp4",
      ".mov": "video/quicktime", ".m4v": "video/x-m4v", ".webm": "video/webm",
      ".json": "application/json", ".txt": "text/plain"}


def main():
    r2, e = from_env()
    code, buckets, raw = r2.list_buckets()
    print(f"   ListBuckets -> HTTP {code}")
    if code != 200:
        print("   " + raw[:400].decode("utf8", "replace").replace("\n", "\n   "))
        return 1
    print(f"   buckets: {buckets or '— none yet'}")
    for b in buckets:
        c, keys, _, _ = r2.list_objects(b, limit=5)
        print(f"     {b}: HTTP {c}, {len(keys)} object(s) sampled")
    return 0


if __name__ == "__main__":
    sys.exit(main())
