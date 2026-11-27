# Speeding up automated slicing with Bambu Studio / OrcaSlicer CLI

Scope: wall-clock time for slicing 5 plates (1–5 PETG parts each, A1, 0.2 mm) from Python on Windows with limited RAM. Sources were read on 2026-11-27. "Source" here means the BambuStudio `master` and OrcaSlicer `main` source files fetched that day (`src/BambuStudio.cpp`, `src/libslic3r/PrintConfig.cpp`, `src/libslic3r/Utils.hpp`, `src/libslic3r/Thread.cpp`, Orca's equivalents). Older installed builds may differ.

## CLI options, plate selection, multithreading, documented performance behavior

### Takeaway
One `--slice 0` process slices plates **one after another** in a loop. Bambu Studio has no CLI flag for thread count. Inside each plate, libslic3r parallelizes with TBB using every core the process may use. The flags that matter for speed are `--slice N`, `--load-slicedata` / `--export-slicedata` (a cache), `--skip-useless-pick`, `--min-save`, `--no-check` and `--mstpp`/`--mtcpp` (limits). Avoid `--orient`/`--arrange` on input that is already oriented.

### Cited Findings
- Official wiki usage: `bambu-studio [OPTIONS] [file.3mf/file.stl ...]`. `--slice plate_index` means 0 = all plates and i = plate i. `--debug level` runs 0 = fatal to 5 = trace. `--load-settings "machine.json;process.json"` takes at most one of each, and each must be a full config. `--load-filaments "f1.json;f2.json"`: an empty entry keeps that slot's 3MF setting. Also documented: `--outputdir`, `--arrange 0|1|other=auto`, `--orient`, `--export-3mf`, `--export-settings`, `--export-slicedata dir`, `--load-slicedata dir`, `--pipe pipename`, `--uptodate`, `--info`, and `--key=value` overrides. Precedence: CLI `--key=value` > `--load-settings`/`--load-filaments` > values in the 3MF — [BambuStudio wiki: Command Line Usage](https://github.com/bambulab/BambuStudio/wiki/Command-Line-Usage)
- Example from the wiki that orients and arranges an STL, then slices with settings: `--orient --arrange 1 --load-settings "machine.json;process.json" --load-filaments "filament.json" --slice 2 --debug 2 --export-3mf output.3mf boat.stl` — [BambuStudio wiki](https://github.com/bambulab/BambuStudio/wiki/Command-Line-Usage)
- Option definitions in source (`CLIActionsConfigDef`): `min_save` ("export 3mf with minimum size"), `mtcpp` ("max triangle count per plate for slicing"), `mstpp` ("max slicing time per plate in seconds"), `no_check` ("Do not run any validity checks, such as gcode path conflicts check"), `normative_check`, `export_png` (0 = all, i = plate i), `export_stls`, `load_defaultfila`. In source, `orient` is `coInt` ("0-disable, 1-enable, others-auto"), but the wiki shows bare `--orient`. In `CLIMiscConfigDef`: `skip_objects`, `clone_objects`, `datadir` ("Use and store all program settings at the given directory"), `outputdir`, `debug`, `enable_timelapse`, `skip_modified_gcodes`, `skip_useless_pick` ("Skip generating useless pick/top images into 3mf"), `allow_newer_file`, `allow_mix_temp`, `camera_view`, `estimate_mode`, `check_preset`, `switch_process`, `import_positions`. **No thread-count option is defined** — [BambuStudio PrintConfig.cpp](https://raw.githubusercontent.com/bambulab/BambuStudio/master/src/libslic3r/PrintConfig.cpp)
- Plate loop in source: `//BBS: slice every partplate one by one` followed by `for (int index = 0; index < partplate_list.get_plate_count(); index ++) { if ((plate_to_slice != 0) && (plate_to_slice != (index + 1))) continue; ...`. So `--slice 0` is sequential across plates within one process — [BambuStudio.cpp](https://raw.githubusercontent.com/bambulab/BambuStudio/master/src/BambuStudio.cpp)
- Threading: libslic3r sizes its worker pool with `tbb::this_task_arena::max_concurrency()`. A source comment says "TBB will respect the task affinity mask on Linux and spawn less threads than std::thread::hardware_concurrency()" — [BambuStudio Thread.cpp](https://raw.githubusercontent.com/bambulab/BambuStudio/master/src/libslic3r/Thread.cpp)
- Version history from a third-party reference: `--allow-newer-file`, `--export-stls`, `--metadata-*` and `--downward-check` arrived in 1.9.7; `--allow-mix-temp` in 2.0.1; `--export-png` and `--camera-view` in 2.1.0; `--estimate-mode` in 2.7.1; `--check-preset` and `--datadir` in 2.8.2; no flag changes in 2.9.1. The same reference says `--skip-useless-pick` "can reduce runtime and output size" and that `--min-save` is "Recommended for production pipelines" — [Printago: Bambu Studio CLI reference](https://printago.io/blog/bambu-studio-cli-reference) (vendor blog, secondary)
- The `--pipe` progress JSON has fields `plate_index`, `plate_count`, `plate_percent`, `total_percent`, and either `message` or `warning`. In source it is written with POSIX `write()` to a pipe fd — [BambuStudio.cpp](https://raw.githubusercontent.com/bambulab/BambuStudio/master/src/BambuStudio.cpp)
- OrcaSlicer CLI shape: `orca-slicer [input files...] [options...]`. Boolean flags take no value, and the docs warn that space-separated `--flag 0` "does not behave as it appears to", so use `=0`. Underscores become hyphens. Repeating a vector flag appends to it. 43 keys cannot be overridden. Example: `orca-slicer model.3mf --load-settings "process.json;printer.json" --load-filaments filament.json --arrange 1 --slice 0 --export-3mf output.3mf` — [OrcaSlicer wiki: CLI mode](https://www.orcaslicer.com/wiki/cli/cli_mode)
- OrcaSlicer `main` (source) adds `--export-statistics`, which writes `plate_N.statistics.json` (print time, filament, feature totals, per layer and per object), and `--logfile` ("Redirects debug logging to file"). Its `--debug` defaults to 1. It also has newer `--mcp`, `--run` and `--cad` options; these are probably recent nightly-only features — [OrcaSlicer PrintConfig.cpp](https://raw.githubusercontent.com/SoftFever/OrcaSlicer/main/src/libslic3r/PrintConfig.cpp)
- CuraEngine for comparison: `CuraEngine slice -j fdmprinter.def.json -s key=value -l model.stl -o out.gcode`. `-m<thread_count>` sets threads ("single digit" only, per the man page for 4.13) — [Ubuntu manpage CuraEngine 4.13](https://manpages.ubuntu.com/manpages/lunar/man1/CuraEngine.1.html)

### Inferences
- With one `--slice 0` call for a 5-plate 3MF, total time ≈ startup + Σ(per-plate slice). Parallelism exists only within each plate. Small plates (1–5 parts) probably leave many cores idle in the serial stages (G-code export, thumbnails), so running plates as separate processes can cut wall-clock time.
- Windows has no thread flag. To cap threads per instance, set CPU affinity (`start /affinity <mask>`, or `psutil.Process.cpu_affinity()` right after spawning). Whether Windows TBB reads affinity at start is **not confirmed**; the source comment only mentions Linux. Use `/affinity` at launch rather than setting it after start.

### Gaps
- No official performance documentation was found for either CLI.
- I have no measured numbers comparing a single `--slice 0` process with N processes running `--slice i`.

## Running multiple CLI instances in parallel: memory, contention, concurrency

### Takeaway
No primary source documents memory use per CLI instance or a recommended concurrency. The CLI writes `peak_rss_mb` to `result.json`, so the pipeline can measure it per plate and set concurrency from free RAM.

### Cited Findings
- `record_exit_reson()` writes `result.json` (in `--outputdir`, or the current directory if none is set) with `return_code`, `error_string`, `plate_index` and `times` (`prepare_time`, `import_time`, `export_time`, `export_3mf_time`, `load_slicedata_time`, `export_slicedata_time`). It also writes **`peak_rss_mb`** and, per plate, `sliced_time`, `sliced_time_with_cache`, stage times (slice layers, walls, infill, support detect / tree generate, detect overhangs, skirt/brim, conflict check, toolpath, export G-code), `triangle_count`, `warning_message` and `obj_cached_cnt` — [BambuStudio.cpp](https://raw.githubusercontent.com/bambulab/BambuStudio/master/src/BambuStudio.cpp)
- One vendor says each slice creates "hundreds of megabytes of temp files in the working directory" and recommends a separate temp directory per slice. This is important for parallel runs — [Printago](https://printago.io/blog/bambu-studio-cli-reference) (secondary)
- GUI report (not CLI): a memory spike during slicing reached about 17.9 GB of system RAM and caused paging, plus a handle leak of about 50–65 handles per slice — [BambuStudio issue #10757](https://github.com/bambulab/BambuStudio/issues/10757) (from the search summary; I did not read the thread in full)
- GUI report: limiting bambustudio.exe to 4 cores in Task Manager stopped crashes during slicing for one commenter — [BambuStudio issue #3899](https://github.com/bambulab/BambuStudio/issues/3899) (anecdotal)
- `CLI_OUT_OF_MEMORY = -14` ("Out of memory during slicing. Please upload a model with lower geometry resolution") exists as a distinct exit code — [Utils.hpp](https://raw.githubusercontent.com/bambulab/BambuStudio/master/src/libslic3r/Utils.hpp), [BambuStudio.cpp](https://raw.githubusercontent.com/bambulab/BambuStudio/master/src/BambuStudio.cpp)

### Inferences
- Pattern: one process per plate (`--slice i`), each with its own `--outputdir` and working directory (cwd), with concurrency = min(plates, floor((free RAM − margin) / measured peak_rss_mb), cores / threads per job). Use peak_rss_mb from earlier runs (store it in a JSON) as the estimate. This fits the existing memjob.py (free RAM − 3 GB).
- Each process pays startup and input/profile loading again. Parallelism only helps when per-plate slicing time is much larger than startup. Measure `prepare_time + import_time` against `sliced_time` in result.json before deciding.
- Do not run two instances in the same cwd or outputdir, because `result.json` and the temp files would overwrite each other.

### Gaps
- No sourced peak RAM figure exists for slicing small PETG parts on an A1 with the CLI. It has to be measured.
- I found no sourced recommendation on concurrency, and no evidence on whether several instances contend over the `datadir` / AppData config.

## Caching: skip re-slicing when inputs are unchanged, incremental slicing, reusing a 3MF

### Takeaway
The CLI has a built-in cache: `--export-slicedata dir` after a slice, then `--load-slicedata dir` next time, keyed per plate by subfolder `dir/<plate>`. If loading fails, it falls back to a normal slice. Caching at the pipeline level (hash STL + profile + CLI version → skip the call entirely) is still the fastest option and simple to build.

### Cited Findings
- Source: with `load_slicedata`, `plate_dir = load_slice_data_dir + "/" + (index+1)`, then `print->load_cached_data(plate_dir)`. If that returns an error, it logs "switch normal slicing" and calls `print->process()`. Otherwise it calls `print->process(nullptr, true)`, which reuses the cache — [BambuStudio.cpp](https://raw.githubusercontent.com/bambulab/BambuStudio/master/src/BambuStudio.cpp)
- Cache-related exit codes: `CLI_EXPORT_CACHE_DIRECTORY_CREATE_FAILED -53`, `CLI_EXPORT_CACHE_WRITE_FAILED -54`, `CLI_IMPORT_CACHE_NOT_FOUND -55`, `CLI_IMPORT_CACHE_DATA_CAN_NOT_USE -56`, `CLI_IMPORT_CACHE_LOAD_FAILED -57` — [Utils.hpp](https://raw.githubusercontent.com/bambulab/BambuStudio/master/src/libslic3r/Utils.hpp)
- The per-plate `obj_cached_cnt` and `sliced_time_with_cache` in result.json show whether the cache was used — [BambuStudio.cpp](https://raw.githubusercontent.com/bambulab/BambuStudio/master/src/BambuStudio.cpp)
- In source, a check that blocked using `load_slicedata` together with `export_slicedata` is commented out. There is still a separate warning/guard when `load_slicedata` is used with `repetitions` or `shrink_to_new_bed` — [BambuStudio.cpp](https://raw.githubusercontent.com/bambulab/BambuStudio/master/src/BambuStudio.cpp)
- `--load-slicedata` is described as "Load cached slicing data from a previous run to avoid re-slicing" — [Printago](https://printago.io/blog/bambu-studio-cli-reference)

### Inferences
- What exactly the cache is valid for (geometry or setting changes) is not documented. The safe approach is a self-built cache key: sha256(each STL/3MF input) + sha256(machine/process/filament json) + bambu-studio version + CLI arguments. On a match, skip the slice and reuse the previous 3MF and result.json. Plates in a multi-plate set that did not change should be cached individually (hash per plate), which only works when each plate is sliced as its own process or its own `--slice i`.
- Reusing a prepared 3MF project (already arranged, profiles embedded) avoids `--orient`/`--arrange`. In source, `need_regenerate_thumbnail = oriented_or_arranged || regenerate_thumbnails`, so orient/arrange forces thumbnails to be re-rendered with OpenGL — [BambuStudio.cpp](https://raw.githubusercontent.com/bambulab/BambuStudio/master/src/BambuStudio.cpp). If the STL is already in print orientation (the existing rule says `--orient 0`), drop arrange/orient as well whenever the positions are already fixed.

### Gaps
- No documentation says which config changes make `--load-slicedata` invalid.
- No measured timings of a cache hit against a full slice were found.

## CLI startup overhead and how to reduce it

### Takeaway
The CLI does **not** start the GUI when an action is given (`start_gui = m_actions.empty() && !downward_check`). It still creates an `OpenGLManager` and renders thumbnails with OpenGL when needed. I found no sourced figure for startup time. `result.json` reports `prepare_time` and `import_time`, so startup can be measured directly.

### Cited Findings
- Source: `bool start_gui = m_actions.empty() && !downward_check; if (start_gui) { ... return Slic3r::GUI::GUI_Run(params); }`. With `--slice`/`--export-3mf` it stays in CLI mode — [BambuStudio.cpp](https://raw.githubusercontent.com/bambulab/BambuStudio/master/src/BambuStudio.cpp)
- In slice mode the source still creates `std::make_shared<Slic3r::GUI::OpenGLManager>()` and uses it for thumbnails. G-code export chooses `opengl_valid ? export_gcode(..., cli_generate_thumbnails) : export_gcode(..., nullptr)` — [BambuStudio.cpp](https://raw.githubusercontent.com/bambulab/BambuStudio/master/src/BambuStudio.cpp)
- `--skip-useless-pick` skips the pick/top images when a plate has ≤1 object (or >64) — [BambuStudio.cpp](https://raw.githubusercontent.com/bambulab/BambuStudio/master/src/BambuStudio.cpp); [Printago](https://printago.io/blog/bambu-studio-cli-reference)
- The CLI reads full profiles from `resources/profiles/BBL/machine_full/`, `process_full/`, `filament_full/` and `cli_config.json` when switching machine or process — [BambuStudio.cpp](https://raw.githubusercontent.com/bambulab/BambuStudio/master/src/BambuStudio.cpp)
- `--datadir` (from 2.8.2) points settings at a separate directory — [PrintConfig.cpp](https://raw.githubusercontent.com/bambulab/BambuStudio/master/src/libslic3r/PrintConfig.cpp); [Printago](https://printago.io/blog/bambu-studio-cli-reference)
- Forum report (GUI, Windows): antivirus slows Bambu Studio — [Bambu forum: slow on Windows? Check your antivirus first](https://forum.bambulab.com/t/bambustudio-slow-on-windows-check-your-antivirus-first/251343) (from the search summary; user-side, not confirmed by Bambu)

### Inferences
- Ways to reduce startup and fixed cost, to be verified by measuring `prepare_time`/`import_time`/`export_3mf_time`:
  1. Pass a 3MF with profiles already embedded, rather than doing a machine/process switch through `--load-settings` on every call.
  2. Use `--skip-useless-pick` and `--min-save` to shrink the 3MF and skip images.
  3. Skip `--orient`/`--arrange` so the CLI does not re-render thumbnails.
  4. Use `--debug 1` or `2` (logging at 5 writes far more).
  5. Use a separate `--datadir` per pipeline to avoid sharing state with the open GUI.
  6. Add a Windows Defender exclusion for the output/temp folder if antivirus turns out to scan the temp files (only if measurements show it).
- There is no "warm server" mode in Bambu Studio CLI. The `--mcp` mode in Orca main keeps a GUI process running, but it is new and unstable, and **not** a CLI daemon that has been tested for this.

### Gaps
- No sourced measurement of Bambu/Orca CLI startup time on Windows was found.

## Lighter-weight validation before a full slice

### Takeaway
`--info` (Bambu, Orca, Prusa) prints model info without slicing. `--mtcpp` lets the slicer reject plates with too many triangles early. The fastest gate is still a mesh-level check in Python, which the pipeline already has. Use it to decide whether to slice at all, and slice only after it passes.

### Cited Findings
- `--info`: "Output the model's information" (Bambu) — [PrintConfig.cpp](https://raw.githubusercontent.com/bambulab/BambuStudio/master/src/libslic3r/PrintConfig.cpp); [BambuStudio wiki](https://github.com/bambulab/BambuStudio/wiki/Command-Line-Usage)
- `--mtcpp <count>` rejects plates over the triangle budget and returns `CLI_TRIANGLE_COUNT_EXCEEDS_LIMIT -59`. `--mstpp <s>` stops a slice that runs too long and returns `CLI_SLICING_TIME_EXCEEDS_LIMIT -58`. There is no built-in timeout without `--mstpp` — [Printago](https://printago.io/blog/bambu-studio-cli-reference); [Utils.hpp](https://raw.githubusercontent.com/bambulab/BambuStudio/master/src/libslic3r/Utils.hpp)
- A slice-speed factor in older Bambu versions: "Detect bridging perimeter" / overhang slowdown makes G-code generation slower. A linked patch skips the overhang-degree calculation when a model has no overhangs — [BambuStudio issue #331](https://github.com/bambulab/BambuStudio/issues/331) (from the search summary)
- User measurement (version not stated, Aug 2025): a 300% Benchy at 0.20 mm Standard on the X1C sliced in under 10 s. Another user went from 55 s to about 15 s after an update — [Bambu forum: speed slicing](https://forum.bambulab.com/t/bambu-studio-speed-slicing/191765)
- Unverified forum claim: Orca merged "Upgrade clipper & improve multi-thread performance" (PR #7177), which Bambu master lacks — [Bambu forum thread](https://forum.bambulab.com/t/bambu-studio-is-still-lagging-while-orca-keeps-fixing-what-bambu-ignores/250577) (opinion, not verified)

### Inferences
- Order of gates: (1) the cache hash matches → stop; (2) mesh check (trimesh: watertight, triangle count, overhang via face normals); (3) only then call the CLI with `--mstpp` as a safety net. Do not use CuraEngine or PrusaSlicer as a pre-gate, because their support and overhang logic differs from Bambu's, so a PASS there does not mean PASS in Bambu.
- `--no-check` skips the G-code path conflict check (`TIME_CONFLICT_CHECK` is a stage in result.json). It saves time, but it removes the CLI's protection that returns `-100`/`-101` on overlap or empty layers. Do not use it in the release-check pipeline.

### Gaps
- No time measurements were found for `--info` or for CuraEngine compared with Bambu on the same model.

## Known issues: Windows quirks, floating regions / support warnings, exit codes

### Takeaway
Exit codes are **negative integers** (0 = success). On Windows the process exit code is a 32-bit value, so −58 shows up as 4294967238 when read unsigned. Slicing warnings, including floating regions and missing support, appear in `result.json` → `sliced_plates[].warning_message`. Only `SlicingEmptyGcodeLayers` and `SlicingGcodeOverlap` (when `--no-check` is off) turn a warning into an error exit (`-100`). Other warnings still exit 0.

### Cited Findings
- Exit code table (Utils.hpp): `0 SUCCESS, -1 ENVIRONMENT_ERROR, -2 INVALID_PARAMS, -3 FILE_NOTFOUND, -5 CONFIG_FILE_ERROR, -6 DATA_FILE_ERROR, -7 INVALID_PRINTER_TECH, -13 EXPORT_3MF_ERROR, -14 OUT_OF_MEMORY, -17 PROCESS_NOT_COMPATIBLE, -18 INVALID_VALUES_IN_3MF, -20 PRINTABLE_SIZE_REDUCED, -21 OBJECT_ARRANGE_FAILED, -22 OBJECT_ORIENT_FAILED, -24 FILE_VERSION_NOT_SUPPORTED, -50 NO_SUITABLE_OBJECTS, -51 VALIDATE_ERROR, -52 OBJECTS_PARTLY_INSIDE, -53..-57 cache errors, -58 SLICING_TIME_EXCEEDS_LIMIT, -59 TRIANGLE_COUNT_EXCEEDS_LIMIT, -60 NO_SUITABLE_OBJECTS_AFTER_SKIP, -61 FILAMENT_NOT_MATCH_BED_TYPE, -62 FILAMENTS_DIFFERENT_TEMP, -63/-64 OBJECT_COLLISION (seq/layer), -100 SLICING_ERROR, -101 GCODE_PATH_CONFLICTS, -102 GCODE_PATH_IN_UNPRINTABLE_AREA, -103 FILAMENT_UNPRINTABLE_ON_FIRST_LAYER, -104 GCODE_PATH_OUTSIDE, -105 GCODE_IN_WRAPPING_DETECT_AREA` — [Utils.hpp](https://raw.githubusercontent.com/bambulab/BambuStudio/master/src/libslic3r/Utils.hpp)
- Warning handling in source: after `print->process()` it loops over `g_slicing_warnings`. If `warning_step != -1` and the message is not a default notification, it sets `sliced_plate_info.warning_message = status.text`. NON_CRITICAL warnings are only logged. Other warnings are logged with `no_check=%3%`, and only `SlicingEmptyGcodeLayers || SlicingGcodeOverlap` triggers `record_exit_reson(..., CLI_SLICING_ERROR)` and `flush_and_exit(-100)` when `!no_check`. A non-empty conflict string gives `-101` — [BambuStudio.cpp](https://raw.githubusercontent.com/bambulab/BambuStudio/master/src/BambuStudio.cpp)
- Each plate keeps a single `warning_message` (a string, not a list), and later warnings overwrite earlier ones in the loop — [BambuStudio.cpp](https://raw.githubusercontent.com/bambulab/BambuStudio/master/src/BambuStudio.cpp)
- `--allow-newer-file --slice 0 --export-3mf` produced no output file for a 3MF input in one report — [BambuStudio issue #9636](https://github.com/bambulab/BambuStudio/issues/9636) (from the search summary)
- `--export-3mf` crashed on macOS with 02.04.00.70 — [Bambu forum](https://forum.bambulab.com/t/add-stl-step-file-to-a-3mf-from-the-command-line/221244) (from the search summary)
- "CLI cannot apply external presets": user profiles must be full configs. The wiki writes `--load_settings` with underscores while its examples use hyphens — [Bambu forum](https://forum.bambulab.com/t/cli-cannot-apply-external-presets/197842); [BambuStudio wiki](https://github.com/bambulab/BambuStudio/wiki/Command-Line-Usage)
- The `--pipe` notifier uses POSIX `write()` on a pipe fd. The Linux-specific callback code is behind `#if defined(__linux__)`. Pipe examples use `mkfifo` — [BambuStudio.cpp](https://raw.githubusercontent.com/bambulab/BambuStudio/master/src/BambuStudio.cpp); [Printago](https://printago.io/blog/bambu-studio-cli-reference)

### Inferences
- In Python on Windows, convert the code: `rc = p.returncode; rc = rc - 2**32 if rc > 2**31 else rc`, then map it with the table above. Always read `result.json` (it has `error_string` and per-plate warnings) instead of parsing stdout/log.
- Floating regions / "support needed" warnings do **not** fail the exit code. The pipeline has to parse `warning_message` itself (the text may be localized; compare against the English strings when the language is unset). Because each plate keeps only one string, warnings can be missed. Keep the separate mesh overhang check as the main gate, or read the log at `--debug 2`, where every warning is logged as "found slicing warnings: ...".
- `--pipe` is probably unreliable on Windows (it depends on POSIX `write`/mkfifo). Use `result.json` instead, and track progress through the log if needed.

### Gaps
- I could not confirm how the installed Windows build behaves for console stdout and exit codes (GUI subsystem). Test it directly with `subprocess.run(...).returncode`.
- I do not have the exact English text of the floating-region warning as written into `warning_message`; it is in the libslic3r strings and still needs to be grepped.
