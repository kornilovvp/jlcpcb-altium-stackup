import json
ER_CORE = {0.08: 3.99, 0.1: 4.36, 0.13: 4.17, 0.15: 4.36, 0.2: 4.36, 0.25: 4.23, 0.3: 4.41, 0.35: 4.36,
           0.4: 4.36, 0.45: 4.36, 0.5: 4.48, 0.55: 4.41, 0.6: 4.36, 0.65: 4.36, 0.7: 4.53}
ER_PP = {"7628": 4.4, "3313": 4.1, "2313": 4.1, "1080": 3.91, "2116": 4.16}
def er_core(th): return ER_CORE.get(th, 4.43)
def load(path):
    api = json.load(open(path, encoding="utf-8"))["data"]
    out = {}
    for t in api:
        seq = []
        for lam in sorted(t["iaminationList"], key=lambda x: x["sort"]):
            c = json.loads(lam["content"])
            if lam["iaminationType"] == 1:
                seq.append(("cu", c["LineLayer"], float(c["LineThickness"][:-2]), None))
            elif lam["iaminationType"] == 2:
                m = c["preMaterialType"]; seq.append(("pp", m, float(c["preThickness"][:-2]), ER_PP[m.split("*")[0]]))
            else:
                th = float(c["coreBoardThickness2"][:-2])
                seq.append(("cu", c["coreBoardLayer1"], float(c["coreBoardThickness1"][:-2]), None))
                seq.append(("core", f"core {th}", th, er_core(th)))
                seq.append(("cu", c["coreBoardLayer3"], float(c["coreBoardThickness3"][:-2]), None))
        out.setdefault(t["templateName"], (seq, t["compressionThickness"]))
    return out
def gaps(seq, a, b):
    cu = [i for i, s in enumerate(seq) if s[0] == "cu"]
    return [s for s in seq[cu[a]+1:cu[b]] if s[0] != "cu"]
