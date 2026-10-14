import re, sys, uuid, datetime

src, dst = sys.argv[1], sys.argv[2]
raw = open(src, encoding="utf-8-sig").read()
pairs = [tok.split("=", 1) for tok in raw[1:].split("|")]
lay_re = re.compile(r"^LAYER_V8_(\d+)(.*)$")
layers = {}
for k, v in pairs:
    m = lay_re.match(k)
    if m: layers.setdefault(int(m.group(1)), []).append([m.group(2), v])

SUB = "{6969CC32-488B-4AAE-B042-4AE22B2D483E}"
PP_TYPE   = "{1A79611A-039D-4D40-A204-53C26C50F8B5}"
CORE_TYPE = "{136C62EF-1FA6-4897-AE71-7E797B632B92}"

# JLC08161H-2313 (Nan Ya NP-155F) materials
MAT = {
 "pp2313": dict(kind="pp",   th="3.7953mil",  er="4.1",  mat="2313*1",        constr="2313", resin="57%", desc="NP-155F prepreg 2313 0.0964mm"),
 "pp7628": dict(kind="pp",   th="8.2047mil",  er="4.4",  mat="7628*1",        constr="7628", resin="49%", desc="NP-155F prepreg 7628 0.2084mm"),
 "core013":dict(kind="core", th="5.1181mil",  er="4.17", mat="NP-155F 0.13mm", desc="NP-155F core 0.13mm H/HOZ (without copper)"),
 "core030":dict(kind="core", th="11.811mil",  er="4.41", mat="NP-155F 0.3mm",  desc="NP-155F core 0.30mm H/HOZ (without copper)"),
}

def get(rec, suf):
    return next(v for s, v in rec if s == suf)

def dielectric(old, name, key):
    m = MAT[key]
    typeid, dt = (PP_TYPE, "2") if m["kind"] == "pp" else (CORE_TYPE, "1")
    assert get(old, "TYPEID") == typeid, f"type mismatch {name}"
    rec = [("LAYERID", None), ("ID", get(old, "ID")), ("TYPEID", typeid), ("NAME", name),
           ("ISHIDDEN", "False"), ("USEDBYPRIMS", "False"),
           ("DIELTYPE", dt), ("DIELHEIGHT", m["th"]), ("DIELCONST", m["er"]), ("DIELMATERIAL", m["mat"]),
           ("$LSM$Thickness", m["th"]), ("$LSM$Material", m["mat"]),
           ("$LSM$DielectricConstant", m["er"]), ("$LSM$LossTangent", "0.02")]
    if m["kind"] == "pp":
        rec += [("$LSM$Material.Constructions", m["constr"]), ("$LSM$Material.Resin", m["resin"])]
    rec += [("$LSM$Material.Frequency", "1GHz"), ("$LSM$Material.GlassTransTemp", "150C"),
            ("$LSM$Material.Manufacturer", "Nan Ya Plastics"), ("$LSM$Material.Description", m["desc"]),
            (f"_{SUB}CONTEXT", "0"), (f"_{SUB}USEDBYPRIMS", "False"), (f"_{SUB}NAME", name), (f"_{SUB}SHARED", "0")]
    return [list(x) for x in rec]

def copper(old, inner):
    rec = [list(x) for x in old]
    for r in rec:
        if r[0] in ("COPTHICK", "$LSM$Thickness"): r[1] = "0.5984mil" if inner else "1.378mil"
        if r[0] == "$LSM$Weight":   r[1] = "0.5oz"  if inner else "1oz"
        if r[0] == "$LSM$Material": r[1] = "CF-003" if inner else "CF-004"
    return rec

keep = lambda old: [list(x) for x in old]
plan = [
    keep(layers[0]),                                   # Top Solder
    copper(layers[1], False),                          # L1
    dielectric(layers[2],  "Dielectric 1", "pp2313"),  # was 0.208mm Er4.5 -> 2313*1
    copper(layers[3], True),                           # L2
    dielectric(layers[4],  "Dielectric 2", "core013"),
    copper(layers[5], True),                           # L3
    dielectric(layers[6],  "Dielectric 3", "pp7628"),
    dielectric(layers[7],  "Dielectric 4", "pp2313"),
    copper(layers[8], True),                           # L4
    dielectric(layers[9],  "Dielectric 5", "core030"),
    copper(layers[10], True),                          # L5
    dielectric(layers[11], "Dielectric 6", "pp2313"),
    dielectric(layers[12], "Dielectric 7", "pp7628"),
    copper(layers[13], True),                          # L6
    dielectric(layers[14], "Dielectric 8", "core013"),
    copper(layers[15], True),                          # L7
    dielectric(layers[16], "Dielectric 9", "pp2313"),  # was 0.208mm Er4.5 -> 2313*1
    copper(layers[17], False),                         # L8
    keep(layers[18]),                                  # Bottom Solder
]
assert len(plan) == len(layers) == 19

diel_id = 17039361
new_layer_pairs = []
for idx, rec in enumerate(plan):
    for suf, val in rec:
        if suf == "LAYERID" and val is None:
            val = str(diel_id); diel_id += 1
        new_layer_pairs.append([f"LAYER_V8_{idx}{suf}", val])

out, emitted = [], False
for k, v in pairs:
    if lay_re.match(k):
        if not emitted: out.extend(new_layer_pairs); emitted = True
        continue
    if k == "STACKUPDOCUMENTREVISIONID": v = "{" + str(uuid.uuid4()).upper() + "}"
    elif k == "STACKUPDOCUMENTREVISIONDATE":
        d = datetime.datetime.now(); v = f"{d.month}/{d.day}/{d.year} {d.hour}:{d.minute:02d}:{d.second:02d}"
    out.append([k, v])
with open(dst, "w", encoding="utf-8-sig", newline="") as f:
    f.write("|" + "|".join(f"{k}={v}" for k, v in out))
print("written", dst, "pairs", len(pairs), "->", len(out))
