// Runs the ACTUAL functions out of ui13-review/index.html — not a copy of them.
import { readFileSync } from "node:fs";
const html = readFileSync(process.argv[2], "utf8");

function grab(name){
  const at = html.indexOf("function " + name + "(");
  if (at < 0) throw new Error("not found in the page: " + name);
  let i = html.indexOf("{", at), d = 0;
  for (let j = i; j < html.length; j++){
    if (html[j] === "{") d++;
    else if (html[j] === "}" && --d === 0) return html.slice(at, j + 1);
  }
  throw new Error("unbalanced: " + name);
}

const src = ["mst", "setsrc", "pool", "adopt", "srcLabel", "mine", "payload"]
  .map(grab).join("\n");
const srcs = {}, rate = {}, note = {}, pairs = {}, nob = {};
const run = new Function("srcs", "rate", "note", "pairs", "nob",
  src + "\nreturn {mst,setsrc,pool,adopt,srcLabel,mine,payload};")(
  srcs, rate, note, pairs, nob);

const beat = {beat: "01-01",
  media: [{id: "m1"}, {id: "m2"}, {id: "both"}],
  broll: [{id: "b1"}, {id: "both"}]};
const out = [];
const eq = (got, want, what) => out.push(
  {ok: JSON.stringify(got) === JSON.stringify(want), what,
   got: JSON.stringify(got), want: JSON.stringify(want)});

// default: media only
eq(run.pool(beat).map(m => m.id), ["m1","m2","both"], "default is media only");
eq(run.mst("01-01"), {m:true, b:false}, "default flags");

// add-on: both sources, deduped, media wins the shared id
run.setsrc("01-01", {b:true});
eq(run.pool(beat).map(m => m.id), ["m1","m2","both","b1"], "add-on unions and dedupes");
eq(run.pool(beat).filter(m => m.fromBroll).map(m => m.id), ["b1"],
   "only genuinely-b-roll rows are flagged");

// replacement: media off, b-roll on — the case the user asked for
run.setsrc("01-01", {m:false});
eq(run.pool(beat).map(m => m.id), ["b1","both"], "replacement is b-roll only");
eq(run.srcLabel("01-01"), "B-roll only", "label says replacement");

// neither
run.setsrc("01-01", {b:false});
eq(run.pool(beat).map(m => m.id), [], "both off yields nothing");
eq(run.srcLabel("01-01"), "Nothing selected", "label says nothing");

// toggling b-roll on must not disturb media
run.setsrc("01-01", {m:true});
run.setsrc("01-01", {b:true});
eq(run.mst("01-01"), {m:true, b:true}, "b-roll on leaves media on");
eq(run.srcLabel("01-01"), "Media + b-roll", "label says add-on");

// saved records
eq(run.adopt({broll:true}), {m:false, b:true}, "old record: checked box meant replacement");
eq(run.adopt({broll:false}), {m:true, b:false}, "old record: unchecked meant media");
eq(run.adopt({media:true, broll:true}), {m:true, b:true}, "new record: add-on survives");
eq(run.adopt({media:false, broll:true}), {m:false, b:true}, "new record: replacement survives");
eq(run.adopt({rating:4}), null, "a record with no source info leaves the default alone");

// --- the sourcing verdict -------------------------------------------------
// "add an additional button that says no eligible b-roll, to track sourcing
// needs" — the record has to carry the verdict AND what was on offer when it
// was given, or "no eligible b-roll" cannot be told from "nothing was fetched".
rate["02-02a"] = 4; note["02-02a"] = "needs the magazine";
pairs["02-02a"] = [{templateId: "t1", assets: ["a1"], at: "x"}];

let p = run.payload("02-02a", 5, "NOW");
eq(p.noBroll, false, "the verdict defaults to not-given");
eq(p.brollOffered, 5, "the record keeps how many clips were on offer");

nob["02-02a"] = true;
p = run.payload("02-02a", 5, "NOW");
eq(p.noBroll, true, "the verdict persists");
eq([p.beat, p.rating, p.note, p.brollOffered],
   ["02-02a", 4, "needs the magazine", 5],
   "none of 5 is a sourcing request, distinct from none of 0");
eq(run.payload("07-07", 0, "NOW").brollOffered, 0,
   "zero offered is recorded as zero, not as an absent field");
eq(Object.keys(run.payload("02-02a", 5, "NOW")).sort(),
   ["beat","broll","brollOffered","media","noBroll","note","pairs","rating","updatedAt"],
   "the record's shape is fixed");
eq(run.adopt({media:true, broll:true, noBroll:true}), {m:true, b:true},
   "adopt only reads source flags — the verdict is restored separately");

console.log(JSON.stringify(out));
process.exit(out.every(r => r.ok) ? 0 : 1);
