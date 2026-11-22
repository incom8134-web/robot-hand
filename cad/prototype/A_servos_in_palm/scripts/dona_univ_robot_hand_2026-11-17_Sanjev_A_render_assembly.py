"""P1 full assembly preview + fit check: base (PSU + board) + stock-size InMoov forearm + hand (x1.28, 5 servos, fingers).
Run after the hand, forearm and base build scripts. Writes img_20..22 and assembly_report.json."""
import os, sys, json
sys.dont_write_bytecode = True
import numpy as np, trimesh, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__))
import importlib.util as _iu
_ps = _iu.spec_from_file_location("p1paths", os.path.join(HERE, "dona_univ_robot_hand_2026-11-17_Sanjev_A_paths.py"))
paths = _iu.module_from_spec(_ps); _ps.loader.exec_module(paths); F = paths.F
_src = open(F("render.py")).read()
exec(_src[_src.index("BG = "):_src.index("def dec(m")])
L = lambda n: trimesh.load(F(n + ".stl"))
base = json.load(open(F("base_report.json"))); fa = json.load(open(F("forearm_report.json")))
H_LID_TOP = base["pan_mm"][2] + base["lid_t"]
sx, sy = base["forearm_socket"]["forearm_xy_shift"]
T_ARM = np.eye(4); T_ARM[:3, 3] = [sx, sy, H_LID_TOP]                     # forearm elbow end sits on the lid
# hand -> arm: X = x, Y = z, Z = -y (fingers up); hand pin (gap centre x, pin y, pin z) onto the tongue bore
S = 1.28
hand_pin = np.array([-17.41, 106.12, 13.96])          # measured on the P1 palm frame (gap centre x, pin y, pin z)
R = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], float)
arm_pin = np.array([fa["wrist"]["pin_xy"][0], fa["wrist"]["pin_xy"][1], fa["wrist"]["pin_z"]])
T_HAND = np.eye(4); T_HAND[:3, :3] = R; T_HAND[:3, 3] = arm_pin - R @ hand_pin
T_HAND = T_ARM @ T_HAND
def put(n, T):
    m = L(n); m.apply_transform(T); return m
import importlib.util
_spec = importlib.util.spec_from_file_location("fa", F("forearm_build.py")); _fa = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_fa)
arm = [put(n, T_ARM @ _fa.asm_matrix(n)) for n in ("05a_forearm_robpart2", "05b_forearm_robpart3", "05c_forearm_robpart4", "05d_forearm_robpart5")]   # STLs are in print orientation
blk, board = put("06_wrist_block", T_ARM), L("ref_board_100x60")          # board is in the base (base frame)
hand = [put(n, T_HAND) for n in ("01_palm_frame", "02_back_cover", "03_palm_cover")]
servos = put("ref_sts3215_x5_placed", T_HAND); fingers = put("ref_fingers_placed", T_HAND)
pan, lid = L("10_base_pan"), L("11_base_lid")
# fit checks
I = lambda a, b: float(trimesh.boolean.intersection([a, b], engine="manifold").volume)
rep = dict(hand_vs_wrist_block_mm3=round(sum(I(h, blk) for h in hand), 2),
           hand_vs_forearm_mm3=round(sum(I(h, a) for h in hand for a in arm), 2),
           forearm_vs_base_lid_mm3=round(sum(I(a, lid) for a in arm), 2),
           board_vs_base_mm3=round(I(board, pan) + I(board, lid), 2),
           total_height_mm=round(max(m.bounds[1][2] for m in hand + [fingers]), 1),
           forearm_scale=fa.get("forearm_scale"),
           note="fingers placed straight, look only (thumb position approximate)")
json.dump(rep, open(F("assembly_report.json"), "w"), indent=1); print(rep)
def dec(m, n=40000): return m.simplify_quadric_decimation(face_count=n) if len(m.faces) > n else m
# colours (user 2026-11-17): palm side black, other hand parts white, arm silver, base silver pan + white lid
Z = np.zeros(3); GR, W_, BK, SV, YE = "#2b2b2b", "#ffffff", "#141416", "#8e949c", "#2ea043"
scene = [(dec(hand[0]), W_, Z), (dec(hand[1]), W_, Z), (dec(hand[2]), BK, Z), (dec(fingers), W_, Z), (dec(blk), SV, Z)] + \
        [(dec(a), SV, Z) for a in arm] + [(dec(pan), SV, Z), (dec(lid), W_, Z)]
cut = [(dec(hand[0]), W_, Z), (dec(servos, 30000), GR, Z), (dec(fingers), W_, Z), (dec(blk), "#e05a5a", Z), (dec(board), YE, Z),
       (dec(arm[0]), SV, Z), (dec(arm[3]), SV, Z), (dec(pan), SV, Z)]   # covers, front shells (robpart3, robpart4) and lid removed
views = [("img_20_full_arm.png", scene, 15, -60, "P1 full arm: hand (5 x STS3215) + InMoov forearm + power base"),
         ("img_21_full_arm_side.png", scene, 10, 20, "P1 full arm - side"),
         ("img_22_forearm_inside.png", cut, 15, -60, "Opened: 5 servos in the palm, wrist block (red), 100 x 60 board in the base (green)")]
for name, ms, el, az, title in views:
    img = render(ms, el, az, res=1000)
    fig = plt.figure(figsize=(7, 7 * img.shape[0] / img.shape[1] + 0.6)); plt.imshow(img); plt.axis("off"); plt.title(title, fontsize=9)
    fig.text(0.01, 0.005, "HAEBOT P1 = InMoov i2 hand x1.28 + InMoov forearm (stock width; elbow half 1.35x, wrist half 1.10x long). Real CAD export, not printed. Fingers placed for look only.", fontsize=7)
    plt.savefig(F(name), dpi=110, bbox_inches="tight"); plt.close(fig)
print("ok")
