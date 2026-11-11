"""Wrap a mesh STL into a faceted STEP solid (for parts that only exist as meshes,
e.g. the modified InMoov WristLarge). The STEP is triangle-faceted, not feature-based:
it imports into Fusion 360 / FreeCAD / SolidWorks as a solid body you can cut, extrude
or measure, but it has no parametric history."""
import sys
from OCP.StlAPI import StlAPI_Reader
from OCP.TopoDS import TopoDS_Shape, TopoDS
from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing, BRepBuilderAPI_MakeSolid
from OCP.STEPControl import STEPControl_Writer, STEPControl_AsIs
from OCP.TopAbs import TopAbs_SHELL
from OCP.TopExp import TopExp_Explorer
from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
shape = TopoDS_Shape(); StlAPI_Reader().Read(shape, sys.argv[1])
sew = BRepBuilderAPI_Sewing(1e-3); sew.Add(shape); sew.Perform(); sewn = sew.SewedShape()
mk = BRepBuilderAPI_MakeSolid(); ex = TopExp_Explorer(sewn, TopAbs_SHELL)
while ex.More(): mk.Add(TopoDS.Shell_s(ex.Current())); ex.Next()
u = ShapeUpgrade_UnifySameDomain(mk.Solid(), True, True, False); u.Build()  # merge coplanar facets
w = STEPControl_Writer(); w.Transfer(u.Shape(), STEPControl_AsIs); w.Write(sys.argv[2]); print("ok", sys.argv[2])
