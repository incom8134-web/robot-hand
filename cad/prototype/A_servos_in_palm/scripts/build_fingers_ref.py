"""P1 look-only finger reference: the stock InMoov i2 fingers (i2_FingersX5V2, x1.28) placed straight on the P1 palm.
Output reference/ref_fingers_placed.stl in the HAND frame (same frame as 01_palm_frame.stl). For renders / STEP only - do NOT print
from this file; print the fingers from the original i2 file scaled 1.28x.
Knuckle hinge holes (Ø4.2 at z 11.5) were measured on 01_palm_frame.stl; the thumb position is approximate (look only)."""
import os, sys, json
sys.dont_write_bytecode = True
import numpy as np, trimesh
HERE = os.path.dirname(os.path.abspath(__file__))
import importlib.util as _iu
_ps = _iu.spec_from_file_location("p1paths", os.path.join(HERE, "dona_univ_robot_hand_2026-11-17_Sanjev_A_paths.py"))
paths = _iu.module_from_spec(_ps); _ps.loader.exec_module(paths); F = paths.F

S = 1.28
SRC = os.path.join(paths.ORIG, "hand_i2", "dona_univ_robot_hand_2026-11-13_Sanjev_i2_fingersx5v2.stl")
HINGE_Z = 11.5
# finger: (hinge centre x, y) measured on the palm frame, direction angle (deg, hand frame; fingers point to -y)
FINGERS = {"index": (32.3, -35.2, -85.7), "middle": (0.0, -47.2, -90.0), "ring": (-35.0, -31.9, -94.9), "pinky": (-64.5, -10.9, -99.4)}
THUMB = (56.0, 34.0, -62.0)          # APPROXIMATE root + direction (look only)
HINGE_FROM_END = 6.0 * S             # hinge hole centre to the piece end
JOINT_OVERLAP = 8.0 * S              # proximal / distal pieces overlap at the middle joint

def pieces():
    m = trimesh.load(SRC); m.apply_scale(S)
    parts = sorted(m.split(only_watertight=False), key=lambda p: -p.extents[1])
    thumb, prox, dist = parts[0], parts[1:5], parts[5:9]
    return thumb, prox, dist

def tip_at_max_y(p):
    """True if the narrow (tip) end of a piece is at +y in its print frame."""
    lo, hi = p.bounds[:, 1]
    a = lambda y: sum(e.area for e in [p.section(plane_origin=[0, y, 0], plane_normal=[0, 1, 0])] if e is not None for e in [e.to_2D()[0]])
    return a(hi - 4) < a(lo + 4)

def place(p, root_xy, ang, start_back, tip_last=True):
    """lay a piece along direction ang from root (piece y -> finger direction, x -> across, z -> palm z)."""
    q = p.copy()
    if tip_at_max_y(q) != tip_last:                                     # flip so the tip end points away from the palm
        q.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [0, 0, 1], q.centroid))
    b = q.bounds
    q.apply_translation([-(b[0][0] + b[1][0]) / 2, -b[0][1] - start_back, HINGE_Z - (b[0][2] + b[1][2]) / 2])
    a = np.radians(ang)
    d, n = np.array([np.cos(a), np.sin(a)]), np.array([np.sin(a), -np.cos(a)])   # local y -> d, local x -> n
    T = np.eye(4); T[:2, 0], T[:2, 1], T[:2, 3] = n, d, root_xy
    q.apply_transform(T)
    return q

if __name__ == "__main__":
    thumb, prox, dist = pieces()
    out = []
    for (name, (x, y, ang)), pr, di in zip(FINGERS.items(), prox, dist):
        L = pr.extents[1]
        out.append(place(pr, (x, y), ang, HINGE_FROM_END))
        out.append(place(di, (x, y), ang, HINGE_FROM_END - (L - JOINT_OVERLAP)))
    out.append(place(thumb, THUMB[:2], THUMB[2], 0.0))
    m = trimesh.util.concatenate(out)
    m.export(F("ref_fingers_placed.stl"))
    print("fingers ref", [round(v, 1) for v in m.bounds.flatten()])
