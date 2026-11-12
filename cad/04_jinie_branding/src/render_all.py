"""Before/after renders: lit orthographic close-ups (ray-cast height map) + 3D overviews.

From the repo root (defaults to the icon+text cover):
  python cad/04_jinie_branding/src/render_all.py
  python cad/04_jinie_branding/src/render_all.py cad/04_jinie_branding/stl/JE_HandCoverV1_JinieIconOnly.stl icon_only
"""
import sys, numpy as np, trimesh, matplotlib, pathlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.colors import LightSource
from render_util import render

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent          # cad/04_jinie_branding
CAD = ROOT.parent           # cad
OFFICIAL = CAD / "01_official_inmoov_i2" / "print" / "i2_HandCoverV1.stl"
DEFAULT_AFTER = ROOT / "stl" / "JE_HandCoverV1_JinieLogo.stl"

before = trimesh.load(OFFICIAL)
after_path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_AFTER
if not after_path.is_absolute():
    after_path = (pathlib.Path.cwd() / after_path).resolve()
after = trimesh.load(after_path)
tag = sys.argv[2] if len(sys.argv) > 2 else "icon_text"
R = ROOT / "renders"; R.mkdir(exist_ok=True)

def hmap(m, x0, x1, z0, z1, res):
    xs = np.arange(x0, x1, res) + 0.00731; zs = np.arange(z0, z1, res) + 0.00419; X, Z = np.meshgrid(xs, zs)  # jitter: avoid edge hits
    o = np.c_[X.ravel(), np.full(X.size, 40.0), Z.ravel()]
    loc, ri, _ = m.ray.intersects_location(o, np.tile([0, -1, 0], (len(o), 1)), multiple_hits=False)
    H = np.full(X.size, np.nan); H[ri] = loc[:, 1]; return H.reshape(X.shape)

def shade(H, res):
    from scipy.ndimage import gaussian_filter
    nan = np.isnan(H); Hf = np.where(nan, np.nanmin(H) - 2, H)
    D = Hf - gaussian_filter(Hf, 2.5 / res)                      # local relief -> colour
    col = plt.cm.Blues_r(np.clip((D + 1.6) / 2.0, 0, 1))[:, :, :3] * 0.6 + 0.4
    rgb = LightSource(azdeg=315, altdeg=35).shade_rgb(col, Hf, vert_exag=2.0, blend_mode="soft", dx=res, dy=res)
    rgb[nan] = 1; return rgb

def outside_view(ax, m, box, res, title):
    x0, x1, z0, z1 = box
    H = hmap(m, x0, x1, z0, z1, res)
    H = np.fliplr(H)   # seen from outside (+Y): +X is on the LEFT
    rgb = shade(H, res)
    ax.imshow(rgb, origin="lower", extent=[x1, x0, z0, z1]); ax.set_title(title)
    ax.set_xlabel("X (mm)  - viewed from outside, wrist at bottom"); ax.set_ylabel("Z (mm)")

# close-up logo strip, before / after
fig, axs = plt.subplots(1, 2, figsize=(9, 14))
for ax, m, t in [(axs[0], before, "BEFORE (InMoov engraving)"), (axs[1], after, f"AFTER ({tag})")]:
    outside_view(ax, m, (36, 59, 16, 90), 0.06, t)
fig.tight_layout(); fig.savefig(R / f"closeup_before_after_{tag}.png", dpi=110); plt.close(fig)

# logo rotated to read horizontally (as a person reads it)
fig, axs = plt.subplots(2, 1, figsize=(14, 7))
for ax, m, t in [(axs[0], before, "before"), (axs[1], after, tag)]:
    H = hmap(m, 39, 56, 19, 87, 0.04); H = np.fliplr(H)        # outside view; row 0 = wrist (bottom)
    img = np.flipud(shade(H, 0.04))                             # as displayed (row 0 = top)
    ax.imshow(np.rot90(img, -1)); ax.set_axis_off()             # turn 90 deg CW -> reads left to right
    ax.set_title(f"{t}: logo strip seen from outside, turned 90 deg so it reads left-to-right (wrist on the left)")
fig.tight_layout(); fig.savefig(R / f"logo_readable_{tag}.png", dpi=110); plt.close(fig)

# full outside view before / after
fig, axs = plt.subplots(1, 2, figsize=(16, 9.5))
for ax, m, t in [(axs[0], before, "BEFORE"), (axs[1], after, f"AFTER ({tag})")]:
    outside_view(ax, m, (-1, 91.5, -1, 108.5), 0.12, t)
fig.tight_layout(); fig.savefig(R / f"full_before_after_{tag}.png", dpi=100); plt.close(fig)

# 3D iso overview of the result
render(after, R / f"iso_{tag}.png", elev=25, azim=110, title=f"{tag} - 3D view (outer face)", size=8)
print("renders done ->", R)
