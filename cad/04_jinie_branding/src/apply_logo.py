"""Replace the engraved "InMoov" text on InMoov i2 HandCoverV1 with the Jinie EduTech logo.

Parametric: every size/position lives in logo_params.yaml. Pipeline (mesh booleans via manifold3d):
 1. Ray-cast a height map of the outer (+Y) surface inside old_logo box.
 2. Fit a smooth surface (robust polynomial), mark pixels deeper than detect_threshold as the old
    engraving, and rebuild the surface over them with biharmonic inpainting.
 3. Union a thin "filler" height-field solid whose top is the rebuilt surface -> old text gone, flush.
 4. Build the logo in 2D (traced icon + font outlines), map it onto the strip (reading wrist->fingers,
    letter tops toward +X, so it reads correctly from outside) and cut/add it as a prism clipped to a
    slab that follows the surface at constant depth. variant "none" stops after the filler (blank cover).
 5. Export STL, 2D DXF of the logo, and a JSON report.

Paths in the YAML are relative to cad/04_jinie_branding/. Run from the repo root:
  python cad/04_jinie_branding/src/apply_logo.py
  python cad/04_jinie_branding/src/apply_logo.py cad/04_jinie_branding/src/logo_params_icon_only.yaml
  python cad/04_jinie_branding/src/apply_logo.py cad/04_jinie_branding/src/logo_params_nologo.yaml
Faceted STEP (optional): python cad/src/stl_to_step.py <stl> <step>
"""
import sys, json, pathlib
import numpy as np, trimesh, yaml, cv2
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union
from shapely import affinity
from skimage.restoration import inpaint_biharmonic
from skimage.morphology import skeletonize
from scipy.ndimage import binary_dilation
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent  # cad/04_jinie_branding

yaml_arg = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "logo_params.yaml"
yaml_path = yaml_arg if yaml_arg.is_absolute() else (pathlib.Path.cwd() / yaml_arg).resolve()
P = yaml.safe_load(yaml_path.read_text())
L = P["logo"]; OL = P["old_logo"]; RES = P["grid_res"]


def resolve(p):
    p = pathlib.Path(p)
    return p if p.is_absolute() else (ROOT / p).resolve()

OUT = resolve(P.get("output_dir", "stl")); OUT.mkdir(parents=True, exist_ok=True)
DXF_DIR = resolve(P.get("dxf_dir", "dxf")); DXF_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR = resolve(P.get("report_dir", "reports")); REPORT_DIR.mkdir(parents=True, exist_ok=True)
NAME = P["output_name"]

orig = trimesh.load(resolve(P["source_stl"]))
assert orig.is_watertight, "source must be watertight"

# ---------------------------------------------------------------- 1. height map
x0, x1 = OL["box_x"]; z0, z1 = OL["box_z"]
# window must also cover the new logo footprint
half_len = L["total_length"] / 2 + 1; half_w = L["icon_height"] / 2 + 1
wx0, wx1 = min(x0, L["center_x"] - half_w), max(x1, L["center_x"] + half_w)
wz0, wz1 = min(z0, L["center_z"] - half_len), max(z1, L["center_z"] + half_len)
xs = np.arange(wx0, wx1 + RES / 2, RES); zs = np.arange(wz0, wz1 + RES / 2, RES)
X, Z = np.meshgrid(xs, zs)
o = np.c_[X.ravel(), np.full(X.size, orig.bounds[1, 1] + 10), Z.ravel()]
loc, ri, _ = orig.ray.intersects_location(o, np.tile([0, -1, 0], (len(o), 1)), multiple_hits=False)
H = np.full(X.size, np.nan); H[ri] = loc[:, 1]; H = H.reshape(X.shape)
assert not np.isnan(H).any(), "window runs off the part - adjust old_logo box / logo position"
from scipy.ndimage import median_filter
assert (np.abs(H - median_filter(H, 5)) > 3).sum() == 0, "ray-cast spike in height map"

# ---------------------------------------------------------------- 2. detect + rebuild
def basis(x, z, d=4):
    x = (x - X.mean()) / np.ptp(X); z = (z - Z.mean()) / np.ptp(Z)
    return np.stack([x**i * z**j for i in range(d + 1) for j in range(d + 1 - i)], -1)
A = basis(X, Z); keep = np.ones_like(H, bool)
for _ in range(10):
    c, *_ = np.linalg.lstsq(A[keep], H[keep], rcond=None)
    r = H - A @ c; keep = r > -0.4
inbox = (X >= x0) & (X <= x1) & (Z >= z0) & (Z <= z1)
old = inbox & (r < -OL["detect_threshold"])
old_d = binary_dilation(old, iterations=max(1, int(round(OL.get("mask_grow", 0.2) / RES)))) & inbox
S = inpaint_biharmonic(H, old_d)              # rebuilt, logo-free outer surface
old_depth = float(np.median(-r[old])) if old.any() else 0.0

def heightfield_solid(top, bottom):
    """Watertight solid between two height maps on the (X,Z) grid; height is the Y coordinate."""
    ny, nx = top.shape
    idx = np.arange(ny * nx).reshape(ny, nx)
    vt = np.c_[X.ravel(), top.ravel(), Z.ravel()]; vb = np.c_[X.ravel(), bottom.ravel(), Z.ravel()]
    a, b, c_, d = idx[:-1, :-1].ravel(), idx[:-1, 1:].ravel(), idx[1:, 1:].ravel(), idx[1:, :-1].ravel()
    ft = np.r_[np.c_[a, c_, b], np.c_[a, d, c_]]
    fb = np.r_[np.c_[a, b, c_], np.c_[a, c_, d]] + ny * nx
    ring = np.r_[idx[0, :], idx[1:, -1], idx[-1, -2::-1], idx[-2:0:-1, 0]]
    rn = np.roll(ring, -1); n = ny * nx
    fs = np.r_[np.c_[ring, rn, rn + n], np.c_[ring, rn + n, ring + n]]
    m = trimesh.Trimesh(np.r_[vt, vb], np.r_[ft, fb, fs], process=True)
    m.fix_normals()
    assert m.is_watertight and m.volume > 0
    return m

filler = heightfield_solid(S - OL["fill_eps"], S - 3.0)
clean = orig.union(filler, engine="manifold") if old.any() else orig.copy()

# ---------------------------------------------------------------- 3. logo in 2D (u = reading dir, v = up)
def to_multipolygon(g):
    g = g.buffer(0)
    return g if isinstance(g, MultiPolygon) else MultiPolygon([g]) if not g.is_empty else MultiPolygon()

def trace_icon(path, height, min_rib):
    img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if img.shape[2] == 4:  # composite on white
        a = img[:, :, 3:4] / 255.0; img = (img[:, :, :3] * a + 255 * (1 - a)).astype(np.uint8)
    b, g, r_ = [img[:, :, i].astype(int) for i in range(3)]
    blue = ((b - r_) > 60).astype(np.uint8)
    cs, hier = cv2.findContours(blue, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    polys = []
    for i, cn in enumerate(cs):
        if hier[0][i][3] != -1 or cv2.contourArea(cn) < 50: continue
        holes = []; j = hier[0][i][2]
        while j != -1:
            if cv2.contourArea(cs[j]) > 20: holes.append(cs[j][:, 0, :])
            j = hier[0][j][0]
        polys.append(Polygon(cn[:, 0, :], holes).buffer(0).simplify(0.6))
    icon = unary_union(polys)
    # measure the white rib width inside the icon (skeleton of the gaps x2)
    hull = cv2.fillPoly(np.zeros_like(blue), [cv2.convexHull(np.vstack([c[:, 0, :] for c in cs]))], 1)
    gaps = (hull.astype(bool) & ~blue.astype(bool))
    gaps = cv2.erode(gaps.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)  # drop hull-edge fringe
    dist = cv2.distanceTransform(gaps.astype(np.uint8), cv2.DIST_L2, 5)
    sk = skeletonize(gaps) & (dist > 2)
    rib_px = float(np.median(2 * dist[sk])) if sk.any() else 0.0
    minx, miny, maxx, maxy = icon.bounds
    s = height / (maxy - miny)
    icon = affinity.scale(icon, s, -s, origin=(0, 0))           # image y points down -> flip
    icon = affinity.translate(icon, -icon.bounds[0], -icon.bounds[1])
    rib_mm = rib_px * s
    grow = max(0.0, (min_rib - rib_mm) / 2)
    if grow: icon = icon.buffer(-grow, join_style=1)          # shrink facets -> ribs widen to min_rib
    return to_multipolygon(icon), rib_mm, rib_mm + 2 * grow

def text_poly(text, font):
    tp = TextPath((0, 0), text, size=1.0, prop=FontProperties(fname=font))
    g = Polygon()
    for ring in tp.to_polygons():
        if len(ring) >= 3: g = g.symmetric_difference(Polygon(ring).buffer(0))   # even-odd fill
    return to_multipolygon(g)

def min_stroke(mp, res=0.02):
    """Approximate thinnest stroke (mm) of a 2D shape: 2 x min distance on its skeleton (ignoring ends)."""
    minx, miny, maxx, maxy = mp.bounds
    w, h = int((maxx - minx) / res) + 4, int((maxy - miny) / res) + 4
    img = np.zeros((h, w), np.uint8)
    for p in mp.geoms:
        cv2.fillPoly(img, [((np.array(p.exterior.coords) - [minx, miny]) / res + 2).astype(np.int32)], 1)
        for it in p.interiors:
            cv2.fillPoly(img, [((np.array(it.coords) - [minx, miny]) / res + 2).astype(np.int32)], 0)
    d = cv2.distanceTransform(img, cv2.DIST_L2, 5)
    sk = skeletonize(img.astype(bool)) & (d > 0.25 / res)
    return (float(np.percentile(2 * d[sk], 5) * res), float(np.median(2 * d[sk]) * res)) if sk.any() else (0.0, 0.0)

report_logo = {}
if L["variant"] == "none":
    result = clean
else:
    parts = []
    icon_h = L["icon_height"]
    if L["variant"] in ("icon_text", "icon_only"):
        icon, rib_src, rib_out = trace_icon(resolve(P["icon_png"]), icon_h, L["min_rib"])
        report_logo.update(icon_size=[round(icon.bounds[2], 2), icon_h], icon_rib_original_mm=round(rib_src, 2),
                           icon_rib_printed_mm=round(rib_out, 2))
        parts.append(icon)
    if L["variant"] in ("icon_text", "text_only"):
        font = pathlib.Path(P["font"])
        if not font.exists():
            raise SystemExit(
                f"Font not found: {font}\n"
                "Install Noto Sans CJK Bold (or Noto Sans Bold) and set 'font:' in the YAML."
            )
        t = text_poly(L["text"], str(font))
        avail = L["total_length"] - ((parts[0].bounds[2] + L["gap"]) if parts else 0)
        k = avail / (t.bounds[2] - t.bounds[0])
        t = affinity.scale(t, k, k, origin=(0, 0))
        if L.get("text_bold", 0): t = to_multipolygon(t.buffer(L["text_bold"], join_style=1))   # thicken strokes
        t = affinity.translate(t, -t.bounds[0] + ((parts[0].bounds[2] + L["gap"]) if parts else 0),
                               (icon_h - (t.bounds[3] - t.bounds[1])) / 2 - t.bounds[1] if parts else -t.bounds[1])
        report_logo.update(text=L["text"], text_height_mm=round(t.bounds[3] - t.bounds[1], 2),
                           text_stroke_mm_p5_median=[round(v, 2) for v in min_stroke(t)])
        parts.append(t)
    logo2d = to_multipolygon(unary_union(parts))
    bx0, by0, bx1, by1 = logo2d.bounds
    logo2d = affinity.translate(logo2d, -(bx0 + bx1) / 2, -(by0 + by1) / 2)   # centre on origin
    report_logo["logo_size_mm"] = [round(bx1 - bx0, 2), round(by1 - by0, 2)]

    # 2D DXF of the logo (for Fusion 360 sketches)
    try:
        import ezdxf
        doc = ezdxf.new(); msp = doc.modelspace()
        for p in logo2d.geoms:
            for ring in [p.exterior, *p.interiors]:
                msp.add_lwpolyline(list(ring.coords), close=True)
        doc.saveas(DXF_DIR / f"{NAME}_logo2d.dxf")
    except ImportError:
        pass

    # ---------------------------------------------------------------- 4. place on the part
    # u (reading) -> +Z (or -Z), v (letter up) -> +X when reading +Z. Seen from outside (+Y) with Z up,
    # +X is on the left, so this is the original's 90deg-CCW orientation and NOT mirrored.
    sgn = 1 if L["reading_dir"] == "+Z" else -1
    y_lo, y_hi = orig.bounds[0, 1] - 5, orig.bounds[1, 1] + 10
    prisms = []
    for p in logo2d.geoms:
        m = trimesh.creation.extrude_polygon(p, y_hi - y_lo)        # local (u, v, w)
        T = np.zeros((4, 4)); T[3, 3] = 1
        # world x = cx + sgn*v ; world z = cz + sgn*u ; world y = y_lo + w
        T[0, 1] = sgn; T[2, 0] = sgn; T[1, 2] = 1
        T[:3, 3] = [L["center_x"], y_lo, L["center_z"]]
        if np.linalg.det(T[:3, :3]) < 0: m.invert()
        m.apply_transform(T); prisms.append(m)
    prism = trimesh.util.concatenate(prisms)
    d = L["depth"]
    if L["style"] == "engrave":
        slab = heightfield_solid(S + 5.0, S - d)
        cutter = prism.intersection(slab, engine="manifold")
        result = clean.difference(cutter, engine="manifold")
    else:
        slab = heightfield_solid(S + d, S - 1.0)
        boss = prism.intersection(slab, engine="manifold")
        result = clean.union(boss, engine="manifold")

# ---------------------------------------------------------------- 5. verify + export
assert result.is_watertight and result.is_winding_consistent, "result not watertight"
# everything outside the edited window must be untouched
pts, fi = trimesh.sample.sample_surface_even(orig, 60000, seed=1)
far = ~((pts[:, 0] > wx0 - 0.5) & (pts[:, 0] < wx1 + 0.5) & (pts[:, 2] > wz0 - 0.5) & (pts[:, 2] < wz1 + 0.5))
_, dist_out, _ = trimesh.proximity.closest_point(result, pts[far])
stl_path = OUT / f"{NAME}.stl"; result.export(stl_path)
rep = dict(source=P["source_stl"], old_logo_detected_px=int(old.sum()), old_logo_depth_mm=round(old_depth, 2),
           old_logo_extent_xz=[[float(X[old].min()), float(X[old].max())], [float(Z[old].min()), float(Z[old].max())]] if old.any() else None,
           style=L["style"], depth=L["depth"], variant=L["variant"], **report_logo,
           watertight=bool(result.is_watertight), faces=len(result.faces),
           volume_orig=round(orig.volume, 1), volume_clean=round(clean.volume, 1), volume_new=round(result.volume, 1),
           bounds_orig=orig.bounds.round(3).tolist(), bounds_new=result.bounds.round(3).tolist(),
           max_dev_outside_window_mm=float(dist_out.max()), edit_window_xz=[[wx0, wx1], [wz0, wz1]])
(REPORT_DIR / f"{NAME}_report.json").write_text(json.dumps(rep, indent=2))
if P.get("write_work"):
    work = ROOT / "work"; work.mkdir(exist_ok=True)
    np.savez(work / f"{NAME}_maps.npz", X=X, Z=Z, H=H, S=S, old=old)
    clean.export(work / "HandCoverV1_clean.stl")
print(json.dumps(rep, indent=2))
