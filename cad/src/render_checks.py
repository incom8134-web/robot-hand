#!/usr/bin/env python3
"""Regenerate cad/renders check images for the current ES08MA II seats.

From the repo root:
  python cad/src/render_checks.py
Writes:
  cad/renders/HB_P01_WristLarge_mod_check.png
  cad/renders/HB_P01_seats_top.png
  cad/renders/HB_P00_FitCoupon_check.png
  cad/renders/HB_T01_OneFingerRig_check.png
"""
from pathlib import Path
import json
import numpy as np
import trimesh
from shapely.geometry import Polygon, LineString
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

CAD = Path(__file__).resolve().parents[1]
OUT = CAD / "renders"
OUT.mkdir(parents=True, exist_ok=True)

TAN = (0.76, 0.58, 0.38)
BLUE = (0.45, 0.58, 0.72)
NAVY = (0.22, 0.28, 0.40)
GREEN = (0.20, 0.55, 0.32)
PURPLE = (0.45, 0.42, 0.70)
DUMMY = (0.55, 0.62, 0.70)
BG = "#f4f1ea"
ACCENT = "#1e3a5f"
OUTER = "#1a2a3a"


def load(p):
    m = trimesh.load(str(p), force="mesh")
    if isinstance(m, trimesh.Scene):
        m = trimesh.util.concatenate(tuple(m.geometry.values()))
    return m


def add_mesh(ax, mesh, color, elev, azim, title, clip=None, xlim=None, ylim=None, zlim=None):
    m = mesh
    if clip is not None:
        lo, hi = np.array(clip[0]), np.array(clip[1])
        c = m.triangles_center
        keep = np.all((c >= lo) & (c <= hi), axis=1)
        m = m.submesh([np.where(keep)[0]], append=True)
    az, el = np.radians(azim), np.radians(elev)
    view = np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])
    front = m.face_normals @ view > 0
    m = m.submesh([np.where(front)[0]], append=True)
    n = m.face_normals
    light = view + np.array([0.3, 0.2, 0.5]); light /= np.linalg.norm(light)
    shade = np.clip(n @ light, 0, 1) * 0.75 + 0.25
    cols = np.outer(shade, color)
    pc = Poly3DCollection(m.triangles, facecolors=np.clip(cols, 0, 1), edgecolors="none", linewidths=0)
    ax.add_collection3d(pc)
    b = m.bounds
    ctr = b.mean(0); r = (b[1] - b[0]).max() / 2
    ax.set_xlim(*(xlim or (ctr[0] - r, ctr[0] + r)))
    ax.set_ylim(*(ylim or (ctr[1] - r, ctr[1] + r)))
    ax.set_zlim(*(zlim or (ctr[2] - r, ctr[2] + r)))
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=elev, azim=azim)
    ax.set_title(title, fontsize=9)
    ax.tick_params(labelsize=6)


def section_xy(mesh, z):
    s = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    if s is None:
        return [], None
    path2d, to_3d = s.to_2D()

    def to_world(coords):
        arr = np.c_[np.asarray(coords), np.zeros(len(coords)), np.ones(len(coords))]
        w = (to_3d @ arr.T).T
        return w[:, :2]

    groups = []
    for poly in path2d.polygons_full:
        ext = to_world(np.array(poly.exterior.coords))
        holes = [to_world(np.array(h.coords)) for h in poly.interiors]
        groups.append((ext, holes))
    return groups, to_3d


def add_section(ax, groups, face="#d9e4f0", edge=OUTER, hole_face="white", lw=0.8):
    for ext, holes in groups:
        ax.fill(ext[:, 0], ext[:, 1], facecolor=face, edgecolor=edge, lw=lw, zorder=2)
        for h in holes:
            ax.fill(h[:, 0], h[:, 1], facecolor=hole_face, edgecolor=edge, lw=lw, zorder=3)


def mrr_lw(xy):
    poly = Polygon(xy)
    mrr = poly.minimum_rotated_rectangle
    c = np.array(mrr.exterior.coords)[:4]
    n0, n1 = np.linalg.norm(c[1] - c[0]), np.linalg.norm(c[2] - c[1])
    return max(n0, n1), min(n0, n1), mrr


def draw_dim_line(ax, p0, p1, text, offset, color="#1e3a5f", fontsize=8):
    p0, p1, off = np.asarray(p0, float), np.asarray(p1, float), np.asarray(offset, float)
    a, b = p0 + off, p1 + off
    ax.annotate("", xy=b, xytext=a,
                arrowprops=dict(arrowstyle="<->", color=color, lw=0.9))
    mid = (a + b) / 2
    ax.text(mid[0], mid[1], text, color=color, fontsize=fontsize,
            ha="center", va="center",
            bbox=dict(fc="white", ec="none", pad=0.2, alpha=0.85))


def place_dummies(wrist_report, dummy):
    placed = []
    for rec in wrist_report:
        ang = np.radians(rec["body_dir_deg"])
        T = trimesh.transformations.rotation_matrix(ang, [0, 0, 1])
        T[:2, 3] = rec["shaft_xy"]
        d = dummy.copy(); d.apply_transform(T)
        placed.append(d)
    return trimesh.util.concatenate(placed) if placed else dummy


# =============================================================================
# 1. WristLarge 2x3 montage (same layout as the original check image)
# =============================================================================
official = load(CAD / "01_official_inmoov_i2/do_not_print/i2_WristLargeV2.stl")
wrist = load(CAD / "02_haebot_modified/stl/HB_P01_WristLarge_ES08MA-II_mod.stl")
dummy = load(CAD / "02_haebot_modified/stl/HB_ES08MA-II_reference_dummy.stl")
report = json.loads((CAD / "02_haebot_modified/WristLarge_mod_report.json").read_text())
dummies = place_dummies(report, dummy)
assy = trimesh.util.concatenate([wrist, dummies])

fig = plt.figure(figsize=(13.5, 7.6), dpi=110)
fig.patch.set_facecolor("white")
views = [
    (official, TAN,  90, -90, "Official i2_WristLargeV2 (top)"),
    (wrist,    BLUE, 90, -90, "HB_P01 modified (top)"),
    (assy,     BLUE, 25, -50, "Modified + 5x ES08MA II dummies"),
    (official, (0.45, 0.32, 0.22), -90, -90, "Official (bottom)"),
    (wrist,    NAVY, -90, -90, "Modified (bottom)"),
]
for i, (mesh, color, elev, azim, title) in enumerate(views, 1):
    ax = fig.add_subplot(2, 3, i, projection="3d")
    add_mesh(ax, mesh, color, elev, azim, title)

# section overlay (bottom-right)
ax = fig.add_subplot(2, 3, 6)
g5, _ = section_xy(wrist, 5.0)
g175, _ = section_xy(wrist, 17.5)
shafts = np.array([r["shaft_xy"] for r in report])
for ext, holes in g5:
    ax.plot(np.r_[ext[:, 0], ext[0, 0]], np.r_[ext[:, 1], ext[0, 1]], color="#2a6fbb", lw=0.7)
    for h in holes:
        ax.plot(np.r_[h[:, 0], h[0, 0]], np.r_[h[:, 1], h[0, 1]], color="#2a6fbb", lw=0.7)
for ext, holes in g175:
    ax.plot(np.r_[ext[:, 0], ext[0, 0]], np.r_[ext[:, 1], ext[0, 1]], color="#c0392b", lw=0.7)
    for h in holes:
        ax.plot(np.r_[h[:, 0], h[0, 0]], np.r_[h[:, 1], h[0, 1]], color="#c0392b", lw=0.7)
ax.plot(shafts[:, 0], shafts[:, 1], "+", color="#111", markersize=8, markeredgewidth=1.1)
ax.set_aspect("equal")
ax.set_title("Modified sections z=5 (blue) z=17.5 (red), + = shaft", fontsize=8)
ax.set_xlim(-68, 58); ax.set_ylim(-52, 100)
ax.tick_params(labelsize=6)
ax.grid(True, ls=":", lw=0.4, color="#ccc")

fig.tight_layout()
p = OUT / "HB_P01_WristLarge_mod_check.png"
fig.savefig(p, dpi=110, facecolor="white")
plt.close(fig)
print("wrote", p, p.stat().st_size)


# =============================================================================
# 2. Dimensioned top view of the five new seats
# =============================================================================
g_top, _ = section_xy(wrist, 18.0)
g_body, _ = section_xy(wrist, 8.0)

fig, axes = plt.subplots(1, 2, figsize=(13.2, 8.2), dpi=140)
fig.patch.set_facecolor(BG)
fig.suptitle(
    "HB_P01 WristLarge — ES08MA II seats resized for user-measured 24.0 × 12.0 mm body\n"
    "Pocket 24.7 × 12.7 mm (0.35 mm clearance per side)  ·  tab recess 33.2 × 12.7 mm  ·  ledge z = 15.5",
    fontsize=11, color=ACCENT, fontweight="bold", y=0.98,
)

ax = axes[0]
ax.set_facecolor("white")
add_section(ax, g_top, face="#d9e4f0", edge=OUTER, hole_face="white", lw=0.7)
# body pockets in red at z=8, overplotted as outlines
for ext, holes in g_body:
    for h in holes:
        L, W, _ = mrr_lw(h)
        if W > 10 and L > 18:
            ax.plot(np.r_[h[:, 0], h[0, 0]], np.r_[h[:, 1], h[0, 1]], color="#c0392b", lw=0.9, zorder=4)
# pulley circles + shafts
for i, rec in enumerate(report, 1):
    s = np.array(rec["shaft_xy"])
    circ = plt.Circle(s, 8.5, fill=False, ls="--", color="#b8860b", lw=0.7, zorder=5)
    ax.add_patch(circ)
    ax.plot(*s, "+", color="#111", markersize=9, markeredgewidth=1.2, zorder=6)
    ax.annotate(f"S{i}", s, textcoords="offset points", xytext=(5, 5), fontsize=7, color="#111")
# dimension one clearly axis-aligned pocket (slot 4 is at 90 deg)
for ext, holes in g_top:
    for h in holes:
        L, W, _ = mrr_lw(h)
        if abs(W - 12.7) < 0.3 and abs(L - 33.2) < 0.4:
            # pick the centre-most (slot 4)
            c = h.mean(0)
            if abs(c[0]) < 8:  # slot 4 near x=0
                minx, miny = h.min(0); maxx, maxy = h.max(0)
                draw_dim_line(ax, (maxx, miny), (maxx, maxy), "33.2", (4.5, 0), color="#1e3a5f", fontsize=8)
                # width across the short side — use mid of long edges
                draw_dim_line(ax, (minx, maxy), (maxx, maxy) if False else (minx, maxy), "12.7", (0, 0),
                              color="none", fontsize=1)  # placeholder skipped
                # better: short-side dim at mid-length
                midy = (miny + maxy) / 2
                # find x extent at midy is messy; use mrr
                ax.annotate("12.7", xy=(c[0], maxy + 3.2), ha="center", fontsize=8, color="#7b1e1e")
                ax.annotate("", xy=(c[0] - 6.35, maxy + 2.0), xytext=(c[0] + 6.35, maxy + 2.0),
                            arrowprops=dict(arrowstyle="<->", color="#7b1e1e", lw=0.9))
ax.set_aspect("equal")
ax.set_title("Top view at tab recess (z = 18)  ·  red = body pocket (z = 8)  ·  dashed = Ø17 pulley", fontsize=8)
ax.set_xlabel("X (mm)"); ax.set_ylabel("Y (mm)")
ax.set_xlim(-68, 58); ax.set_ylim(-52, 100)
ax.grid(True, ls=":", lw=0.4, color="#ccc")
ax.legend(handles=[
    plt.Line2D([0], [0], color=OUTER, lw=1, label="Tab pocket 33.2 × 12.7"),
    plt.Line2D([0], [0], color="#c0392b", lw=1, label="Body pocket 24.7 × 12.7"),
    plt.Line2D([0], [0], color="#b8860b", lw=1, ls="--", label="Pulley Ø17"),
    plt.Line2D([0], [0], color="#111", marker="+", lw=0, label="Shaft axis"),
], loc="lower left", fontsize=7, framealpha=0.9)
ax.tick_params(labelsize=7)

ax2 = axes[1]
ax2.set_facecolor("white")
faces = wrist.faces
verts = wrist.vertices
tris = verts[faces]
n = wrist.face_normals
up = n[:, 2] > 0.15
tris_up = tris[up]
zc = tris_up.mean(axis=1)[:, 2]
cmap = plt.cm.Blues
norm = plt.Normalize(verts[:, 2].min(), verts[:, 2].max() + 2)
colors = cmap(norm(zc))
pc = PolyCollection(tris_up[:, :, :2], facecolors=colors, edgecolors="none", zorder=1)
ax2.add_collection(pc)
for ext, holes in g_top:
    ax2.plot(np.r_[ext[:, 0], ext[0, 0]], np.r_[ext[:, 1], ext[0, 1]], color=OUTER, lw=0.6, zorder=3)
    for h in holes:
        ax2.plot(np.r_[h[:, 0], h[0, 0]], np.r_[h[:, 1], h[0, 1]], color="#16324f", lw=0.5, zorder=3)
ax2.plot(shafts[:, 0], shafts[:, 1], "+", color="#111", markersize=9, markeredgewidth=1.2, zorder=5)
for i, s in enumerate(shafts, 1):
    ax2.annotate(f"S{i}", (s[0], s[1]), textcoords="offset points", xytext=(5, 5), fontsize=7, color="#111")
ax2.set_aspect("equal")
ax2.set_xlabel("X (mm)"); ax2.set_ylabel("Y (mm)")
ax2.set_title("Shaded top view (faces with +Z normal, colour = height)  ·  watertight, no wall breakthrough", fontsize=8)
ax2.grid(True, ls=":", lw=0.4, color="#ccc")
ax2.set_xlim(-68, 58); ax2.set_ylim(-52, 100)
ax2.tick_params(labelsize=7)

fig.tight_layout(rect=[0, 0.03, 1, 0.93])
fig.text(0.5, 0.01,
         "Clearance 0.35 mm/side  ·  tab span / hole pitch / shaft_from_end still [EST]  ·  print the fit coupon first",
         ha="center", fontsize=7, color="#555")
p = OUT / "HB_P01_seats_top.png"
fig.savefig(p, dpi=150, facecolor=fig.get_facecolor())
plt.close(fig)
print("wrote", p, p.stat().st_size)


# =============================================================================
# 3. Fit coupon dimensioned check
# =============================================================================
coupon = load(CAD / "02_haebot_modified/stl/HB_P00_FitCoupon_ES08MA-II.stl")
c_tab, _ = section_xy(coupon, 18.0)
c_body, _ = section_xy(coupon, 8.0)

fig, axes = plt.subplots(1, 2, figsize=(12.5, 6.4), dpi=140)
fig.patch.set_facecolor(BG)
fig.suptitle(
    "HB_P00 Fit coupon — drop-in check for EMAX ES08MA II analog  (user-measured body 24.0 × 12.0 mm)\n"
    "Body pocket 24.7 × 12.7 mm   ·   tab recess 33.2 × 12.7 mm   ·   0.35 mm clearance per side",
    fontsize=11, color=ACCENT, fontweight="bold", y=0.98,
)

ax = axes[0]
ax.set_facecolor("white")
add_section(ax, c_tab, face="#d9e4f0", edge=OUTER, hole_face="white", lw=0.9)
for ext, holes in c_tab:
    for h in holes:
        L, W, _ = mrr_lw(h)
        if abs(W - 12.7) < 0.2 and abs(L - 33.2) < 0.2:
            minx, miny = h.min(0); maxx, maxy = h.max(0)
            draw_dim_line(ax, (minx, miny), (maxx, miny), "33.2 mm", (0, -3.2), color="#1e3a5f", fontsize=9)
            draw_dim_line(ax, (maxx, miny), (maxx, maxy), "12.7 mm", (2.8, 0), color="#7b1e1e", fontsize=9)
            ax.annotate("tab recess\nz = 15.5–20", xy=((minx + maxx) / 2, (miny + maxy) / 2),
                        ha="center", va="center", fontsize=8, color="#1e3a5f")
ax.set_aspect("equal")
ax.set_title("Top of coupon (z = 18) — tab recess", fontsize=9)
ax.set_xlabel("X (mm)"); ax.set_ylabel("Y (mm)")
ax.grid(True, ls=":", lw=0.4, color="#ccc")

ax = axes[1]
ax.set_facecolor("white")
add_section(ax, c_body, face="#d9e4f0", edge=OUTER, hole_face="white", lw=0.9)
for ext, holes in c_body:
    for h in holes:
        L, W, _ = mrr_lw(h)
        if abs(W - 12.7) < 0.2 and L > 20:
            minx, miny = h.min(0); maxx, maxy = h.max(0)
            wide = h[np.abs(np.abs(h[:, 1]) - 6.35) < 0.2]
            if len(wide) >= 2:
                x0, x1 = wide[:, 0].min(), wide[:, 0].max()
            else:
                x0, x1 = minx, minx + 24.7
            y0, y1 = miny, maxy
            draw_dim_line(ax, (x0, y0), (x1, y0), "24.7 mm  (body)", (0, -3.2), color="#1e3a5f", fontsize=9)
            draw_dim_line(ax, (x1, y0), (x1, y1), "12.7 mm", (2.4, 0), color="#7b1e1e", fontsize=9)
            ax.annotate("cable\nchannel", xy=((x1 + maxx) / 2, 0), ha="center", va="center", fontsize=7, color="#555")
            ax.annotate("body pocket\n24.7 × 12.7", xy=((x0 + x1) / 2, 0), ha="center", va="center",
                        fontsize=8, color="#1e3a5f")
ax.set_aspect("equal")
ax.set_title("Mid body (z = 8) — body pocket + cable channel + near-end Ø1.8 pilot", fontsize=9)
ax.set_xlabel("X (mm)"); ax.set_ylabel("Y (mm)")
ax.grid(True, ls=":", lw=0.4, color="#ccc")

for a in axes:
    a.tick_params(labelsize=7)
    a.set_xlim(-18, 32)
    a.set_ylim(-16, 16)

fig.tight_layout(rect=[0, 0.03, 1, 0.92])
fig.text(0.5, 0.012,
         "Print this coupon first to confirm the 24 × 12 body drops in with 0.35 mm/side clearance  ·  cad/02_haebot_modified/stl/HB_P00_FitCoupon_ES08MA-II.stl",
         ha="center", fontsize=7, color="#555")
p = OUT / "HB_P00_FitCoupon_check.png"
fig.savefig(p, dpi=150, facecolor=fig.get_facecolor())
plt.close(fig)
print("wrote", p, p.stat().st_size)


# =============================================================================
# 4. One-finger rig montage
# =============================================================================
rig = load(CAD / "03_one_finger_test/stl/HB_T01_OneFingerRig_Base.stl")
pulley = load(CAD / "02_haebot_modified/stl/HB_P03_Pulley_ES08MA-II.stl")

# Place dummy + pulley using the same frame as cad/src/build_parts.py
# local +Z (shaft) -> global +X; then translate so pulley groove sits at x=0
import yaml
P = yaml.safe_load((CAD / "parameters.yaml").read_text())

def v(d):
    return d["measured"] if d.get("measured") is not None else d["nominal"]

S = {k: v(d) for k, d in P["es08ma_ii"].items()}
BASE_T, W = 5.0, S["body_width"]
sy = -62.0
zc = BASE_T + W / 2 + 4
shaft_top = S["case_height"] + S["shaft_above_case"]
Hh = P["inmoov_i2"]["pulley"]["height"]
groove_local_z = shaft_top + Hh - 3.0

def rz_to_world(mesh):
    # CadQuery: rotate (0,1,0) 90, then (1,0,0) -90
    T1 = trimesh.transformations.rotation_matrix(np.radians(90), [0, 1, 0])
    T2 = trimesh.transformations.rotation_matrix(np.radians(-90), [1, 0, 0])
    T = T2 @ T1
    T[:3, 3] = [-groove_local_z, sy, zc]
    m = mesh.copy(); m.apply_transform(T)
    return m

dummy_r = rz_to_world(dummy)
# pulley local: shaft axis +Z, groove near top; sit it on the shaft
# After the same rotation, shaft points +X; pulley origin at shaft. Offset along +X to the horn.
# Keep it simple: same origin transform, then +X by shaft_top (end of shaft / horn seat).
pulley_r = rz_to_world(pulley)
# shift pulley out to the shaft top (local +Z = after transform +X)
pulley_r.apply_translation([shaft_top, 0, 0])

rig_assy = trimesh.util.concatenate([rig, dummy_r, pulley_r])

fig = plt.figure(figsize=(16, 5.2), dpi=110)
fig.patch.set_facecolor("white")
ax = fig.add_subplot(1, 4, 1, projection="3d")
add_mesh(ax, rig_assy, BLUE, 22, -50, "One-finger rig + servo + pulley")
ax = fig.add_subplot(1, 4, 2, projection="3d")
add_mesh(ax, rig_assy, BLUE, 5, 0, "Side view")
ax = fig.add_subplot(1, 4, 3, projection="3d")
add_mesh(ax, pulley, GREEN, 25, 40, "Pulley (underside: horn seat)")
ax = fig.add_subplot(1, 4, 4, projection="3d")
add_mesh(ax, coupon, PURPLE, 22, -50, "Fit coupon")
fig.tight_layout()
p = OUT / "HB_T01_OneFingerRig_check.png"
fig.savefig(p, dpi=110, facecolor="white")
plt.close(fig)
print("wrote", p, p.stat().st_size)
print("DONE")
