import os
import re as _re

occtBasePath = "/occt/src/"

def _generateHandleTypedefs() -> str:
  """Generate Handle_ClassName typedefs for all OCCT classes using DEFINE_STANDARD_RTTIEXT.

  OCCT 8.0 removed DEFINE_STANDARD_HANDLE from most classes, so Handle_ClassName
  typedefs no longer exist. The binding generator needs these typedefs to create
  Handle binding files via templateTypedefGenerator.
  """
  typedefs = []
  seen = set()
  pattern = _re.compile(r'DEFINE_STANDARD_RTTIEXT\s*\(\s*(\w+)\s*,')
  # Classes that are macro parameters or unavailable in WASM builds
  _skip = {'Class'}
  _skip_prefixes = ('IVtk', 'IVtkVTK', 'IVtkOCC', 'IVtkDraw')
  for dirpath, dirnames, filenames in os.walk(occtBasePath):
    for fname in filenames:
      if not fname.endswith('.hxx'):
        continue
      filepath = os.path.join(dirpath, fname)
      try:
        with open(filepath, 'r', errors='replace') as f:
          for line in f:
            m = pattern.search(line)
            if m:
              className = m.group(1)
              if className in _skip or className.startswith(_skip_prefixes):
                continue
              if className not in seen:
                seen.add(className)
                typedefs.append(
                  f"typedef opencascade::handle<{className}> Handle_{className};"
                )
      except OSError:
        pass
  return "\n".join(typedefs)

handleTypedefs = _generateHandleTypedefs()
print(f"Generated {len(handleTypedefs.splitlines())} Handle typedefs for OCCT 8.0 compatibility")

# OCCT 8.0 moved NCollection aliases to Deprecated/NCollectionAliases/.
# We can't #include those headers (some have broken #include chains referencing
# removed OCCT types). Instead, inject the needed typedefs directly into myMain.h.
# Add entries here for any NCollection alias your build config requires.
ncollectionTypedefs = "\n".join([
  "typedef NCollection_Array1<gp_Pnt> TColgp_Array1OfPnt;",
  "typedef NCollection_Array1<gp_Dir> TColgp_Array1OfDir;",
  "typedef NCollection_Array1<gp_Pnt2d> TColgp_Array1OfPnt2d;",
  "typedef NCollection_Array1<gp_Vec> TColgp_Array1OfVec;",
  "typedef NCollection_Array1<double> TColStd_Array1OfReal;",
  "typedef NCollection_Array1<int> TColStd_Array1OfInteger;",
  "typedef NCollection_IndexedMap<TopoDS_Shape, TopTools_ShapeMapHasher> TopTools_IndexedMapOfShape;",
  "typedef NCollection_Array1<Poly_Triangle> Poly_Array1OfTriangle;",
  "typedef NCollection_HArray1<gp_Pnt> TColgp_HArray1OfPnt;",
  "typedef opencascade::handle<TColgp_HArray1OfPnt> Handle_TColgp_HArray1OfPnt;",
])
print(f"Injecting {len(ncollectionTypedefs.splitlines())} NCollection typedefs for OCCT 8.0 compatibility")
