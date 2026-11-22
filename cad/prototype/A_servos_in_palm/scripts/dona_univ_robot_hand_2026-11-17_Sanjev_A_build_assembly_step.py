"""
P1 full-arm STEP assembly for viewing in Fusion 360 / SolidWorks (one file, named + coloured parts, real positions).
Run after build_hand, build_forearm, build_base. Writes assembly/asm_P1_full_arm.step.

- base pan / lid / PSU straps / ring pulleys: the real parametric STEP solids (exact B-rep)
- 5 x STS3215: the Feetech STEP model (exact)
- InMoov-derived parts (palm frame, covers, forearm shells) and the wrist block: meshes converted to faceted
  solids; the curved InMoov parts are simplified (VIEW_FACES) so the file stays openable. For printing use the STLs in print/.
"""
import os, sys, json, math
sys.dont_write_bytecode = True
import numpy as np, trimesh
import cadquery as cq
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace, BRepBuilderAPI_Sewing, BRepBuilderAPI_MakeSolid
from OCP.gp import gp_Pnt
from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
from OCP.TopoDS import TopoDS
HERE = os.path.dirname(os.path.abspath(__file__))
import importlib.util as _iu
def _load(fn, name):
    sp = _iu.spec_from_file_location(name, fn); m = _iu.module_from_spec(sp); sp.loader.exec_module(m); return m
paths = _load(os.path.join(HERE, "dona_univ_robot_hand_2026-11-17_Sanjev_A_paths.py"), "p1paths"); F = paths.F

VIEW_FACES = {"ref_fingers_placed": 8000, "01_palm_frame": 6000, "02_back_cover": 9000, "03_palm_cover": 8000, "06_wrist_block": 2500,
              "05a_forearm_robpart2": 3000, "05b_forearm_robpart3": 3000, "05c_forearm_robpart4": 3000, "05d_forearm_robpart5": 3000}
# colours (user 2026-11-17): palm side black, other hand parts white, arm silver, base silver pan + white lid
COL = {"hand": (1.0, 1.0, 1.0), "back": (1.0, 1.0, 1.0), "palm": (0.08, 0.08, 0.09), "arm": (0.56, 0.58, 0.61), "arm_blue": (0.56, 0.58, 0.61),
       "servo": (0.12, 0.12, 0.12), "pulley": (0.90, 0.75, 0.20), "block": (0.56, 0.58, 0.61), "tray": (0.95, 0.56, 0.17),
       "board": (0.18, 0.63, 0.26), "base": (0.56, 0.58, 0.61), "lid": (1.0, 1.0, 1.0), "strap": (0.35, 0.35, 0.35)}

def mesh_to_shape(m, max_faces=None):
    if max_faces and len(m.faces) > max_faces:
        import manifold3d as mf
        d = m.simplify_quadric_decimation(face_count=max_faces)
        M = mf.Manifold(mf.Mesh(vert_properties=np.asarray(d.vertices, np.float32), tri_verts=np.asarray(d.faces, np.uint32))).to_mesh()
        m = trimesh.Trimesh(M.vert_properties[:, :3], M.tri_verts)
    sew = BRepBuilderAPI_Sewing(1e-3); V = m.vertices
    for f in m.faces:
        p = BRepBuilderAPI_MakePolygon(gp_Pnt(*V[f[0]]), gp_Pnt(*V[f[1]]), gp_Pnt(*V[f[2]]), True)
        sew.Add(BRepBuilderAPI_MakeFace(p.Wire(), True).Face())
    sew.Perform(); sh = sew.SewedShape()
    u = ShapeUpgrade_UnifySameDomain(sh, True, True, False); u.Build(); sh = u.Shape()
    try: return cq.Shape.cast(BRepBuilderAPI_MakeSolid(TopoDS.Shell_s(sh)).Solid())
    except Exception: return cq.Shape.cast(sh)

def loc(T):
    """4x4 numpy -> cq.Location (rotation + translation)"""
    from OCP.gp import gp_Trsf
    t = gp_Trsf()
    t.SetValues(*[float(T[i, j]) for i in range(3) for j in range(4)])
    return cq.Location(t)

def main():
    fa = _load(F("forearm_build.py"), "fa")
    hand = _load(F("build.py"), "hand")
    base_rep = json.load(open(F("base_report.json"))); fa_rep = json.load(open(F("forearm_report.json")))
    # same placement as render_assembly
    T_ARM = np.eye(4); T_ARM[:3, 3] = [*base_rep["forearm_socket"]["forearm_xy_shift"], base_rep["pan_mm"][2] + base_rep["lid_t"]]
    R = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], float)
    hand_pin = np.array([-17.41, 106.12, 13.96])
    arm_pin = np.array([fa_rep["wrist"]["pin_xy"][0], fa_rep["wrist"]["pin_xy"][1], fa_rep["wrist"]["pin_z"]])
    T_HAND = np.eye(4); T_HAND[:3, :3] = R; T_HAND[:3, 3] = arm_pin - R @ hand_pin; T_HAND = T_ARM @ T_HAND
    asm = cq.Assembly(name="HAEBOT_P1_full_arm")
    def add_mesh(key, T, color, name):
        m = trimesh.load(F(key + ".stl")); m.apply_transform(T)
        asm.add(mesh_to_shape(m, VIEW_FACES.get(key)), name=name, color=cq.Color(*color))
    # hand
    add_mesh("01_palm_frame", T_HAND, COL["hand"], "01_palm_frame")
    add_mesh("02_back_cover", T_HAND, COL["back"], "02_back_cover_logo")
    add_mesh("03_palm_cover", T_HAND, COL["palm"], "03_palm_cover")
    add_mesh("ref_fingers_placed", T_HAND, COL["hand"], "ref_fingers_i2_x1.28_look_only")
    servo = cq.importers.importStep(hand.SERVO_STEP).val()
    pulley = cq.importers.importStep(F("04_ring_pulley_x5.step")).val()
    for k in hand.SLOTS:
        Ts = T_HAND @ hand.place(k)
        asm.add(servo, name=f"STS3215_{hand.SERVO_ID[k]}_{k}", loc=loc(Ts), color=cq.Color(*COL["servo"]))
        Tp = Ts @ trimesh.transformations.translation_matrix([hand.SHAFT_X, 0, hand.HORN_Z[1] - hand.RP_SKIRT])
        asm.add(pulley, name=f"04_ring_pulley_{k}", loc=loc(Tp), color=cq.Color(*COL["pulley"]))
    # forearm (STLs are in print orientation -> assembled)
    for key in ("05a_forearm_robpart2", "05b_forearm_robpart3", "05c_forearm_robpart4", "05d_forearm_robpart5"):
        add_mesh(key, T_ARM @ fa.asm_matrix(key), COL["arm_blue" if key[2] in "cd" else "arm"], key)
    add_mesh("06_wrist_block", T_ARM, COL["block"], "06_wrist_block")
    b = trimesh.load(F("ref_board_100x60.stl"))                     # board is in the base (base frame)
    (x0, y0, z0), (x1, y1, z1) = b.bounds
    asm.add(cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0)).val(), name="ref_board_100x60_envelope", color=cq.Color(*COL["board"]))
    # base (exact STEP)
    asm.add(cq.importers.importStep(F("10_base_pan.step")).val(), name="10_base_pan", color=cq.Color(*COL["base"]))
    asm.add(cq.importers.importStep(F("11_base_lid.step")).val(), name="11_base_lid", color=cq.Color(*COL["lid"]))
    bb = _load(F("base_build.py"), "bb")
    strap = cq.importers.importStep(F("12_psu_strap_x2.step")).val()
    for i, x in enumerate((bb.PSU_LO[0] + 45, bb.PSU_HI[0] - 45)):
        T = trimesh.transformations.translation_matrix([x - 7, bb.PSU_LO[1] - bb.PSU_CLR - 8, bb.PSU_HI[2] + 2])
        asm.add(strap, name=f"12_psu_strap_{i + 1}", loc=loc(T), color=cq.Color(*COL["strap"]))
    psu = cq.Workplane("XY").box(*[bb.PSU_HI[i] - bb.PSU_LO[i] for i in range(3)], centered=False).translate(tuple(bb.PSU_LO)).val()
    asm.add(psu, name="ref_MeanWell_LRS-350-12_envelope", color=cq.Color(0.6, 0.6, 0.6))
    out = F("asm_P1_full_arm.step")
    asm.save(out)
    print("wrote", out, round(os.path.getsize(out) / 1e6, 1), "MB")

if __name__ == "__main__":
    main()
