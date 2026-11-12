"""Small offscreen mesh renderer (matplotlib, Lambert shading) for before/after checks."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

def render(mesh, path, elev=20, azim=-60, title="", xlim=None, ylim=None, zlim=None, size=8, color=(0.75,0.78,0.85), clip=None, highlight=None):
    m = mesh
    if clip is not None:  # keep faces whose centroid is inside box
        lo, hi = np.array(clip[0]), np.array(clip[1])
        c = m.triangles_center
        keep = np.all((c >= lo) & (c <= hi), axis=1)
        m = m.submesh([np.where(keep)[0]], append=True)
    az, el = np.radians(azim), np.radians(elev)
    view = np.array([np.cos(el)*np.cos(az), np.cos(el)*np.sin(az), np.sin(el)])
    front = m.face_normals @ view > 0          # back-face culling (fixes painter's-algorithm artefacts)
    m = m.submesh([np.where(front)[0]], append=True)
    tris = m.triangles
    n = m.face_normals
    light = view + np.array([0.3, 0.2, 0.5]); light /= np.linalg.norm(light)
    shade = np.clip(n @ light, 0, 1) * 0.75 + 0.25
    cols = np.outer(shade, color)
    if highlight is not None:
        cols[highlight[:len(cols)]] = np.outer(shade[highlight[:len(cols)]], (0.1, 0.45, 0.85))
    fig = plt.figure(figsize=(size, size))
    ax = fig.add_subplot(111, projection="3d")
    pc = Poly3DCollection(tris, facecolors=np.clip(cols,0,1), edgecolors="none", linewidths=0)
    ax.add_collection3d(pc)
    b = m.bounds
    ctr = b.mean(0); r = (b[1]-b[0]).max()/2
    ax.set_xlim(*(xlim or (ctr[0]-r, ctr[0]+r)))
    ax.set_ylim(*(ylim or (ctr[1]-r, ctr[1]+r)))
    ax.set_zlim(*(zlim or (ctr[2]-r, ctr[2]+r)))
    ax.set_box_aspect((1,1,1))
    ax.view_init(elev=elev, azim=azim)
    ax.set_xlabel("X"); ax.set_ylabel("Y"); ax.set_zlabel("Z")
    ax.set_title(title)
    fig.tight_layout(); fig.savefig(path, dpi=110); plt.close(fig)
