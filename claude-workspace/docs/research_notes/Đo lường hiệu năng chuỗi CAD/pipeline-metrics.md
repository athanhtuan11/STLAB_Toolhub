# Lightweight continuous performance measurement for a local scripted CAD build pipeline (Windows, single developer)

Context: Python orchestrator -> Blender headless, assembly checker, CAD exporter, Bambu Studio CLI slicer; many runs/day; one Windows 11 PC; no server. Research date 2026-11-27.

## 1. Recording format and storage; which fields; examples from build tools

### Takeaway
Mainstream build tools record each run as a self-contained per-run file (JSON, often Chrome Trace Event Format) and keep a small rolling history. Turborepo `--summarize` and pytest-benchmark `--benchmark-autosave` are the closest model for this pipeline: one JSON per run, with task timings, cache hash/status and git commit in the filename. For one developer, append-only JSONL (one line per step per run) is the simplest store. A Chrome-trace JSON written alongside it gives the timeline view at no extra cost.

### Cited Findings
- **Bazel**: build commands write a profile to the output base as `command-$INVOCATION_ID.profile.gz`, with a `command.profile.gz` symlink to the latest. `--generate_json_trace_profile` turns it on or off, and `--profile` sets the path (`.gz` means gzip). By default Bazel keeps the last 5 profiles (`--profiles_to_retain`), and passing `--profile` explicitly disables that garbage collection. — [Bazel JSON trace profile](https://bazel.build/advanced/performance/json-trace-profile)
- Bazel's format is Chrome Trace Event Format JSON. The top level has `otherData` (metadata: build ID, date, output base) and `traceEvents`. Timestamps and durations are in **microseconds**, and `cat` holds a `ProfilerTask` enum. Short nearby events are merged ("slim profile"), and `--noslim_profile` turns that off. Special rows include `action count`, `CPU usage (Bazel)` (1 = one busy core), `Critical Path`, `Main Thread` and `Garbage Collector`. You can post-process with `jq` (the docs give an example extracting `sandbox.createFileSystem` durations) or use the EngFlow Bazel Invocation Analyzer. — [Bazel JSON trace profile](https://bazel.build/advanced/performance/json-trace-profile)
- **CMake**: `--profiling-format=google-trace` plus `--profiling-output=<path>` (added in 3.18) writes Google Trace Format, which you can view in Chrome's about:tracing or Trace Compass. — [cmake(1)](https://cmake.org/cmake/help/latest/manual/cmake.1.html)
- **Ninja**: keeps `.ninja_log` in the build root (or `builddir`), "a log of the command used to build it" for each output. Its main purpose is rebuild detection. The official manual does not document the field layout or any profiling tool. — [Ninja manual](https://ninja-build.org/manual.html)
- **Turborepo**: `--summarize` "Generates a JSON file in `.turbo/runs` containing metadata about the run", including affected packages, executed tasks "including their timings and hashes", and the files in the cached artifact. The docs say it is meant for debugging cache misses and "task timing changes over time". `--profile` writes two traces: Chrome Tracing (viewable in Perfetto) and a Markdown file "easier for LLMs to consume". `--anon-profile` redacts sensitive information. — [Turborepo run reference](https://turborepo.dev/docs/reference/run)
- **pytest-benchmark**: `--benchmark-autosave` writes files like `0001_c9cca5de6a4c7eb2_20150815_215724.json` (auto-increment ID, commit ID, timestamp) under `.benchmarks/<platform-python>/`. `--benchmark-save=name` sets a custom name. — [pytest-benchmark comparing](https://pytest-benchmark.readthedocs.io/en/latest/comparing.html)
- **asv** result schema stores per-benchmark `stats_*` fields (`ci_99_a`, `ci_99_b` confidence interval bounds, `q_25`, `q_75`, `repeat`, `number`) plus raw `samples`. Floats are truncated to 5 significant digits when saved. — [asv developer docs](https://asv.readthedocs.io/en/stable/dev.html)
- **sccache**: `sccache --show-stats` "will print a summary of cache statistics". The README does not list the counters or a JSON output mode. — [sccache README](https://github.com/mozilla/sccache)
- **MongoDB** perf CI produces "over 100k distinct results per software commit". — [MongoDB blog](https://www.mongodb.com/blog/post/using-change-point-detection-find-performance-regressions)

### Inferences
- Recommended store: `metrics/runs.jsonl`, append-only, one line per step. Fields:
  - `run_id`, `ts_start` (ISO), `git_commit`, `git_dirty`
  - `mode` (fast/release), `step`, `part`/`plate`, `duration_s`, `exit_code`
  - `cache` (hit/miss/na), `input_hash`, input sizes (`tri_count`, file bytes, number of parts/plates)
  - `peak_rss_mb` (child), `cpu_s` (child user+sys), `sys_mem_avail_mb_start`, `sys_cpu_pct_start` (machine load)
  - `tool_versions` (Blender/Bambu)
  - A single `run` summary line with the total.
- JSONL is appendable from parallel workers, survives crashes (a partial last line can be skipped), and is grep/pandas friendly.
- SQLite is worth it only once you want ad-hoc SQL over months of data. With about 50 runs/day × about 10 steps, JSONL stays in the low-MB range per year, which pandas reads in well under a second. This is an estimate, not measured.
- Mirror Bazel's retention idea: keep the full JSONL forever (small), but keep only the last N Chrome-trace files.
- Put `git_commit` in each record, as pytest-benchmark does in the filename. Commit-level attribution is what makes change-point results actionable.

### Gaps
- Gradle Build Scan fields and local (non-server) use were not fetched. Build scans normally need the Develocity/scans.gradle.com service, which does not fit a no-server setup (unverified here).
- `.ninja_log` v5/v6 field layout (start, end, mtime, output, hash) is not in the official manual. That layout is from memory and not confirmed here.
- sccache counter names and JSON stats format were not confirmed from docs.

## 2. Regression detection for noisy single-machine timings; repeats; warm vs cold cache

### Takeaway
A fixed percentage threshold against the previous run produces false positives on noisy steps and misses small drifts. That was MongoDB's documented experience with a 10% threshold. Change-point detection over the whole history (E-Divisive / Hunter / Apache Otava, or asv's L1 step detection) answers "which commit changed performance". For a solo developer, a cheap per-step rolling median + MAD guard on every run, plus an occasional change-point pass, is the pragmatic combination. Always compare like with like: same `mode` and same cache state.

### Cited Findings
- MongoDB originally flagged >10% changes between versions with a human reviewing each flag. This "missed small regressions, they flagged a lot of false positives on noisier tests, and sometimes they flagged real things, but at the wrong time". Per-test thresholds and baseline resets "did not fundamentally overcome the challenges". The question they reframed to: "Which software changes altered performance?" — [MongoDB blog](https://www.mongodb.com/blog/post/using-change-point-detection-find-performance-regressions)
- MongoDB's workflow: change-point detection flags regressions and improvements, then a team triages them, isolates each to a commit and assigns it. Some speedups turned out to be bugs. — [MongoDB blog](https://www.mongodb.com/blog/post/using-change-point-detection-find-performance-regressions)
- The algorithm is E-Divisive means, published as Daly et al., ICPE 2020, "The Use of Change Point Detection to Identify Software Performance Regressions in a Continuous Integration System". — [ICPE 2020 PDF](https://research.spec.org/icpe_proceedings/2020/proceedings/p67.pdf); [arXiv 2003.00584](https://arxiv.org/pdf/2003.00584v1.pdf)
- **Hunter** (open source) modifies E-Divisive by replacing the randomized permutation significance test with a Student's t-test, because the randomized approach "did not produce deterministic results" at reasonable iteration counts. It also finds nearby change points the original missed, and was evaluated against PELT and DYNP. — [Hunter, arXiv 2301.03034](https://arxiv.org/abs/2301.03034)
- E-Divisive was later implemented in Apache Otava (incubating), donated to the ASF in 2024. This comes from the search summary only; the arXiv paper was not opened. — [arXiv 2505.06758](https://arxiv.org/html/2505.06758v1)
- **asv step detection**:
  - It models data as "piecewise constant plus random noise".
  - It uses Laplace noise, so the fit is L1 and the level per segment is a weighted median. That makes it robust to outliers.
  - Each point is weighted by the inverse of its relative confidence interval.
  - The number of segments comes from a BIC-like penalty "fudged" to β·ln m / m, with β tuned empirically and its value not given.
  - Noise floor: `sigma_0 = 0.1*w0*min(abs(diff(mu)))`.
  - There is an AR(1) term for autocorrelated noise.
  - Not all steps are reported (see `asv.step_detect.detect_regressions`).
  — [asv step detection](https://asv.readthedocs.io/en/stable/step_detection.html)
- **pytest-benchmark**: `--benchmark-compare=0001` compares against a saved run. `--benchmark-compare-fail=min:5%` fails if Min is 5% slower, and `mean:0.001` fails if Mean is 1 ms slower. — [pytest-benchmark comparing](https://pytest-benchmark.readthedocs.io/en/latest/comparing.html)
- **hyperfine** (for deliberate A/B tests, not every-run monitoring):
  - By default it does "at least 10 benchmarking runs and estimate a run count targeting roughly 3 seconds".
  - `--warmup N` gives warm-cache runs, `--prepare CMD` runs before each run (cold cache), and `-r/--runs` sets an exact count.
  - It has statistical outlier detection "to detect interference from other programs and caching effects".
  - Export formats: CSV, JSON, Markdown, AsciiDoc and org-mode.
  - It is cross-platform. On Windows, peak memory and hardware counters are not supported.
  - The `scripts/` folder has Python analysis helpers (histogram, whisker plots).
  — [hyperfine README](https://github.com/sharkdp/hyperfine)

### Inferences
- **Per-run guard (cheap, immediate)**:
  - For each (`step`, `mode`, `cache` state) group, take the last ~20 matching records. Compute median and MAD.
  - Flag WARN if `duration > median + max(k·1.4826·MAD, abs_floor, rel_floor·median)`, with k≈3–4, an absolute floor of about 0.5–1 s, and a relative floor of about 10–20%.
  - Require 2 consecutive breaches before shouting, to cut single-spike noise.
  - The floors and k are engineering choices, not sourced numbers. Tune them on your own history.
- **Periodic (daily or on demand) change-point pass** per step series:
  - Library options: Apache Otava/Hunter (E-Divisive, deterministic t-test variant) or the `ruptures` Python library (PELT). Both are offline Python with no server.
  - Report the commit at each change point plus the before/after medians. This mirrors MongoDB's triage loop.
- **Never mix warm and cold**:
  - Tag every record with `cache: hit|miss` and `mode: fast|release`, and baseline only within the same tag.
  - A cache hit that takes 1 s and a miss that takes 30 s are different populations. Mixing them destroys median/MAD.
  - Also watch the hit ratio itself. A drop in hit rate is a regression even if per-step times are flat (Turborepo explicitly targets "cache misses" debugging).
- **Normalize by input size** where it varies, e.g. slice seconds per 100k triangles or Blender boolean seconds per operand. Otherwise a model that legitimately grew looks like a regression.
- **Repeats**:
  - Every-run monitoring uses n=1 per run but many runs over time. The history is the sample.
  - For a deliberate A/B check (e.g. a new export flag), use hyperfine with `--warmup 1` and its default of at least 10 runs. For multi-minute steps, cap it with `-r 3..5` and accept a wider uncertainty.
- **Record machine load at start** (available RAM, CPU%) and exclude or annotate runs that started under heavy load. This matters on a PC also used for other work. The repo already wraps heavy jobs with a RAM guard (`memjob.py`), and its decision could be logged too.

### Gaps
- Mozilla Perfherder's alerting algorithm (a t-test over windows of 12/12 points) was not fetched or verified.
- asv `asv continuous` default factor and `repeat`/`warmup_time` defaults were not retrieved (the dev page lacks them).
- No source gives a validated number of repeats for multi-minute CAD/slicer steps.
- The MongoDB blog gives no false-positive rate or minimum points per segment. The ICPE paper may, but its body was not read.

## 3. Measuring child-process peak memory and CPU on Windows from Python

### Takeaway
Windows tracks a lifetime peak working set per process (`PeakWorkingSetSize`), so you do not need high-frequency polling to get a true peak. You do need to read it before the process handle disappears. psutil 8 exposes this as `memory_info().peak_rss`. For a process tree (e.g. Blender or the slicer spawning helpers), a Windows Job Object gives `PeakProcessMemoryUsed`/`PeakJobMemoryUsed`, which the system "tracks constantly". That is the most accurate and lowest-overhead option. CPU time per child comes from `cpu_times()`. psutil's `children_*` CPU fields are always 0 on Windows, so you must sum descendants yourself.

### Cited Findings
- psutil (current docs, v8): on Windows, `memory_info().peak_rss` maps to `PeakWorkingSetSize` and `peak_vms` maps to `PeakPagefileUsage`. Version 8.0.0 renamed `peak_wset` → `peak_rss` and `peak_pagefile` → `peak_vms` (and `wset` → `rss`, `pagefile`/`private` → `vms`, `num_page_faults` → `page_faults()`). Old names "still work but raise DeprecationWarning". — [psutil API](https://psutil.io/api/)
- Older psutil Windows `pmem` named tuple fields include `peak_wset`, `pagefile`, `peak_pagefile` (psutil 7.1.0 source). — [psutil 7.1.0 _pswindows.py](https://sources.debian.org/data/main/p/python-psutil/7.1.0-1/psutil/_pswindows.py)
- Win32 `PROCESS_MEMORY_COUNTERS` provides `PeakWorkingSetSize` (bytes) and `PeakPagefileUsage` (peak commit charge over process lifetime). — [Microsoft Learn PROCESS_MEMORY_COUNTERS](https://learn.microsoft.com/en-us/windows/win32/api/psapi/ns-psapi-process_memory_counters)
- psutil `memory_full_info()` is deprecated since 8.0.0 in favor of `memory_footprint()`. That function "walks the full process address space, so it is slower than memory_info() and may require higher privileges". Avoid it in hot paths. — [psutil API](https://psutil.io/api/)
- psutil `cpu_times()`: `children_user` is "always 0 on Windows and macOS", and `children_system` is "always 0 on Windows…". — [psutil API](https://psutil.io/api/)
- psutil `cpu_percent(interval=0.0/None)` "returns the utilization since the last call or module import". The first call returns "a meaningless 0.0 value which you are supposed to ignore". — [psutil API](https://psutil.io/api/)
- psutil `children(recursive=True)` returns all descendants. If an intermediate process disappears, its descendants are no longer returned because the parent link is lost. — [psutil API](https://psutil.io/api/)
- `psutil.Popen` behaves like `subprocess.Popen` but exposes all `psutil.Process` methods. On Windows, `wait()` returns the exit code via GetExitCodeProcess. `oneshot()` is a "Context manager that speeds up retrieval of multiple process attributes". Its speedup figures were not retrieved. — [psutil API](https://psutil.io/api/)
- Job Objects: `JOBOBJECT_EXTENDED_LIMIT_INFORMATION.PeakProcessMemoryUsed` is "The peak memory used by any process ever associated with the job", and `PeakJobMemoryUsed` is "The peak memory usage of all processes currently associated with the job". "The system tracks the value … constantly." The same struct can set a process or job memory limit (`JOB_OBJECT_LIMIT_PROCESS_MEMORY` / `JOB_OBJECT_LIMIT_JOB_MEMORY`). The values are committed virtual memory, not working set. Supported since Windows XP. — [Microsoft Learn JOBOBJECT_EXTENDED_LIMIT_INFORMATION](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information)
- hyperfine does not support peak memory on Windows. — [hyperfine README](https://github.com/sharkdp/hyperfine)

### Inferences
- **Option A (simplest)**:
  - Launch with `psutil.Popen`, then run a background thread every ~0.5–1 s. Each tick calls `p.memory_info().peak_rss` and `cpu_times()` for the process plus `children(recursive=True)`, inside `oneshot()`. Keep the max and the last value.
  - The final sample before exit catches the OS-tracked peak of the main process. Short-lived grandchildren may be missed.
  - Overhead: a handful of syscalls per second. That is negligible against multi-second steps (estimate, not measured).
- **Option B (most accurate for trees)**:
  - Create a Job Object (via `pywin32` `win32job` or `ctypes`) and assign the child right after spawn, so descendants inherit it.
  - After exit, query `JobObjectExtendedLimitInformation` for `PeakProcessMemoryUsed`/`PeakJobMemoryUsed`, and `JobObjectBasicAccountingInformation` for total user/kernel time across all job processes. Basic accounting was not fetched here; verify it.
  - This needs zero polling. The same job can enforce the RAM cap that `memjob.py` currently handles.
  - Caveat: Job peaks are commit (private bytes), not working set, so they are not directly comparable with `peak_rss`. Record which metric you used in the record.
- Time with `time.perf_counter()` around `Popen`…`wait()`. Record wall time, plus child CPU seconds as a load-independent signal: CPU-s rising while wall time is flat means the work grew.
- Pre-existing nested job objects (some launchers put processes in jobs) are allowed on Windows 8+ (nested jobs). Not verified in fetched sources.

### Gaps
- psutil `oneshot()` speedup numbers and per-call overhead on Windows were not retrieved (the performance page returned 404).
- Whether Blender `--background` or Bambu Studio CLI spawn child processes was not verified. This determines whether Option B is needed.
- `JOBOBJECT_BASIC_ACCOUNTING_INFORMATION` fields were not fetched.

## 4. Simple visualization: run timeline (Chrome trace / Perfetto) and trend charts

### Takeaway
Write a Chrome Trace Event Format JSON per run, using complete `X` events for steps and `C` counter events for RAM/CPU, and open it in ui.perfetto.dev or chrome://tracing. This is the same format Bazel, CMake and Turborepo emit. For trends, a small script reads the JSONL with pandas and renders per-step lines (median band + markers at flagged runs or change points) to a static HTML or PNG file, viewable offline or embedded in the existing Toolhub web.

### Cited Findings
- Perfetto UI opens Chrome JSON (Trace Event Format) directly:
  - B/E and X events are shown as slices, I as instant points, C as counter tracks, M as metadata, and s/t/f as flow arrows.
  - Trace Processor loads them into SQL tables (`slice`, `track`, `process`, `thread`, `counter`, `args`).
  - Limitation: duration events must nest. Overlapping events go to an overflow track, so use async events for overlap.
  — [Perfetto: other formats](https://perfetto.dev/docs/getting-started/other-formats)
- Bazel trace: timestamps/durations in microseconds, viewable in chrome://tracing (keys 1–4 switch modes). — [Bazel JSON trace profile](https://bazel.build/advanced/performance/json-trace-profile)
- CMake google-trace output is viewable in Chrome about:tracing or Trace Compass. — [cmake(1)](https://cmake.org/cmake/help/latest/manual/cmake.1.html)
- Turborepo's Chrome trace is "inspect[ed] visually in a tool like Perfetto". — [Turborepo run reference](https://turborepo.dev/docs/reference/run)
- pytest-benchmark `--benchmark-histogram` renders a modified Tukey box plot (needs `pygal`, `pygaljs`). — [pytest-benchmark comparing](https://pytest-benchmark.readthedocs.io/en/latest/comparing.html)

### Inferences
- Minimal per-run trace: `{"traceEvents":[{"name":"slice","cat":"step","ph":"X","ts":<µs>,"dur":<µs>,"pid":1,"tid":<worker>,"args":{"cache":"miss","tri":123456}}, {"name":"ram_mb","ph":"C","ts":...,"pid":1,"args":{"mb":2100}}], "otherData":{"commit":"...","mode":"fast"}}`.
  - Use a distinct `tid` per parallel worker so parallel steps don't overlap on one track. Perfetto requires nesting per track.
  - Keep `ts`/`dur` in microseconds, as Bazel does.
- Trend chart: one subplot per step, x = run index or time, y = duration. Shade the rolling median ± 3·MAD, colour by cache hit/miss, use a marker shape per mode, and draw vertical lines at detected change points labelled with the short commit hash. Plotly offline HTML (single file) or matplotlib PNG both work without a server.
- Fits house rule "review as images": a PNG contact sheet of trend charts is the natural review artifact.

### Gaps
- The Trace Event Format spec itself (Google Doc) could not be fetched. Field names above are corroborated by the Perfetto and Bazel pages only for event types and units, not every field.
- Perfetto UI offline/local-only operation and JSON size limits were not confirmed (the "Opening Large Traces" page was not read).

## 5. Keeping measurement cheap and undistorted; tagging runs

### Takeaway
Measure at step boundaries in the orchestrator, not inside tools. Use OS-tracked peaks rather than tight polling. Write one JSONL line per step after it finishes. Tag every record with mode, cache state, commit and machine-load snapshot so comparisons are like-for-like. The tools surveyed all do measurement as a by-product of the normal run (Bazel profile on by default, Turborepo summary flag), not as a separate benchmark job.

### Cited Findings
- Bazel generates the JSON profile by default on build commands and merges very short events to keep the profile small (`--noslim_profile` to disable). — [Bazel JSON trace profile](https://bazel.build/advanced/performance/json-trace-profile)
- Bazel's default retention is the last 5 profiles. — [Bazel JSON trace profile](https://bazel.build/advanced/performance/json-trace-profile)
- hyperfine separates warm (`--warmup`) from cold (`--prepare` to clear caches) runs and detects outliers caused by "interference from other programs and caching effects". — [hyperfine README](https://github.com/sharkdp/hyperfine)
- psutil `memory_footprint()` / `memory_full_info()` walk the full address space and are slower. `memory_info()` is the cheap call. — [psutil API](https://psutil.io/api/)
- Turborepo `--summarize` output targets cache-miss debugging and timing changes over time. Its `--anon-profile` exists to redact sensitive data before sharing. — [Turborepo run reference](https://turborepo.dev/docs/reference/run)

### Inferences
- **Cheapness checklist**:
  - Use perf_counter at step boundaries.
  - Have one sampler thread per child at about 1 Hz, or a Job Object with no sampler.
  - Never call `memory_footprint`/`memory_full_info` in the loop.
  - Compute triangle counts only where the step already loads the mesh, and pass them up in the step's JSON result.
  - Append a line with a flush, not a rewrite.
  - Generate traces and charts lazily, on demand or once per day.
- **Tags**:
  - `mode` (fast = 3MF-only loop, release = .sc/.step/.blend export)
  - `cache` (hit/miss per step, plus the run-level hit ratio)
  - `parallelism` (worker count)
  - `trigger` (manual / auto-run / gate)
  - `git_commit` + `git_dirty`
  - `host_load` (CPU%, available RAM at start)
  - `tool_versions`
  - Annotate a Blender or Bambu Studio upgrade with a version tag, so a step change is explained instead of flagged.
- **Distortion risks**:
  - Parallel workers compete with each other, so per-step wall time depends on concurrency. Record `parallelism` and compare within it.
  - Antivirus or indexing on first file access inflates cold runs. Tagging `cache=miss` plus `first_run_after_boot` helps.
  - Thermal/power plan state on a laptop or desktop (not verified for this PC).
- **Don't gate on n=1**: a per-run WARN is informational. Only a sustained shift, from consecutive breaches or a change point, should block or alert. That is MongoDB's lesson about raw threshold false positives.
- **Privacy**: if traces are ever shared, strip absolute paths and usernames, as Turborepo's `--anon-profile` does.

### Gaps
- No sourced measurement of psutil/Job Object overhead on Windows. Claims of "negligible" are estimates.
- No source on Windows Defender's impact on build timing was consulted.
