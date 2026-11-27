# Speeding up a scripted Blender (bpy) CAD build pipeline

Scope: headless `blender -b --factory-startup -P build.py`, about 15 parts, many Boolean modifiers (MANIFOLD / EXACT), about 12 s per full build, Windows PC with limited RAM.

Source note: docs.blender.org, developer.blender.org, projects.blender.org and devtalk.blender.org all returned HTTP 403 to the fetch tool. Statements from those sites are therefore taken from search-engine snippets of the official pages, not from a full read. To fill the gap in measured numbers, I ran **local micro-benchmarks on this PC** (Blender 5.2, `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe`; manifold3d 3.5.5 on CPython 3.13.9). The scripts are kept in the session scratchpad (`bench_bool.py`, `bench_m3d.py`) and are labelled "Local benchmark" below. They are single runs on one synthetic case: a 40 mm cube minus 36 through-cylinders of r = 2 mm. Treat them as indicative, not as general truth.

## 1. Blender Boolean solvers (Manifold vs Exact vs Float), batching cutters, and per-op evaluation cost

### Takeaway
On manifold inputs, use the MANIFOLD solver with **one Boolean modifier that has a COLLECTION operand holding all cutters**, and evaluate once. Locally this was 25–60x faster than EXACT. It was also about 10x faster than stacking one MANIFOLD modifier per cutter. Evaluating the depsgraph (or `new_from_object`) after every operation is the single biggest avoidable cost.

### Cited Findings
- Blender 4.5 LTS introduced the Manifold solver. It is based on the open-source Manifold library (also used in Nomad Sculpt) and is described as "as fast as, and sometimes faster" than the Float solver. It is available both in the Boolean modifier and in the Mesh Boolean geometry node. The old "Fast" solver was renamed "Float". — [CG Channel, Blender 4.5 LTS](https://www.cgchannel.com/2025/07/blender-4-5-lts-is-out-check-out-its-5-key-features); [All3DP](https://all3dp.com/4/new-blender-4-5-offers-powerful-mesh-curve-point%e2%80%91cloud-enhancements-for-3d-modelers/)
- Blender manual (via search snippets, since the page fetch returned 403): Float/Fast "offers good performance but lacks support for overlapping geometry". Exact "has full support for overlapping geometry, but is much slower". Manifold "is usually fastest but only works on Manifold meshes" and "will not work at all on non-manifold meshes". — [Blender Manual 5.0, Boolean Modifier](https://docs.blender.org/manual/en/5.0/modeling/modifiers/generate/booleans.html)
- The Exact solver handles self-intersection "at the cost of performance". With the Fast/Float solver, Intersect is not allowed for collection operands. — [Blender Manual, Boolean Modifier](https://www.blender.org/manual/en/modeling/modifiers/generate/booleans.html)
- Collection operand semantics differ by solver. With Fast/Float, Blender "will just apply the Boolean as many times as there are Mesh Objects in the Collection". With Exact, "the whole Boolean is done in one operation". — [developer.blender.org T82277](https://developer.blender.org/T82277) (search snippet, Blender 2.91-era statement)
- The Boolean modifier converts Mesh to BMesh, runs the Boolean, then converts back. That conversion cost is paid on every evaluation. — [bf-committers mailing list, Nov 2020](https://lists.blender.org/pipermail/bf-committers/2020-November/050737.html) (search snippet)
- Developer Howard Trickey's feature request describes Manifold as a float solver that uses symbolic perturbation to guarantee manifold output from manifold input. He expected it to be more robust than Float and "probably faster" (an expectation, not a measurement). In the same work he says the current Exact solver is too slow except on small meshes. — [projects.blender.org #120182](https://projects.blender.org/blender/blender/issues/120182); [Exact Boolean V2 #114476](https://projects.blender.org/blender/blender/issues/114476) (search snippets)
- A known issue: Boolean modifiers are re-evaluated even when nothing moves. — [developer.blender.org T86236 / related](https://developer.blender.org/T86236) (search snippet)
- **Local benchmark, Blender 5.2.** Case: 40 mm cube minus 36 cylinders. Modes: `seq_once` = 36 stacked modifiers, evaluated once; `seq_eval_each` = `view_layer.update()` + `new_from_object` after each added modifier, which re-evaluates the growing stack; `collection` = one modifier with a COLLECTION operand.

  | segments | solver | seq_once | seq_eval_each | collection |
  |---|---|---|---|---|
  | 32 | FLOAT | 0.122 s | 1.87 s | 0.122 s |
  | 32 | EXACT | 1.02 s | 17.6 s | 0.408 s |
  | 32 | MANIFOLD | 0.208 s | 2.84 s | **0.018 s** |
  | 64 | FLOAT | 0.316 s | 4.85 s | 0.325 s |
  | 64 | EXACT | 2.05 s | 31.8 s | 0.766 s |
  | 64 | MANIFOLD | 0.327 s | 4.35 s | **0.032 s** |
  | 128 | FLOAT | 0.871 s | 13.9 s | 0.897 s |
  | 128 | EXACT | 3.96 s | 64.1 s | 1.60 s |
  | 128 | MANIFOLD | 0.548 s | 7.90 s | **0.064 s** |

  Face counts were consistent across solvers (about 1.2k / 2.35k / 4.65k), so every run produced a comparable result. In this test, FLOAT gained nothing from a collection, which matches the "applied once per object" behaviour above. EXACT gained about 2.5x and MANIFOLD about 9–12x. — Local benchmark (`bench_bool.py`)

### Inferences
- On a 12 s build, the likely biggest wins, in order: (1) remove intermediate evaluation (`view_layer.update`, `evaluated_depsgraph_get`, `new_from_object`, `modifier_apply`) between operations, and evaluate each part once at the end; (2) group all cutters for one target into a collection and use a single MANIFOLD DIFFERENCE; (3) keep EXACT only for the few operations that truly need non-manifold or self-intersecting input.
- MANIFOLD requires every operand to be closed and manifold. bmesh primitives (`create_cube`, `create_cone` with `cap_ends=True`, `create_uvsphere`) qualify. Open or coplanar-merged hand-built meshes may not. A practical fallback is to try MANIFOLD and, if the result is empty or an error is reported, retry that operation with EXACT. (Not verified how Blender 5.x reports a Manifold failure from Python; TODO.)
- With a collection operand, the cutters stay as objects. Remove or hide them before export (or keep them in an excluded collection).

### Gaps
- No official Blender benchmark comparing Manifold vs Exact vs Float was found (the official pages were unreadable through 403s). Only the local numbers above exist.
- The isolated per-call cost of `view_layer.update()` vs `evaluated_depsgraph_get()` vs `new_from_object()` was not measured separately. The `seq_eval_each` column includes re-evaluation of the growing modifier stack (an O(N²) effect).
- Whether a pure bmesh path (`bmesh.ops` has no robust Boolean; Booleans live in the modifier / geometry nodes) can avoid the Mesh↔BMesh conversion: no source found.

## 2. Using manifold3d (pip) directly instead of Blender Booleans

### Takeaway
manifold3d gives the same Boolean kernel without Blender's object, modifier and depsgraph overhead. It offers n-ary `batch_boolean`, lazy evaluation, and a numpy mesh interface. Locally it was roughly as fast as Blender's MANIFOLD collection Boolean, and much faster than any stacked approach. It can run in plain Python without Blender at all.

### Cited Findings
- Package: `manifold3d` on PyPI, version 3.5.5 released 2026-11-13. Wheels exist for CPython 3.9–3.15 on Windows x86-64, including free-threaded 3.14t/3.15t builds. Apache-2.0 license. Stated "primary goal is reliability: guaranteed manifold output without caveats or edge cases", with performance as a secondary goal. — [PyPI manifold3d](https://pypi.org/project/manifold3d/)
- A non-manifold input mesh produces an error status. `Merge` can fix slightly non-manifold meshes. TBB parallelism applies when built with `MANIFOLD_PAR=ON`; small problems fall back to serial. Triangulation is serial. — [GitHub elalish/manifold](https://github.com/elalish/manifold)
- Python API, as used in the official example: `Manifold.cube/cylinder/sphere/extrude/revolve`, `Manifold(mesh)`, static `Manifold.batch_boolean(list, OpType.Add)`, `batch_hull`, methods `translate/rotate/scale/transform/mirror/split_by_plane/trim_by_plane/decompose/to_mesh/status/volume`, plus `Mesh.merge` and the `vert_properties` attribute. — [manifold bindings/python/examples/all_apis.py](https://raw.githubusercontent.com/elalish/manifold/master/bindings/python/examples/all_apis.py)
- Mesh layout: `vertProperties` is a flat interleaved array whose first 3 properties are x, y, z, and `triVerts` holds 3 indices per triangle in CCW order. — [manifoldcad.org Mesh docs (JS, same layout)](https://manifoldcad.org/jsdocs/classes/manifold.Mesh.html)
- Locally verified Python signature: `manifold3d.Mesh(vert_properties: float32[N,k] C-order, tri_verts: uint32[M,3] C-order, ...)`. The arrays returned by `to_mesh()` are **read-only views**. Passing them back in fails with "incompatible function arguments". Use `np.array(..., copy=True, order="C")`. — Local benchmark (`bench_m3d.py`)
- Performance guidance from the maintainers: operations are lazy, and the cost appears when results are forced (`to_mesh`, `num_vert`, and so on). Flatten chains of unions into one n-ary op. Combine smaller meshes first. Use transforms (much cheaper than CSG) to reuse cached shapes. Compose is a fast union for non-intersecting parts. Shared sub-results are evaluated once. — [Manifold wiki: Performance Considerations](https://github.com/elalish/manifold/wiki/Performance-Considerations)
- Third-party (vendor) benchmark on a 2M-triangle mesh: Manifold union about 0.27 s, intersection 0.19 s, difference 0.21 s. MeshLib claims it is about 3x faster than Manifold and about 150x faster than Blender via trimesh. These are vendor-run numbers. — [MeshLib comparison](https://meshlib.io/blog/comparing-3d-boolean-libraries/)
- Maintainers note that performance varies widely by benchmark and hardware. — [manifold discussion #383](https://github.com/elalish/manifold/discussions/383)
- **Local benchmark (manifold3d 3.5.5, CPython 3.13.9, same cube minus 36 cylinders).** `import manifold3d` took 0.15 s warm (0.95 s cold, first import). `batch_boolean` + difference + `to_mesh`: 0.018 s at 32 segments, 0.032 s at 64, 0.071 s at 128. Sequential difference with evaluation forced after each step: 0.093 / 0.146 / 0.281 s. Rebuilding a Manifold from numpy arrays (about 18.6k triangles): 0.009 s. Status was `NoError` in all runs. — Local benchmark (`bench_m3d.py`)

### Inferences
- Compared with Blender MANIFOLD collection (0.018 / 0.032 / 0.064 s), manifold3d batch was about the same speed. The gain from manifold3d is not the Boolean kernel itself. It comes from skipping object creation, modifiers, depsgraph and Blender startup (about 1.7 s, see section 4), and from being able to run in a normal Python process or worker pool.
- Hybrid option: keep Blender for anything it uniquely provides (bevel modifier, .blend output, rendering), but generate solid geometry in manifold3d and push it into Blender via `mesh.from_pydata` or `foreach_set` from numpy. Installing manifold3d into Blender's bundled Python requires a wheel matching Blender 5.2's Python version (not checked; TODO). A `pip --target` folder added to `sys.path` avoids touching the Blender install.
- manifold3d works in float32 vertex positions on the Mesh interface (there is also `to_mesh64`). For mm-scale printable parts, precision is not a practical concern (inference, not tested on tight clearances).

### Gaps
- No independent Blender-vs-manifold3d benchmark on real CAD parts was found.
- Behaviour of the Windows PyPI wheel with TBB (parallel or serial) is not stated on PyPI. Unknown.

## 3. Incremental / cached builds

### Takeaway
None of Blender, CadQuery or build123d offers built-in parameter-hash caching. Code-CAD communities build it themselves: hash the inputs of each part, and store the outputs (STL/STEP/mesh arrays) on disk keyed by that hash.

### Cited Findings
- The OpenFlexure microscope (an OpenSCAD project) added an intermediate step that compiles to CSG with includes resolved and variables replaced by constants. The plan was to hash those CSG files and reuse cached STLs when hashes match. Timestamps had to be stripped so the hashes stay stable. — [OpenFlexure MR !308](https://gitlab.com/openflexure/openflexure-microscope/-/merge_requests/308)
- A CadQuery-based asset pipeline keeps a "cache" of solids as STEP files on disk, which "greatly accelerates our iterative cycles". — [fx-bricks/fx-cad-notes](https://github.com/fx-bricks/fx-cad-notes) (search snippet)
- Manifold internally caches shared sub-results so each is evaluated only once within a process. — [Manifold wiki: Performance Considerations](https://github.com/elalish/manifold/wiki/Performance-Considerations)

### Inferences
- A suggested pattern for build.py: for each part, compute `key = sha256(json.dumps(params_for_part, sort_keys=True) + source_of_part_function + versions)` and look up `cache/<part>-<key>.npz`. The .npz holds `verts` float32 and `tris` uint32. On a hit, load it (about 0.01 s for about 20k triangles, judging by the numpy→Manifold timing) and skip the Booleans. On a miss, build and save. Include the source code of the shared helpers in the hash, or changes to them will be missed.
- In an edit-check loop, usually only 1–2 of the 15 parts change. With per-part caching, a rebuild becomes startup + 1–2 parts + export, not all 15.
- `np.savez` (uncompressed) is the fastest to read. PLY/STL are interoperable, but parsing them is slower (not measured).

### Gaps
- No published timings for cache hit/miss in a Blender pipeline were found.

## 4. Parallelism, Blender startup time, and memory

### Takeaway
Starting a background Blender costs about 1.7 s and about 190–260 MB of RAM per process on this PC. Running one process per part pays that tax 15 times. Prefer one process with batched Booleans plus caching. If you parallelise, use 2–4 worker processes that each build a group of parts, sized to free RAM.

### Cited Findings
- `--factory-startup` skips reading the user's startup.blend. `-b` runs without UI. `--python-exit-code` sets the exit code on a Python exception. `--log-show-timestamp` can show where startup time goes. — [Blender Manual 4.5, Command Line Arguments](https://docs.blender.org/manual/en/4.5/advanced/command_line/arguments.html) (search snippets)
- **Local measurement.** `blender -b --factory-startup --python-expr "import bpy"` (Blender 5.2): 1.83 s, 1.71 s, 1.72 s over 3 runs. — Local benchmark
- **Local measurement.** An idle Blender 5.2 background process (factory startup) used 187 MB working set and 256 MB private memory. — Local benchmark
- Manifold supports free-threaded Python 3.14t+ with the GIL disabled, which allows thread-level parallelism in plain Python. — [GitHub elalish/manifold](https://github.com/elalish/manifold)
- `bpy` is published on PyPI as "Blender as a Python module". Each release supports exactly one Python version (for example, 5.0.x and 4.5.x ship cp311 wheels). Older versions are removed from PyPI but kept at download.blender.org/pypi/bpy/. Past releases had wheel/Python-version mismatches. — [PyPI bpy](https://pypi.org/project/bpy/); [PyPI bpy 5.0.0](https://pypi.org/project/bpy/5.0.0/); [projects.blender.org #120801](https://projects.blender.org/blender/blender/issues/120801)

### Inferences
- A persistent-process option: `pip install bpy` (into a venv with the exact Python version that matches that bpy release) lets a long-running Python process `import bpy` once, then rebuild on each file change (watchdog loop or socket). Scene state must be reset between builds, for example with `bpy.ops.wm.read_factory_settings(use_empty=True)` (not measured). This removes the about 1.7 s startup from each iteration. Risk: the bpy version may lag the installed Blender 5.2 (PyPI showed 5.0.x as the latest found). TODO: verify that a bpy 5.2 wheel exists.
- An alternative without bpy-from-pip: run `blender -b --factory-startup --python server.py`, where the server listens on localhost and re-executes build.py via `runpy` on request. Same benefit, same state-reset caveat.
- Python `multiprocessing` inside Blender spawns fresh interpreters on Windows (spawn start method), and each child does not have bpy loaded in the usual way. Separate `blender -b` subprocesses are the practical form of parallelism (inference, not verified in a source).
- On limited RAM: each worker costs at least about 250 MB plus its geometry. For 15 small parts, 2–3 workers is a sensible cap. Combine with the existing memjob-style free-RAM guard.

### Gaps
- No official or community figure for Blender startup time was found. Only the local measurement exists.
- Did not test whether `import bpy` from the pip wheel starts faster than the `blender -b` executable.

## 5. Mesh resolution (segments) vs Boolean time

### Takeaway
Boolean time grows roughly linearly with segment count in these tests: doubling segments roughly doubled the time for every solver. Pick segments from the physical chord error instead of using a fixed high number.

### Cited Findings
- Local Blender 5.2 benchmark (36 cylinders, collection operand): MANIFOLD 0.018 → 0.032 → 0.064 s, EXACT 0.41 → 0.77 → 1.60 s, FLOAT 0.12 → 0.33 → 0.90 s at 32 → 64 → 128 segments. — Local benchmark (`bench_bool.py`)
- Local manifold3d benchmark: 0.018 → 0.032 → 0.071 s at 32 → 64 → 128 segments. — Local benchmark (`bench_m3d.py`)
- Manifold: Boolean cost grows with vertex and edge counts, so combine small meshes first. — [Manifold wiki: Performance Considerations](https://github.com/elalish/manifold/wiki/Performance-Considerations)
- manifold3d exposes `CircularQuality` / `segments_for` (parameters `segments`, `min_angle`, `min_edge_length`) to choose segments automatically from radius. — [all_apis.py](https://raw.githubusercontent.com/elalish/manifold/master/bindings/python/examples/all_apis.py)

### Inferences
- Chord error (sagitta) for radius r and n segments is r·(1 − cos(π/n)). For a hole of r = 1.5 mm, n = 32 gives about 0.007 mm, far below a 0.2 mm FDM nozzle/line tolerance. n = 128 adds about 4x the Boolean cost for no printable benefit. A rule such as `n = clamp(ceil(π / acos(1 − e/r)), 16, 64)` with e ≈ 0.01–0.02 mm is a reasonable default. Note that the polygon is inscribed: radius-critical holes then print slightly small. The existing "+0.2 mm" clearance rule covers far more than this, but use circumscribed radius r/cos(π/n) for precise fits if needed.
- Use lower segments in the fast "check" loop and full segments only for the final export, if the check gate does not depend on exact curvature.

### Gaps
- No published source quantifies Blender Boolean time vs polygon count on real CAD parts. Only the synthetic local test exists.
