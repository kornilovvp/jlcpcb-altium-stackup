"""Build an Altium .stackup file for a JLCPCB template from the saved API JSON.

usage: python -I build_stackup.py <api.json> <templateName> <donor.stackup> <out.stackup>

The donor supplies the document header, solder mask layers, the 8 copper layers
(with their GUIDs, so impedance profiles keep working) and a pool of dielectric
GUIDs.  Dielectric layers are rebuilt from the API data with NP-155F Er values.
"""
import sys, os, re, uuid, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stacks8L import load

api_path, template, donor, out = sys.argv[1:5]

SUB = "{6969CC32-488B-4AAE-B042-4AE22B2D483E}"      # Board Layer Stack id (donor)
PP_TYPE = "{1A79611A-039D-4D40-A204-53C26C50F8B5}"
CORE_TYPE = "{136C62EF-1FA6-4897-AE71-7E797B632B92}"
RESIN = {"7628": "49%", "3313": "57%", "2313": "57%", "1080": "67%", "2116": "54%"}
MIL = 0.0254

def mil(mm):
    return f"{mm / MIL:.4f}".rstrip("0").rstrip(".") + "mil"

# ---- donor ----
raw = open(donor, encoding="utf-8-sig").read()
pairs = [tok.split("=", 1) for tok in raw[1:].split("|")]
lay_re = re.compile(r"^LAYER_V8_(\d+)(.*)$")
layers = {}
for k, v in pairs:
    m = lay_re.match(k)
    if m:
        layers.setdefault(int(m.group(1)), []).append([m.group(2), v])
get = lambda rec, suf: next(v for s, v in rec if s == suf)
by_name = {get(r, "NAME"): r for r in layers.values()}
diel_guids = [get(r, "ID") for i, r in sorted(layers.items()) if get(r, "TYPEID") in (PP_TYPE, CORE_TYPE)]
assert get(layers[0], "NAME") == "Top Solder" and get(layers[max(layers)], "NAME") == "Bottom Solder"

# ---- API sequence ----
seq, ct = load(api_path)[template]

def dielectric(name, gid, kind, label, th_mm, er):
    if kind == "pp":
        constr = label.split("*")[0]
        typeid, dt, mat = PP_TYPE, "2", label
        extra = [("$LSM$Material.Constructions", constr), ("$LSM$Material.Resin", RESIN[constr])]
        desc = f"NP-155F prepreg {constr} {th_mm:.4f}mm"
    else:
        typeid, dt, mat = CORE_TYPE, "1", f"NP-155F {th_mm:g}mm"
        extra = []
        desc = f"NP-155F core {th_mm:.2f}mm H/HOZ (without copper)"
    th = mil(th_mm)
    rec = [("LAYERID", None), ("ID", gid), ("TYPEID", typeid), ("NAME", name),
           ("ISHIDDEN", "False"), ("USEDBYPRIMS", "False"),
           ("DIELTYPE", dt), ("DIELHEIGHT", th), ("DIELCONST", str(er)), ("DIELMATERIAL", mat),
           ("$LSM$Thickness", th), ("$LSM$Material", mat),
           ("$LSM$DielectricConstant", str(er)), ("$LSM$LossTangent", "0.02")] + extra + [
           ("$LSM$Material.Frequency", "1GHz"), ("$LSM$Material.GlassTransTemp", "150C"),
           ("$LSM$Material.Manufacturer", "Nan Ya Plastics"), ("$LSM$Material.Description", desc),
           (f"_{SUB}CONTEXT", "0"), (f"_{SUB}USEDBYPRIMS", "False"), (f"_{SUB}NAME", name), (f"_{SUB}SHARED", "0")]
    return [list(x) for x in rec]

def copper(rec, th_mm, inner):
    rec = [list(x) for x in rec]
    for r in rec:
        if r[0] in ("COPTHICK", "$LSM$Thickness"): r[1] = mil(th_mm)
        if r[0] == "$LSM$Weight":   r[1] = "0.5oz" if inner else "1oz"
        if r[0] == "$LSM$Material": r[1] = "CF-003" if inner else "CF-004"
    return rec

plan = [[list(x) for x in layers[0]]]           # Top Solder
cu_i, di_i = 0, 0
for kind, label, th, er in seq:
    if kind == "cu":
        cu_i += 1
        plan.append(copper(by_name[f"L{cu_i}"], th, inner=1 < cu_i < 8))
    else:
        di_i += 1
        gid = diel_guids[di_i - 1] if di_i <= len(diel_guids) else "{" + str(uuid.uuid4()).upper() + "}"
        plan.append(dielectric(f"Dielectric {di_i}", gid, kind, label, th, er))
plan.append([list(x) for x in layers[max(layers)]])  # Bottom Solder
assert cu_i == 8, cu_i

diel_id = 17039361
new_pairs = []
for idx, rec in enumerate(plan):
    for suf, val in rec:
        if suf == "LAYERID" and val is None:
            val = str(diel_id); diel_id += 1
        new_pairs.append([f"LAYER_V8_{idx}{suf}", val])

outp, emitted = [], False
for k, v in pairs:
    if lay_re.match(k):
        if not emitted:
            outp.extend(new_pairs); emitted = True
        continue
    if k == "STACKUPDOCUMENTREVISIONID":
        v = "{" + str(uuid.uuid4()).upper() + "}"
    elif k == "STACKUPDOCUMENTREVISIONDATE":
        d = datetime.datetime.now()
        v = f"{d.month}/{d.day}/{d.year} {d.hour}:{d.minute:02d}:{d.second:02d}"
    outp.append([k, v])
with open(out, "w", encoding="utf-8-sig", newline="") as f:
    f.write("|" + "|".join(f"{k}={v}" for k, v in outp))
print(f"{template}: {len(plan)} layers ({di_i} dielectric), JLC total {ct} mm -> {out}")
