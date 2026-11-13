#!/usr/bin/env python3
"""HAEBOT Hand prototype - ONE script for all our parts, checks and guide images.

What it makes (all in this folder, flat):
  01_FitTest_ServoSeat.step/.stl         one ES08MA II seat, prints in ~10 min
  02_ServoAdapter_ES08MA-II_x5.step/.stl drops into each servo slot of the OFFICIAL i2_WristLargeV2
  03_Pulley_ES08MA-II_x5.step/.stl       tendon pulley on the servo's stock single-arm horn
  10_DeskStand.step/.stl                 holds the hand upright by its wrist prongs (M8 bolt)
  img_*.png                              assembly-guide and verification images
  99_check_report.json                   numbers from the checks

Why an adapter and not a re-cut WristLarge: InMoov's own "small servo" option (inmoov.fr/inmoov-hand,
option 3) puts JX-PDI1109MG / SG90-size servos in an adapter (i2_Adapter1109MG) that drops into
the unmodified WristLarge slot. The ES08MA II is the same size class, so we follow that method with
our own adapter cut for the ES08MA II (+ wiggle room). The WristLarge you already printed is reused.

Run (from anywhere):  python 99_build_prototype.py          (build + check + images)
                      python 99_build_prototype.py --no-img (build + check only)
Needs: cadquery, trimesh, manifold3d, shapely, matplotlib, pyyaml
"""
import json, sys, pathlib
import numpy as np, yaml
import cadquery as cq
import trimesh
from shapely.geometry import Polygon

HERE = pathlib.Path(__file__).resolve().parent
ORIG = HERE.parent / "original" / "hand_i2"
P = yaml.safe_load((HERE / "99_parameters.yaml").read_text())
C = P["clearance"]; S = P["servo"]; T = P["seat"]; PU = P["pulley"]; ST = P["stand"]

# ------------------------------------------------------------------ derived seat numbers (local frame)
SLOT_HALF = 39.9 / 2                                   # [SRC] slot length 39.9
Y_SHAFT = -SLOT_HALF + T["jx_shaft_from_slot_end"]     # ES08MA II spline axis = estimated JX axis
Y_BODY0 = Y_SHAFT - S["shaft_from_end"]                # servo body, finger end
Y_BODY1 = Y_BODY0 + S["body_length"]                   # servo body, wrist end
Y_BODYC = (Y_BODY0 + Y_BODY1) / 2
Z0 = T["ledge_z"] - S["tab_bottom_z"]                  # servo bottom
Z_CASE = Z0 + S["case_height"]
Z_SPLINE = Z0 + S["total_height"]
Z_PULLEY = Z_SPLINE - PU["horn"]["hub_height"]         # pulley underside (sits on the horn)
W2, L2, H = 10.4, 19.66, T["height"]          # L2 = finger-end face of the outline
PK = dict(x=S["body_width"] / 2 + C, y0=Y_BODY0 - C, y1=Y_BODY1 + C)          # body pocket
TR = dict(y0=Y_BODYC - S["tab_span"] / 2 - C, y1=Y_BODYC + S["tab_span"] / 2 + C)  # tab recess
PILOTS = [Y_BODYC - S["tab_hole_pitch"] / 2, Y_BODYC + S["tab_hole_pitch"] / 2]


def box(xa, xb, ya, yb, za, zb):
    return cq.Workplane("XY").box(xb - xa, yb - ya, zb - za, centered=False).translate((xa, ya, za))


def zcyl(r, x, y, za, zb):
    return cq.Workplane("XY").circle(r).extrude(zb - za).translate((x, y, za))


def seat_cut(top):
    """Everything removed for one ES08MA II seat (body pocket, tab recess, pilots, cable notches)."""
    cut = box(-PK["x"], PK["x"], PK["y0"], PK["y1"], -5, T["ledge_z"] + 0.01)
    cut = cut.union(box(-PK["x"], PK["x"], TR["y0"], TR["y1"], T["ledge_z"], top + 1))
    for y in PILOTS:
        cut = cut.union(zcyl(T["pilot_dia"] / 2, 0, y, T["ledge_z"] - T["pilot_depth"], T["ledge_z"] + 0.1))
    nw = T["cable_notch_width"] / 2
    cut = cut.union(box(-nw, nw, PK["y0"] - T["cable_notch_depth_finger"], PK["y0"] + 0.1, -5, T["cable_notch_height"]))
    cut = cut.union(box(-nw, nw, PK["y1"] - 0.1, PK["y1"] + T["cable_notch_depth_wrist"], -5, T["cable_notch_height"]))
    return cut


# Outer outline of the official i2_Adapter1109MG (traced from the STL at z = 3 mm, slot-centre frame).
# It already fits all 5 WristLarge slots, including the two side bumps and the post at the wrist end.
# Changes vs the official outline: wrist-end corners chamfered a bit more and the wrist-end notch
# widened by 0.2 mm per side, so it clears all 5 slots (the slots differ by a few tenths).
OUTLINE = [(10.29, -19.66), (10.15, -2.19), (9.54, -2.19), (9.54, 2.04), (10.11, 2.04), (9.95, 15.0),
           (9.20, 19.89), (2.25, 19.89), (2.25, 16.88), (-2.55, 16.88), (-2.55, 19.89), (-9.50, 19.89),
           (-10.40, 15.0), (-10.50, 2.04), (-9.92, 2.04), (-9.92, -2.19), (-10.51, -2.19), (-10.50, -19.66)]


def servo_adapter():
    blk = cq.Workplane("XY").polyline(OUTLINE).close().extrude(H)
    lz, lw = T["lip_z"], T["lip_half_width"]
    zc = T["lip_chamfer_z"]   # lip face vertical up to here, then 45 deg out to lip_y_high
    lip = (cq.Workplane("YZ").polyline([(-19.0, lz), (T["lip_y_low"], lz), (T["lip_y_low"], zc),
                                        (T["lip_y_high"], zc + (T["lip_y_low"] - T["lip_y_high"])),
                                        (T["lip_y_high"], H), (-19.0, H)]).close()
           .extrude(2 * lw).translate((-lw, 0, 0)))
    a = blk.union(lip).cut(seat_cut(H))
    # engraved arrow on the wrist-end top face, pointing to the finger end (= shaft end)
    yt = TR["y1"] + 1.8
    arrow = cq.Workplane("XY").polyline([(-2.0, yt + 1.3), (2.0, yt + 1.3), (0, yt - 1.3)]).close().extrude(1).translate((0, 0, H - 0.6))
    return a.cut(arrow)


def fit_coupon():
    zb = T["ledge_z"] - 4.0
    blk = box(-W2, W2, TR["y0"] - 3, TR["y1"] + 3, zb, H)
    return blk.cut(seat_cut(H)).translate((0, 0, -zb))


def pulley():
    h = PU["horn"]; D, Hh, gz = PU["dia"], PU["height"], PU["groove_z"]
    p = cq.Workplane("XY").circle(D / 2).extrude(Hh)
    p = p.cut(cq.Workplane("XY").add(cq.Solid.makeTorus(D / 2, 1.0, cq.Vector(0, 0, gz), cq.Vector(0, 0, 1))))
    cl = 0.15
    p = p.cut(cq.Workplane("XY").circle(h["hub_dia"] / 2 + cl).extrude(h["hub_height"]))
    arm = (cq.Workplane("XY").polyline([(0, -h["arm_width_hub"] / 2 - cl), (h["arm_length"] - 1, -h["arm_width_tip"] / 2 - cl),
                                        (h["arm_length"] - 1, h["arm_width_tip"] / 2 + cl), (0, h["arm_width_hub"] / 2 + cl)]).close()
           .extrude(h["arm_thickness"] + cl))
    p = p.cut(arm)
    p = p.cut(cq.Workplane("XY").circle(h["screw_dia"] / 2).extrude(Hh + 1))                 # horn screw
    p = p.cut(cq.Workplane("XY").circle(2.4).extrude(2).translate((0, 0, Hh - 2)))           # screw head
    p = p.cut(cq.Workplane("YZ").circle(0.6).extrude(D).translate((0, 0, gz)))               # line hole into groove
    p = p.cut(cq.Workplane("XY").circle(0.8).extrude(Hh + 1).translate((5.0, 0, 0)))          # tie-off hole
    return p


def desk_stand():
    """In WristLarge coordinates (hand frame). Tongue fits between the two wrist prongs."""
    xa, xb = -29.95 + 0.3, 2.74 - 0.3            # [SRC] prongs at x -36.83..-29.95 and 2.74..9.62
    yh, zh = ST["m8_hole_y"], ST["m8_hole_z"]
    yb = yh + ST["neck_length"]; t = ST["base"]["thickness"]
    za, zb = 0.5, 19.2
    prof = (cq.Workplane("YZ").moveTo(yh, za).lineTo(yb, za).lineTo(yb, zb).lineTo(yh, zb)
            .threePointArc((yh - 7.6, zh + 0.0), (yh, za)).close())
    tongue = prof.extrude(xb - xa).translate((xa, 0, 0))
    xc, zc = (xa + xb) / 2, (za + zb) / 2
    base = box(xc - ST["base"]["width"] / 2, xc + ST["base"]["width"] / 2, yb, yb + t,
               zc - ST["base"]["depth"] / 2, zc + ST["base"]["depth"] / 2).edges("|Y").fillet(6)
    gus = []
    for s in (-1, 1):
        z1 = zb if s > 0 else za
        g = (cq.Workplane("YZ").polyline([(yb, z1), (yb - 22, z1), (yb, z1 + s * 22)]).close()
             .extrude(xb - xa).translate((xa, 0, 0)))
        gus.append(g)
    st = tongue.union(base).union(gus[0]).union(gus[1])
    st = st.cut(cq.Workplane("YZ").circle(ST["m8_hole_dia"] / 2).extrude(80).translate((xc - 40, yh, zh)))
    for dx in (-48, 48):
        for dz in (-38, 38):
            st = st.cut(cq.Workplane("XZ").circle(2.2).extrude(-t - 2).translate((xc + dx, yb - 1, zc + dz)))
    return st


def servo_dummy():
    """ES08MA II stand-in for checks and pictures (caliper size = worst case)."""
    bw = S["body_width"] / 2
    d = box(-bw, bw, Y_BODY0, Y_BODY1, Z0, Z_CASE)
    d = d.union(box(-bw, bw, Y_BODYC - S["tab_span"] / 2, Y_BODYC + S["tab_span"] / 2, T["ledge_z"], T["ledge_z"] + S["tab_thickness"]))
    d = d.union(zcyl(5.0, 0, Y_SHAFT, Z_CASE, Z_CASE + 1.5))
    d = d.union(zcyl(S["spline_dia"] / 2, 0, Y_SHAFT, Z_CASE + 1.5, Z_SPLINE))
    return d


def to_mesh(shape, tol=0.02):
    v, f = shape.val().tessellate(tol, 0.1)
    m = trimesh.Trimesh([(p.x, p.y, p.z) for p in v], f, process=True)
    trimesh.repair.fix_normals(m)
    return m


def export(shape, name, step=True, mesh_transform=None):
    if step:
        cq.exporters.export(shape, str(HERE / f"{name}.step"))
    m = to_mesh(shape)
    if mesh_transform is not None:
        m.apply_transform(mesh_transform)
    m.export(str(HERE / f"{name}.stl"))
    print("exported", name, "watertight", m.is_watertight)
    return m


# ------------------------------------------------------------------ slot poses in the official WristLarge
def slot_poses(wl):
    s = wl.section(plane_origin=[0, 0, 1.0], plane_normal=[0, 0, 1])
    p2, Tm = s.to_2D(); off = Tm[:2, 3]
    rects = []
    for poly in p2.polygons_full:
        for h in poly.interiors:
            hp = Polygon(h)
            if 700 < hp.area < 1200:
                c4 = np.array(hp.minimum_rotated_rectangle.exterior.coords)[:4] + off
                e = [c4[1] - c4[0], c4[2] - c4[1]]
                u = max(e, key=np.linalg.norm); u = u / np.linalg.norm(u)
                rects.append((c4.mean(0), u))
    g = wl.section(plane_origin=[0, 0, 22.5], plane_normal=[0, 0, 1])
    guides = [d[:, :2].mean(0) for d in g.discrete if Polygon(d[:, :2]).area > 20]
    poses = []
    for c, u in rects:
        ends = [c + u * SLOT_HALF, c - u * SLOT_HALF]
        dist = [min(np.linalg.norm(gp - e) for gp in guides) for e in ends]
        to_guide = u if dist[0] < dist[1] else -u           # local -Y
        yax = -to_guide; xax = np.array([yax[1], -yax[0]])  # right-handed, Z up
        M = np.eye(4); M[:2, 0] = xax; M[:2, 1] = yax; M[:2, 3] = c
        gpt = min(guides, key=lambda gp: np.linalg.norm(gp - (c + to_guide * SLOT_HALF)))
        poses.append(dict(M=M, centre=c, guide=gpt, guide_dist=float(min(dist))))
    return poses


# finger names by nearest finger knuckle (VERIFY by tracing each line on the real hand)
FINGER_BY_X = [("THUMB", -45), ("INDEX", -23), ("MIDDLE", 0), ("RING", 22)]


def name_seats(poses):
    named = []
    for p in poses:
        c = p["centre"]
        if abs(p["M"][1, 1]) < 0.5:          # the slot lying across the palm near the wrist
            nm, ch = "PINKY", 4
        else:
            nm = min(FINGER_BY_X, key=lambda f: abs(f[1] - c[0]))[0]
            ch = ["THUMB", "INDEX", "MIDDLE", "RING"].index(nm)
        named.append(dict(p, finger=nm, channel=ch))
    return sorted(named, key=lambda d: d["channel"])


def mesh_inter(a, b):
    try:
        r = trimesh.boolean.intersection([a, b], engine="manifold")
        return float(r.volume) if r is not None and len(r.faces) else 0.0
    except Exception as e:  # noqa
        return float("nan")


def wall_thickness(m, n=6000, seed=1):
    pts, fi = trimesh.sample.sample_surface(m, n, seed=seed)
    nrm = m.face_normals[fi]
    org = pts - nrm * 1e-3
    loc, ri, _ = m.ray.intersects_location(org, -nrm, multiple_hits=False)
    d = np.full(n, np.inf); d[ri] = np.linalg.norm(loc - org[ri], axis=1)
    return d


# ================================================================== guide / check images
def _view(elev, azim):
    az, el = np.radians(azim), np.radians(elev)
    return np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])


def draw_meshes(ax, items, elev, azim, pad=0.05, lims=None, zoom=1.0):
    """items: list of (mesh, rgb). One depth-sorted collection so overlaps look right."""
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    v = _view(elev, azim)
    light = v + np.array([0.35, 0.25, 0.6]); light /= np.linalg.norm(light)
    tris, cols = [], []
    for m, c in items:
        n = m.face_normals
        f = (n @ v) > -0.05
        sh = np.clip(n[f] @ light, 0, 1) * 0.65 + 0.35
        tris.append(m.triangles[f]); cols.append(np.clip(np.outer(sh, c), 0, 1))
    pc = Poly3DCollection(np.vstack(tris), facecolors=np.vstack(cols), edgecolors="none", linewidths=0)
    ax.add_collection3d(pc)
    if lims is None:
        b = np.vstack([m.bounds for m, _ in items]); lo, hi = b.min(0), b.max(0)
    else:
        lo, hi = np.array(lims[0]), np.array(lims[1])
    c = (lo + hi) / 2; r = (hi - lo).max() / 2 * (1 + pad) * zoom
    ax.set_xlim(c[0] - r, c[0] + r); ax.set_ylim(c[1] - r, c[1] + r); ax.set_zlim(c[2] - r, c[2] + r)
    ax.set_box_aspect((1, 1, 1)); ax.view_init(elev=elev, azim=azim); ax.set_axis_off()


def label3d(ax, p, text, color="#1e3a5f", size=9, **kw):
    ax.text(p[0], p[1], p[2], text, color=color, fontsize=size, fontweight="bold", zorder=100,
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=color, lw=0.8, alpha=0.9), **kw)


def arrow3d(ax, p0, p1, color="#c0392b"):
    p0, p1 = np.array(p0), np.array(p1)
    ax.plot(*zip(p0, p1), color=color, lw=2, zorder=99)
    d = p1 - p0; d = d / np.linalg.norm(d)
    ax.quiver(*(p1 - d * 6), *(d * 6), color=color, arrow_length_ratio=0.9, lw=2, zorder=99)


GREY = (0.82, 0.80, 0.76); BLUE = (0.25, 0.50, 0.85); DARK = (0.18, 0.20, 0.24); ORANGE = (0.95, 0.55, 0.15)
GREEN = (0.25, 0.65, 0.35); BEIGE = (0.90, 0.84, 0.70); PURPLE = (0.55, 0.45, 0.80)
BRAND = "#1e3a5f"


def _fig(title, w=12, h=9):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(w, h), facecolor="white")
    fig.suptitle(title, fontsize=15, fontweight="bold", color=BRAND, x=0.02, ha="left", y=0.98)
    return plt, fig


def _save(plt, fig, ctx, name, note=None):
    if note:
        fig.text(0.02, 0.015, note, fontsize=9, color="#555", ha="left")
    fig.savefig(ctx.HERE / name, dpi=110, facecolor="white")
    plt.close(fig); print("image", name)


def _tm(x=0, y=0, z=0):
    return trimesh.transformations.translation_matrix([x, y, z])


def screw_mesh(length=6, d=2.0, head=3.8):
    s = trimesh.creation.cylinder(radius=d / 2, height=length, sections=24); s.apply_translation([0, 0, -length / 2])
    h = trimesh.creation.cylinder(radius=head / 2, height=1.3, sections=24); h.apply_translation([0, 0, 0.65])
    return trimesh.util.concatenate([s, h])


def horn_mesh(ctx):
    h = ctx.P["pulley"]["horn"]
    hub = trimesh.creation.cylinder(radius=h["hub_dia"] / 2, height=h["hub_height"], sections=32)
    hub.apply_translation([0, 0, h["hub_height"] / 2])
    arm = trimesh.creation.box([h["arm_length"], h["arm_width_hub"] * 0.8, h["arm_thickness"]])
    arm.apply_translation([h["arm_length"] / 2, 0, h["arm_thickness"] / 2])
    return trimesh.util.concatenate([hub, arm])


def render_all(ctx):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Circle, FancyArrowPatch, Polygon as MPoly
    H_ = ctx.HERE
    ld = lambda n: trimesh.load(str(H_ / n))

    # ---------- 01 parts overview
    plt_, fig = _fig("Prototype print set - what each numbered file looks like", 16, 8)
    parts = [("01_FitTest_ServoSeat.stl", "01 Fit test seat  x1", BLUE),
             ("02_ServoAdapter_ES08MA-II_x5.stl", "02 Servo adapter  x5", BLUE),
             ("03_Pulley_ES08MA-II_x5.stl", "03 Pulley  x5", ORANGE),
             ("04_WristLarge_official.stl", "04 WristLarge (official)  x1", GREY),
             ("05_Fingers_official_plate.stl", "05 Fingers plate (official)  x1", GREY),
             ("06_FingerTips_official_plate.stl", "06 Finger tips plate (official)  x1", GREY),
             ("07_FingerCover_official.stl", "07 Finger cover (official)  x1", GREY),
             ("08_PalmCover_official.stl", "08 Palm cover (official)  x1", GREY),
             ("09_HandCover_JinieLogo.stl", "09 Hand cover, Jinie logo  x1", BEIGE),
             ("10_DeskStand.stl", "10 Desk stand  x1", GREEN)]
    for i, (f, t, c) in enumerate(parts):
        ax = fig.add_subplot(2, 5, i + 1, projection="3d")
        draw_meshes(ax, [(ld(f), c)], 35, -60)
        b = ld(f).extents
        ax.set_title(f"{t}\n{b[0]:.0f} x {b[1]:.0f} x {b[2]:.0f} mm", fontsize=9, color=BRAND)
    _save(plt_, fig, ctx, "img_01_parts_overview.png", "Blue/orange/green = our parts (STEP + STL).  Grey/beige = official InMoov i2 meshes (STL).  Shown in print orientation.")

    # ---------- 02 fit test
    plt_, fig = _fig("Step 2 - Fit test: does the ES08MA II drop in with a little wiggle room?", 14, 7)
    zb = ctx.P["seat"]["ledge_z"] - 4.0
    co = ld("01_FitTest_ServoSeat.stl")
    du = ctx.m_du.copy(); du.apply_translation([0, 0, -zb])
    ax = fig.add_subplot(1, 2, 1, projection="3d")
    dup = du.copy(); dup.apply_translation([0, 0, 28])
    scr = [screw_mesh() for _ in ctx.PILOTS]
    for s_, y in zip(scr, ctx.PILOTS):
        s_.apply_translation([0, y, ctx.P["seat"]["ledge_z"] - zb + 2.5 + 48])
    draw_meshes(ax, [(co, BLUE), (dup, DARK)] + [(s_, ORANGE) for s_ in scr], 25, -55, zoom=0.7)
    arrow3d(ax, [0, -26, 40], [0, -26, 14])
    label3d(ax, [0, 22, 0], "01 fit test seat")
    label3d(ax, [0, 20, 38], "ES08MA II")
    label3d(ax, [0, -16, 62], "M2 x 6 self-tap x2", color="#a35400")
    ax.set_title("1. push the servo in from the top", fontsize=10)
    ax = fig.add_subplot(1, 2, 2, projection="3d")
    draw_meshes(ax, [(co, BLUE), (du, DARK)], 25, -55, zoom=0.75)
    ax.set_title("2. tabs rest on the ledge, body hangs below", fontsize=10)
    _save(plt_, fig, ctx, "img_02_fit_test.png",
          f"Pocket {2*ctx.PK['x']:.1f} x {ctx.PK['y1']-ctx.PK['y0']:.1f} mm, tab recess {2*ctx.PK['x']:.1f} x {ctx.TR['y1']-ctx.TR['y0']:.1f} mm "
          f"(= servo + {ctx.P['clearance']} mm per side).  Too tight -> clearance 0.5, too loose -> 0.3 in 99_parameters.yaml, re-run.")

    # ---------- 03 servo into adapter (+ section)
    plt_, fig = _fig("Step 3 - Mount each servo in an adapter (02): shaft goes to the end the engraved arrow points at", 15, 7.5)
    ad = ctx.m_ad
    ax = fig.add_subplot(1, 2, 1, projection="3d")
    dup = ctx.m_du.copy(); dup.apply_translation([0, 0, 30])
    scr = [screw_mesh() for _ in ctx.PILOTS]
    for s_, y in zip(scr, ctx.PILOTS):
        s_.apply_translation([0, y, ctx.P["seat"]["ledge_z"] + 2.5 + 52])
    draw_meshes(ax, [(ad, BLUE), (dup, DARK)] + [(s_, ORANGE) for s_ in scr], 28, -50, zoom=0.7)
    arrow3d(ax, [0, -32, 48], [0, -32, 22])
    label3d(ax, [12, 18, 2], "02 adapter")
    label3d(ax, [10, 10, 52], "ES08MA II (shaft toward FINGER end)")
    label3d(ax, [0, -40, 70], "M2 x 6 self-tap x2", color="#a35400")
    label3d(ax, [0, 24, 22], "engraved arrow = points to finger end", color="#555", size=8)
    ax.set_title("exploded view", fontsize=10)
    ax = fig.add_subplot(1, 2, 2)
    for m, fc, ec in ((ad, "#bcd3f2", "#2b5c9e"), (ctx.m_du, "#55595f", "#222")):
        sec = m.section(plane_origin=[0, 0, 0], plane_normal=[1, 0, 0])
        if sec is None:
            continue
        p2, _ = sec.to_2D(to_2D=np.array([[0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, 0], [0, 0, 0, 1]], float))
        for poly in p2.polygons_full:
            xs, ys = poly.exterior.xy
            ax.fill(xs, ys, fc=fc, ec=ec, lw=1)
            for hh in poly.interiors:
                hx, hy = hh.xy; ax.fill(hx, hy, fc="white", ec=ec, lw=0.8)
    ax.axhline(0, color="#999", lw=0.8, ls="--"); ax.axhline(19.74, color="#999", lw=0.8, ls="--")
    ax.text(21, 0.3, "WristLarge back face (z 0)", fontsize=7, color="#777")
    ax.text(21, 20.0, "WristLarge palm face (z 19.7)", fontsize=7, color="#777")
    ax.axvline(ctx.Y_SHAFT, color="#c0392b", lw=1, ls="-.")
    ax.text(ctx.Y_SHAFT + 0.5, 27, f"shaft axis\n(= original JX axis)", fontsize=8, color="#c0392b")
    ax.annotate("", (ctx.PK["y0"], -2), (ctx.PK["y1"], -2), arrowprops=dict(arrowstyle="<->", color=BRAND))
    ax.text((ctx.PK["y0"] + ctx.PK["y1"]) / 2, -4.2, f"body pocket {ctx.PK['y1']-ctx.PK['y0']:.1f}", ha="center", fontsize=8, color=BRAND)
    ax.annotate("", (ctx.TR["y0"], 22.6), (ctx.TR["y1"], 22.6), arrowprops=dict(arrowstyle="<->", color=BRAND))
    ax.text((ctx.TR["y0"] + ctx.TR["y1"]) / 2, 23.2, f"tab recess {ctx.TR['y1']-ctx.TR['y0']:.1f}", ha="center", fontsize=8, color=BRAND)
    ax.text(-30, ctx.P["seat"]["ledge_z"], f"tab ledge z {ctx.P['seat']['ledge_z']}", fontsize=8, color=BRAND, va="center")
    ax.text(-30, 3.0, "stop lip rests\non inner shelf", fontsize=7, color="#555")
    ax.set_aspect("equal"); ax.set_xlim(-32, 28); ax.set_ylim(-6, 30); ax.grid(alpha=0.25)
    ax.set_xlabel("along slot (mm)   <- finger end        wrist end ->"); ax.set_ylabel("height (mm)")
    ax.set_title("cut through the middle of one seat (servo = dark)", fontsize=10)
    _save(plt_, fig, ctx, "img_03_servo_into_adapter.png")

    # ---------- 04 adapters into WristLarge
    plt_, fig = _fig("Step 4 - Drop the 5 adapters into the WristLarge from the PALM side", 14, 9)
    ax = fig.add_subplot(1, 1, 1, projection="3d")
    items = [(ctx.wl, GREY)]
    for k, pl in enumerate(ctx.placed):
        lift = 0 if k < 2 else 34
        a = pl["a"].copy(); a.apply_translation([0, 0, lift]); d = pl["d"].copy(); d.apply_translation([0, 0, lift])
        items += [(a, BLUE), (d, DARK)]
        c = pl["seat"]["centre"]
        off = {"THUMB": (-14, 0), "INDEX": (-6, -14), "MIDDLE": (0, -22), "RING": (12, -10), "PINKY": (6, 14)}[pl['seat']['finger']]
        label3d(ax, [c[0] + off[0], c[1] + off[1], 24 + lift + 14], f"{pl['seat']['finger']} (ch {pl['seat']['channel']})", size=8)
        if lift:
            arrow3d(ax, [c[0] + 14, c[1], lift + 18], [c[0] + 14, c[1], 22])
    draw_meshes(ax, items, 42, -70, zoom=0.62)
    _save(plt_, fig, ctx, "img_04_adapters_into_wristlarge.png",
          "Thumb + index shown seated, middle/ring/pinky lifted. Arrow on each adapter points to the fingers. Finger names per seat are from geometry - VERIFY by tracing each tendon.")

    # ---------- 05 servo 90 deg + pulley
    plt_, fig = _fig("Step 5 - Set the servo to 90 deg, then horn + pulley + long screw", 14, 7.5)
    ax = fig.add_subplot(1, 2, 1, projection="3d")
    hz = ctx.Z_SPLINE - ctx.P["pulley"]["horn"]["hub_height"]
    hm = horn_mesh(ctx); hm.apply_transform(_tm(0, ctx.Y_SHAFT, hz + 10) @ trimesh.transformations.rotation_matrix(np.pi / 2, [0, 0, 1]))
    pm = ctx.m_pu.copy(); pm.apply_translation([0, ctx.Y_SHAFT, ctx.Z_PULLEY + 24])
    sc = screw_mesh(12, 2.0, 3.8); sc.apply_translation([0, ctx.Y_SHAFT, ctx.Z_PULLEY + 24 + 10 + 14])
    draw_meshes(ax, [(ctx.m_ad, BLUE), (ctx.m_du, DARK), (hm, (0.95, 0.95, 0.95)), (pm, ORANGE), (sc, (0.6, 0.6, 0.6))], 22, -40, zoom=0.7)
    label3d(ax, [10, ctx.Y_SHAFT, hz + 12], "stock single-arm horn (arm -> wrist)", size=8)
    label3d(ax, [10, ctx.Y_SHAFT, ctx.Z_PULLEY + 30], "03 pulley (horn sits in its underside)", size=8)
    label3d(ax, [10, ctx.Y_SHAFT, ctx.Z_PULLEY + 52], "M2 x 12 horn screw  VERIFY length", size=8, color="#a35400")
    ax = fig.add_subplot(1, 2, 2); ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(Rectangle((-6, -18), 12, 24, fc="#55595f")); ax.add_patch(Circle((0, 0), 8.5, fc="#f5b041", ec="#a35400", lw=2))
    ax.add_patch(Circle((0, 0), 1.2, fc="k"))
    ax.annotate("", (0, 8.5), (0, 0), arrowprops=dict(arrowstyle="-", lw=4, color="white"))
    ax.plot([-8.5, -8.5, -30], [0, 30, 30], color="#c0392b", lw=2)
    ax.text(-29, 31.5, "tendon to the finger (finger end = up)", color="#c0392b", fontsize=9)
    ax.add_patch(FancyArrowPatch((6, 9), (9, -6), connectionstyle="arc3,rad=-0.5", arrowstyle="->", mutation_scale=18, color=BRAND, lw=2))
    ax.text(10.5, 2, "servo turns this way\n= line wraps on\n= finger CLOSES", fontsize=9, color=BRAND)
    ax.text(-30, -26, "Pulley Ø17 -> 13.4 mm of line per 90 deg.\n180 deg travel = 26.7 mm max.  VERIFY the finger closes fully;\n"
            "if not, raise pulley dia in 99_parameters.yaml (e.g. 20 mm = 31 mm travel).", fontsize=8.5, color="#333")
    ax.set_xlim(-32, 32); ax.set_ylim(-30, 36)
    ax.set_title("top view of one seat (palm side)", fontsize=10)
    _save(plt_, fig, ctx, "img_05_servo_center_and_pulley.png")

    # ---------- 06 top view verification
    plt_, fig = _fig("Check - all 5 ES08MA II seats in the official WristLarge (palm-side view)", 13, 12)
    ax = fig.add_subplot(1, 1, 1, projection="3d")
    items = [(ctx.wl, GREY)]
    for pl in ctx.placed:
        items += [(pl["a"], BLUE), (pl["d"], DARK), (pl["p"], ORANGE)]
    draw_meshes(ax, items, 90, -90, pad=0.0, zoom=0.72)
    for r, pl in zip(ctx.rep["seats"], ctx.placed):
        sx, sy = r["shaft_xy"]; gx, gy = r["guide_xy"]
        ax.plot([sx], [sy], [45], "r+", ms=14, mew=2.5, zorder=101)
        ax.plot([gx], [gy], [45], "o", color="#1b8a3a", ms=8, zorder=101)
        ax.plot([sx, gx], [sy, gy], [45, 45], color="#c0392b", lw=1.5, ls="--", zorder=101)
        c = pl["seat"]["centre"]
        label3d(ax, [c[0] - 9, c[1] + 6, 46], f"{r['finger']}\nch {r['pca_channel']}", size=8)
    _save(plt_, fig, ctx, "img_06_check_top_view_5_seats.png",
          "Blue = 02 adapter, dark = ES08MA II, orange = 03 pulley.  Red + = servo shaft (on the original JX axis).  Green dot = official tendon guide.  "
          "Dashed = line run.  0.000 mm3 overlap between any parts (99_check_report.json).")

    # ---------- 07 finger + tendon schematic
    plt_, fig = _fig("Step 6-8 - One finger: tendon on the palm side, elastic on the back", 15, 7)
    ax = fig.add_subplot(1, 1, 1); ax.set_aspect("equal"); ax.axis("off")
    segs = [(0, 32, "root (proximal)"), (34, 58, "middle"), (60, 80, "tip (screws on)")]
    for x0, x1, nm in segs:
        ax.add_patch(Rectangle((x0, -6), x1 - x0, 12, fc="#e5e1d8", ec="#666", lw=1.2, joinstyle="round"))
        ax.text((x0 + x1) / 2, -10, nm, ha="center", fontsize=9)
    for x in (0, 33, 59):
        ax.add_patch(Circle((x, 0), 1.65, fc="white", ec="k", lw=1.2))
    ax.text(-2, 9, "M3 x 16 pin + nut\n(holes Ø3.3 / Ø3.6)", fontsize=8, ha="center")
    ax.add_patch(Rectangle((-60, -10), 58, 20, fc="#d5d2cc", ec="#666"))
    ax.text(-58, 11.5, "04 WristLarge (palm face up)", fontsize=9)
    ax.add_patch(Rectangle((-48, 10), 20, 6, fc="#4a80d9", ec="#2b5c9e")); ax.add_patch(Circle((-38, 19), 8.5, fc="#f5b041", ec="#a35400"))
    ax.text(-48, 29, "03 pulley on servo", fontsize=8, color="#a35400")
    ax.plot([-29.5, -14, -6, 70, 79], [19, 12, 4.2, 4.2, 3], color="#c0392b", lw=2.2)
    ax.text(20, 6, "tendon: 0.8 mm braided line through Ø2.4 channels", color="#c0392b", fontsize=9)
    ax.plot([-20, -6, 70, 78], [-6, -4.2, -4.2, -3], color="#1b8a3a", lw=2.2, ls=(0, (4, 2)))
    ax.text(20, -3.2, "elastic return: 1 mm round elastic in the Ø6 channel", color="#1b8a3a", fontsize=9)
    ax.text(-16, 14.5, "guide arch (official)", fontsize=8, color="#555")
    ax.text(-58, -16, "PALM side = up in this sketch.  Servo turns -> tendon shortens -> finger curls.  Servo back -> elastic opens it.", fontsize=9)
    ax.set_xlim(-62, 85); ax.set_ylim(-19, 33)
    _save(plt_, fig, ctx, "img_07_finger_tendon_elastic.png",
          "Schematic, not to scale.  Channel sizes measured from the official finger STL.  Exact hole-to-hole route through the WristLarge: VERIFY on the print.")

    # ---------- 08 wiring
    plt_, fig = _fig("Step 9 - Wiring: servos to the PCA9685 on the HAEBOT controller board", 14, 7.5)
    ax = fig.add_subplot(1, 1, 1); ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 46, 70, fc="#1f1f1f", ec="k")); ax.text(23, 72, "HAEBOT controller\nPCA9685 servo headers", ha="center", fontsize=10, fontweight="bold")
    names = ["THUMB", "INDEX", "MIDDLE", "RING", "PINKY", "WRIST (later)"]
    for i, nm in enumerate(names):
        y = 62 - i * 10.5
        for j, (col, lab) in enumerate((("#7a4a1e", "GND"), ("#d62728", "6V"), ("#ff9f1a", "SIG"))):
            ax.add_patch(Rectangle((34 + j * 3.6, y - 1.5), 3, 3, fc=col, ec="k"))
        ax.text(31, y, f"CH {i}", color="white", ha="right", va="center", fontsize=10, fontweight="bold")
        if i < 5:
            for j, col in enumerate(("#7a4a1e", "#d62728", "#ff9f1a")):
                ax.plot([35.5 + j * 3.6, 70, 95], [y, y + j * 0.9 - 0.9, y + j * 0.9 - 0.9], color=col, lw=2)
            ax.add_patch(Rectangle((95, y - 3), 22, 6, fc="#33383f", ec="k")); ax.text(106, y, "ES08MA II", color="white", ha="center", va="center", fontsize=8)
            ax.text(120, y, nm, va="center", fontsize=11, fontweight="bold", color=BRAND)
        else:
            ax.text(48, y, "reserved", va="center", fontsize=9, color="#888")
    ax.text(0, -6, "Plug brown = GND to the outer pin (check the board silkscreen).  6 V rail: TPSM41625 on the board, or a 6 V / 5 A bench supply for the first test.\n"
            "Never power servos from the Nano/USB 5 V.  Servo GND and logic GND are common on the board.", fontsize=9)
    ax.set_xlim(-2, 140); ax.set_ylim(-12, 80)
    _save(plt_, fig, ctx, "img_08_wiring_pca9685.png",
          "Channel = the finger the servo actually pulls (trace the line), not the seat.  Seat-to-finger names are a geometry estimate - VERIFY.")

    # ---------- 09 stand
    plt_, fig = _fig("Step 10 - Mount the hand on the desk stand (10) with one M8 bolt", 13, 9)
    ax = fig.add_subplot(1, 1, 1, projection="3d")
    st = ctx.m_st.copy(); st.apply_translation([0, 28, 0])
    bolt = trimesh.creation.cylinder(radius=4, height=62, sections=32)
    bolt.apply_transform(_tm(-13.6 - 60, ctx.P["stand"]["m8_hole_y"], ctx.P["stand"]["m8_hole_z"]) @ trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0]))
    items = [(ctx.wl, GREY), (st, GREEN), (bolt, (0.55, 0.55, 0.58))]
    for pl in ctx.placed:
        items += [(pl["a"], BLUE), (pl["d"], DARK), (pl["p"], ORANGE)]
    Rup = trimesh.transformations.rotation_matrix(-np.pi / 2, [1, 0, 0])      # hand frame -> standing up
    up = []
    for m, c in items:
        m2 = m.copy(); m2.apply_transform(Rup); up.append((m2, c))
    draw_meshes(ax, up, 15, 120, zoom=0.62)
    tp = lambda p: (Rup @ [p[0], p[1], p[2], 1])[:3]
    label3d(ax, tp([-13, 160, 60]), "10 desk stand (base on the table)")
    label3d(ax, tp([-95, 82.9, 25]), "M8 x 60 bolt + nyloc nut + 2 washers", color="#555")
    label3d(ax, tp([-13, -20, 40]), "palm faces you, fingers up")
    arrow3d(ax, tp([-13, 125, 10]), tp([-13, 100, 10]), color="#1b8a3a")
    _save(plt_, fig, ctx, "img_09_desk_stand.png",
          "The stand tongue fits between the two wrist prongs (gap 32.7 mm measured).  Tighten the nut until the hand stays where you put it.")


if __name__ == "__main__":
    want_img = "--no-img" not in sys.argv
    ad = servo_adapter(); co = fit_coupon(); pu = pulley(); stand = desk_stand(); dummy = servo_dummy()
    flipX = trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0])
    m_co = export(co, "01_FitTest_ServoSeat")
    m_ad = export(ad, "02_ServoAdapter_ES08MA-II_x5")
    m_pu_print = export(pu, "03_Pulley_ES08MA-II_x5", mesh_transform=flipX @ trimesh.transformations.translation_matrix([0, 0, -PU["height"]]))
    Rst = trimesh.transformations.rotation_matrix(-np.pi / 2, [1, 0, 0])
    yb = ST["m8_hole_y"] + ST["neck_length"] + ST["base"]["thickness"]
    m_st_print = export(stand, "10_DeskStand", mesh_transform=trimesh.transformations.translation_matrix([0, 0, yb]) @ Rst)
    m_pu = to_mesh(pu); m_st = to_mesh(stand); m_du = to_mesh(dummy)

    wl = trimesh.load(str(ORIG / "i2_WristLargeV2.stl"))
    seats = name_seats(slot_poses(wl))
    assert len(seats) == 5, f"expected 5 slots, got {len(seats)}"
    rep = dict(parameters=dict(clearance=C), seat={}, seats=[], pairwise={}, notes=[])
    rep["seat"] = dict(body_pocket=[round(2 * PK["x"], 2), round(PK["y1"] - PK["y0"], 2)],
                       tab_recess=[round(2 * PK["x"], 2), round(TR["y1"] - TR["y0"], 2), round(H - T["ledge_z"], 2)],
                       ledge_z=T["ledge_z"], pilot_pitch=S["tab_hole_pitch"], pilot_dia=T["pilot_dia"],
                       shaft_local_y=round(Y_SHAFT, 2), servo_bottom_z=Z0, case_top_z=Z_CASE, spline_top_z=Z_SPLINE,
                       pulley_z=[Z_PULLEY, Z_PULLEY + PU["height"]], groove_z=Z_PULLEY + PU["groove_z"],
                       walls=dict(side=round(W2 - PK["x"], 2),
                                  finger_end_below_lip=round(PK["y0"] - (-L2), 2),
                                  finger_end_cable_notch=round(PK["y0"] - T["cable_notch_depth_finger"] - (-L2), 2),
                                  finger_end_at_tab=round(TR["y0"] - T["lip_y_high"], 2),
                                  wrist_end_at_tab=round(16.88 - TR["y1"], 2),
                                  pilot_to_pocket=round(min(PK["y0"] - PILOTS[0], PILOTS[1] - PK["y1"]) - T["pilot_dia"] / 2, 2),
                                  pilot_to_lip_end=round(PILOTS[0] - T["pilot_dia"] / 2 - T["lip_y_low"], 2),
                                  side_at_bump=round(9.54 - PK["x"], 2),
                                  pilot_floor_above_cable_notch=round(T["ledge_z"] - T["pilot_depth"] - T["cable_notch_height"], 2)))
    wt = wall_thickness(m_ad)
    rep["seat"]["mesh_wall_thickness_min"] = round(float(np.min(wt)), 2)
    rep["seat"]["mesh_wall_thickness_p1"] = round(float(np.percentile(wt, 1)), 2)
    placed = []
    for s_ in seats:
        M = s_["M"]
        a = m_ad.copy(); a.apply_transform(M)
        d = m_du.copy(); d.apply_transform(M)
        p = m_pu.copy(); p.apply_transform(M @ trimesh.transformations.translation_matrix([0, Y_SHAFT, Z_PULLEY]))
        sweep = trimesh.creation.cylinder(radius=PU["dia"] / 2 + 0.5, height=PU["height"], sections=64)
        sweep.apply_transform(M @ trimesh.transformations.translation_matrix([0, Y_SHAFT, Z_PULLEY + PU["height"] / 2]))
        down = a.copy(); down.apply_translation([0, 0, -0.3])
        shaft = (M @ [0, Y_SHAFT, 0, 1])[:2]
        jx = (M @ [0, -SLOT_HALF + T["jx_shaft_from_slot_end"], 0, 1])[:2]
        row = dict(finger=s_["finger"], pca_channel=s_["channel"], slot_centre=np.round(s_["centre"], 2).tolist(),
                   shaft_xy=np.round(shaft, 2).tolist(), jx_axis_xy=np.round(jx, 2).tolist(),
                   shaft_offset_from_jx=round(float(np.linalg.norm(shaft - jx)), 3),
                   guide_xy=np.round(s_["guide"], 1).tolist(), shaft_to_guide=round(float(np.linalg.norm(shaft - s_["guide"])), 1),
                   adapter_vs_wristlarge_mm3=round(mesh_inter(a, wl), 3),
                   adapter_0p3_lower_vs_wristlarge_mm3=round(mesh_inter(down, wl), 2),
                   servo_vs_wristlarge_mm3=round(mesh_inter(d, wl), 3),
                   servo_vs_adapter_mm3=round(mesh_inter(d, a), 3),
                   pulley_sweep_vs_wristlarge_mm3=round(mesh_inter(sweep, wl), 3),
                   pulley_sweep_vs_adapter_mm3=round(mesh_inter(sweep, a), 3))
        rep["seats"].append(row)
        placed.append(dict(seat=s_, a=a, d=d, p=p, sweep=sweep))
        print(row)
    for i in range(5):
        for j in range(i + 1, 5):
            A = trimesh.util.concatenate([placed[i]["a"], placed[i]["d"], placed[i]["sweep"]])
            B = trimesh.util.concatenate([placed[j]["a"], placed[j]["d"], placed[j]["sweep"]])
            v = sum(mesh_inter(x, y) for x in (placed[i]["a"], placed[i]["d"], placed[i]["sweep"])
                    for y in (placed[j]["a"], placed[j]["d"], placed[j]["sweep"]))
            rep["pairwise"][f"{seats[i]['finger']}-{seats[j]['finger']}"] = round(v, 3)
    rep["stand_vs_wristlarge_mm3"] = round(mesh_inter(m_st, wl), 3)
    print(json.dumps(rep["seat"], indent=1)); print(rep["pairwise"]); print("stand", rep["stand_vs_wristlarge_mm3"])
    (HERE / "99_check_report.json").write_text(json.dumps(rep, indent=1))
    if want_img:
        from types import SimpleNamespace
        ctx = SimpleNamespace(wl=wl, seats=seats, placed=placed, m_ad=m_ad, m_co=m_co, m_pu=m_pu, m_du=m_du, m_st=m_st,
                              rep=rep, Y_SHAFT=Y_SHAFT, Z_PULLEY=Z_PULLEY, P=P, HERE=HERE, ORIG=ORIG,
                              PK=PK, TR=TR, PILOTS=PILOTS, Z0=Z0, Z_CASE=Z_CASE, Z_SPLINE=Z_SPLINE, L2=L2, W2=W2, H=H)
        render_all(ctx)
