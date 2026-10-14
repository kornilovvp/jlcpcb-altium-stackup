"""Verify an Altium .stackup file against a JLCPCB template from the saved API JSON.

usage: python -I verify_stackup.py <api.json> <templateName> <file.stackup>
Checks layer order/type, thickness, Er (NP-155F table), internal consistency,
sequential dielectric LAYERIDs and that impedance/via-span references resolve.
Exit code 1 on any mismatch.
"""
import sys, os, re
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stacks8L import load

api_path, template, path = sys.argv[1:4]
MIL = 0.0254
SUBNAME = "_{6969CC32-488B-4AAE-B042-4AE22B2D483E}NAME"

seq, ct = load(api_path)[template]
ref = [(s[0], s[2], s[3]) for s in seq]

raw = open(path, encoding="utf-8-sig").read()
kv = dict(x.split("=", 1) for x in raw[1:].split("|"))
lay = re.compile(r"^LAYER_V8_(\d+)([A-Z$_].*)$")
layers = {}
for k, v in kv.items():
    m = lay.match(k)
    if m:
        layers.setdefault(int(m.group(1)), {})[m.group(2)] = v

st, lids, errors = [], [], []
for i in sorted(layers):
    L = layers[i]
    if L["NAME"] != L[SUBNAME]:
        errors.append(f"layer {i}: NAME mismatch")
    if "COPTHICK" in L:
        if L["COPTHICK"] != L["$LSM$Thickness"]:
            errors.append(f"layer {i}: COPTHICK != $LSM$Thickness")
        st.append(("cu", round(float(L["COPTHICK"][:-3]) * MIL, 4), None, f'{L["NAME"]} {L["$LSM$Weight"]} {L["$LSM$Material"]}'))
    elif L["DIELTYPE"] != "3":
        if L["DIELHEIGHT"] != L["$LSM$Thickness"] or L["DIELCONST"] != L["$LSM$DielectricConstant"]:
            errors.append(f"layer {i}: DIEL* != $LSM$*")
        lids.append(int(L["LAYERID"]))
        st.append(("core" if L["DIELTYPE"] == "1" else "pp", round(float(L["DIELHEIGHT"][:-3]) * MIL, 4), float(L["DIELCONST"]), f'{L["NAME"]} {L["DIELMATERIAL"]}'))

print(f"{path}  vs  {template}")
if len(st) != len(ref):
    errors.append(f"layer count {len(st)} != {len(ref)}")
for i, (r, o) in enumerate(zip(ref, st)):
    ok = r[0] == o[0] and abs(r[1] - o[1]) < 0.0005 and (r[2] is None or abs(r[2] - o[2]) < 1e-6)
    if not ok:
        errors.append(f"layer {i}: {r} vs {o[:3]}")
    print(f"  {i:>2} {r[0]:<5} JLC {r[1]:>7.4f} Er {str(r[2] or '-'):<5} | file {o[1]:>7.4f} Er {str(o[2] or '-'):<5} {o[3]:<34} {'ok' if ok else '<<< MISMATCH'}")
tot = round(sum(o[1] for o in st), 4)
if abs(tot - ct) > 0.0005:
    errors.append(f"total {tot} != JLC {ct}")
if lids != list(range(17039361, 17039361 + len(lids))):
    errors.append(f"dielectric LAYERIDs not sequential: {lids}")
ids = {L["ID"] for L in layers.values()}
dangling = [k for k, v in kv.items() if (k.startswith("TRACEIMPEDANCE") or k.startswith("VIASPAN"))
            and (k.endswith("LAYERID") or k.endswith("REFID")) and v not in ids]
if dangling:
    errors.append(f"dangling refs: {dangling}")
print(f"  total file {tot} / JLC {ct} mm, revision {kv['STACKUPDOCUMENTREVISIONDATE']}")
if errors:
    print("  ERRORS:"); [print("   -", e) for e in errors]; sys.exit(1)
print("  OK: 0 mismatches")
