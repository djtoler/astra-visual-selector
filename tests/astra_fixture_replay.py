"""Fixture-only adapter around the existing matcher; never used by production."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "reports/astra-p0-p2/28-28-replay-v1"
LEGACY = "reports/visualtask-match-pilot-28-28.json"
LEGACY_SHA = "f7328a5860113597fc51366eae61b076a405bfa2eb01c05df108f137da1b2e77"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def capture():
    sys.path.insert(0, str(ROOT))
    from pipeline import visualtask_matching as matcher
    DIRECTORY.mkdir(parents=True, exist_ok=True)
    inventory = {
        "media": matcher.M.load(),
        "templates": matcher.C.load(content_class="*"),
        "policies": {
            "projects": sorted(matcher.M.projects()),
            "classTags": sorted(matcher.M.class_tags()),
            "uniqueRosterTokens": sorted(matcher.M.unique_roster_tokens()),
            "suppressedClaims": sorted(matcher.M.suppressed_claims()),
            "corrections": sorted(matcher.M.corrections()),
            "pickedIds": sorted(matcher.C._picked_ids()),
        },
    }
    write(DIRECTORY / "effective-inventory.json", inventory)
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    paths = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", revision,
                                     "pipeline", "match-trial", "grammar"], cwd=ROOT, text=True).splitlines()
    # Bind every archived code/grammar input, including policy sidecars. External
    # lookups are materialized above, so replay never reads a library or provider.
    bindings = [{"path": p, "sha256": sha(subprocess.check_output(
        ["git", "show", f"{revision}:{p}"], cwd=ROOT))} for p in paths]
    manifest = {
        "schemaVersion": "astra-visualtask-replay@1", "codeRevision": revision,
        "legacy": {"path": LEGACY, "sha256": LEGACY_SHA, "status": "legacy_non_replayable"},
        "lineage": "Original live media state was not recoverable. Historical report is preserved; this is a versioned deterministic migration, not historical replay.",
        "inventory": {"path": "effective-inventory.json", "sha256": sha((DIRECTORY / "effective-inventory.json").read_bytes()),
                      "mediaCount": len(inventory["media"]), "templateCount": len(inventory["templates"])},
        "boundRevisionFiles": bindings,
    }
    write(DIRECTORY / "manifest.json", manifest)
    output = replay(manifest, check_output=False)
    (DIRECTORY / "fixture.json").write_bytes(output)
    manifest["fixture"] = {"path": "fixture.json", "sha256": sha(output)}
    write(DIRECTORY / "manifest.json", manifest)


def replay(manifest=None, *, check_output=True):
    manifest = manifest or json.loads((DIRECTORY / "manifest.json").read_text())
    if manifest["schemaVersion"] != "astra-visualtask-replay@1":
        raise ValueError("unsupported replay version")
    if sha((ROOT / LEGACY).read_bytes()) != LEGACY_SHA:
        raise ValueError("historical evidence changed")
    inventory_path = DIRECTORY / manifest["inventory"]["path"]
    if sha(inventory_path.read_bytes()) != manifest["inventory"]["sha256"]:
        raise ValueError("inventory digest mismatch")
    revision = manifest["codeRevision"]
    paths = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", revision,
                                     "pipeline", "match-trial", "grammar"], cwd=ROOT, text=True).splitlines()
    if set(paths) != {r["path"] for r in manifest["boundRevisionFiles"]}:
        raise ValueError("bound input omitted")
    for row in manifest["boundRevisionFiles"]:
        actual = subprocess.check_output(["git", "show", f"{revision}:{row['path']}"], cwd=ROOT)
        if sha(actual) != row["sha256"]:
            raise ValueError("bound input digest mismatch")
    archive = subprocess.check_output(["git", "archive", revision, "pipeline", "match-trial", "grammar"], cwd=ROOT)
    with tempfile.TemporaryDirectory(prefix="astra-replay-") as directory:
        with tarfile.open(fileobj=io.BytesIO(archive)) as bundle:
            bundle.extractall(directory, filter="data")
        output = subprocess.check_output([sys.executable, str(Path(__file__).resolve()),
                                          "--worker", directory, str(inventory_path)], cwd=directory)
    if check_output:
        fixture = (DIRECTORY / manifest["fixture"]["path"]).read_bytes()
        if sha(fixture) != manifest["fixture"]["sha256"] or fixture != output:
            raise ValueError("fixture replay mismatch")
    return output


def worker(root, inventory_path):
    sys.path.insert(0, root)
    from pipeline import visualtask_matching as matcher
    inventory = json.loads(Path(inventory_path).read_text())
    policy = inventory["policies"]
    with patch.object(matcher.M, "load", return_value=inventory["media"]), \
         patch.object(matcher.C, "load", return_value=inventory["templates"]), \
         patch.object(matcher.M, "projects", return_value=set(policy["projects"])), \
         patch.object(matcher.M, "class_tags", return_value=set(policy["classTags"])), \
         patch.object(matcher.M, "unique_roster_tokens", return_value=set(policy["uniqueRosterTokens"])), \
         patch.object(matcher.M, "suppressed_claims", return_value={tuple(r) for r in policy["suppressedClaims"]}), \
         patch.object(matcher.M, "corrections", return_value={tuple(r) for r in policy["corrections"]}), \
         patch.object(matcher.C, "_picked_ids", return_value=set(policy["pickedIds"])):
        result = matcher.build(source_beat="28-28")
        matcher.validate(result)
        print(matcher.dumps(result), end="")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--capture", action="store_true")
    parser.add_argument("--worker", nargs=2)
    args = parser.parse_args()
    if args.worker:
        worker(*args.worker)
    elif args.capture:
        capture()
    else:
        replay()
        print("Versioned replay passed; legacy bytes preserved.")
