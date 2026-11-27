# Faster, smaller "open-and-measure" export formats for mesh-based assemblies

Context: the current pipeline goes STL meshes, then faceted B-rep solids, then STEP. It takes about 38 s for 14 parts and produces an 89 MB file. Every finding below is backed by a web source or by a local benchmark run on 2026-11-27 (FreeCAD 1.1 freecadcmd + trimesh 5.2.2, scripts in scratchpad). Local numbers are labelled "[local benchmark]".

## 1. Why faceted-B-rep STEP made from meshes is large and slow, and how to shrink it

### Takeaway
Each triangle becomes a separate B-rep face, with its own plane, loop, edges and vertices. That costs roughly 1 KB of STEP text per triangle, so file size and build time grow linearly with triangle count. "Refine / UnifySameDomain" only merges coplanar faces. It does not turn a faceted cylinder or sphere back into an analytic surface, so it helps only for prismatic parts (box-like parts with many flat faces).

### Cited findings
- A 100,000-triangle STL becomes a STEP file with 100,000 individual faces, which "drastically increases file size and consumes heavy RAM". Flipped normals, overlapping triangles or tiny holes make solid creation fail and leave a surface model. — [Convert.Guru STL→STP](https://convert.guru/stl-to-stp)
- You cannot make such a file smaller on import. The creator has to use a larger (coarser) tessellation tolerance. — [PTC community](https://community.ptc.com/3d-part-assembly-design-327/importing-large-stl-file-115563)
- OCCT: converting a ~4 MB STL by creating one face per triangle and then calling `BRepBuilderAPI_Sewing` took ~13 h. Almost all of that time was in `Sewing::Perform()`, and changing the tolerance made no difference. The OCCT developer said sewing "is not designed for such kind of input". The advice was to build the B-rep with shared vertices and edges from the start instead of sewing. Reconstructing analytic or B-spline surfaces (SSP, GeomPlate) is complex and usually needs a human in the loop. — [OCCT forum: Conversion from STL to STEP is slow](https://occt3d.com/dev/content/conversion-stl-step-slow/index.html)
- FreeCAD workflow: Shape from mesh, then Convert to solid, then Refine shape. Refine is optional and "cleans the solid of most residual edges on planar and cylindrical surfaces". — [FreeCAD wiki: FreeCAD and Mesh Import](https://wiki.freecad.org/FreeCAD_and_Mesh_Import)
- `ShapeUpgrade_UnifySameDomain::UnifyFaces` "makes if possible a common face from each group of faces lying on coincident surfaces". — [OCCT 8.0.0 refman](https://dev.opencascade.org/doc/refman/html/class_shape_upgrade___unify_same_domain.html). It has known bugs that produce invalid faces (OCCT 7.7.1). — [OCCT forum](https://dev.opencascade.org/content/shapeupgradeunifysamedomain-possible-problem)
- [local benchmark] FreeCAD 1.1 `makeShapeFromMesh(tol 0.01)` + `makeSolid` + `exportStep`:
  - icosphere with 20,480 triangles: 20,480 faces, **22.0 MB STEP (~1,075 B/triangle)**. Build 6.5 s, build+write 8.8 s. `removeSplitter()` (Refine) took a further **21.9 s** and still left 20,480 faces and the same size, because no two faces are coplanar.
  - box with 12 triangles: 12 faces (10.5 KB). After refine: 6 faces (6.9 KB).
  - cylinder with 64 sides (256 triangles): 256 faces (225 KB). After refine: 66 faces (98 KB, −57 %). The 2 end caps merged, and each side pair of triangles merged into a flat rectangle, but **no cylindrical surface was recreated**.
  - The STL source of the 20,480-triangle sphere is 1.0 MB, so the faceted STEP is ~21× larger than the binary STL.

### Inferences
- At ~1.07 KB/triangle, 89 MB corresponds to roughly 80–85k triangles across the 14 parts. This is an estimate. TODO: check against the actual triangle count.
- In faceted STEP, size is proportional to triangle count. Halving the triangles (decimating or meshing more coarsely in the generator) halves both size and time. This is the cheapest lever if the output must stay STEP.
- Refine only pays off for parts with large flat faces (box-like parts, mounting plates). For round parts it costs more time than it saves. If you use it, apply it selectively, for example only to parts with a high ratio of coplanar triangles.
- The fastest way is not to go through mesh at all. If the parts are generated parametrically (SolidCraft / build123d / CadQuery), export the original analytic B-rep straight to STEP. Faces then correspond to real faces, not triangles. Whether SolidCraft can export B-rep instead of STL is outside this note's scope (TODO).

### Gaps
- No public measurement of the time for OCCT `BRepBuilderAPI_MakeShapeOnMesh` (the fast shared-topology mesh-to-B-rep path) at large triangle counts. Its existence and speed were not verified in this round.
- No reliable automatic tool was found that turns a faceted mesh back into planes and cylinders for free (mesh-to-CAD reverse engineering). Commercial tools exist, but no numbers were found.

## 2. STEP AP242 tessellated geometry (tessellated_shape_representation)

### Takeaway
AP242 lets STEP store triangle meshes directly (TRIANGULATED_FACE with point and index arrays) instead of one B-rep face per triangle. OCCT 7.7+ can read and write this. The catch is that support in commercial CAD is uneven: SolidWorks opens it as a graphics body, and no documentation confirms Fusion or Onshape import tessellated STEP.

### Cited findings
- OCCT STEP translator:
  - `read.step.tessellated` reads TESSELLATED_SHAPE_REPRESENTATION, TESSELLATED_SHELL, TESSELLATED_SOLID, TRIANGULATED_FACE and COMPLEX_TRIANGULATED_FACE into `Poly_Triangulation`. Default 1 (On).
  - `write.step.tessellated` writes TESSELLATED_SHAPE_REPRESENTATION, TESSELLATED_SHELL, TESSELLATED_SOLID and TRIANGULATED_FACE, taken from the active triangulation of each TopoDS_Face. Values: 0 Off / 1 On / 2 OnNoBRep. **Default 2 (OnNoBRep)**: tessellation is written only for entities that have no B-rep.

  — [OCCT User Guide: STEP translator](https://occt3d.com/dev/doc/overview/html/occt_user_guides__step.html)
- Tessellated-STEP support first appeared in OCCT 7.7.0. — [OCCT forum: Retrieve tessellated geometry from STEP](https://dev.opencascade.org/content/retrieve-tessellated-geometry-step)
- Usage example from the forum: set `write.step.schema` = AP242DIS, `write.step.tessellated` = On, and initialise the STEP controller first. Known issues:
  - UV data is not generated for tessellated objects. For pure mesh export, a maintainer recommends glTF/OBJ.
  - OCCT 7.7.1 fails on TRIANGULATED_FACE without pnindex (fixed in March 2024).
  - 7.8.0 fails on triangulated_face that is not tied to a B-rep surface.

  — [OCCT forum: UV data missing](https://dev.opencascade.org/content/uv-data-missing-tessellated-geometry-objects); [OCCT forum: Problems exporting pre-tessellated geometry](https://dev.opencascade.org/content/problems-exporting-pre-tessellated-geometry-step); [search summary from tracker #33623/#33412](https://tracker.dev.opencascade.org/view.php?id=33623)
- SolidWorks: a STEP file with FACETEDBREP data is imported as a **graphics body** by default, and you must choose "Load Geometry" to get B-rep. The "As Graphical Body" option (3D Interconnect) imports tessellated third-party files as graphical meshes. — [SolidWorks Help: Reading Tessellation Data from Third-Party CAD Files](https://help.solidworks.com/2025/English/SolidWorks/sldworks/t_reading_tessellated_data_third_party_cad.htm); [Importing STEP, IGES, ACIS](https://help.solidworks.com/2024/English/SolidWorks/Sldworks/t_reading_step_iges_acis_sw.htm). A forum user reports a tessellated STEP that showed no graphics in SolidWorks (no answer). — [3DSwym forum](https://3dswym.3dexperience.3ds.com/question/solidworks-user-forum/can-solidworks-import-read-tessellated-data-and-the-step-format-ap242_PiKYFKZzQ2CqJTQ1gQTiiQ)
- PTC Creo reads and writes 3D tessellation for parts and assemblies in STEP ap242 / ap242_e3. — [PTC Creo: About STEP Files](https://support.ptc.com/help/creo/creo_pma/usascii/data_exchange/interface/About_STEP_Files.html)
- Onshape lists STEP AP203/214/242 for parts and assemblies, "geometry and face color only". It does not mention tessellated data. — [Onshape Supported File Formats](https://cad.onshape.com/help/Content/File/supported_file_formats.htm)

### Inferences
- In tessellated STEP, each vertex and triangle is an entry in a list rather than a chain of ~10 entities (plane, edge loop, vertices...). The file should therefore be much smaller than faceted B-rep, but **no published number was found**. TODO: measure yourself with OCP/pythonOCC (FreeCAD 1.1's Python does not readily expose `Interface_Static`; not tested).
- Since "open in any CAD and measure" is the goal, tessellated STEP is risky: SolidWorks shows it as a graphics body (whether you can measure on it is not confirmed), and nothing confirms Fusion or Onshape support it. Do not use it as the only format.

### Gaps
- No documentation on whether Fusion and Onshape import STEP AP242 tessellated data.
- No published size comparison between tessellated STEP and faceted B-rep.
- Whether FreeCAD 1.x enables the tessellated option on STEP import is unclear (the OCCT read default is On, but FreeCAD's import path was not verified).
- Whether CadQuery/build123d expose tessellated STEP writing: not found.

## 3. 3MF assembly and GLB/glTF: CAD support, size, write speed

### Takeaway
3MF and GLB are much smaller and faster to write than faceted STEP: [local benchmark] tens of ms and roughly 13–18 B/triangle, versus ~1 KB/triangle and seconds. 3MF carries multiple named objects with transforms, and Bambu Studio, Onshape, SolidWorks and Fusion all import it. The downside is that it opens as a mesh, so you measure vertex to vertex or face to face, not to the centre of a real hole.

### Cited findings
- [local benchmark] Scene with 3 meshes (sphere 20,480 + box 12 + cylinder 256 triangles, 20,748 total) exported with trimesh 5.2.2:
  - **3MF 263,520 B in 0.068 s**
  - **GLB 375,212 B in 0.002 s**
  - binary STL 1,037,484 B in 0.009 s

  The faceted STEP of the sphere alone was 22.0 MB / 8.8 s, so 3MF is about 80× smaller and over 100× faster.
- Onshape: 3MF and glTF 2.0 are supported for both **parts and assemblies**. STL and OBJ are parts only, "view and reference meshes only, unable to edit a mesh". Parasolid is the preferred format. — [Onshape Supported File Formats](https://cad.onshape.com/help/Content/File/supported_file_formats.htm)
- SolidWorks: 3MF can be imported as a graphics body, solid body or surface body (Mesh Files, VRML, 3MF import options). As a graphics body it keeps colour, texture and transparency; as a Mesh BREP only transparency. — [SolidWorks Help 2025: Mesh Files, VRML, and 3MF Import Options](https://help.solidworks.com/2025/English/SolidWorks/Sldworks/HIDD_OPTIONS_IMPORT_VRML.htm). On mesh BREP bodies you can measure distances between mesh elements with the Measure tool and get mass properties. — [SolidWorks Help: Workflows for Mesh BREP Bodies](https://help.solidworks.com/2024/english/SolidWorks/sldworks/c_mesh_workflows.htm). A unit warning: an edge of 1 m in the original document can come in as 1 mm if units are switched. — same source group (search summary)
- Fusion: the supported-formats table lists 3MF for all license types. STEP is supported for all licenses except Personal Use, per the Fusion Import page. — [Autodesk Fusion Supported file formats](https://help.autodesk.com/cloudhelp/ENU/Fusion-Designs/files/TPD-SUPPORTED-FILE-FORMATS.htm). Mesh workflow: STL, OBJ and 3MF are inserted as mesh bodies, with inspection and repair in the Mesh tab. — [Packt: 3D Printing with Fusion 360, ch.1](https://www.packtpub.com/product/3d-printing-with-fusion-360/9781803246642). A 2025 forum thread reports that File > Open of a local .3mf fails while Upload / Insert Mesh works, and that a mesh import bug appears with the UI in German. — [Autodesk forum](https://forums.autodesk.com/t5/fusion-support-forum/unable-to-open-3mf-files-what-is-fusion-team/m-p/13723241/highlight/true)
- No source lists glTF/GLB as a Fusion import format. — (search result: not found on the Autodesk page)
- Bambu Studio: importing STEP automatically creates an Assembly View that keeps each part's relative position. The view has a **Measure** tool for checking clearance between parts. Assembly View exists only when the source is an assembled model such as STEP. — [Bambu wiki: Assembly view guide](https://wiki.bambulab.com/en/software/bambu-studio/assembly-view-guide); [Project-based workflow](https://wiki.bambulab.com/software/bambu-studio/project-based-workflow). Since version 2.8 the STEP importer names objects after the part name inside the STEP (2.7 used the filename). — [Bambu forum](https://forum.bambulab.com/t/please-import-object-names-in-step-file/165349)
- Python writers: build123d's mesher uses lib3mf (from the 3MF Consortium) to create a model with multiple mesh objects. — [build123d mesher source](https://build123d.readthedocs.io/en/stable/_modules/mesher.html). trimesh 5.2.2 exports a Scene to 3MF directly ([local benchmark]: the file was created). An old trimesh README did not list 3MF export, so check your version. — [trimesh README](https://raw.githubusercontent.com/mikedh/trimesh/6c158cce226500fc64b12acd265af0cf01d1c212/README.md)

### Inferences
- If the maker's main tools are Bambu Studio and Onshape/Fusion, a **3MF assembly with one named object per part, mm units, and build-item transforms** meets the "open and see the assembly" need in under 1 s and at a few MB. Measurement is mesh-based: you can measure between faces and vertices, but you cannot pick the axis of a hole.
- Exception: Bambu Studio's Assembly View plus Measure is documented only for STEP sources, not 3MF. That needs testing.
- GLB is the smallest and fastest to write, but its CAD support is weaker (Onshape only). It suits viewing in Blender or the web more than measuring.

### Gaps
- Whether trimesh's 3MF exporter keeps the node name as the object name, and whether it keeps per-part transforms or bakes them in: not verified. TODO: unzip `3D/3dmodel.model` to check.
- FreeCAD 1.x importing 3MF as multiple named meshes, and Blender 4.x 3MF support (built-in or add-on): no source fetched this round. Blender imports glTF built in (general knowledge, not cited).
- Whether you can measure on a graphics body (SolidWorks) or on a mesh body in Fusion: no explicit documentation found.

## 4. Converting meshes back to analytic surfaces for small files

### Takeaway
No fast, reliable, free automatic route exists. FreeCAD/OCCT Refine merges coplanar faces only (good for box-like parts). Real reverse engineering to planes and cylinders needs surface fitting, which tends to need a person. The right place to save size is upstream: keep the original B-rep from the parametric generator.

### Cited findings
- Sewing per-triangle faces is very slow (13 h for a 4 MB STL). Fitting B-spline surfaces with SSP/GeomPlate is complex and often needs user interaction. — [OCCT forum](https://occt3d.com/dev/content/conversion-stl-step-slow/index.html)
- Refine shape cleans residual edges on planar and cylindrical surfaces. — [FreeCAD wiki](https://wiki.freecad.org/FreeCAD_and_Mesh_Import). [local benchmark] On a faceted cylinder it merged only the coplanar faces (256 → 66 faces) and did not recreate the cylinder. On a 20k-triangle sphere it added 21.9 s with zero effect.
- UnifySameDomain sometimes produces invalid faces. — [OCCT forum](https://dev.opencascade.org/content/shapeupgradeunifysamedomain-possible-problem)
- Inventor: a mesh converts to a surface, and to a solid only if it closes. A billion-triangle mesh stays billions of small faces. — [Autodesk Inventor forum](https://forums.autodesk.com/t5/inventor-forum/how-can-i-export-a-large-stl-file-as-a-step-file/m-p/11893913)

### Inferences
- Merging coplanar triangles before building the B-rep (polygon faces, one face per coplanar region) would cut both build and refine time. That needs testing; no source found.

### Gaps
- No speed or reliability data was found for automatic primitive-fitting tools (cylinder or hole detection on meshes).

## 5. Recommended patterns

### Takeaway
No single mesh-based format is both "open in any CAD" and "measure like a solid". The best compromise is to keep STEP only where it is essential and make it smaller, and to add a fast 3MF for slicing and viewing.

### Cited findings
- Onshape: 3MF and glTF work for assemblies, but meshes are view/reference only. — [Onshape](https://cad.onshape.com/help/Content/File/supported_file_formats.htm)
- Bambu Studio has Assembly View + Measure only for STEP sources. — [Bambu wiki](https://wiki.bambulab.com/en/software/bambu-studio/assembly-view-guide)
- SolidWorks reads faceted STEP as a graphics body by default. — [SolidWorks Help](https://help.solidworks.com/2024/English/SolidWorks/Sldworks/t_reading_step_iges_acis_sw.htm)

### Inferences (proposal, ordered by impact)
1. **Best**: if the generator (SolidCraft/build123d) has analytic B-rep, export STEP straight from B-rep, with no STL in between. The file is small (faces = real faces) and fast. TODO: check SolidCraft's capability.
2. If you must start from STL: **decimate / mesh more coarsely** before building the faceted B-rep. Size and time scale linearly with triangle count (~1 KB/triangle). Apply refine only to box-like parts. Build the B-rep with shared topology instead of sewing.
3. **Add** (not replace) a 3MF assembly (named objects, mm, transforms): ~0.1 s and a few MB. It suits Bambu Studio, Onshape and Fusion when you only need to see positions and do rough measurements.
4. Tessellated STEP AP242 is worth benchmarking for size (OCCT 7.7+, `write.step.tessellated=1`, schema AP242DIS). Do not adopt it as the only format until Fusion, Onshape and SolidWorks are confirmed to open it and allow measuring.

### Gaps
- No real trial of opening each format in Fusion, SolidWorks or Onshape to check whether measuring works. Needs manual testing on the machine.
