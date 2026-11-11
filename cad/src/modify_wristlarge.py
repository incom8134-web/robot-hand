"""Convert InMoov i2_WristLargeV2 (5 x JX PDI-6225MG slots) into ES08MA II seats.

Method (mesh boolean, manifold3d):
 1. Slice the official part every 0.5 mm and capture each servo slot outline.
 2. Rebuild each slot as a stack of extrusions (+0.3 mm) = "fill" and union it -> slot closed.
 3. Place the ES08MA II pocket cutter (cad/02_haebot_modified/stl/HB_ES08MA-II_pocket_cutter.stl)
    so its output shaft sits where the JX shaft sat (10.1 mm [EST] from the slot end nearest
    the official tendon guide) and subtract it.
Run after build_parts.py:
    python cad/src/modify_wristlarge.py            (uses cad/01_official_inmoov_i2/do_not_print/i2_WristLargeV2.stl)
"""
import sys, json, pathlib
import numpy as np, trimesh, yaml
from shapely.geometry import Polygon

ROOT = pathlib.Path(__file__).resolve().parents[1]
P = yaml.safe_load((ROOT / "parameters.yaml").read_text())
SHAFT_FROM_END = P["inmoov_i2"]["jx6225_shaft_from_slot_end"]["nominal"]
SRC = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "01_official_inmoov_i2" / "do_not_print" / "i2_WristLargeV2.stl"
OUT = ROOT / "02_haebot_modified" / "stl" / "HB_P01_WristLarge_ES08MA-II_mod.stl"
CUTTER = ROOT / "02_haebot_modified" / "stl" / "HB_ES08MA-II_pocket_cutter.stl"

orig = trimesh.load(SRC)
assert orig.is_watertight


def holes_at(z):
    s = orig.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    if s is None:
        return []
    p, _ = s.to_2D(to_2D=np.eye(4))
    return [Polygon(h) for poly in p.polygons_full for h in poly.interiors if 600 < Polygon(h).area < 1200]


# --- 1. slot outlines at the base define the 5 slots
base = holes_at(0.25)
assert len(base) == 5, f"expected 5 servo slots, found {len(base)}"
slots = []
for h in base:
    r = np.array(h.minimum_rotated_rectangle.exterior.coords)[:4]
    e = [r[1] - r[0], r[2] - r[1]]
    u = e[0] if np.linalg.norm(e[0]) > np.linalg.norm(e[1]) else e[1]
    L = np.linalg.norm(u); u = u / L
    slots.append(dict(c=np.array(h.centroid.coords[0]), u=u, L=L))

# official tendon guides sit just above the plate (z~22): small open profiles near one slot end
g = orig.section(plane_origin=[0, 0, 22], plane_normal=[0, 0, 1])
guides = [np.asarray(d)[:, :2].mean(0) for d in g.discrete]

# --- 2. fill
z_levels = np.arange(0.25, 20.0, 0.5)
fills = []
for sl in slots:
    last = None
    for z in z_levels:
        cand = [h for h in holes_at(z) if np.linalg.norm(np.array(h.centroid.coords[0]) - sl["c"]) < 8]
        poly = cand[0] if cand else last          # merged with wiring cavity -> reuse previous outline
        if poly is None:
            continue
        last = poly
        ext = trimesh.creation.extrude_polygon(poly.buffer(0.3, join_style=2), 0.52)
        ext.apply_translation([0, 0, z - 0.25 - 0.01])
        fills.append(ext)
fill = trimesh.boolean.union(fills, engine="manifold")
# clip the fill to the plate envelope (bottom 0 .. top 20.0)
fill = trimesh.boolean.intersection([fill, trimesh.creation.box(bounds=[[-200, -200, 0], [200, 200, 20.0]])],
                                    engine="manifold")
closed = trimesh.boolean.union([orig, fill], engine="manifold")

# --- 3. cut ES08MA II seats
cut0 = trimesh.load(CUTTER)
report = []
cutters = []
for i, sl in enumerate(slots):
    ends = [sl["c"] + sl["u"] * sl["L"] / 2, sl["c"] - sl["u"] * sl["L"] / 2]
    dist = [min(np.linalg.norm(gp - e) for gp in guides) for e in ends]
    near = ends[int(np.argmin(dist))]
    to_far = (sl["c"] - near) / np.linalg.norm(sl["c"] - near)
    shaft = near + to_far * SHAFT_FROM_END
    ang = np.arctan2(to_far[1], to_far[0])
    T = trimesh.transformations.rotation_matrix(ang, [0, 0, 1])
    T[:2, 3] = shaft
    c = cut0.copy(); c.apply_transform(T); cutters.append(c)
    report.append(dict(slot=i + 1, slot_centre=sl["c"].round(2).tolist(), slot_len=round(sl["L"], 2),
                       shaft_xy=shaft.round(2).tolist(), body_dir_deg=round(np.degrees(ang), 1),
                       guide_end_distance=round(min(dist), 1)))
mod = trimesh.boolean.difference([closed, trimesh.boolean.union(cutters, engine="manifold")], engine="manifold")
assert mod.is_watertight
mod.export(OUT)
(OUT.parent.parent / "WristLarge_mod_report.json").write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
print("volume orig %.1f cm3 -> mod %.1f cm3, watertight=%s" % (orig.volume / 1e3, mod.volume / 1e3, mod.is_watertight))
