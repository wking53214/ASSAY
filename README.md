# ASSAY

*Formerly TOUCHSTONE. Renamed in October 2026; the role is unchanged.*

**Specimen corpus, not a system.** Real code, really damaged, with independently-known correct answers. Two named specimens (3.6 and 3.7) are constructed reproductions of failures recorded in the ecosystem's own history rather than recovered files, and say so in their own text. Fuel for [`ghost_tools`](https://github.com/wking53214/ghost_tools), [`SWIZZLE`](https://github.com/wking53214/SWIZZLE) and [`Warden`](https://github.com/wking53214/Warden), which read the answer key as data from `assay_production/registry.json`. Absorbed retired [`VANGUARD`](https://github.com/wking53214/VANGUARD) files as evidence.

## What This Is

ASSAY is a folder of real code files that were damaged in known ways, plus a written answer for each one saying what is wrong with it. A program in this repository, `verify_manifest.py`, checks on every run that those answers are still true and that nobody has changed a specimen or an answer without saying so. Other tools in the same group of repositories read the answers to see whether they find what they should. It is test data and a checker. It is not a product, and it has no users outside that group that the maintainer knows of.

To try it: install as in section 9, then run `python3 verify_manifest.py --strict`. Section 4 says what is proven and what is not, section 11 lists what broke in this repository and how it was fixed, and section 13 says what code cannot fix.

## 1. Pipeline Position & Role

**ASSURANCE FIXTURES.** Not Admission, Observe, Policy, Decision, Conservation, Execution, or Custody.

## 2. Full System Scope & Architectural Depth

`MANIFEST.md` + `verify_manifest.py` + specimen trees (including `.ghost_archive`). Known-damage cases with expected findings. matplotlib/numpy appear in some specimens (not a product stack). The counts of unfinished-work markers, numpy and matplotlib imports, and hashed files are generated in section 4 below, not typed here.

## 3. What It Does NOT Do / Non-Goals

Does not run a governance kernel. Does not pass CI as "the app." Shipping it as a product is a category error (commercial: **NOT COMMERCIALLY RELEVANT**; possibly test data).

## 4. Brutally Honest Current Status & Gaps

If `verify_manifest.py` and the archive disagree, the corpus is lying: treat that as a P0 for assurance. VANGUARD wrapper does not run; it is preserved damage, not a dependency.

### What works, and what shows it

Each line names the test, the CI job (`.github/workflows/tests.yml`: `pytest` on Python 3.11, 3.12 and 3.13, `consumers`, `baseline`, `wheel`) or the command that shows it. A line with no such pointer would be cut.

- **The verifier proves the key from the files.** `python3 verify_manifest.py --strict` exits 0 on a clean checkout and prints the summary line. CI runs it in every `pytest` job. `tests/test_verifier.py::test_clean_corpus_passes` runs it on a copy.
- **Tampering is caught.** `tests/test_verifier.py` copies the corpus and changes the prose, the machine block, the table, `registry.json`, a specimen, a README number, adds a file, adds a link or bytecode, and checks that each makes the run fail with a message naming the cause.
- **Specimens run in a sandbox that refuses what it says it refuses.** `tests/test_sandbox.py` covers writes outside the scratch folder, starting programs, network, credential and `/proc` reads, time and output limits, and a result file forged by a specimen. What it cannot stop is listed under "How the verifier runs specimens, and what it cannot stop".
- **A claim that cannot run fails the run.** Without numpy or matplotlib the verifier exits 1 and says the key is not proven (`tests/test_skips.py::test_default_run_without_numpy_fails_closed`).
- **The summary line means what section 4 says.** `tests/test_verifier.py::test_summary_line_is_machine_readable_and_matches_the_human_text` and `tests/test_summary_semantics.py` run the verifier and compare.
- **One version, read the same everywhere.** `tests/test_version_exposure.py` runs every documented version command. The `wheel` CI job builds the wheel, installs it in a fresh environment and checks the installed command.
- **ASSAY works without CNS.** `tests/test_cns_independence.py` runs the package and the verifier with CNS blocked.
- **The CNS gate.** `tests/test_cns_connector.py` and `tests/test_cns_assay_row.py` cover each outcome in the table in section 8. `tests/test_cns_assay_row.py::test_the_installed_cns_row_and_the_connector_agree_on_a_real_summary` feeds the verifier's real summary line to the installed CNS row. The `pytest` CI job installs the `cns` extra, so they run there.
- **Other tools can load the key.** The `consumers` CI job runs `tests/test_consumers.py` against SWIZZLE and WARDEN checked out at fixed commits and fails if any test is skipped. Those commits are the last set this repository's CI tested on its own. They are not the current heads of SWIZZLE or WARDEN. Whether the set that lands together works together is checked by the `stack` job in the CNS repository, not here.
- **The Ghost baseline is checked.** `.ghost_baseline.json` lists the Ghost findings this repository has agreed to stop seeing. The `baseline` CI job installs ghost_tools at a pinned commit and `tests/test_ghost_baseline.py` fails if an entry matches nothing or a finding is not in the baseline (apart from the folder-dependent ids named under "Known defects (open)").
- **The CI libraries are pinned.** `tests/test_ci_constraints.py` holds `ci-constraints.txt`, the README sentence about it and the workflow to each other.
- **Install hints name commands that work.** `tests/test_install_hints.py` fails if a document or hint in this repository tells a reader to install a bare name from this group of repositories.

**What "proven" means here, in plain words.** Every answer in the key is one of three kinds, and the verifier works out which kind by what it actually did on the run. Nobody types the kind in.

- *Verified by execution*: the verifier ran the specimen in a sandbox and saw it do what the verdict says.
- *Verified by static check*: the verdict is a fact about the file text (for example "these two files are the same code"), and the verifier compared the text. Nothing was run.
- *Unvalidated*: the verdict rests on a human judgement or on an outside measurement that this verifier does not repeat (for example the "faithful reconstruction" verdicts rest on a class-name coverage measurement made on 2026-09-07). The verifier only checks that the files exist, are still damaged as described, and have not changed. Each such entry in `registry.json` says why.

The numbers below are generated. If they ever disagree with what the verifier finds, verification fails.

<!-- ASSAY-STATUS:BEGIN (generated by `python3 -m assay_production.manifest_registry --write` and checked by `verify_manifest.py`; do not edit by hand) -->
**The answer key at a glance** (generated by the verifier's write command; `verify_manifest.py` fails if any number here drifts)

- Claims the verifier checks on every run: **60**.
- Specimens in the answer key: **27** (failure mode 7, reconstruction pair 6, reference 7, superseded 6, version progression 1).
- **11** are `VERIFIED_BY_EXECUTION`: the verifier ran the specimen in a sandbox and asserted the behaviour the verdict names.
- **3** are `VERIFIED_BY_STATIC_CHECK`: the verdict is a property of the file text and the verifier compared the text. Nothing was run.
- **13** are `UNVALIDATED`: the verdict rests on a human judgement or an outside measurement the verifier does not repeat. Each entry in `registry.json` says why.
- Files under `specimens/` whose SHA-256 is recorded and checked: **44**.
- Specimen files that import numpy: **3**; matplotlib: **1**.
- Unfinished-work markers (the word TO-DO in capitals) in the specimens, manifest and code: **0**.
<!-- ASSAY-STATUS:END -->

### What does not work, or is not proven

- **The sandbox is not a wall.** A specimen that gets past its Python-level guard (for example through `ctypes`), or that finds the report pipe in `/proc/self/fd`, can still write outside its folder or forge the facts for its own run. The details are under "How the verifier runs specimens, and what it cannot stop". No test claims otherwise.
- **The CNS gate runs the candidate's verifier with no sandbox.** A hostile checkout can print a passing summary and exit 0. Section 10 says so; the digest only detects a substituted verifier if the consumer already holds the digest it expects.
- **Unvalidated entries are not proven.** The entries marked `UNVALIDATED` in the status block rest on a human judgement or an outside measurement the verifier does not repeat. The verifier only checks that their files still exist, are still damaged as described and have not changed.
- **Only Linux, and only the three Pythons in CI, have ever been run.** CI is `ubuntu-latest` on Python 3.11, 3.12 and 3.13. The sandbox uses Linux features (`/proc`, `unshare`). Nothing has been run on macOS or Windows, so whether it works there is not known.
- **A local `pytest` without the optional pieces is not a full run.** The CNS tests skip where CNS is not installed, and `tests/test_consumers.py` skips where there is no SWIZZLE or WARDEN checkout. A skipped test proves nothing. Only the `consumers` CI job turns a skip into a failure. For a full local run, install the `cns` extra and point `SWIZZLE_ROOT` and `WARDEN_ROOT` at checkouts.
- **No known user outside the author's own repositories.** Nothing here has been used by anyone else, so how it behaves on other people's machines and workflows is untested.

### Known defects (open)

- `specimens/reference/sovereign_kernel.py` is listed as a working reference, but it loads five sibling files from its own folder and three of them live in `specimens/pairs/`. It cannot run where it sits. The verifier proves it by placing its siblings next to it in a scratch folder. The same is true of `specimens/pairs/sre_system_resilience_evaluator_adapter.py`, which needs `specimens/reference/resilience_stability_kernel.py` beside it. Nobody has changed the layout, because that would change the specimens.
- The sandbox is a safety net for accidents and careless code, not a wall. See the top of `assay_production/sandbox.py` for exactly what it blocks and what it cannot.
- If numpy or matplotlib is missing, the claims that need them are reported as `SKIP` instead of being counted as drift, but a skipped claim is not a proof: the verifier exits 1 and says the key is not proven (use `--allow-skips` to accept the gap knowingly, section 9). Install them with `pip install numpy matplotlib` to run every claim, normally, so that their own dependencies come with them (do not use `--no-deps`: matplotlib needs packages of its own, such as `packaging`, and without them a claim that imports it fails, with the missing module named in the message, for example `ModuleNotFoundError: No module named 'packaging'`, instead of being skipped); with both installed (and a SWIZZLE and a WARDEN checkout beside this one, or `SWIZZLE_ROOT` / `WARDEN_ROOT` set), `pytest` skips nothing. CI installs them with `pip install -c ci-constraints.txt numpy matplotlib`, which pins numpy 2.4.6 on Python 3.11, numpy 2.5.4 on Python 3.12 and later, and matplotlib 3.11.2, so that the number of claims that run cannot change because an upstream release did (`tests/test_ci_constraints.py` fails if that file, this sentence and the workflow disagree). The number of tests is deliberately not written here: it changes with every commit, and `tests/test_docs_claims.py` fails if this file quotes a pass count.
- `specimens/reference/agent-factory-tactical-agents.py` raises `KeyError: 'AGENT_000'` in `initialize_full_agent_array()` as written. That is a defect in the specimen. It is left as it is, because editing a specimen is a change to the answer key, and the claim for that specimen does not assert that function (CHANGELOG, 0.11.1).
- The full test suite is slow. It runs the verifier and the sandbox many times, and on the maintainer's machine a complete run takes a long time (run it in the background). The verifier alone takes seconds. CI runs the suite on three Pythons, so a push is not checked quickly.
- The name `cns` on PyPI belongs to an unrelated project. This repository only reaches CNS through the git URL in `pyproject.toml`, so the problem appears if someone installs CNS by that bare name.
- **The Ghost baseline cannot hold every finding.** Ghost 1.10.8 gave findings that share an id a short suffix that included the absolute path of the checkout, so the same finding had a different id in a different folder. A baseline entry with it would be stale everywhere except the folder it was built in, and Warden refuses a stale baseline. So `.ghost_baseline.json` holds none of those entries, and those findings (the repeated `except` handlers in `sandbox.py` and a few other repeated shapes) are reported in every Ghost run. That was a ghost_tools defect and it was fixed in ghost_tools 1.10.9 (folder-independent ids): the circuit's ghost_tools no longer has it. The baseline still omits the suffixed entries because this repository's `baseline` CI job tests Ghost 1.10.8, and a baseline built for the fixed Ghost would not match it.
- **Ghost's structure scan reports two findings that are not baselined.** With the structure scan on (Warden's options turn it off) Ghost says numpy and matplotlib are imported but declared nowhere. They are imported only by specimens, and ASSAY declares no dependency on purpose (see `pyproject.toml`). They are not baselined, because an entry for them would be stale under Warden's options.
- **The baseline accepts findings in files kept as they are.** Ghost's findings in `specimens/` and `recovered-originals/` (duplicates, dead code, unparsable files) are listed as accepted, because those files are damaged or copied on purpose and are not edited. Ghost's silence about them says nothing about their content.
- **A stray bytecode cache fails the run.** A `specimens/__pycache__` folder with a `.pyc` in it makes `verify_manifest.py` fail with reason `bytecode` (the `specimens.layout` claim, and the hash set). This is the documented design (section 4, "Integrity"), not an accident, but it means that importing a specimen with bytecode writing on, or letting a tool do it, breaks the run until the folder is deleted. Set `PYTHONDONTWRITEBYTECODE=1` when experimenting with specimens.

**How the verifier runs specimens, and what it cannot stop**

Every specimen that is run goes through `assay_production/sandbox.py`. In plain words:

- *Its own folders.* Each run gets a fresh private folder. The specimen works inside `work/` (its working directory, `HOME`, and a private temp folder `work/tmp` that `TMPDIR` points at). The harness, the request and the result live in `ctl/`, where the specimen may not write. Everything is deleted afterwards: on success, on timeout, on an error, on Ctrl-C, on SIGTERM or SIGHUP, and at exit. A verifier killed with SIGKILL cannot tidy up, but its children die with it and a later run removes the abandoned folder once it is 15 minutes old (the sweep's minimum age is 900 seconds, `min_age=900` in `sweep_abandoned`).
- *Stray writes are found by comparison, not by watching `/tmp`.* Before and after each run the verifier lists the specimen's own source folder, the sandbox's control folder and the top of the run folder, and reports anything new, removed or changed. Other programs creating files in `/tmp` (for example `warden-journal-*`) cannot affect the result. Residual limit: a hostile specimen that gets past the Python-level guard (for example through `ctypes`) and writes somewhere that is not one of those places, including the shared `/tmp`, is not seen.
- *A result cannot be forged by writing a file.* The specimen runs in a child of a small trusted harness. The harness keeps a random nonce the specimen never receives, collects the observed facts (names defined, exception raised, exit code) over a pipe, and is the only writer of the result. A file the specimen writes (including `__assay_result__.json`) is never read, a result without the nonce is refused, and a report that disagrees with the real process exit code is refused. A specimen that exits early (`os._exit(0)`) is reported as "ended without a report". Residual limit: a hostile specimen that finds the report pipe by listing `/proc/self/fd` and writes a well-formed report into it can still forge the facts for its own run. Closing that needs the specimen to run in a different container, virtual machine or user than the supervisor. Likewise a plain `print` of "ALL CHECKS PASSED" followed by exit 0 is believed by claims that look for that text, because that is all a script-mode claim can observe.
- *The caller's secrets stay out.* `verify_manifest.py` restarts itself once with a minimal environment (PATH, locale, HOME, TMPDIR, TERM, TZ and `ASSAY_*` only), marks itself non-dumpable and sets `no_new_privs`. The child gets a scrubbed environment, a new session, its own network and process-ID namespaces where `unshare` allows it (so the verifier's `/proc/<pid>` entries are invisible), and limits on CPU, memory, file size, open files and processes. The write guard also refuses reads of `/proc/<pid>/environ`, `mem`, `fd` and the usual credential files under the real home directory. Residual limits: the guard is a Python-level net that `ctypes` can bypass; reading other ordinary files on the machine is still possible; where the process-ID namespace is unavailable and the verifier runs as root, a specimen can still read other processes' memory. Run untrusted specimens in a disposable environment.
- *Output is capped.* At most `ASSAY_OUTPUT_CAP` bytes (default 1 MiB) of stdout and of stderr are kept; a specimen that prints more is killed and the failure says so.
- *Integrity.* The hash set covers every entry under `specimens/`, bytecode caches included. Symbolic links, special files and `.pyc` files fail the run (`specimens.layout`), and a specimen replaced by a link to identical content no longer matches its hash. Specimens are always compiled from their source text; an existing `.pyc` beside a specimen is never imported.

*Time limits.* Each run gets `ASSAY_CLAIM_TIMEOUT` seconds (an exact value when set). If it is not set, the default is 120 seconds, stretched up to four times when the machine's load average is above its CPU count. All runs together get `ASSAY_TOTAL_TIMEOUT` seconds (default 300). A value of `ASSAY_CLAIM_TIMEOUT`, `ASSAY_TOTAL_TIMEOUT` or `ASSAY_OUTPUT_CAP` that is not a positive number is ignored: a warning on stderr (logging module, once per run) names the variable and the default used instead, and stdout is unchanged. A run that runs out of either is reported as `timeout` and says which limit was hit and what the machine load was, so a slow machine is not mistaken for a changed specimen.

*Why a claim failed.* On failure the last line of stderr names the failing claims and the reason, for example `ASSAY: answer key NOT PROVEN (<passed>/<total> claims hold). claim fm3_4.critical_unreachable failed because timeout: timed out after 120s ...`. The printed report repeats it as a `Reason:` line under each failure. Reason codes: `timeout`, `stray_write`, `violation`, `output_overflow`, `child_died`, `forged_result`, `specimen_error`, `behaviour_changed`, `hash_mismatch`, `symlink`, `bytecode`, `unexpected_file`, `answer_key_drift`, `specimen_changed`, `claim_failed`.

**The summary line** (for SWIZZLE, Warden and other relays). Every run prints one line starting with `ASSAY-SUMMARY: ` followed by compact JSON, as the last line of stdout, whether the key is proven or not. The human text above it is unchanged. Exit codes are 0 proven, 1 not (a skipped claim counts as not proven unless `--allow-skips` is given; the line is printed either way, with `claims.skipped` and `all_claims_hold: false`). A command line the verifier does not understand exits 2 before anything is checked and prints no summary line (see section 9).

<!-- ASSAY-SUMMARY-EXAMPLE:BEGIN (generated by `python3 -m assay_production.manifest_registry --write` and checked by `verify_manifest.py`; do not edit by hand) -->
```text
ASSAY-SUMMARY: {"schema":"assay-summary/1","all_claims_hold":true,"status":"ANSWER_KEY_UNVALIDATED",
  "claims":{"total":60,"passed":60,"failed":0,"skipped":0},
  "entries":{"total":27,
             "counts":{"VERIFIED_BY_EXECUTION":11,"VERIFIED_BY_STATIC_CHECK":3,"UNVALIDATED":13},
             "status":{"<entry id>":"VERIFIED_BY_EXECUTION", "...":"..."}},
  "failures":[{"claim":"<claim id>","reason":"<reason code>","detail":"<text, at most 400 characters>"}]}
```
<!-- ASSAY-SUMMARY-EXAMPLE:END -->

**What `claims.total` counts.** `claims.total` is the number of claims that were run to a verdict, held or failed: `claims.passed` + `claims.failed` = `claims.total`, always. A claim that could not be run on this machine (numpy or matplotlib missing) is not run to a verdict, so it is counted in `claims.skipped` only and is not in `claims.total`. The number of claims the verifier made in the run is therefore `claims.total` + `claims.skipped`, which is the figure in the generated "Claims the verifier checks on every run" line above. With numpy missing the line says total 59 and skipped 1, passed 59 and failed 0: that is 60 claims made, 59 run and held, 1 not run, so `passed` + `skipped` is not `total`, and `all_claims_hold` is `false` because a claim that was not run proves nothing. A consumer must read `skipped` before it reads `total` or `passed`: `passed` equal to `total` says nothing about the claims that were left out of `total`. The shape `assay-summary/1` is unchanged by this description: the CNS gate checks that `passed` + `failed` = `total` and treats a non-zero `skipped` as a `RETRY`, and the `cns.assay` row carries `claims` through as it is.

The example above is generated from this checkout's real counts, and `verify_manifest.py` fails if its numbers drift. (The real line is a single line; it is wrapped here to read.) "N of M entries unvalidated" is `entries.counts.UNVALIDATED` of `entries.total`. `entries.status` gives the level of every entry. `all_claims_hold` says every claim that could be run held; it does not mean every entry is validated. When the key cannot be proven, `status` is `MANIFEST_INCONSISTENT` and `failures` lists each failing claim with its reason code.

## 5. Core Invariants & Guarantees

Independently-known answers. Manifest verification. Specimens must not be "fixed" into green code without updating the known-answer file (that would poison SWIZZLE).

**The rule: a specimen edit is a change to the answer key and must be reviewed.** Every file under `specimens/` has its SHA-256 recorded. Changing, adding or removing any of them makes `verify_manifest.py` fail and name the verdicts it can no longer prove. The only way to re-record is the deliberate command `python3 -m assay_production.manifest_registry --write`, which refuses to run unless every claim about the specimens still holds, and whose result (the MANIFEST.md block, `registry.json`, this README's status block) is reviewed like any other change to the answer key.

## 6. Inputs, Outputs & Type Contracts

Manifest records: specimen path, specimen class, expected verdict, MANIFEST section. Published as `assay_production/registry.json`; regenerate with `python3 -m assay_production.manifest_registry --write`.

The answer exists in four places that are checked against each other on every run: the prose of `MANIFEST.md`, a generated machine block at the end of `MANIFEST.md`, the table in `assay_production/manifest_registry.py`, and `registry.json`. A difference in any direction fails verification, so flipping a verdict in one place alone is caught.

Fields consumers already read (`specimen_id`, `specimen_class`, `path`, `expected_verdict`, `epistemic_status`, `isolation_required`, `metadata.companions`) are unchanged. Added fields: `sha256`, `companion_sha256`, `manifest_block_sha256`, `validation` (level, which claims were asserted, what was asserted, and the reason when unvalidated). `manifest_status` now carries the derived level instead of always saying unvalidated.

Run the tests with `python3 -m pytest tests -q`. They copy the corpus to a temporary folder, apply each known way of tampering with it, and check that verification fails with the right message.

## 7. Stack Integration Topology

```text
VANGUARD (retired) → specimens here
MANIFEST.md → assay_production/registry.json (generated; guarded by verify_manifest.py)
registry.json → swizzle assay → ghost_buster scored (also in ghost_tools CI)
registry.json → Warden AssayAdapter (and `warden tagteam --assay-root` or `--stack FOLDER`: Ghost is graded here before anything is written; see STACK.md)
```

**Reading ASSAY's version (for Warden and other relays).** The version is dynamic: `pyproject.toml` has no static `[project] version`, it reads `assay_production/_version.py`. A reader that parses `[project].version` out of `pyproject.toml` therefore finds nothing, by design (a run record that shows `versions.assay.version = null` is that, not a missing version). Read it from the package instead. This is the supported, stable way, and it works from a checkout or from an install:

```bash
python3 -c "import assay_production; print(assay_production.__version__)"
```

It prints exactly the version and a newline (for example `0.11.10`) on stdout, nothing on stderr, exits 0, needs no network, and has no other side effect (importing the package does not import CNS and does not run a specimen). From a checkout that is not installed, run it inside the checkout or set `PYTHONPATH` to it. The installed distribution carries the same string, and the commands print it too:

```bash
python3 -c "import importlib.metadata as m; print(m.version('assay'))"   # the installed distribution
assay-verify --version        # assay-verify 0.11.10   (also: assay-manifest, verify_manifest.py, python3 -m assay_production)
```

`tests/test_version_exposure.py` runs the commands above exactly as written here and fails if any of them disagrees with `assay_production/_version.py`.

## 8. Optional CNS connection

ASSAY does not need CNS. It has no runtime dependency, nothing in the package imports CNS when it loads, and the verifier and the sandbox never import it (`tests/test_cns_independence.py` checks all of this with CNS blocked). `assay_production/cns_connector.py` is the one place that knows CNS exists. ASSAY is not published on PyPI, so it cannot be installed by name (a package called assay there is not this project). From a checkout, install the extra with `pip install -e '.[cns]'`, or install just CNS with `pip install "cns @ git+https://github.com/wking53214/CNS.git@v2.2.0"`; without CNS, building a gate raises `CnsNotInstalled` and nothing else changes.

It offers one gate in CNS's shared gate contract (`cns.gate`), `AssayKeyGate`, which answers only ASSAY's own question: *is the answer key proven, before anyone grades against it?* It sits at the `ALPHA` end, because a key that is not proven means the grading never starts. What a refusal means for a whole run is the Judge's to decide, not this gate's.

```python
from assay_production.cns_connector import AssayKeyGate
result = AssayKeyGate().check("/path/to/ASSAY")      # a checkout, not a result
```

The candidate is the path of an ASSAY checkout. The gate runs that checkout's own `verify_manifest.py` as a subprocess, unsandboxed (section 10 says exactly what that means and what it does not protect) and reads the `ASSAY-SUMMARY` line together with the exit code. About 5 seconds on an idle machine (up to the 300 second total limit if it is busy).

| ASSAY says | CNS outcome | Why |
|---|---|---|
| every claim holds, none skipped (exit 0) | `PASS` | The key is proven. The reason says how many entries are still `UNVALIDATED`: PASS does not mean those were re-measured. |
| a claim failed: a changed specimen or hash, the four copies disagreeing, a tripped guard, any reason code not listed below | `TERMINAL_BREACH` | The key is not what was recorded. No retry repairs a changed key. |
| only claims that timed out | `RETRY` | A slow machine, not a changed specimen (the hash claims held). |
| a claim could not be run here (numpy or matplotlib missing) | `RETRY` | It was not measured, so nothing is proven. Install them normally, with their dependencies, and ask again. |
| the verifier crashed, was killed, could not be started, or ran out of time; or the key changed while it was being proven | `RETRY` | Nothing was measured. |
| a summary or exit code the gate does not recognise, or a summary a shared `cns.assay` row refuses, where the installed CNS has one (see below) | `TERMINAL_BREACH` | An unknown answer is never read as permission. |
| a candidate that is not a path, not an ASSAY checkout, or whose key cannot be read and hashed | `TERMINAL_BREACH`, unbound | Nothing can be proven about it. |

The verdict is bound with `cns.gate.subject_digest` to the key's real content, read with the verifier's own functions: the parsed `registry.json` (with the recorded SHA-256 of every specimen), the SHA-256 the verifier computes now for every file under `specimens/`, the hash of `MANIFEST.md`, and the hash of `verify_manifest.py` and the modules that prove the key. A PASS therefore cannot be moved onto a different key, and the same key at another path digests alike. This is tamper-evidence: a consumer compares the digest with the one it expects (`GateResult.binds`).

The `ASSAY-SUMMARY` line is read by the gate's own checks: the schema, the types of the documented fields, and counts that add up. The pinned CNS (v2.2.0, see below) ships a shared row for that line: `importlib.util.find_spec("cns.assay")` is not `None` there. A CNS that has no such row (v1.8.0 and earlier) is still supported: the gate then relies on its own reading alone. A CNS that ships `cns.assay.AssaySummary` is picked up without a code change: when the row is importable, the gate also passes every summary it has already accepted through it, and a summary the row refuses is a `TERMINAL_BREACH` that says so (ASSAY and CNS have drifted apart and neither is guessed at). The row is looked up only when a summary is read, so loading the package still never imports CNS. `tests/test_docs_claims.py` checks this paragraph against the CNS it is installed with.

**The CNS pin.** The `cns` extra is pinned to the tag `v2.2.0` (a lightweight tag, so the tag is the commit `ce6bd05578a7a3e3cafa0cfa1e9a2cca8a5f171f`, recorded in a comment beside the pin), spelled exactly as in the other seven repositories that pin it (the other four of the five-repository circuit and the three released from it), because CNS's `seat_pins` check compares the pin text across them and pip refuses one package at two different direct URLs. Migration note: the pin moved from `v1.9.0` to `v2.0.0` in ASSAY 0.11.5 (the tag then peeled to commit `b13e5d2f9e0e4291725f82794b89117c3d840ac1`), from `v2.0.0` to `v2.1.0` in ASSAY 0.11.7, and from `v2.1.0` to `v2.2.0` in ASSAY 0.11.8. ASSAY imports only `cns.gate` and `cns.assay`, and the connector and row tests pass against the installed 2.2.0 with no change to the connector's logic. To bump it, change the tag in `pyproject.toml` and update this paragraph (the test above fails if the two disagree), in all eight repositories together. CNS is a public repository: https://github.com/wking53214/CNS.

The connector tests (`tests/test_cns_connector.py`) skip where CNS is absent and run in CI, which installs the extra. `tests/test_cns_assay_row.py` covers the row with a stand-in, so it runs against any CNS, and against the real row where CNS has one.

## 9. Install, commands, exit codes, logging

ASSAY is not on PyPI, and the name `assay` there belongs to another project, so do not install it by name. Install from a checkout. These commands work as written from a fresh clone (they were run in a new virtual environment):

```bash
git clone https://github.com/wking53214/ASSAY.git
cd ASSAY
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
pip install -c ci-constraints.txt numpy matplotlib
python3 verify_manifest.py --strict
```

The last command should exit 0. Without the numpy and matplotlib line it exits 1 and says the key is not proven (section 4). Add `[cns]` to the extras (`pip install -e '.[dev,cns]'`) for the CNS gate in section 8. The rest of this section lists the commands and exit codes.

```bash
pip install -e .            # from a checkout; add [dev] for pytest, ruff and mypy, [cns] for the CNS gate
assay-verify                # the same as: python3 verify_manifest.py
assay-verify --strict       # the same as the default, kept for callers that pass it: a claim that could not be run is a failure
assay-verify --allow-skips  # the explicit opt-out: unrun claims are listed as SKIPPED, NOT PROVEN, and exit 0 if nothing else is wrong
assay-manifest              # print registry.json;  assay-manifest --write  re-records the key
assay-verify --version      # also: assay-manifest --version, verify_manifest.py --version
```

Before pushing, the same gates as CI: `ruff check . && mypy && python3 verify_manifest.py --strict && python3 -m pytest -q`. The ruff and mypy settings are in `pyproject.toml` with the reasons (the specimens are deliberately damaged files and are never linted; the line length is 120 because that is how the code is written).

The answer key is data in the repository (`specimens/` and `MANIFEST.md`) and is not part of the installed package. The installed commands therefore need a checkout: run them inside one, or pass `--root PATH` (or set `ASSAY_ROOT`). Without one they say so and exit 2. With an editable install (`pip install -e .`) the commands find the checkout the package sits in, so they work from any folder; a wheel install has no checkout and needs one of the three. `python3 verify_manifest.py` in a checkout works as before and takes no `--root`.

| Exit code | Meaning |
|---|---|
| 0 | The key is proven (`--write`: the key was re-recorded). With `--allow-skips`, also: no claim failed, and any claim that could not be run was listed as SKIPPED and NOT PROVEN. |
| 1 | The key is not proven: a claim failed, a claim could not be run here (numpy or matplotlib missing) and `--allow-skips` was not given, or the verifier itself failed (`--write`: it refused). |
| 2 | The command line was not understood. Nothing was checked and no summary line is printed. |

Arguments are parsed strictly and abbreviations are off, so a typo such as `--stirct` is an error (exit 2), never a quietly weaker check. `ASSAY_STRICT=1` (also `true`, `yes`, `on`; case does not matter) is the same as `--strict`, and `ASSAY_STRICT=0` (also `false`, `no`, `off`, or empty) is not, so it does not conflict with `--allow-skips`; any other value is a usage error (exit 2, nothing is checked). Failing on a skipped claim is the default (the verifier refuses when it is unsure); `--allow-skips` is the only opt-out, there is deliberately no environment variable for it, and combining it with `--strict`, `ASSAY_STRICT` or `--write` is an error (exit 2). A consumer that runs `verify_manifest.py` with no flags (SWIZZLE, the CNS gate) therefore gets exit 1 on a machine without numpy, and the gate reads the skip in the summary as `RETRY`.

Diagnostics use the standard `logging` module on **stderr**, at the level named by `ASSAY_LOG_LEVEL` (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`; case does not matter; default `WARNING`, which prints nothing on a normal run; an unknown value is reported once and ignored). They never touch stdout, so the report and the final `ASSAY-SUMMARY:` line are unchanged, and the last stderr line of a failed run is still the line that names the failing claims.

The version lives in one place, `assay_production/_version.py`; `pyproject.toml`, `assay_production.__version__` and every `--version` read it. Changes are listed in [CHANGELOG.md](CHANGELOG.md). Release tags are made by the owner, not by the code. Check the repository's tags and releases on GitHub for what exists; this README does not list them.

## 10. Security and limits

This section says exactly what is and is not isolated. Nothing here is a sandbox unless it says so.

- **Specimens are sandboxed, as far as section 4 describes.** Every specimen the verifier runs goes through `assay_production/sandbox.py`: a safety net for accidents and careless code, not a wall against hostile code.
- **The verifier's own code is trusted, and so is the checkout it runs.** `verify_manifest.py` and the `assay_production` modules it imports run unsandboxed, with the privileges of whoever runs them. `assay-verify --root PATH` uses the installed package's code against the data in `PATH`; the specimens in `PATH` are sandboxed, the code is not.
- **The CNS gate runs the candidate's own verifier, with no sandbox at all.** `AssayKeyGate().check(path)` starts `<path>/verify_manifest.py` in a subprocess with the same Python, in that folder. That script and the modules it imports come from the candidate checkout, so they are the candidate's code, running as the calling user with the caller's file system and network. What the gate does apply is limited to: a reduced environment (only `PATH`, locale, `HOME`, `TMPDIR`, `TERM`, `TZ` and `ASSAY_*` variables are passed, so the caller's secrets are not inherited), its own process group, no stdin, and a wall-clock timeout after which the group is killed. There is no container, no separate user, no resource limit on the gate's child, and no network isolation. A hostile candidate can therefore run arbitrary code as you, and can print a passing summary and exit 0 without proving anything.
- **What the digest does and does not give you.** The verdict is bound to the key's content and to the hashes of `verify_manifest.py` and the modules that prove the key (section 8). A consumer that holds the digest it expects detects a substituted verifier or a changed key. It does not make an untrusted candidate safe to run, and a PASS is only as trustworthy as the checkout you chose to point the gate at.
- **So:** point the gate only at a checkout you trust, or run the gate itself in a disposable container, virtual machine or separate user.
- **No network is needed or used** by the verifier, the connector or the tests, except that installing the `cns` extra fetches CNS from GitHub.

## 11. What Broke and How It Was Fixed

Newest first. Each entry says what was wrong, how it was found when that is known, the version that fixed it, and what now stops it coming back: a named test, or "no test yet". The sources are `CHANGELOG.md`, `git log` and, for the 0.11.4 CI failure, the recorded GitHub Actions run. Where a fix was incomplete or wrong, the entry says so. Open problems are in section 4, under "Known defects (open)".

**0.11.6**
- *The Ghost baseline went stale again.* `.ghost_baseline.json` had been rebuilt in 0.11.0, when 80 of its entries matched nothing. By 0.11.5 code had moved (lines in `sandbox.py`, `verification.py` and `manifest_registry.py`) and `recovered-originals/` had arrived, so 34 of its 104 entries matched nothing and many findings were not in it. Warden refuses a run with a stale baseline, and the circuit's self-hosting run on 0.11.5 ended REJECT for that reason alone (section 12). Found by the round-6 independent audit on 2026-10-23 and 2026-10-24, and reproduced with ghost_tools 1.10.8. Fixed in 0.11.6: the baseline was rebuilt after reading every finding (the commit message of Step 1 lists the categories), and a CI job, `baseline`, now fails if it goes stale. Guard: `tests/test_ghost_baseline.py` and the `baseline` CI job.
- *The 0.11.0 fix did not last, and did not say how to keep it.* Nothing compared the baseline with a fresh scan, so the next edit that moved lines made entries stale without any test failing. Guard: the same test.

**0.11.4**
- *CI libraries floated.* numpy and matplotlib were installed unpinned, so the number of claims that ran could change with an upstream release. Fixed with `ci-constraints.txt`, passed with `-c` by every CI install. Guard: `tests/test_ci_constraints.py`.
- *Install hints named a package that does not exist.* The connector's message and the README told users to install the bare name `assay[cns]`. ASSAY is not on PyPI, so that fails or installs someone else's package. Now they name a checkout install or the git URL. Guard: `tests/test_install_hints.py`.
- *`claims.total` was undocumented.* It counts the claims run to a verdict, so a skipped claim is in `claims.skipped` only. A reader could take `passed` equal to `total` as everything proven. Only the README changed; the behaviour did not. Guard: `tests/test_summary_semantics.py`.
- *The main branch failed CI after a merge.* Merging `recovered-originals/` (three modules copied unchanged from an archived repository) made `ruff check .` fail, and the `pytest` jobs stopped at that step (GitHub Actions run 39795356360, commit 18a527a). The directory is now excluded from ruff, the way `specimens/` is, so those files are not linted. Guard: the ruff step in CI; no other test.

**0.11.3**
- *The README gave an install that breaks claims.* Installing numpy and matplotlib with `--no-deps` leaves matplotlib without packages it needs, such as `packaging`. The claim that imports it then fails with `ModuleNotFoundError: No module named 'packaging'`, and the claims that compare the recorded status and the README with that result fail with it. The README now says to install them normally. No code changed. No test yet for that sentence.
- *The connector accepted two summary shapes the real CNS row refuses.* A blank `status`, and an `entries` that is present but not an object. With a CNS that has `cns.assay` installed, both are now `TERMINAL_BREACH` (before, a timeout-only summary with a blank status was a `RETRY`). The verifier never writes either shape. Guard: `tests/test_cns_assay_row.py::test_the_installed_row_refuses_what_the_connector_alone_would_let_through`.
- *Text said the pinned CNS had no `cns.assay` row after the pin moved to a CNS that has one.* README, `STACK.md` and comments corrected. Guard: `tests/test_docs_claims.py::test_readme_claim_about_the_cns_assay_row_matches_the_installed_cns`.

**0.11.2**
- *The 0.11.1 fix for `ref.agent_factory.runs` was not enough.* It checked the Citadel line for one config value only, so a specimen that returned the fixed string `CITADEL: Layer 7 secured.` still passed, and `--write` re-recorded it. The claim now spawns a second Citadel with priority 3 and requires that agent's own line. Guard: the `mutate_hardcode_priority` case in `tests/test_agent_factory_claim.py::test_a_replaced_specimen_fails_the_claim`.
- *`ASSAY_STRICT=0` counted as strict.* Any non-empty value did, so `ASSAY_STRICT=0 --allow-skips` exited 2. Now `1`, `true`, `yes`, `on` mean strict, `0`, `false`, `no`, `off` and empty mean not, and anything else is a usage error. Guard: `tests/test_skips.py::test_strict_from_environment_parses_every_documented_spelling` and the tests beside it.
- *Bad time or size settings were ignored silently.* A bad `ASSAY_CLAIM_TIMEOUT`, `ASSAY_TOTAL_TIMEOUT` or `ASSAY_OUTPUT_CAP` fell back to the default with no message, and `inf` was accepted as a timeout and broke the output cap. Now each warns once on stderr and `inf` counts as invalid. Guard: `tests/test_sandbox.py::test_an_invalid_number_in_the_environment_warns_once_and_names_the_default` and `tests/test_cli.py::test_an_invalid_time_or_output_setting_warns_once_on_stderr_and_leaves_stdout_alone`.
- *A bad `ASSAY_LOG_LEVEL` warned twice,* once in the verifier and once in its restarted copy. Guard: `tests/test_cli.py::test_a_bad_log_level_is_reported_once_not_once_per_process`.

**0.11.1**
- *A claim that could not run still exited 0.* Only `--strict` failed on it, so a bare run without numpy exited 0 with one claim skipped. Now the default fails closed (exit 1, "NOT PROVEN") and `--allow-skips` is the loud opt-out. Callers that ran the verifier with no flags on a machine without numpy now see exit 1. Guard: `tests/test_skips.py::test_default_run_without_numpy_fails_closed`.
- *`ref.agent_factory.runs` checked almost nothing.* It only asserted that the specimen ran and exited 0, so an independent audit replaced the specimen with `raise SystemExit(0)` and re-recording accepted it. The claim now checks the specimen's behaviour. This fix was itself incomplete; see 0.11.2. Guard: `tests/test_agent_factory_claim.py`.
- *The tag wording was wrong.* The README and CHANGELOG said or implied that no tag existed, when an older `v0.10.0` tag does. The README now makes no claim about tags (section 13). No test for the README side.
- *`CRITICAL` was missing from the documented log levels* in the README, the `--help` text and a module comment, though the code accepted it. Guard: `tests/test_docs_claims.py::test_readme_log_levels_equal_the_accepted_set` and `test_log_levels_in_help_and_module_docs_match_the_accepted_set`.
- *The documented install left untracked files* because `.gitignore` lacked `*.egg-info/`, `build/` and `dist/`. Guard: `tests/test_docs_claims.py::test_gitignore_covers_what_the_documented_install_leaves_behind`.

**0.11.0**
- *A mistyped flag ran a weaker check.* `verify_manifest.py --stirct` was ignored and the non-strict check ran. Arguments are now parsed strictly: an unknown one exits 2 and checks nothing. Guard: `tests/test_cli.py::test_verify_manifest_rejects_a_mistyped_flag`.
- *The README stated things that were not true.* A passing-test count, a summary example and a description of the CNS behaviour were wrong, and `STACK.md` called the public CNS repository private. The README counts are now generated and checked by the verifier, and the README may not quote a pass count. Guard: `tests/test_verifier.py::test_readme_numbers_cannot_drift`, `tests/test_docs_claims.py::test_readme_does_not_quote_a_test_count` and `test_stack_doc_does_not_call_the_public_cns_repository_private`.
- *The Ghost baseline was stale.* 80 baseline entries matched nothing after Ghost's identity keys changed, which made Warden refuse the folder (commit 22d7ea1, listed under 0.11.0 in the CHANGELOG). The baseline was rebuilt. No test at the time; the 0.11.6 baseline test (`tests/test_ghost_baseline.py`, see 0.11.6 above) guards it since.

**0.10.0 and before**
- *The README claims and the consumer tests were wrong (0.10.0, #18).* Specimen paths and the numpy/matplotlib note did not match the code, and two consumer tests were being skipped because the sibling checkouts were only found through environment variables. Both were fixed. Guard: the `consumers` CI job fails on any skip (added in #21).
- *The key was trusted, not checked (0.10.0, #16).* The verifier did not prove the answer key. Since this change every claim is run, the four copies are compared and every file under `specimens/` has a recorded SHA-256. Guard: `tests/test_verifier.py`.
- *Two of five "faithful" verdicts were wrong (2026-09-07, #8), and the correction was wrong too (#9).* The reconstruction verdicts were inherited prose that nobody had measured. A class-name coverage measurement showed two were lossy. A second change (#9) found that the worst case, solvar, had been paired with the wrong reconstruction and nothing had been lost; the pair was corrected. Those verdicts are still a one-off measurement, so they are recorded as `UNVALIDATED`. No test repeats the measurement.

## 12. Self-Hosting

Roster note: this section is the dated record of the old eight-repository circuit. The circuit is now five repositories (ghost_tools, SWIZZLE, ASSAY, JUDGE and WARDEN); DRAFTER, BURNISH and WATCHER_MCU are released from the circuit by owner ruling (2026-10-29). ASSAY is not released: it stays an instrument that grades the scanner.

The circuit as it was then (Warden with the Drafter, Judge and Burnish seats) was run over a fresh clone of each of its eight repositories. The record is `docs/evidence/SELFHOSTING_2026-10-23.md` in the CNS repository (https://github.com/wking53214/CNS), on the branch `claude/horsemen-production-status-5wsndb` until that branch is merged.

For ASSAY (commit `184679c06e0a636a9a08a8403efa410b375c9429`, version 0.11.5) the record holds one run, and its decision is REJECT. The reason it gives: Ghost reported that 34 of the 104 entries in the committed `.ghost_baseline.json` matched nothing in the scan, and Warden refuses a run whose baseline is stale. Because of that refusal the target's suite, the Drafter and the finisher never ran, so the record says nothing about ASSAY's own suite under Warden. It lists 7 declined checks (mutate, kernel, structure, tests, project, secrets, correlate), 12 gaps in all, and 89 Ghost findings still reported. The cause is in this repository: the baseline was out of date with the code. It is fixed in 0.11.6 (section 11).

What the record does not mean. It does not cover 0.11.6: no circuit run has been made on the fixed commit, and this README states no result for one. For the repositories where the circuit said ACCEPT, the ACCEPT came with the same 7 declined checks counted as gaps; it does not mean there are no secrets or weak tests, and it does not mean Ghost found nothing. A REJECT for a stale baseline says nothing about whether the specimens or the verifier are sound.

## 13. Ceilings Code Cannot Fix

- The repository is young. Its history starts in August 2026.
- It has one human maintainer, and most commits were written with an AI assistant (the commit trailers say so).
- It has no known outside users.
- Releases are tagged by the owner, not by the code. Check the repository's tags and releases on GitHub for what exists.

Apache License 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE). Copyright 2026 William N. King.
