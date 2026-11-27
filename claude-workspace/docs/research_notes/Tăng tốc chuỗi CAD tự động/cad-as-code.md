# CAD-as-code pipelines vs scripted Blender mesh booleans for 3D-printed enclosures

Context: the baseline is a Blender bpy mesh-boolean script of about 1400 lines (superellipsoid shells, many booleans, build about 12 s) at a maker studio running Windows 11. Research date: 2026-11-27. Numbers below come only from the cited sources. Anything without a source is marked unknown or listed under Gaps.

## 1. OpenSCAD with the Manifold backend: speedups, status, limitations

### Takeaway
On boolean-heavy models Manifold is one to two orders of magnitude faster than CGAL. It has been the default in OpenSCAD development snapshots since August 2025, and I found no stable release (newer than 2021.01) that makes it the default. Output is mesh only (no STEP), and some operations (minkowski) still fall back to CGAL.

### Cited Findings
- On 2025-08-17 Marius Kintel announced that Manifold had become the default backend in development snapshots. CGAL is still available with `openscad --backend=cgal`. — [OpenSCAD mailing list](https://lists.openscad.org/empathy/thread/TMJEJCZINIJNYJX2YF7IDNBAPQY66KIF) (via search summary)
- Manifold stopped being "experimental" in September 2024 and could be selected in Preferences or with `--backend=manifold`. In a June 2025 thread CGAL was still the default. — [OpenSCAD mailing list](https://lists.openscad.org/empathy/thread/WC6UVRBYPBFHCXY5Z4BFBUOXWMTDSYAN) (via search summary)
- Some features still need CGAL: minkowski uses CGAL Nef minkowski as a fallback when convex decomposition fails, even with Manifold enabled. — [openscad/openscad#4825](https://github.com/openscad/openscad/issues/4825), [mailing list](https://lists.openscad.org/empathy/thread/WC6UVRBYPBFHCXY5Z4BFBUOXWMTDSYAN?page=2) (via search summary)
- Stable release status: I did not find an official 2026 stable release. A January 2026 thread pointed to the 2026.01.19 snapshot as the most stable build. A third-party mirror lists a "2026.02.10 stable snapshot", which I could not confirm on openscad.org. — [mailing list Jan 2026](https://lists.openscad.org/empathy/thread/FAP73KWTGJQ37CU4MWJ4YDF35FCLWP2E), [OlderGeeks mirror](https://www.oldergeeks.com/downloads/file.php?id=2116)
- Speedup figures quoted in the Manifold maintainers' discussion:
  - OpenSCAD with Manifold vs CGAL fast-csg: 5–30x faster.
  - fast-csg vs CGAL Nef: 30–150x faster.
  - An earlier 2022 analysis gave Manifold as "100–1,000 times faster" than OpenSCAD/CGAL.
  - Source: [elalish/manifold Discussion #383](https://github.com/elalish/manifold/discussions/383)
- One model fell from about 1 min to about 400 ms with Manifold plus rewrite-tree plus lazy-union, against about 2 s with fast-csg. — [ochafik gist (TL;DR fast-csg)](https://gist.github.com/ochafik/6e95596a6e6188b2062ee056b55ce47d) (via search summary)
- ochafik micro-benchmarks, baseline CGAL vs fast-csg (the predecessor of the Manifold path; the author says they "need updating" and that fast-csg "is now being obsoleted by Manifold"):

  | Model | CGAL baseline | fast-csg | Speedup |
  |---|---|---|---|
  | cube-with-half-spheres-dents | 3 min 32 s | 1.2 s | 178x |
  | spheres-grid | 188 s | 1.1 s | 170x |
  | Bricks benchmark | 61 s | 0.6 s | 108x |
  | chainmail | 24 min 15 s | 4 min 27 s | 5x |
  | maze | more than 10 hours | 5 min 15 s | not calculated |

  Source: [ochafik benchmarks gist](https://gist.github.com/ochafik/2db96400e3c1f73558fcede990b8a355)
- Python Manifold vs OpenSCAD/CGAL on a "rounded slices" model: 0.228 s vs 18.75 s (January 2024, hardware not stated). — [Discussion #383](https://github.com/elalish/manifold/discussions/383)
- Robustness: one user reported a complicated model where CGAL failed with an assertion violation but Manifold completed, taking about 12 min 25 s. — [OpenSCAD mailing list](https://lists.openscad.org/empathy/thread/PTTJIQYC3ZS6HNZMUQE5CINEJ55JQLXL) (via search summary; I could not confirm which thread from the snippet)
- PythonSCAD, an OpenSCAD fork with Python scripting, released v1.1.2 in July 2026 with a "July 2026 OpenSCAD sync". — [PythonSCAD group](https://groups.google.com/g/pythonscad/c/2m45BzEY4-E)

### Inferences
- OpenSCAD's geometry kernel is mesh CSG (CGAL or Manifold), so it cannot produce true B-rep STEP. Its outputs are meshes (STL, 3MF and so on). I did not fetch an official export-format list in this session (see Gaps).
- Superellipsoid shells would have to be generated as `polyhedron()` point lists in the OpenSCAD language. That is awkward compared with Python. PythonSCAD or manifold3d used directly from Python are more natural ways to port a bpy script.

### Gaps
- No official 2026 OpenSCAD stable-release notes found. Whether a stable release with Manifold as default exists is unknown.
- No source states OpenSCAD's export format list or 3MF color support (not fetched).
- No benchmark on enclosure-like models (shell plus about 50 cutouts).

## 2. build123d and CadQuery (OpenCASCADE B-rep): build times, slow operations, caching, live preview, assemblies, STEP

### Takeaway
I found no published per-part build-time benchmarks for build123d or CadQuery. The documented slow spots are booleans accumulated one at a time in loops (about 12x slower than one batched fuse in a reported case) and 3D fillets on complex fused bodies. STEP export is native B-rep, and shallow copies keep assembly files small (550 KB vs 51,938 KB for 100 screws). Live preview comes from OCP CAD Viewer (VS Code, v4.x). I found no documented memoizing cache.

### Cited Findings
- **Batch vs sequential fuse.** A build123d user on r/cadquery timed fusing solids one at a time at about 28.5 s, against about 2.3 s for a single fuse of all solids together (about 12x). — [r/cadquery Oct 2024 (redlib mirror)](https://redlib.hbubli.cc/r/cadquery/comments/1g8bobg/boolean_operation_with_many_solids_cadquery)
- **Loops in algebra mode.** The build123d docs warn that creating many Shapes in a loop calls fuse and clean on every step. — [build123d algebra performance docs](https://build123d.readthedocs.io/en/v0.11.1/_sources/algebra_performance.rst.txt) (via search summary; the latest URL returned 404)
- **Fillets in raw OCC.** One OpenCascade user reported that filleting after a fuse was "the most time-consuming process taking ~45 minutes". This was a raw OCC case, not build123d. — [OCC forum](https://dev.opencascade.org/content/more-efficient-way-use-brepfilletapimakefillet)
- **Official build123d tips:**
  - Build profiles in 2D, then extrude or revolve: 3D operations are slower and more failure-prone.
  - Do chamfers and fillets late; 2D fillets fail less often than 3D ones.
  - Try `loft()` when a multi-section `sweep()` fails.
  - Self-touching geometry can be invalid even when `is_valid()` returns True.
  - The page gives no timings and does not mention caching.
  - Source: [build123d Tips](https://build123d.readthedocs.io/en/stable/tips.html)
- **Shallow copy and STEP size.** For 100 M6 screws, `copy.copy` instances took about 0.25 s and gave a 550 KB STEP file. `deepcopy` took about 5 s and gave 51,938 KB. Assemblies export with `export_step(Compound(children=...))`. — [build123d assemblies docs](https://build123d.readthedocs.io/en/v0.11.1/_sources/assemblies.rst.txt)
- **Freeform surfaces.** build123d's own docs say mesh-based systems handle freeform surfaces better. The examples include a Gordon surface for doubly curved shapes with no obvious analytic form. — [build123d docs](https://build123d.readthedocs.io/en/latest/) (via search summary), [build123d examples](https://build123d.readthedocs.io/en/latest/examples_1.html)
- **build123d vs CadQuery.** build123d is derived from parts of CadQuery but is heavily refactored into an independent framework on OpenCascade. — [build123d GitHub](https://github.com/gumyr/build123d) (via search summary)
- **Live preview: OCP CAD Viewer for VS Code** (supports both build123d and CadQuery):
  - `show()` sends objects to the viewer.
  - v4.0.0 added a built-in mesh measurement backend: area, length, volume, bounding box, min/center distance (BVH-accelerated) and angle.
  - The install docs reference v4.3.0.
  - Source: [vscode-ocp-cad-viewer](https://github.com/bernhard-42/vscode-ocp-cad-viewer)
  - I could not confirm auto-reload on save from that page.
- **CadQuery Web Viewer** refreshes a browser view when you re-run Python, and has an optional memory or disk cache for GLBs. — [cadquery-web-viewer PyPI](https://pypi.org/project/cadquery-web-viewer/1.0.1/)
- **Caching.** Searches found nothing on "cq-cache". I found no documented memoization layer for build123d or CadQuery.
- **CadQuery assemblies** support constraints plus `solve()` for placement. `solve()` needs at least one constraint and two entities. — [CadQuery assembly docs](https://cadquery.readthedocs.io/en/latest/assy.html) (via search summary)

### Inferences
- For a medium enclosure, OCC's cost is dominated by booleans on curved faces and by fillets. The practical pattern is 2D-first, batched fuse/cut (one `cut` with a compound of all cutters), and fillets last.
- No built-in incremental rebuild exists. Caching would have to be hand-written, for example by pickling or BREP-serializing sub-parts keyed by a parameter hash. That is an inference: no source documents such a tool.
- STEP from build123d/CadQuery is true B-rep, which matches the studio's need to measure CAD files. Shallow copies matter for repeated hardware.

### Gaps
- No sourced build-time numbers for a typical enclosure-sized part in build123d or CadQuery.
- No sourced STEP export speed for single parts.
- No information on cq-cache (it may not exist under that name).

## 3. Hybrid approaches: manifold3d directly, or B-rep plus mesh

### Takeaway
manifold3d (Python bindings, on PyPI) does booleans in tenths of a second on million-triangle meshes, and its output is guaranteed manifold. In a 2026 third-party benchmark it ran about 50x faster than Blender-via-trimesh booleans. Swapping the bpy boolean step for manifold3d, while keeping the superellipsoid generation code, is the lowest-cost speedup. B-rep (build123d) suits mechanical sub-parts that must ship as STEP.

### Cited Findings
- **MeshLib benchmark** (vendor; tested 2026-06-27; Apple M5, minimum of 10 runs, I/O excluded). Times are union / intersection / difference in seconds:

  | Case | Manifold | Trimesh-Manifold | Trimesh-Blender | CGAL |
  |---|---|---|---|---|
  | Nefertiti, 2M triangles | 0.27 / 0.19 / 0.21 | about 1.0 | 14 / 13 / 14 | 4.4 / 3.6 / 3.8 |
  | Dental, 280K–500K triangles | 0.05 / 0.04 / 0.05 | 0.15 | about 4 | fail or hang |

  MeshLib's own product was faster still (0.09 s on Nefertiti). Treat vendor numbers with caution. — [MeshLib: Comparing 3D boolean libraries](https://meshlib.io/blog/comparing-3d-boolean-libraries/)
- **Python timings** (January 2024, hardware unknown): 1,000 3D unions took 10.47 s, and a 1,000-shape batch union took 9.87 s. 1,000 rounded boxes made as hulls of 8 spheres took 3.39 s. — [Discussion #383](https://github.com/elalish/manifold/discussions/383)
- **Binding overhead.** The PyPI page says the Python binding is "not quite as fast as our raw C++" but good for interoperability. — [manifold3d PyPI](https://pypi.org/project/manifold3d/) (via search summary)
- **Performance rules** from the Manifold wiki:
  - CSG is lazy. Calls return instantly and work happens on `GetMesh` or `NumVerts`, so benchmarks must include evaluation.
  - Reuse cached results and transform them, because transforms are much cheaper than CSG.
  - Consecutive unions flatten to n-ary unions.
  - Process smaller meshes first.
  - Use `Compose` for bodies whose bounding boxes do not overlap.
  - Parallelism is optional (the `MANIFOLD_PAR` build flag, with TBB).
  - Sources: [Manifold wiki Performance Considerations](https://github.com/elalish/manifold/wiki/Performance-Considerations), [manifold3d PyPI](https://pypi.org/project/manifold3d/) (via search summary)
- **Blender's own Manifold solver.** The Blender manual describes a solver "usually fastest but only works on Manifold meshes" and the Exact solver as "much slower". The 4.5 German page labels the fast solver "Float". — [Blender 4.5 manual](https://docs.blender.org/manual/en/4.5/modeling/modifiers/generate/booleans.html), [Blender manual (latest)](https://www.blender.org/manual/en/modeling/modifiers/generate/booleans.html) (via search summary; direct fetch returned 403)
- **One practitioner's split:** build123d for precise parametric parts and families of variants, Blender for anything organic. — [blog "why I chose build123d", 2026-03-25](https://nj22az.github.io/theofficeofnilsjohansson/projects/blog/2026/03/25/why-i-chose-build123d.html) (via search summary; the page returned 404 on fetch)

### Inferences
- Lowest migration cost: keep the bpy shell generators, or port the superellipsoid math to numpy (straightforward), and do all booleans in manifold3d with batched cutters.
  - Expected time: well under 1 s for meshes up to about 1M triangles, based on the 0.05–0.27 s figures above.
  - Alternative: first try switching the existing bpy Boolean modifiers to the Manifold solver (no rewrite needed), if the installed Blender version has it.
  - Both of these are inferences from the cited numbers, not measured on this script.
- Mesh pipelines still give no STEP. If the studio needs measurable STEP (it currently uses SolidCraft `.sc`), the realistic hybrid is:
  - superellipsoid shells as meshes, or as B-rep lofts/Gordon surfaces (risky);
  - mechanical features (bosses, screw holes, snap fits) as build123d B-rep exported to STEP.

### Gaps
- No independent benchmark of manifold3d against Blender's built-in Manifold or Float solver on the same model.
- I could not confirm which Blender version first shipped the solver named "Manifold".

## 4. Community experience and pain points (OCC robustness on Windows, freeform in B-rep)

### Takeaway
Windows installation of the OCC stack is now pip wheels (cadquery-ocp 7.9.3.1 for cp312, win_amd64). The main reported pain points are 3D fillet failures and slow fused-body fillets, plus the documented weakness of B-rep with freeform surfaces. I found no Reddit or Discourse threads specifically on superellipsoids in B-rep.

### Cited Findings
- **Windows wheels.** cadquery-ocp 7.9.3.1 has a CPython 3.12 Windows x86-64 wheel of about 46.5 MB, and there is also a `cadquery-ocp-novtk` variant. 7.7.2.1 was yanked because of a broken VTK dependency. CadQuery docs list Python 3.9–3.12 support. — [cadquery-ocp PyPI](https://pypi.org/project/cadquery-ocp), [cadquery-ocp-novtk](https://pypi.org/project/cadquery-ocp-novtk/), [cadquery PyPI](https://pypi.org/project/cadquery)
- **Freeform.** build123d's docs concede that mesh systems handle freeform better. Its tips page says 3D fillets and chamfers fail more often than 2D ones and that "patience and alternative approaches" may be needed. — [build123d docs](https://build123d.readthedocs.io/en/latest/) (via search summary), [Tips](https://build123d.readthedocs.io/en/stable/tips.html)
- **Fused-body fillet timing.** The roughly 45-minute fillet after a fuse was in raw OCC. — [OCC forum](https://dev.opencascade.org/content/more-efficient-way-use-brepfilletapimakefillet)

### Inferences
- A superellipsoid is not an OCC primitive. In B-rep it would need approximation as a BSpline surface (loft of superellipse sections, or a Gordon surface). After that, offsets for wall thickness and fillets on those faces are the operations most likely to fail or be slow. This is an inference consistent with the docs' freeform caveat; I found no direct report.

### Gaps
- No sourced Windows-specific OCC crash or robustness reports found in this session.
- No first-hand reports from makers building organic printable enclosures in build123d or CadQuery.

## 5. Assembly interference checking in these ecosystems vs BVH mesh overlap

### Takeaway
build123d has a built-in `Compound.do_children_intersect()`. It runs a bounding-box prefilter, then an exact B-rep `intersect`, and sums the common volume against a tolerance. CadQuery has no official interference API; the community pattern is `BRepAlgoAPI_Common` plus a volume calculation, reported as slow on complex parts. Mesh-side, Manifold intersection on large meshes takes about 0.04–0.19 s (section 3), and OCP CAD Viewer measures distances with a BVH.

### Cited Findings
- **build123d `Compound.do_children_intersect`:**
  - Signature: `do_children_intersect(include_parent: bool = False, tolerance: float = 1e-5) -> tuple[bool, tuple[Shape|None, Shape|None], float]`.
  - Method: it places each part globally, pre-filters pairs by bounding-box overlap, then calls `intersect` and sums the common volume.
  - It returns the first pair whose common volume is greater than the tolerance.
  - The docstring calls the tolerance a "maximum allowable volume difference", but the code uses it as a minimum common volume.
  - Source: [build123d source, topology/composite.py (dev)](https://raw.githubusercontent.com/gumyr/build123d/dev/src/build123d/topology/composite.py)
- **build123d joints.** Assemblies are trees built from `Compound` parent/children. The Joint tutorial includes a step titled "Check that the components in the assembly don't intersect" (code is in an external file). — [build123d assemblies docs](https://build123d.readthedocs.io/en/v0.11.1/_sources/assemblies.rst.txt)
- **CadQuery.** No official interference recipe found. A community script computes the `BRepAlgoAPI_Common` volume via `GProp_GProps` against a threshold. Its comments say the call "takes too long", and it contains bugs. — [volume_collision.py](https://diyhpl.us/cgit/skdb/tree/geom/volume_collision.py)
- **Third-party wrapper.** The "cad-khana" skill wraps build123d with `assert_no_interference("pin", "bracket")` style checks. — [cad-khana SKILL.md](https://skillsmp.com/skills/cyberchitta-cad-khana-skills-cad-khana-skill-md)
- **OCP CAD Viewer** v4 computes min/center distance with a BVH for large models, which is useful for clearance checks during interactive review. — [vscode-ocp-cad-viewer](https://github.com/bernhard-42/vscode-ocp-cad-viewer)

### Inferences
- `do_children_intersect` stops at the first colliding pair, so a gate that wants every pair needs its own loop. It checks for overlapping volume only. A clearance check (for example, gap of at least 0.2 mm) needs an extra step:
  - offset or scale one part by the clearance, then intersect again; or
  - use a distance query (OCC `BRepExtrema_DistShapeShape` exists, but this session did not source its speed).
- A mesh gate (BVH broadphase plus Manifold intersection volume) is probably faster for many pairs than OCC common-volume checks. That is an inference: no head-to-head source was found.

### Gaps
- No timing for `do_children_intersect` or `BRepAlgoAPI_Common` on enclosure-sized parts.
- No documented build123d joint-based motion or collision sweep.
