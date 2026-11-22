"""
HAEBOT Hand - PROTOTYPE A: all 5 Feetech STS3215 in the palm (InMoov "servos in the palm" layout).
Built only by MODIFYING the original InMoov i2 files in cad/original/hand_i2 (SHA-256 checked). Concept CAD, not printed.

What the script does
  1. Scale the InMoov palm parts uniformly by SCALE so the 5 stock servo slots (made for JX PDI-6225MG, 39.9 x 21.0 mm)
     hold an STS3215 (45.4 x 24.8 x 35.3 mm, from the Feetech STEP in cad/original/sts3215) with >= 1.5 mm walls between slots.
  2. i2_WristLargeV2  -> palm frame: 5 STS3215 pockets cut in the 5 stock slots (same centres + angles as InMoov).
     Servo stands in the slot, horn on the BACK of the hand (+z); finger servos have the horn at the finger end,
     the thumb servo lies across the wrist end with the horn toward the thumb (as in the user's photo).
  3. i2_HandPDI6225V2 (back cover) and i2_PalmCoverV2 (palm cover) -> scaled + servo pockets carved inside.
     The two covers sandwich the servos (no ears on STS3215): palm cover pocket floor = servo bottom stop,
     back cover pocket ceiling = servo top stop. Cable holes for the 5264 plugs go through the palm cover.
  4. New small part: ring pulley that clamps on the Feetech D20 disc horn (no extra height above the horn).
Frame = InMoov i2 WristLargeV2 frame x SCALE: +x thumb side, -y fingers, +y wrist, z = 0 palm face of the frame.
Run: python dona_univ_robot_hand_2026-11-17_Sanjev_A_build.py   (numpy trimesh manifold3d cadquery shapely)
"""
import hashlib, json, math, os, sys
sys.dont_write_bytecode = True
import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
import importlib.util as _iu
_ps = _iu.spec_from_file_location("p1paths", os.path.join(HERE, "dona_univ_robot_hand_2026-11-17_Sanjev_A_paths.py"))
paths = _iu.module_from_spec(_ps); _ps.loader.exec_module(paths); F = paths.F
ORIG = paths.ORIG
P_OUT = "dona_univ_robot_hand_2026-11-17_Sanjev_A_"
P_IN = "dona_univ_robot_hand_2026-11-13_Sanjev_"
SRC = {   # file -> sha256 (cad/original/dona_univ_robot_hand_2026-11-13_Sanjev_sha256sums.txt)
    "i2_wristlargev2": "6c00cf5018ca36226bfb36d62c7f4a0429c2354fe4e0bb4b60157ffc00cd114d",
    "i2_handpdi6225v2": "722f1023509d4871b39de68474c65d65c8a79ee0ba9514f1ddf90945cc4884b2",
    "i2_palmcoverv2": "27f0410fd2f9f00447d169aa8c49ebb7ef1489b345234a4e5d1e09549108d95a",
}
SERVO_STEP = os.path.join(ORIG, "sts3215", "dona_univ_robot_hand_2026-11-17_Sanjev_servo_motor_sts3215_v10.step")
SERVO_SHA = "418869e1533cd6b4dc6e6f234e2fbf9fb7777415cca8e685f226109b7dbde594"

# ---------------------------------------------------------------- PARAMETERS
SCALE = 1.28            # smallest scale with >= 1.8 mm wall between neighbouring STS3215 pockets (1.21 -> 0.3 mm, too thin)
# STS3215 envelope in its own STEP frame (measured from the Feetech STEP): x = long side, horn at +x, shaft along +z
CASE = (-22.7, 22.7, -12.4, 12.4, -18.3, 17.0)
SHAFT_X = 12.5          # shaft from case centre (= 10.2 mm from the horn end)
HORN_D, HORN_Z = 20.0, (14.7, 18.7)            # disc horn D20, hub + disc
CONN = (-6.0, 3.0, -11.0, 11.0, -21.1, -6.0)   # two 5264 sockets on the bottom face (STEP), protrude 2.8 mm
PLUG_LEN = 8.0                                 # mating plug + cable bend below the sockets - ESTIMATE
CLR = 0.3
SERVO_Z0 = 11.0         # servo STEP origin height in the palm frame: case z -7.3..28.0, horn ring top 32.3
# the 5 stock InMoov slots (unscaled i2 frame, measured on i2_WristLargeV2 at z = 3); angle = direction of the horn end
SLOTS = {
    "thumb":  ((-1.1, 56.9), -11.4),
    "index":  ((21.9, 17.2), -85.7),
    "middle": ((0.0, 7.9), -90.0),
    "ring":   ((-22.4, 19.7), -94.9),
    "pinky":  ((-43.0, 35.7), -99.4),
}
SERVO_ID = {"thumb": 1, "index": 2, "middle": 3, "ring": 4, "pinky": 5}   # suggestion only - IDs are the user's decision
# cover placement on the i2 frame (unscaled; found by matching the cover screw holes to the frame screw holes)
def cover_tf(dx, dy, dz):
    M = np.eye(4); M[:3, :3] = [[1, 0, 0], [0, 0, -1], [0, 1, 0]]; M[:3, 3] = [dx, dy, dz]; return M
TF_HAND = cover_tf(-55.9, 94.7, 20.0)     # i2_HandPDI6225V2 -> on the back of the frame (frame top z = 20)
TF_PALM = cover_tf(-57.1, 91.7, -15.5)    # i2_PalmCoverV2  -> under the frame (z = 0)
# company logo on the back cover (replaces the engraved "InMoov" text)
LOGO_DXF = os.path.join(paths.BRAND, "dona_univ_robot_hand_2026-11-13_Sanjev_jinie_icon_logo2d.dxf")
INMOOV_TEXT_BOX = (-25.0, -2.0, 6.0, 100.0)   # x0, x1, y0, y1 (scaled frame) of the InMoov groove text, found by surface analysis
LOGO_ICON_CENTRE, LOGO_ICON_W = (-13.0, 78.0), 34.0
LOGO_TEXT, LOGO_TEXT_H, LOGO_TEXT_Y = "JINIE EDUTECH", 7.5, (14.0, 60.0)   # text runs along the hand (+y), like InMoov's
LOGO_DEPTH = 1.0                              # engraving depth into the dome
LOGO_GRID = 1.0                               # height-map grid for the groove fill (mm)
# ring pulley (new part)
RP_ID, RP_OD, RP_SKIRT, RP_CAP = 20.4, 26.0, 4.5, 1.5    # clamps over the D20 disc horn
RP_PCD_XY, RP_HOLE = 5.0, 2.2                            # horn holes at (+-5, +-5) from the shaft (STEP), M2 screws
RP_ENV_D = RP_OD + 2.0

# ---------------------------------------------------------------- helpers
def safe_export(mesh, path):
    """export STL and make sure the saved file reloads as a closed volume (manifold re-merge after float32 rounding)."""
    import manifold3d as mf
    m = mesh.copy(); m.merge_vertices()
    M = mf.Manifold(mf.Mesh(vert_properties=np.asarray(m.vertices, np.float32), tri_verts=np.asarray(m.faces, np.uint32)))
    o = M.to_mesh(); out = trimesh.Trimesh(o.vert_properties[:, :3], o.tri_verts)
    out.export(path)
    chk = trimesh.load(path)
    assert chk.is_watertight and chk.is_volume, f"export not watertight: {path}"
    return out

def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
def load(name):
    p = os.path.join(ORIG, "hand_i2", P_IN + name + ".stl")
    assert sha(p) == SRC[name], f"{name}: checksum mismatch - cad/original must stay unmodified"
    m = trimesh.load(p)
    return max(m.split(only_watertight=True), key=lambda x: x.volume)    # WristLargeV2 has a loose 0.2 cm3 sliver
def U(ms): return trimesh.boolean.union(ms, engine="manifold")
def D(a, bs): return trimesh.boolean.difference([a] + list(bs), engine="manifold")
def I(a, b): return trimesh.boolean.intersection([a, b], engine="manifold")
def box(x0, x1, y0, y1, z0, z1):
    m = trimesh.creation.box(extents=[x1 - x0, y1 - y0, z1 - z0]); m.apply_translation([(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2]); return m
def cyl(x, y, z0, z1, d): return trimesh.creation.cylinder(radius=d / 2, segment=[[x, y, z0], [x, y, z1]], sections=64)

def place(name):
    """4x4 transform: servo STEP frame -> palm frame for slot `name`."""
    (cx, cy), ang = SLOTS[name]
    M = trimesh.transformations.rotation_matrix(math.radians(ang), [0, 0, 1])
    M[:3, 3] = [cx * SCALE, cy * SCALE, SERVO_Z0]
    return M

def envelopes(name, clr):
    """case / horn ring / plug zone envelopes in the palm frame."""
    x0, x1, y0, y1, z0, z1 = CASE
    case = box(x0 - clr, x1 + clr, y0 - clr, y1 + clr, z0 - clr, z1 + clr)
    ring = cyl(SHAFT_X, 0, HORN_Z[0] - 0.5, HORN_Z[1] + RP_CAP + 2.0, RP_ENV_D)      # ring pulley + screw heads
    c = CONN
    plug = box(c[0] - 1, c[1] + 1, c[2] - 1, c[3] + 1, c[4] - PLUG_LEN, c[5])
    M = place(name)
    for m in (case, ring, plug): m.apply_transform(M)
    return case, ring, plug


# ---------------------------------------------------------------- logo
def _heightfield_solid(X, Y, ztop, zbot):
    """closed mesh between two height maps on a regular grid (all cells valid)."""
    ny, nx = X.shape
    vt = np.c_[X.ravel(), Y.ravel(), ztop.ravel()]; vb = np.c_[X.ravel(), Y.ravel(), zbot.ravel()]
    V = np.vstack([vt, vb]); off = nx * ny; F = []
    idx = lambda i, j: i * nx + j
    for i in range(ny - 1):
        for j in range(nx - 1):
            a, b, c, d = idx(i, j), idx(i, j + 1), idx(i + 1, j + 1), idx(i + 1, j)
            F += [[a, b, c], [a, c, d], [a + off, c + off, b + off], [a + off, d + off, c + off]]
    ring = [idx(0, j) for j in range(nx)] + [idx(i, nx - 1) for i in range(1, ny)] + \
           [idx(ny - 1, j) for j in range(nx - 2, -1, -1)] + [idx(i, 0) for i in range(ny - 2, 0, -1)]
    for k in range(len(ring)):
        a, b = ring[k], ring[(k + 1) % len(ring)]
        F += [[a, a + off, b + off], [a, b + off, b]]
    m = trimesh.Trimesh(V, np.array(F), process=True)
    if m.volume < 0: m.invert()
    return m

def _top_map(mesh, x0, x1, y0, y1, step=0.5):
    xs = np.arange(x0, x1 + 1e-6, step); ys = np.arange(y0, y1 + 1e-6, step); X, Y = np.meshgrid(xs, ys)
    P = np.c_[X.ravel(), Y.ravel(), np.full(X.size, 400.0)]
    loc, ri, _ = mesh.ray.intersects_location(P, np.tile([0, 0, -1.0], (len(P), 1)), multiple_hits=False)
    t = np.full(len(P), np.nan); t[ri] = loc[:, 2]
    return X, Y, t.reshape(X.shape)

def logo_polygons():
    """Jinie icon (brand DXF) + text, as shapely polygons in the scaled frame."""
    import ezdxf
    from ezdxf import path as ezpath
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    from shapely import affinity
    doc = ezdxf.readfile(LOGO_DXF)
    polys = []
    for e in doc.modelspace().query("LWPOLYLINE"):
        pts = [(v.x, v.y) for v in ezpath.make_path(e).flattening(0.02)]
        polys.append(Polygon(pts).buffer(0))
    icon = unary_union(polys)
    minx, miny, maxx, maxy = icon.bounds
    k = LOGO_ICON_W / (maxx - minx)
    icon = affinity.scale(icon, k, k, origin=((minx + maxx) / 2, (miny + maxy) / 2))
    icon = affinity.rotate(icon, 90, origin="centroid")            # top of the icon toward the wrist, like the text
    c = icon.centroid; icon = affinity.translate(icon, LOGO_ICON_CENTRE[0] - c.x, LOGO_ICON_CENTRE[1] - c.y)
    from matplotlib.textpath import TextPath
    from matplotlib.font_manager import FontProperties
    tp = TextPath((0, 0), LOGO_TEXT, size=10, prop=FontProperties(family="DejaVu Sans", weight="bold"))
    rings = [Polygon(r) for r in tp.to_polygons() if len(r) > 2]
    txt = None
    for r in sorted(rings, key=lambda p: -p.area):                  # outer letters minus counters (holes)
        if txt is None: txt = r.buffer(0)
        elif txt.contains(r.representative_point()) and any(o.contains(r) for o in getattr(txt, "geoms", [txt])): txt = txt.difference(r)
        else: txt = txt.union(r.buffer(0))
    tminx, tminy, tmaxx, tmaxy = txt.bounds
    L = LOGO_TEXT_Y[1] - LOGO_TEXT_Y[0]
    sx = L / (tmaxx - tminx); sy = LOGO_TEXT_H / (tmaxy - tminy)
    txt = affinity.scale(txt, sx, sy, origin=(tminx, tminy))
    txt = affinity.rotate(txt, 90, origin=(tminx, tminy))          # reads from the fingers toward the wrist
    b = txt.bounds
    txt = affinity.translate(txt, LOGO_ICON_CENTRE[0] - (b[0] + b[2]) / 2, LOGO_TEXT_Y[0] - b[1])
    return icon, txt

def apply_logo(cover):
    """fill the InMoov text grooves to the smooth dome, then engrave the Jinie logo following the dome."""
    from scipy.interpolate import griddata
    from scipy import ndimage
    x0, x1, y0, y1 = INMOOV_TEXT_BOX
    X, Y, t = _top_map(cover, x0 - 6, x1 + 6, y0 - 6, y1 + 6, step=LOGO_GRID)
    smooth = ndimage.gaussian_filter(np.nan_to_num(t, nan=np.nanmin(t)), 6)
    groove = (smooth - t) > 0.25
    inbox = (X >= x0) & (X <= x1) & (Y >= y0) & (Y <= y1)
    good = ~(groove & inbox) & ~np.isnan(t)
    zs = griddata(np.c_[X[good], Y[good]], t[good], (X, Y), method="cubic")
    zs = np.where(np.isnan(zs), t, zs)
    k = int(round(6 / LOGO_GRID)); sel = (slice(k, -k), slice(k, -k))   # back to the groove box
    Xb, Yb, Zb = X[sel], Y[sel], zs[sel]
    filler = _heightfield_solid(Xb, Yb, Zb, Zb - 5.0)
    cover = U([cover, I(filler, cover.convex_hull)])
    icon, txt = logo_polygons()
    cut = []
    for poly in (icon, txt):
        for g in getattr(poly, "geoms", [poly]):
            pr = trimesh.creation.extrude_polygon(g, 80.0); pr.apply_translation([0, 0, -10.0]); cut.append(pr)
    band = _heightfield_solid(Xb, Yb, Zb + 3.0, Zb - LOGO_DEPTH)
    cutter = I(U(cut), band)
    return D(cover, [cutter]), icon, txt

# ---------------------------------------------------------------- parts
def frame_part():
    f = load("i2_wristlargev2"); f.apply_scale(SCALE)
    cuts = []
    for k in SLOTS:
        case, ring, plug = envelopes(k, CLR)
        tall = case.copy(); tall.apply_translation([0, 0, 0])
        x0, x1, y0, y1, _, _ = CASE
        t = box(x0 - CLR, x1 + CLR, y0 - CLR, y1 + CLR, -60, 60); t.apply_transform(place(k)); cuts += [t, ring]
    return D(f, cuts)

# back cover extension (user 2026-11-17: "cover the remaining part of the hand"): the stock i2 cover is widened to the
# frame outline and gets a lip down to the frame, so the servos / pulleys / frame sides are hidden. Kept OPEN: knuckles
# (fingers must bend), thumb joint, wrist prongs.
EXT_GRID = 0.5
EXT_SKIN = 2.0           # cover thickness in the new area
EXT_CLR = 0.4            # gap to the frame / servos / pulleys below (wiggle room)
EXT_LIP = 2.4            # width of the lip that goes down to the frame
KNUCKLES = [(32.3, -35.2, -85.7), (0.0, -47.2, -90.0), (-35.0, -31.9, -94.9), (-64.5, -10.9, -99.4)]   # hinge x, y, finger dir
KNUCKLE_KEEP = 16.0      # free zone around each knuckle hinge (and everything beyond it toward the fingertips)
THUMB_JOINT, THUMB_KEEP = (56.0, 34.0), 20.0
WRIST_Y = 92.0           # no extension past this toward the wrist prongs

def _down_map(mesh, X, Y):
    """highest z of a mesh at each (x, y) (ray from above), nan where missed"""
    P = np.c_[X.ravel(), Y.ravel(), np.full(X.size, 400.0)]
    loc, ri, _ = mesh.ray.intersects_location(P, np.tile([0, 0, -1.0], (len(P), 1)), multiple_hits=False)
    t = np.full(len(P), np.nan); t[ri] = loc[:, 2]
    return t.reshape(X.shape)

def cover_extension(h):
    from scipy import ndimage
    from shapely.geometry import Polygon, Point, LineString, box as sbox
    from shapely.ops import unary_union
    from shapely.vectorized import contains
    frame = load("i2_wristlargev2"); frame.apply_scale(SCALE)
    obst = [frame]
    for k in SLOTS:
        case, ring, plug = envelopes(k, 0.0); obst += [case, ring]
    obst = trimesh.util.concatenate(obst)
    # region = frame outline (top view) minus the stock cover, knuckles, thumb joint, wrist
    lo, hi = frame.bounds
    X, Y = np.meshgrid(np.arange(lo[0] - 3, hi[0] + 3, EXT_GRID), np.arange(lo[1] - 3, hi[1] + 3, EXT_GRID))
    hit = ~np.isnan(_down_map(frame, X, Y))                          # frame silhouette (top view), raster -> polygon
    fo = unary_union([sbox(X[i, j] - EXT_GRID / 2, Y[i, j] - EXT_GRID / 2, X[i, j] + EXT_GRID / 2, Y[i, j] + EXT_GRID / 2) for i, j in np.argwhere(hit)]).buffer(6).buffer(-6)
    fo = Polygon(max(getattr(fo, "geoms", [fo]), key=lambda g: g.area).exterior)
    keep = [Point(x, y).buffer(KNUCKLE_KEEP) for x, y, a in KNUCKLES]
    keep += [LineString([(x, y), (x + 200 * math.cos(math.radians(a)), y + 200 * math.sin(math.radians(a)))]).buffer(KNUCKLE_KEEP) for x, y, a in KNUCKLES]
    kn = np.array([(x, y) for x, y, _ in KNUCKLES]); keep.append(Polygon(np.r_[kn, kn[::-1] + [0, -200]]).convex_hull)   # between the knuckles
    keep += [Point(*THUMB_JOINT).buffer(THUMB_KEEP), sbox(-500, WRIST_Y, 500, 500)]
    region = fo.buffer(0).difference(unary_union([k.buffer(0) for k in keep])).buffer(-0.5)
    tc = _down_map(h, X, Y)                                         # stock cover top
    inside = contains(region, X, Y)
    # cover top continued outward (nearest stock-cover height, smoothed), never below the obstacles + clearance + skin
    idx = ndimage.distance_transform_edt(np.isnan(tc), return_distances=False, return_indices=True)
    text = ndimage.gaussian_filter(tc[tuple(idx)], 3.0 / EXT_GRID)
    ob = np.nan_to_num(_down_map(obst, X, Y), nan=-50.0)
    ob = ndimage.maximum_filter(ob, size=9)                         # clearance in x/y too
    top = np.maximum(text, ob + EXT_CLR + EXT_SKIN)
    # lip: near the region's outer edge the skin goes down to the frame top (+ clearance)
    edge_d = ndimage.distance_transform_edt(inside) * EXT_GRID
    fr = ndimage.maximum_filter(np.nan_to_num(_down_map(frame, X, Y), nan=-50.0), size=9)
    bot = np.where(edge_d <= EXT_LIP, np.maximum(fr + EXT_CLR, 0.0), top - EXT_SKIN)
    bot = np.maximum(bot, np.where(edge_d <= EXT_LIP, fr + EXT_CLR, ob + EXT_CLR))
    bot = np.minimum(bot, top - 0.8)
    sheet = _heightfield_solid(X, Y, top, bot)
    prisms = []
    for g in getattr(region, "geoms", [region]):
        if g.area < 40: continue
        pr = trimesh.creation.extrude_polygon(g, 200.0); pr.apply_translation([0, 0, -50.0]); prisms.append(pr)
    ext = I(sheet, U(prisms))
    return U([h, ext]), region

def hand_cover_part():
    h = load("i2_handpdi6225v2"); h.apply_transform(TF_HAND); h.apply_scale(SCALE)
    cuts = []
    for k in SLOTS:
        case, ring, plug = envelopes(k, CLR)
        cuts += [case, ring]
    h, _, _ = apply_logo(h)          # logo first ...
    h, _ = cover_extension(h)        # ... then widen the cover over the rest of the hand ...
    frame = load("i2_wristlargev2"); frame.apply_scale(SCALE)
    h = D(h, cuts)                   # ... servo pockets last, so the groove fill can never close a pocket
    return h

PALM_SKIN = 1.6        # closed palm: min cover skin under the servo bottoms / plugs (user: no holes in the cover)
PALM_SMOOTH = 5.0      # smoothing (mm) of the local palm bulges so they look like part of the InMoov cover

def _ray_first(m, X, Y):
    O = np.c_[X.ravel(), Y.ravel(), np.full(X.size, -80.0)]; Dd = np.tile([0, 0, 1.0], (X.size, 1))
    loc, ri, _ = m.ray.intersects_location(O, Dd, multiple_hits=True)
    z = np.full(X.size, np.nan)
    for i in np.unique(ri): z[i] = loc[ri == i, 2].min()
    return z.reshape(X.shape)

def palm_cover_part():
    """stock palm cover; where the servo bottoms / plugs would break through, the outside is pushed out locally (smooth bulge)
    so the cover stays CLOSED with >= PALM_SKIN material, then the pockets are carved."""
    from scipy import ndimage
    from shapely.geometry import box as sbox_, Polygon
    p = load("i2_palmcoverv2"); p.apply_transform(TF_PALM); p.apply_scale(SCALE)
    cuts = []
    for k in SLOTS:
        case, ring, plug = envelopes(k, CLR)
        cuts += [case, plug]
    lo, hi = p.bounds
    X, Y = np.meshgrid(np.arange(lo[0] - 2, hi[0] + 2, 1.0), np.arange(lo[1] - 2, hi[1] + 2, 1.0))
    zo = _ray_first(p, X, Y); ze = _ray_first(trimesh.util.concatenate(cuts), X, Y)
    deficit = np.where(np.isnan(zo) | np.isnan(ze), 0.0, np.minimum((ze - PALM_SKIN) - zo, 0.0))
    if deficit.min() < 0:
        sm = ndimage.gaussian_filter(ndimage.minimum_filter(deficit, size=int(3 * PALM_SMOOTH) | 1), PALM_SMOOTH)   # soft pad, covers the deficit
        zf = np.nan_to_num(zo, nan=np.nanmax(zo))
        bot = np.minimum(zf + sm, np.where(np.isnan(ze), np.inf, ze - PALM_SKIN))
        bot = np.minimum(bot, zf)
        top = np.maximum(np.minimum(zf + 3.0, -0.3), bot + 0.05)        # stays below the frame (frame bottom z = 0)
        pad = _heightfield_solid(X, Y, top, bot)
        from shapely.ops import unary_union as _uu
        cells = np.argwhere(sm < -0.05)
        region = _uu([sbox_(X[i, j] - 0.5, Y[i, j] - 0.5, X[i, j] + 0.5, Y[i, j] + 0.5) for i, j in cells]).buffer(1.0)
        foot = trimesh.path.polygons.projected(p, normal=[0, 0, 1]).buffer(10.0).buffer(-10.3)
        foot = Polygon(foot.exterior if foot.geom_type == "Polygon" else max(foot.geoms, key=lambda g: g.area).exterior).intersection(region)   # outline only, no inner gaps
        prisms = []
        for g in getattr(foot, "geoms", [foot]):
            pr = trimesh.creation.extrude_polygon(g, 60.0); pr.apply_translation([0, 0, lo[2] - 40.0]); prisms.append(pr)
        pad = I(pad, U(prisms))
        p = U([p, pad])
    return D(p, cuts)

def ring_pulley_part():
    import cadquery as cq
    r = cq.Workplane("XY").circle(RP_OD / 2).extrude(RP_SKIRT + RP_CAP)
    r = r.cut(cq.Workplane("XY").circle(RP_ID / 2).extrude(RP_SKIRT))                       # sits over the horn disc
    r = r.cut(cq.Workplane("XY").add(cq.Solid.makeTorus(RP_OD / 2, 1.0, cq.Vector(0, 0, RP_SKIRT / 2), cq.Vector(0, 0, 1))))  # tendon groove
    r = r.cut(cq.Workplane("XY").circle(3.0).extrude(20).translate((0, 0, -1)))              # horn screw access
    for sx in (-1, 1):
        for sy in (-1, 1):
            r = r.cut(cq.Workplane("XY").circle(RP_HOLE / 2).extrude(20).translate((sx * RP_PCD_XY, sy * RP_PCD_XY, -1)))
    r = r.cut(cq.Workplane("XZ").circle(0.8).extrude(-30, both=True).translate((0, 0, RP_SKIRT / 2)))   # tendon tie hole
    return r

def servo_ghosts():
    """Feetech STEP mesh placed 5x (reference only)."""
    import cadquery as cq
    assert sha(SERVO_STEP) == SERVO_SHA, "servo STEP checksum mismatch"
    tmp = os.path.join(HERE, "_servo_tmp.stl")
    cq.exporters.export(cq.Workplane().add(cq.importers.importStep(SERVO_STEP).val()), tmp, tolerance=0.08, angularTolerance=0.3)
    s = trimesh.load(tmp); os.remove(tmp)
    out = []
    for k in SLOTS:
        m = s.copy(); m.apply_transform(place(k)); out.append(m)
        rp = cyl(SHAFT_X, 0, HORN_Z[0] + 0.5, HORN_Z[1] + RP_CAP, RP_OD); rp.apply_transform(place(k)); out.append(rp)
    return trimesh.util.concatenate(out)

# ---------------------------------------------------------------- checks + export
def min_wall(frame):
    """thinnest frame material between pocket and pocket / outer edge, measured in the z = 10 section."""
    from shapely.geometry import Polygon
    s = frame.section(plane_origin=[0, 0, 10.0], plane_normal=[0, 0, 1])
    polys = [Polygon(e[:, :2]).buffer(0) for e in s.discrete]
    outer = max(polys, key=lambda p: p.area)
    pockets = []
    for k in SLOTS:
        x0, x1, y0, y1, _, _ = CASE
        b = np.array([[x0 - CLR, y0 - CLR, 0, 1], [x1 + CLR, y0 - CLR, 0, 1], [x1 + CLR, y1 + CLR, 0, 1], [x0 - CLR, y1 + CLR, 0, 1]])
        q = (place(k) @ b.T).T[:, :2]; pockets.append((k, Polygon(q)))
    out = {}
    for i, (a, pa) in enumerate(pockets):
        for b, pb in pockets[i + 1:]:
            d = pa.distance(pb)
            if d < 8: out[f"{a}-{b}"] = round(d, 2)
        out[f"{a}-outer_edge"] = round(pa.exterior.distance(outer.exterior), 2) if outer.contains(pa) else 0.0
    return out

if __name__ == "__main__":
    import cadquery as cq
    parts = {"01_palm_frame": frame_part(), "02_back_cover": hand_cover_part(), "03_palm_cover": palm_cover_part()}
    # 00: fit-test piece = the middle-finger slot cut out of part 01 (print this first with a real servo)
    cxy = np.array(SLOTS["middle"][0]) * SCALE
    tb = box(cxy[0] - 18, cxy[0] + 18, cxy[1] - 28, cxy[1] + 28, -30, 50)
    safe_export(I(parts["01_palm_frame"], tb), F("00_fit_test_middle_slot.stl"))
    rp = ring_pulley_part()
    for n, m in parts.items():
        parts[n] = safe_export(m, F(n + ".stl"))
    cq.exporters.export(rp, F("04_ring_pulley_x5.stl"), tolerance=0.02, angularTolerance=0.1)
    cq.exporters.export(rp, F("04_ring_pulley_x5.step"))
    gh = servo_ghosts(); gh.export(F("ref_sts3215_x5_placed.stl"))
    # checks
    env = {k: envelopes(k, 0.0) for k in SLOTS}
    coll = {}
    for n, m in parts.items():
        coll[n] = {k: round(float(sum(I(m, e).volume for e in env[k] if I(m, e).volume > 0)), 2) for k in SLOTS}
    # cover skin left over the servo pockets (thin = < 1.2 mm, 0 = opening)
    def skin(cover, top):
        """material left between a servo pocket face and the outside of the cover (0 = opening)."""
        res = {}
        for k in SLOTS:
            case, ring, plug = envelopes(k, CLR)
            tgt = ring if top else case
            (x0, y0, z0), (x1, y1, z1) = tgt.bounds
            g = np.array([[x, y] for x in np.linspace(x0, x1, 15) for y in np.linspace(y0, y1, 15)])
            inside = tgt.contains(np.c_[g, np.full(len(g), (z0 + z1) / 2)])
            g = g[inside]
            face = z1 if top else z0
            start = np.c_[g, np.full(len(g), 400.0 if top else -400.0)]
            d = np.array([0, 0, -1.0]) if top else np.array([0, 0, 1.0])
            loc, ri, _ = cover.ray.intersects_location(start, np.tile(d, (len(g), 1)), multiple_hits=False)
            sk = np.zeros(len(g)); sk[ri] = (loc[:, 2] - face) if top else (face - loc[:, 2])
            sk = np.clip(sk, 0, None)
            res[k] = dict(min_skin_mm=round(float(sk.min()), 2), opening_fraction=round(float((sk < 0.4).mean()), 2))
        return res
    bb = trimesh.util.concatenate(list(parts.values())).bounds
    report = dict(
        status="CONCEPT - prototype A, not printed",
        sources={k: "sha256 OK" for k in SRC}, servo_step="sha256 OK", scale=SCALE,
        assembled_hand_palm_bbox_mm=[round(float(v), 1) for v in (bb[1] - bb[0])], bbox_min=bb[0].round(1).tolist(), bbox_max=bb[1].round(1).tolist(),
        stock_i2_palm_bbox_mm=[112.6, 137.7, 51.8],
        servo_z0=SERVO_Z0, servo_case_z=[round(SERVO_Z0 + CASE[4], 2), round(SERVO_Z0 + CASE[5], 2)],
        min_wall_mm=min_wall(parts["01_palm_frame"]),
        servo_vs_part_overlap_mm3=coll,
        back_cover_over_horn=skin(parts["02_back_cover"], True),
        palm_cover_under_case=skin(parts["03_palm_cover"], False),
        watertight={n: bool(m.is_watertight) for n, m in parts.items()},
        solids={n: len(m.split()) for n, m in parts.items()},
        volume_cm3={n: round(m.volume / 1000, 1) for n, m in parts.items()},
        servo_positions={k: dict(id_suggestion=SERVO_ID[k], centre_xy=[round(SLOTS[k][0][0] * SCALE, 1), round(SLOTS[k][0][1] * SCALE, 1)],
                                 horn_direction_deg=SLOTS[k][1],
                                 shaft_xy=[round(float(v), 1) for v in (place(k) @ np.array([SHAFT_X, 0, 0, 1]))[:2]]) for k in SLOTS},
        print_also_at_scale=["i2_FingersX5V2", "i2_FingersTipX5V2", "i2_CoverFingerV3", "i2_WristGearV1 (if the InMoov wrist is used)"],
        knuckle_pin_d=round(3.3 * SCALE, 1), wrist_pin_d=round(8.3 * SCALE, 1))
    json.dump(report, open(F("report.json"), "w"), indent=1)
    print(json.dumps(report, indent=1))
