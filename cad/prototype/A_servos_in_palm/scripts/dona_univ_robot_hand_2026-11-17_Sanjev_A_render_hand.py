"""Preview PNGs for prototype A (numpy z-buffer renderer, no OpenGL). Run after ..._A_build.py.
Green = Feetech STS3215 STEP model placed 5x + ring pulleys (reference only)."""
import os, sys, json
sys.dont_write_bytecode = True
import numpy as np, trimesh, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__))
import importlib.util as _iu
_ps = _iu.spec_from_file_location("p1paths", os.path.join(HERE, "dona_univ_robot_hand_2026-11-17_Sanjev_A_paths.py"))
paths = _iu.module_from_spec(_ps); _ps.loader.exec_module(paths); F = paths.F
L = lambda n: trimesh.load(F(n + ".stl"))
fr, bc, pc, gh = L("01_palm_frame"), L("02_back_cover"), L("03_palm_cover"), L("ref_sts3215_x5_placed")
BG = (0.86, 0.88, 0.91)        # light grey-blue background so white parts stay visible
def render(meshes, elev, azim, res=900, pad=8):
    e, a = np.radians(elev), np.radians(azim)
    d = np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])          # towards viewer
    up0 = np.array([0, 0, 1.0]) if abs(d[2]) < 0.95 else np.array([0, 1.0, 0])
    r = np.cross(up0, d); r /= np.linalg.norm(r); u = np.cross(d, r)
    allv = np.vstack([m.vertices + o for m, c, o in meshes])
    X, Y = allv @ r, allv @ u
    x0, x1, y0, y1 = X.min() - pad, X.max() + pad, Y.min() - pad, Y.max() + pad
    s = res / max(x1 - x0, y1 - y0); W, H = int((x1 - x0) * s) + 1, int((y1 - y0) * s) + 1
    zb = np.full((H, W), -1e9); img = np.ones((H, W, 3)) * np.array(BG)[None, None, :]
    L = np.array([0.35, -0.45, 0.82]); L = L / np.linalg.norm(L)
    for m, col, off in meshes:
        v = m.vertices + off; tri = v[m.faces]
        px = ((tri @ r) - x0) * s; py = (y1 - (tri @ u)) * s; pz = tri @ d
        n = m.face_normals; vis = (n @ d) > -1e-6
        shade = 0.55 + 0.45 * np.abs(n @ (0.6 * L + 0.4 * d) / np.linalg.norm(0.6 * L + 0.4 * d))
        col = np.array(matplotlib.colors.to_rgb(col))
        for i in np.nonzero(vis)[0]:
            xs, ys, zs = px[i], py[i], pz[i]
            ix0, ix1 = max(int(xs.min()), 0), min(int(xs.max()) + 1, W - 1)
            iy0, iy1 = max(int(ys.min()), 0), min(int(ys.max()) + 1, H - 1)
            if ix1 < ix0 or iy1 < iy0: continue
            gx, gy = np.meshgrid(np.arange(ix0, ix1 + 1) + 0.5, np.arange(iy0, iy1 + 1) + 0.5)
            (xa, xb, xc), (ya, yb, yc) = xs, ys
            den = (yb - yc) * (xa - xc) + (xc - xb) * (ya - yc)
            if abs(den) < 1e-12: continue
            w1 = ((yb - yc) * (gx - xc) + (xc - xb) * (gy - yc)) / den
            w2 = ((yc - ya) * (gx - xc) + (xa - xc) * (gy - yc)) / den
            w3 = 1 - w1 - w2
            msk = (w1 >= -1e-3) & (w2 >= -1e-3) & (w3 >= -1e-3)
            if not msk.any(): continue
            z = w1 * zs[0] + w2 * zs[1] + w3 * zs[2]
            sub = zb[iy0:iy1 + 1, ix0:ix1 + 1]; upd = msk & (z > sub)
            sub[upd] = z[upd]; img[iy0:iy1 + 1, ix0:ix1 + 1][upd] = col * shade[i]
    return img

def dec(m, n=50000):
    return m.simplify_quadric_decimation(face_count=n) if len(m.faces) > n else m
FR, BC, PC, G = dec(fr), dec(bc), dec(pc), dec(gh, 60000)
Z = np.zeros(3)
W, GR, BL, OR = "#ffffff", "#2b2b2b", "#ffffff", "#141416"     # frame white, back cover white, palm cover black (user 2026-11-17)
views = [
    ("img_01_top_like_photo.png", [(FR, W, Z), (G, GR, Z)], 89.9, -90, "Prototype A - 5 x STS3215 in the enlarged InMoov palm (back of hand, cover off)"),
    ("img_02_exploded.png", [(FR, W, Z), (G, GR, Z), (BC, BL, np.array([0, 0, 45.0])), (PC, OR, np.array([0, 0, -45.0]))], 28, -60, "Exploded: back cover (blue), frame + servos, palm cover (orange)"),
    ("img_03_assembled_back.png", [(FR, W, Z), (BC, BL, Z), (PC, OR, Z)], 35, -115, "Assembled - back of hand"),
    ("img_04_assembled_palm.png", [(FR, W, Z), (BC, BL, Z), (PC, OR, Z), (G, GR, Z)], -40, -70, "Assembled - palm side (servo bottoms show through, like InMoov PDI build)"),
]
for name, ms, el, az, title in views:
    img = render(ms, el, az)
    fig = plt.figure(figsize=(9, 9 * img.shape[0] / img.shape[1] + 0.6)); plt.imshow(img); plt.axis("off"); plt.title(title, fontsize=10)
    fig.text(0.01, 0.005, "HAEBOT prototype A = InMoov i2 palm parts x1.28, modified for 5 x STS3215. Real CAD export, not printed.", fontsize=8)
    plt.savefig(F(name), dpi=100, bbox_inches="tight"); plt.close(fig)
print("ok")
