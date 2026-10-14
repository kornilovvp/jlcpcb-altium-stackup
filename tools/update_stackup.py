import re, sys, uuid, datetime

src, dst = sys.argv[1], sys.argv[2]
raw = open(src, encoding="utf-8-sig").read()
assert raw.startswith("|"), "unexpected format"
pairs = []
for tok in raw[1:].split("|"):
    k, v = tok.split("=", 1)
    pairs.append([k, v])

# ---- collect layer records (LAYER_V8_<n><suffix>) ----
lay_re = re.compile(r"^LAYER_V8_(\d+)(.*)$")
layers = {}        # old idx -> list of [suffix, value]
first_layer_pos = None
for i, (k, v) in enumerate(pairs):
    m = lay_re.match(k)
    if m:
        n = int(m.group(1))
        if first_layer_pos is None:
            first_layer_pos = i
        layers.setdefault(n, []).append([m.group(2), v])

SUB = "{6969CC32-488B-4AAE-B042-4AE22B2D483E}"   # Board Layer Stack id
PP_TYPE   = "{1A79611A-039D-4D40-A204-53C26C50F8B5}"
CORE_TYPE = "{136C62EF-1FA6-4897-AE71-7E797B632B92}"

# JLC08161H-7628 (Nan Ya NP-155F) parameters
PP_T   = "8.2835mil"   # 0.2104 mm, 7628*1
PP_ER  = "4.4"
CORE_T = "7.874mil"    # 0.20 mm core, H/HOZ, without copper
CORE_ER= "4.36"
IN_CU  = "0.5984mil"   # 0.0152 mm
OUT_CU = "1.378mil"    # 0.035 mm

def get(rec, suf):
    for s, v in rec:
        if s == suf: return v
    raise KeyError(suf)

def dielectric(old, new_name, kind):
    """rebuild a dielectric layer record from scratch, keeping its GUID"""
    gid = get(old, "ID")
    if kind == "pp":
        typeid, dt, th, er, mat = PP_TYPE, "2", PP_T, PP_ER, "7628*1"
        extra = [("$LSM$Material.Constructions", "7628"),
                 ("$LSM$Material.Resin", "49%")]
        desc = "NP-155F prepreg 7628 0.2104mm"
    else:
        typeid, dt, th, er, mat = CORE_TYPE, "1", CORE_T, CORE_ER, "NP-155F 0.2mm"
        extra = []
        desc = "NP-155F core 0.2mm H/HOZ (without copper)"
    assert get(old, "TYPEID") == typeid, f"type mismatch for {new_name}"
    rec = [("LAYERID", None), ("ID", gid), ("TYPEID", typeid), ("NAME", new_name),
           ("ISHIDDEN", "False"), ("USEDBYPRIMS", "False"),
           ("DIELTYPE", dt), ("DIELHEIGHT", th), ("DIELCONST", er), ("DIELMATERIAL", mat),
           ("$LSM$Thickness", th), ("$LSM$Material", mat),
           ("$LSM$DielectricConstant", er), ("$LSM$LossTangent", "0.02")]
    rec += extra
    rec += [("$LSM$Material.Frequency", "1GHz"),
            ("$LSM$Material.GlassTransTemp", "150C"),
            ("$LSM$Material.Manufacturer", "Nan Ya Plastics"),
            ("$LSM$Material.Description", desc),
            (f"_{SUB}CONTEXT", "0"), (f"_{SUB}USEDBYPRIMS", "False"),
            (f"_{SUB}NAME", new_name), (f"_{SUB}SHARED", "0")]
    return [list(x) for x in rec]

def copper(old, inner):
    rec = [list(x) for x in old]
    th = IN_CU if inner else OUT_CU
    for r in rec:
        if r[0] in ("COPTHICK", "$LSM$Thickness"): r[1] = th
        if inner and r[0] == "$LSM$Weight":   r[1] = "0.5oz"
        if inner and r[0] == "$LSM$Material": r[1] = "CF-003"
        if not inner and r[0] == "$LSM$Weight":   r[1] = "1oz"
        if not inner and r[0] == "$LSM$Material": r[1] = "CF-004"
    return rec

def keep(old):
    return [list(x) for x in old]

# new physical order: (old idx, builder)
plan = [
    (0,  keep(layers[0])),                               # Top Solder
    (1,  copper(layers[1], inner=False)),                # L1
    (2,  dielectric(layers[2],  "Dielectric 1", "pp")),  # 7628*1
    (3,  copper(layers[3], inner=True)),                 # L2
    (4,  dielectric(layers[4],  "Dielectric 2", "core")),# 0.2 core
    (5,  copper(layers[5], inner=True)),                 # L3
    (6,  dielectric(layers[6],  "Dielectric 3", "pp")),  # 7628*1   (old 7 = 2313 removed)
    (8,  copper(layers[8], inner=True)),                 # L4
    (9,  dielectric(layers[9],  "Dielectric 4", "core")),# 0.2 core
    (10, copper(layers[10], inner=True)),                # L5       (old 11 = 2313 removed)
    (12, dielectric(layers[12], "Dielectric 5", "pp")),  # 7628*1
    (13, copper(layers[13], inner=True)),                # L6
    (14, dielectric(layers[14], "Dielectric 6", "core")),# 0.2 core
    (15, copper(layers[15], inner=True)),                # L7
    (16, dielectric(layers[16], "Dielectric 7", "pp")),  # 7628*1
    (17, copper(layers[17], inner=False)),               # L8
    (18, keep(layers[18])),                              # Bottom Solder
]
removed = sorted(set(layers) - {o for o, _ in plan})
for o in removed:
    print("removed old layer", o, get(layers[o], "NAME"), get(layers[o], "DIELMATERIAL"), get(layers[o], "DIELHEIGHT"))

# sequential dielectric LAYERIDs by physical position (0x01040001 ...)
diel_id = 17039361
new_layer_pairs = []
for new_idx, (old_idx, rec) in enumerate(plan):
    for suf, val in rec:
        if suf == "LAYERID" and val is None:
            val = str(diel_id); diel_id += 1
        new_layer_pairs.append([f"LAYER_V8_{new_idx}{suf}", val])

# ---- reassemble ----
out = []
emitted = False
for k, v in pairs:
    if lay_re.match(k):
        if not emitted:
            out.extend(new_layer_pairs); emitted = True
        continue
    if k == "STACKUPDOCUMENTREVISIONID":
        v = "{" + str(uuid.uuid4()).upper() + "}"
    elif k == "STACKUPDOCUMENTREVISIONDATE":
        d = datetime.datetime.now()
        v = f"{d.month}/{d.day}/{d.year} {d.hour}:{d.minute:02d}:{d.second:02d}"
    out.append([k, v])

text = "|" + "|".join(f"{k}={v}" for k, v in out)
with open(dst, "w", encoding="utf-8-sig", newline="") as f:
    f.write(text)
print("layers:", len(plan), " pairs:", len(pairs), "->", len(out))
