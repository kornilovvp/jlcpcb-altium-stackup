"""Build an Altium .stackup file for a JLCPCB template from the saved API JSON.

usage: python -I build_stackup.py <api.json> <templateName> <donor.stackup> <out.stackup>

The donor supplies the document header, solder mask layers, the copper layers
(with their GUIDs, so impedance profiles keep working) and a pool of dielectric
GUIDs.  Dielectric layers are rebuilt from the API data with NP-155F Er values.

A template with fewer copper layers than the donor keeps the donor's outer halves
(4L from 8L: L1 L2 + L7 L8 -> L1..L4, renamed and renumbered); impedance entries
and via spans that reference a dropped layer are removed.
"""
import sys, os, re, uuid, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stacks8L import load

api_path, template, donor, out = sys.argv[1:5]

SUB = "{6969CC32-488B-4AAE-B042-4AE22B2D483E}"      # Board Layer Stack id (donor)
PP_TYPE = "{1A79611A-039D-4D40-A204-53C26C50F8B5}"
CORE_TYPE = "{136C62EF-1FA6-4897-AE71-7E797B632B92}"
CU_TYPE = "{F4ECCD87-2CFB-4F37-BE50-4F3A272B4D01}"
TOP_LAYERID, BOTTOM_LAYERID = 16777217, 16842751    # mid layers follow Top: 16777218, ...
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
donor_cu = [r for i, r in sorted(layers.items()) if get(r, "TYPEID") == CU_TYPE]
diel_guids = [get(r, "ID") for i, r in sorted(layers.items()) if get(r, "TYPEID") in (PP_TYPE, CORE_TYPE)]
assert get(layers[0], "NAME") == "Top Solder" and get(layers[max(layers)], "NAME") == "Bottom Solder"

# ---- API sequence ----
seq, ct = load(api_path)[template]
n_cu = sum(s[0] == "cu" for s in seq)
assert n_cu % 2 == 0 and n_cu <= len(donor_cu), (n_cu, len(donor_cu))
cu_recs = donor_cu[:n_cu // 2] + donor_cu[len(donor_cu) - n_cu // 2:]

def dielectric(name, gid, kind, label, th_mm, er):
    if kind == "pp":
        constr = label.split("*")[0]
        typeid, dt, mat = PP_TYPE, "2", label
        extra = [("$LSM$Material.Constructions", constr), ("$LSM$Material.Resin", RESIN[constr])]
        desc = f"NP-155F prepreg {constr} {th_mm:.4f}mm"
    else:
        typeid, dt, mat = CORE_TYPE, "1", f"NP-155F {th_mm:g}mm"
        extra = []
        desc = f"NP-155F core {th_mm:.2f}mm H/HOZ (without copper)" if th_mm == round(th_mm, 2) else \
               f"NP-155F core {th_mm:g}mm H/HOZ (without copper)"
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

def copper(rec, idx, th_mm):
    inner = 0 < idx < n_cu - 1
    lid = BOTTOM_LAYERID if idx == n_cu - 1 else TOP_LAYERID + idx
    rec = [list(x) for x in rec]
    for r in rec:
        if r[0] == "LAYERID": r[1] = str(lid)
        if r[0] in ("NAME", f"_{SUB}NAME"): r[1] = f"L{idx + 1}"
        if r[0] in ("COPTHICK", "$LSM$Thickness"): r[1] = mil(th_mm)
        if r[0] == "$LSM$Weight":   r[1] = "0.5oz" if inner else "1oz"
        if r[0] == "$LSM$Material": r[1] = "CF-003" if inner else "CF-004"
    return rec

plan = [[list(x) for x in layers[0]]]           # Top Solder
cu_i, di_i = 0, 0
for kind, label, th, er in seq:
    if kind == "cu":
        plan.append(copper(cu_recs[cu_i], cu_i, th))
        cu_i += 1
    else:
        di_i += 1
        gid = diel_guids[di_i - 1] if di_i <= len(diel_guids) else "{" + str(uuid.uuid4()).upper() + "}"
        plan.append(dielectric(f"Dielectric {di_i}", gid, kind, label, th, er))
plan.append([list(x) for x in layers[max(layers)]])  # Bottom Solder

# impedance entries / via spans: drop those that point at a dropped copper layer, renumber the rest
kept = {get(r, "ID") for r in plan}
grp_re = re.compile(r"^(TRACEIMPEDANCE_V8_|VIASPAN_V8_\{[^}]+\}_)(\d+)(\D.*)$")
dead, renum = set(), {}
for k, v in pairs:
    m = grp_re.match(k)
    if m and m.group(3).endswith(("LAYERID", "REFID")) and v not in kept:
        dead.add(m.group(1, 2))
for k, v in pairs:
    m = grp_re.match(k)
    if m and m.group(1, 2) not in dead and m.group(1, 2) not in renum:
        renum[m.group(1, 2)] = sum(p == m.group(1) for p, _ in renum)

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
    m = grp_re.match(k)
    if m:
        if m.group(1, 2) in dead:
            continue
        k = f"{m.group(1)}{renum[m.group(1, 2)]}{m.group(3)}"
    if k.startswith("VIASPAN_V8_") and k.endswith("NAME") and re.fullmatch(r"Thru 1:\d+", v):
        v = f"Thru 1:{n_cu}"
    if k == "STACKUPDOCUMENTREVISIONID":
        v = "{" + str(uuid.uuid4()).upper() + "}"
    elif k == "STACKUPDOCUMENTREVISIONDATE":
        d = datetime.datetime.now()
        v = f"{d.month}/{d.day}/{d.year} {d.hour}:{d.minute:02d}:{d.second:02d}"
    outp.append([k, v])
with open(out, "w", encoding="utf-8-sig", newline="") as f:
    f.write("|" + "|".join(f"{k}={v}" for k, v in outp))
print(f"{template}: {len(plan)} layers ({n_cu} copper, {di_i} dielectric), JLC total {ct} mm, "
      f"{len(dead)} impedance/via entries dropped -> {out}")
