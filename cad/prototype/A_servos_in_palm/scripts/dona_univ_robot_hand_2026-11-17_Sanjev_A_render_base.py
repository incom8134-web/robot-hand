"""Preview PNGs for the P1 base (numpy z-buffer renderer). Run after ..._A_base_build.py. Green = PSU + inlet envelopes (reference)."""
import os, sys
sys.dont_write_bytecode = True
import numpy as np, trimesh, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__))
import importlib.util as _iu
_ps = _iu.spec_from_file_location("p1paths", os.path.join(HERE, "dona_univ_robot_hand_2026-11-17_Sanjev_A_paths.py"))
paths = _iu.module_from_spec(_ps); _ps.loader.exec_module(paths); F = paths.F
_src = open(F("render.py")).read()
exec(_src[_src.index("BG = "):_src.index("def dec(m")])       # same renderer as the hand
L = lambda n: trimesh.load(F(n + ".stl"))
pan, lid, ref, board = L("10_base_pan"), L("11_base_lid"), L("ref_base_psu_iec"), L("ref_board_100x60")
Z = np.zeros(3); SV, WH = "#8e949c", "#ffffff"          # base: silver pan, white lid (user 2026-11-17)
views = [
    ("img_10_base_open.png", [(pan, SV, Z), (ref, "#555a63", Z), (board, "#2ea043", Z), (lid, WH, np.array([0, 0, 70.0]))], 35, -60,
     "P1 base - lid lifted: SMPS at the back, board front-left (green), inlet in the right wall (mains corner)"),
    ("img_11_base_back.png", [(pan, SV, Z), (lid, WH, Z)], 20, 60, "P1 base - right side: your C14 inlet (fuse + switch, screw mount)"),
    ("img_12_base_front.png", [(pan, SV, Z), (lid, WH, Z)], 25, -110, "P1 base - front: USB mini-B, vents, socket for the forearm"),
    ("img_14_base_usb_closeup.png", [(pan, SV, Z), (lid, WH, Z), (board, "#2ea043", Z)], 8, -90, "P1 base - front, straight on: USB mini-B hole (14 x 9 mm + 2 x M3, 28 mm pitch)"),
]
for name, ms, el, az, title in views:
    img = render(ms, el, az)
    fig = plt.figure(figsize=(9, 9 * img.shape[0] / img.shape[1] + 0.6)); plt.imshow(img); plt.axis("off"); plt.title(title, fontsize=9)
    fig.text(0.01, 0.005, "HAEBOT P1 base. Real CAD export, not printed.", fontsize=8)
    plt.savefig(F(name), dpi=100, bbox_inches="tight"); plt.close(fig)
print("ok")
