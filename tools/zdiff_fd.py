import numpy as np, scipy.sparse as sp, scipy.sparse.linalg as spl
EPS0 = 8.854187817e-12; CL = 299792458.0

def _solve(er, fixed_mask, fixed_val):
    ny, nx = er.shape                      # cells
    NY, NX = ny + 1, nx + 1                # nodes
    erp = np.pad(er, 1, mode="edge")       # erp[j+1, i+1] == er[j, i]
    # horizontal edge (j,i)-(j,i+1): cells below (j-1,i) and above (j,i)
    ch = 0.5 * (erp[0:NY, 1:NX] + erp[1:NY+1, 1:NX])      # shape (NY, nx)
    # vertical edge (j,i)-(j+1,i): cells left (j,i-1) and right (j,i)
    cv = 0.5 * (erp[1:NY, 0:NX] + erp[1:NY, 1:NX+1])      # shape (ny, NX)
    idx = np.arange(NY * NX).reshape(NY, NX)
    rows, cols, vals = [], [], []
    def add(a, b, c):
        rows.append(a.ravel()); cols.append(b.ravel()); vals.append(c.ravel())
    a, b = idx[:, :-1], idx[:, 1:]
    add(a, b, ch); add(b, a, ch); add(a, a, -ch); add(b, b, -ch)
    a, b = idx[:-1, :], idx[1:, :]
    add(a, b, cv); add(b, a, cv); add(a, a, -cv); add(b, b, -cv)
    A = sp.coo_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(NY*NX, NY*NX)).tocsr()
    f = fixed_mask.ravel(); fv = fixed_val.ravel()
    # Dirichlet rows
    D = sp.diags((~f).astype(float)); I = sp.diags(f.astype(float))
    A2 = D @ A + I
    b2 = np.where(f, fv, 0.0)
    phi = spl.spsolve(A2.tocsc(), b2).reshape(NY, NX)
    W = 0.5 * EPS0 * (np.sum(ch * (phi[:, 1:] - phi[:, :-1])**2) + np.sum(cv * (phi[1:, :] - phi[:-1, :])**2))
    return W

def build(up, dn, w, s, t=0.0152, d=0.005, margin=1.0, single=False):
    """up/dn: lists of (thickness_mm, er) starting from the trace going outward to the plane."""
    Hd = sum(th for th, _ in dn); Hu = sum(th for th, _ in up)
    nt = max(1, int(round(t / d))); nw = max(1, int(round(w / d))); ns = int(round(s / d)); nm = int(round(margin / d))
    nd = [int(round(th / d)) for th, _ in dn]; nu = [int(round(th / d)) for th, _ in up]
    ny = sum(nd) + nt + sum(nu); nx = 2 * nm + (nw if single else 2 * nw + ns)
    er = np.ones((ny, nx)); y = 0
    for n, (th, e) in zip(reversed(nd), reversed(dn)): er[y:y+n, :] = e; y += n
    y_t0 = y; er[y:y+nt, :] = dn[0][1]; y += nt
    for n, (th, e) in zip(nu, up): er[y:y+n, :] = e; y += n
    NY, NX = ny + 1, nx + 1
    fm = np.zeros((NY, NX), bool); fv = np.zeros((NY, NX))
    fm[0, :] = fm[-1, :] = fm[:, 0] = fm[:, -1] = True
    if single:
        fm[y_t0:y_t0+nt+1, nm:nm+nw+1] = True; fv[y_t0:y_t0+nt+1, nm:nm+nw+1] = 1.0
    else:
        fm[y_t0:y_t0+nt+1, nm:nm+nw+1] = True; fv[y_t0:y_t0+nt+1, nm:nm+nw+1] = 0.5
        x2 = nm + nw + ns
        fm[y_t0:y_t0+nt+1, x2:x2+nw+1] = True; fv[y_t0:y_t0+nt+1, x2:x2+nw+1] = -0.5
    return er, fm, fv

def zdiff(up, dn, w, s, **kw):
    er, fm, fv = build(up, dn, w, s, **kw)
    C = 4 * _solve(er, fm, fv); C0 = 4 * _solve(np.ones_like(er), fm, fv)
    zodd = 1 / (CL * np.sqrt(C * C0)); return 2 * zodd, np.sqrt(C / C0)

def z0(up, dn, w, **kw):
    er, fm, fv = build(up, dn, w, 0, single=True, **kw)
    C = 2 * _solve(er, fm, fv); C0 = 2 * _solve(np.ones_like(er), fm, fv)
    return 1 / (CL * np.sqrt(C * C0))

def find_w(up, dn, s, target=100.0, lo=0.05, hi=0.40, d=0.005):
    # Zdiff decreases with w; bisection on the 5um grid
    nlo, nhi = int(round(lo / d)), int(round(hi / d))
    zlo = zdiff(up, dn, nlo * d, s, d=d)[0]; zhi = zdiff(up, dn, nhi * d, s, d=d)[0]
    if zlo < target: return nlo * d, zlo
    if zhi > target: return nhi * d, zhi
    while nhi - nlo > 1:
        mid = (nlo + nhi) // 2
        z = zdiff(up, dn, mid * d, s, d=d)[0]
        if z > target: nlo, zlo = mid, z
        else: nhi, zhi = mid, z
    # linear interpolation between grid points
    w = nlo * d + (zlo - target) / (zlo - zhi) * d
    return w, None
