# Changelog

All notable changes to ASSAY are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org/). The version is written once, in
`assay_production/_version.py`.

Release tags are made by the repository owner. An older `v0.10.0` tag exists. It
dates from the earlier numbering (it points at the end of the work listed under
0.10.0 below, before the package had a version file) and does not correspond to
the version of this package. Releases of 0.11.x are not tagged yet; tagging is
the owner's decision.

## [0.11.8] - 2026-10-30

Not tagged. The CNS pin moves to the `v2.2.0` tag. One commit per step.

### Changed
- Pin22 step 1. The `cns` extra is pinned to `cns @ git+https://github.com/wking53214/CNS.git@v2.2.0`, with the comment
  `# v2.2.0 = ce6bd05578a7a3e3cafa0cfa1e9a2cca8a5f171f` (a lightweight tag, so the tag is the commit), from the `v2.1.0`
  tag. The `cns` package at v2.2.0 equals v2.1.0 except its version string. The README pin paragraph and the sentence
  about the `cns.assay` row, `STACK.md`, the connector docstring and the install hint in
  `assay_production/cns_connector.py` carry the same spelling. The `consumers` pins (SWIZZLE, WARDEN) and the
  ghost_tools pin are unchanged. Pre-existing tests edited under the exact-behaviour rule, each asserting the old pin
  text and nothing else changed: `tests/test_packaging.py` (the pinned spec, the comment line, and
  `test_the_cns_extra_is_pinned_to_the_v2_1_0_tag`, renamed `..._v2_2_0_tag`), `tests/test_install_hints.py`
  (`CNS_SPEC` and one install string), `tests/test_docs_claims.py`
  (`test_readme_claim_about_the_cns_assay_row_matches_the_installed_cns`: the installed version it runs against is 2.2.0)
  and the docstring of `tests/test_cns_assay_row.py`.
- Pin22 step 2. Version 0.11.8 in `assay_production/_version.py` and the two README examples that show the version,
  and this entry.
- A Warden run that governs a tree carries eight declined checks (mutate, kernel, structure, tests, project, secrets,
  correlate, ledger), not seven, because ghost_tools 1.10.11 lists the ledger as declined under `--no-ledger`. The
  README section 12 quotes the 2026-10-23 self-hosting record, which had seven; that record is unchanged.

## [0.11.7] - 2026-10-29

Not tagged. The CNS pin moves to the `v2.1.0` tag. One commit per step.

### Changed
- Pin21 step 1. The `cns` extra is pinned to `cns @ git+https://github.com/wking53214/CNS.git@v2.1.0`, with the comment
  `# v2.1.0 = fde931ffa89aebec95647742256ad53033bd3d02` (the commit the annotated tag peels to; the tag object is
  `0cc90472f7edc46c3bf40079e69fb03a06718e29`), from the `v2.0.0` tag. The README pin paragraph and the sentence about
  the `cns.assay` row, `STACK.md`, the connector docstring and the install hint in `assay_production/cns_connector.py`
  carry the same spelling. The `consumers` pins (SWIZZLE, WARDEN) and the ghost_tools pin are unchanged. ruff, mypy and
  `verify_manifest.py --strict` are clean against the installed CNS 2.1.0, and the suite passed with no skip other
  than the one that needs ghost_tools, which the CI `baseline` job installs. Pre-existing tests edited under the
  exact-behaviour rule, each asserting the old pin text and nothing else changed: `tests/test_packaging.py` (the pinned
  spec, the comment line, and `test_the_cns_extra_is_pinned_to_the_v2_0_0_tag`, renamed `..._v2_1_0_tag`),
  `tests/test_install_hints.py` (`CNS_SPEC` and one install string), `tests/test_docs_claims.py`
  (`test_readme_claim_about_the_cns_assay_row_matches_the_installed_cns` now runs against 2.1.0 instead of skipping)
  and the docstring of `tests/test_cns_assay_row.py`.
- Pin21 step 2. Version 0.11.7 in `assay_production/_version.py` and the two README examples that show the version,
  and this entry.

## [0.11.6] - 2026-10-24

The committed Ghost baseline is rebuilt and guarded, and the README says what the self-hosting record holds.

### Changed
- Step 1. `.ghost_baseline.json` was stale. With ghost_tools 5a9154d (1.10.8), `ghost-buster . --no-tests --no-branches
  --single-repo --no-ledger --baseline .ghost_baseline.json` reported 34 of 104 entries matching nothing, 61 new findings,
  70 suppressed, exit 1, and the circuit rejected ASSAY for it. Every finding was read. 44 of the new findings are the
  same findings as 44 stale entries under new ids (code moved lines); 27 are in or about `recovered-originals/`, kept
  byte for byte; 2 are new in product code and accepted knowingly (`cns_connector.py` name_disagreement, `registry_checks`
  long_function); 4 stale entries have no replacement because the code changed. The file was rebuilt from scratch with
  the options Warden uses (plus no branches). The entries whose id carries Ghost's place suffix were left out, because
  that suffix includes the absolute checkout path (15 of 17 differ between two folders), so such an entry is stale in
  every other folder; those findings stay reported. Result with Warden's options, at two folders: 0 stale. With the
  command above: 0 stale and 2 new structure findings (undeclared numpy and matplotlib), exit 1; they are not baselined
  because they would be stale under Warden's options. No test needed an edit.
- Step 2. New CI job `baseline` installs ghost_tools at `5a9154d3c76670f5bf1f46d845acadfed46d7bc8` and runs the new
  `tests/test_ghost_baseline.py`, failing on any skip. The test compares a fresh Ghost scan with the baseline in both
  directions and requires the baseline to hold no folder-dependent id. It skips only where ghost_tools is absent, and
  `ASSAY_REQUIRE_GHOST_BASELINE=1` makes that a failure. Shown to fail on a removed entry, an added suffixed entry and a
  new finding.
- Step 3. README: the stale-baseline item in the ledger; four open defects (folder-dependent ids, the two structure
  findings, accepted findings in kept files, a stray `specimens/__pycache__` failing the run); the `consumers` pins
  described as the last set this repository's CI tested, not the heads of SWIZZLE and WARDEN (same in the workflow
  comments, where the "commits after tag" notes are gone); and the self-hosting section now states what the CNS record
  holds for ASSAY (REJECT at 0.11.5 for the stale baseline) and what it does not mean. `tests/test_readme_ledger.py` holds
  those numbers and now knows the `baseline` job. No existing test needed an edit.
- Step 4. Version 0.11.6, and this entry.

## [0.11.5] - 2026-10-22

The CNS pin moves to the v2.0.0 tag, and the README is rewritten to say plainly what works, what does not and what broke.

### Changed
- Step 1. The `cns` extra is pinned to `cns @ git+https://github.com/wking53214/CNS.git@v2.0.0`, with the comment
  `# v2.0.0 = b13e5d2f9e0e4291725f82794b89117c3d840ac1` (the commit the annotated tag peels to), spelled as in the
  other circuit repositories. The README, `STACK.md`, the `pyproject.toml` comments, the connector docstring and
  `INSTALL_HINT` name the new tag. Entries below about earlier releases are left as written. Against the installed
  cns 2.0.0 the verifier's real summary line is accepted by `cns.assay.AssaySummary`, and the connector, row,
  independence, docs, install-hint, packaging and consumer tests pass with no skips (SWIZZLE
  `522658415b026ac3211d3fc130ba7da7c77cc400` and WARDEN `380894f0304ef40587dd29efd41b4ceccf94a5d3`, the refs the
  `consumers` job already uses and still uses). Tests edited because they assert the pin spelling:
  `tests/test_packaging.py` (the pinned spec, and the test is renamed `test_the_cns_extra_is_pinned_to_the_v2_0_0_tag`),
  `tests/test_install_hints.py` (the spec), `tests/test_docs_claims.py` (the CNS version the row test runs against, so
  it does not skip) and the docstring of `tests/test_cns_assay_row.py`. Added
  `test_the_cns_pin_comment_names_the_commit_the_tag_peels_to`.
- Step 2. README: a short "What This Is"; a list of what works with the test, CI job or command that shows it; what
  does not work or is not proven; open known defects; install commands run in a fresh virtual environment; and new
  sections "What Broke and How It Was Fixed" (checked against this file, `git log` and the recorded CI run of the failing
  main commit), "Self-Hosting" and "Ceilings Code Cannot Fix". The README no longer says whether a release tag
  exists. No code changed. New `tests/test_readme_ledger.py` holds the README to the repository: the tests and CI jobs it
  names exist, the versions in the ledger are headings in this file, the required sections are present, and no
  marketing words. One test edited because it asserted the sentence this step removes:
  `tests/test_packaging.py::test_the_tagging_statement_is_true_and_the_same_in_both_documents` no longer requires the
  README to say a `v0.10.0` tag exists; the half that checks this file is unchanged.
- Step 3. Version 0.11.5, and this entry.

## [0.11.4] - 2026-10-22 (not yet tagged)

Newer tested siblings, install hints that work, pinned CI libraries, and the meaning of `claims.total` written down.

### Changed
- Step 1. CI: the `consumers` job now checks out SWIZZLE 0.8.5 (`522658415b026ac3211d3fc130ba7da7c77cc400`, current
  SWIZZLE main) instead of 0.8.4 (`6bd88f3a6e9de1f83e64f401e13cbcb5233499fc`), and WARDEN 0.13.8
  (`380894f0304ef40587dd29efd41b4ceccf94a5d3`, not tagged, 29 commits after tag `v0.12.0`) instead of 0.13.7
  (`1636e1a21f124eedbf6e158db95dc75344f4308d`). The CNS pin stays at the tag `@v1.9.0`. The job still fails on any
  skip. `tests/test_consumers.py` passes (9 passed, 0 skipped) against clean clones of exactly those commits. No test
  needed an edit.
- Step 2. Install hints: `assay_production/cns_connector.py` (its docstring and `INSTALL_HINT`, which
  `CnsNotInstalled` prints) and the README told users to install the bare `assay[cns]` name. ASSAY is not published on
  PyPI, so that fails, or installs a different package of the same name. They now say `pip install -e '.[cns]'` from a
  checkout, or, for just CNS, `pip install "cns @ git+https://github.com/wking53214/CNS.git@v1.9.0"` (the spec of the
  `cns` extra). Two tests asserted the old hint text and now assert the new one, nothing else about them changed:
  `test_the_connector_says_what_is_missing_when_cns_is_blocked` in `tests/test_cns_independence.py` and
  `test_building_a_gate_without_cns_names_the_extra` in `tests/test_cns_connector.py`. New
  `tests/test_install_hints.py` fails if a user-facing document, the workflow or the package tells users to
  `pip install` a bare name from this stack, and holds the hint to the pyproject spec.
- Step 3. CI: numpy and matplotlib were installed unpinned, so the number of claims that run could change with an
  upstream release. `ci-constraints.txt` (numpy 2.4.6 below Python 3.12, numpy 2.5.4 from 3.12, matplotlib 3.11.2) is
  now passed with `-c` by every CI install of them (the pytest job, the consumers job and both installs in the wheel
  job), and the README states the same versions. `tests/test_ci_constraints.py` holds the file to the README, requires
  `-c` on every such install in the workflow, and in GitHub Actions checks the installed versions. With the constraints
  installed together with their dependencies, the verifier proves 60 of 60 claims, none skipped, on Python 3.11, 3.12
  and 3.13.
- Step 4. README: the summary-line section now says what `claims.total` counts. It is the number of claims run to a
  verdict (held or failed), so `passed` + `failed` = `total`; a skipped claim is counted in `skipped` only, so the claims
  made are `total` + `skipped`, and with numpy missing the line reads total 59, passed 59, skipped 1 (60 made). No code
  and no row shape changed (`assay-summary/1`; the CNS gate and its `cns.assay` row read the same fields).
  `tests/test_summary_semantics.py` holds the text to real runs.
- Step 5. Version 0.11.4, and this entry.

### Merged from main
- `recovered-originals/` (three modules preserved from an archived repository, copied unchanged) came in with main.
  `ruff check .` reported errors in those files, so `pyproject.toml` excludes the directory from ruff, as it does
  `specimens/`. The files are not edited, and the verifier does not check them.

## [0.11.3] - 2026-10-21 (not yet tagged)

The tested sibling set moved again, and the README names a dependency trap.

### Changed
- Step 1. CI: the `consumers` job now checks out SWIZZLE 0.8.4 (`6bd88f3a6e9de1f83e64f401e13cbcb5233499fc`) instead of
  0.8.1 (`8166c47f321ecfb66b8efa72c1deac5d954e8e48`), and WARDEN 0.13.7 (`1636e1a21f124eedbf6e158db95dc75344f4308d`,
  22 commits after tag `v0.12.0`) instead of 0.13.4 (`36e98433f4928b7d12905f02b56e55ee1943b56e`). The CNS pin stays at
  the tag `@v1.9.0`. The job still fails on any skip. `tests/test_consumers.py` passes (9 passed, 0 skipped) against
  clean clones of exactly those commits. No test needed an edit.
- Step 2. README: where it says to install numpy and matplotlib, it now says to install them normally, with their
  dependencies. Installing them with `--no-deps` leaves 56 of 60 claims proven, because matplotlib needs packages of
  its own such as `packaging`. The failing claim already names the missing module in its message
  (`ModuleNotFoundError: No module named 'packaging'`), so no code changed, and no claim semantics changed.
- Step 3. Version 0.11.3, and this entry.

### Already on main since 0.11.2
- The optional `cns` extra moves from CNS v1.8.0 (`5252ceebe98185f7be81212d988055ccf9884568`) to CNS v1.9.0, pinned
  to the tag `@v1.9.0`, as the seven circuit repositories move to CNS 1.9.0 together. The pin is the tag, spelled
  as in the other six, so CNS's `seat_pins` check sees identical text. CNS 1.9.0 ships the shared `cns.assay` row that 1.8.0 lacked, so
  with the extra installed the gate now passes every summary through `cns.assay.AssaySummary`; the README, `STACK.md`,
  the `pyproject.toml` comments and the `cns_connector` docstring no longer say the pinned CNS has no such row. A CNS
  without the row is still supported. The verifier's real summary is accepted by the row. Two shapes the connector's
  own checks let through, and the real row refuses, are now a `TERMINAL_BREACH` where the row is installed: a blank or
  empty `status`, and an `entries` that is present but not an object. Before, a timeout-only summary with a blank
  `status` was a `RETRY`; now it is a `TERMINAL_BREACH`. The verifier never writes either shape.
- CI: the `consumers` job now checks out WARDEN 0.13.4 (`36e98433f4928b7d12905f02b56e55ee1943b56e`, 18 commits after
  tag `v0.11.4`) instead of 0.13.3 (`580f659336818b4a5a2c0ca235d2344012536426`). SWIZZLE stays at 0.8.1
  (`8166c47f321ecfb66b8efa72c1deac5d954e8e48`). Warden 0.13.4 reads ASSAY's version statically and requires
  instrument roots to be git checkouts. Superseded by step 1 below.

## [0.11.2] - 2026-10-21 (not yet tagged)

Small findings from the third audit round, and the tested sibling set moved.

### Changed
- CI: the `consumers` job now checks out SWIZZLE 0.8.1 (`8166c47f321ecfb66b8efa72c1deac5d954e8e48`, 22 commits after
  its older `v0.10.0` tag) and WARDEN 0.13.3 (`580f659336818b4a5a2c0ca235d2344012536426`, 16 commits after tag
  `v0.11.4`). `tests/test_consumers.py` passes (9 passed, 0 skipped) against clean clones of exactly those commits,
  and against the previous SWIZZLE commit `123d7aba5d91896b6c9b381c8b0de4c89365ab81` too. Warden 0.13.2 and later
  reads ASSAY's dynamic version statically, so its run record carries the real ASSAY version instead of `null`.
- BEHAVIOR CHANGE: `ASSAY_STRICT` is parsed. `1`, `true`, `yes`, `on` (any case) mean strict; `0`, `false`, `no`,
  `off` and empty mean not strict; any other value is a usage error (exit 2, nothing is checked, a message names the
  variable). Before, any non-empty value, `0` included, counted as strict, so `ASSAY_STRICT=0 --allow-skips` exited 2.
  `--strict` and `ASSAY_STRICT=1` keep their meaning.
- An invalid `ASSAY_CLAIM_TIMEOUT`, `ASSAY_TOTAL_TIMEOUT` or `ASSAY_OUTPUT_CAP` (not a number, zero, negative, `nan`
  or `inf`) is still ignored in favour of the default, but no longer silently: one warning per variable and run on
  stderr, through the `logging` module, names the variable, the value and the default used. stdout is untouched.
  (`inf` used to be accepted as a timeout and broke `ASSAY_OUTPUT_CAP`; it now counts as invalid.)
- `tests/test_packaging.py::test_changelog_leads_with_the_current_version` accepts an `[Unreleased]` heading above the
  current version, as Keep a Changelog prescribes; the rest of that test is unchanged.

### Added
- `tests/test_version_exposure.py::test_version_file_stays_a_single_plain_string_literal_assignment`: fails if
  `assay_production/_version.py` stops being one top-level `__version__ = "literal"` assignment, or pyproject stops
  pointing at it. That is the contract Warden relies on to read the version without importing ASSAY.

### Fixed
- `ref.agent_factory.runs` checked the Citadel line for one config value only (priority 7), so a specimen that
  returned the fixed string `CITADEL: Layer 7 secured.` passed, and `--write` re-recorded it. The probe now spawns a
  second Citadel with priority 3 and the claim requires `CITADEL: Layer 3 secured.` and that agent's config kept. The
  claim's assertions are defined in code (`AGENT_FACTORY_FACTS` in `verification.py`, probe in `sandbox.py`), not in
  the answer key; the key records only the claim's description. Re-recorded with `manifest_registry --write`: only
  that description text changed in `registry.json`; no specimen and no hash. A new mutant in
  `tests/test_agent_factory_claim.py` (the hard-coded string) fails the verifier and is refused by `--write`.
- A bad `ASSAY_LOG_LEVEL` printed its warning twice, once in the verifier and once in the copy it restarts with a
  minimal environment. It is printed once now (the restarted copy is told by `ASSAY_RELAUNCHED=1`, which it removes
  from its environment at once).

## [0.11.1] - 2026-10-17 (not yet tagged)

Cleanup after an independent audit of 0.11.0.

### Changed
- BEHAVIOR CHANGE, fail closed: a claim that could not be run (numpy or matplotlib missing) now fails the run by
  default (exit 1, `NOT PROVEN` on stderr, `SKIP` lines and the skipped claim ids in the report). Before, only
  `--strict` did that and a bare run exited 0 with one skipped claim (`ref.solvar_cleanup.runs`). The new explicit
  opt-out is `--allow-skips`: it prints a `WARNING` naming each skipped claim as SKIPPED and NOT PROVEN, reports that
  the key is not fully proven, exits 0 only if nothing failed, and still prints the `ASSAY-SUMMARY:` last line
  (`claims.skipped`, `all_claims_hold: false`). `--strict` and `ASSAY_STRICT=1` keep their meaning (now the same as
  the default); `--allow-skips` with either, or with `--write`, exits 2. Exit codes 0/1/2 and the summary schema
  are unchanged. Callers that ran the verifier with no flags on a machine without numpy (SWIZZLE; the CNS gate,
  which maps a skipped claim to `RETRY`) now see exit 1 there.
- CI: every GitHub Action is pinned by full commit SHA with its tag in a comment (`actions/checkout` v4.2.2,
  `actions/setup-python` v5.6.0), and a test guards it.
- CI: the `consumers` job checks SWIZZLE and WARDEN out at the tested set (full SHAs). The comments say what is
  true of each commit: its own version file, and how far it is past that repository's last tag.

### Added
- README, section 7: how another process reads ASSAY's version (`python3 -c "import assay_production; print(assay_production.__version__)"`),
  with the reason a reader of `pyproject.toml` gets none (the version is dynamic, by design), and a test that runs
  the documented commands. Warden's run record showed `versions.assay.version = null` for that reason; Warden is
  not changed here.
- CI, `wheel` job: the installed distribution metadata and `assay_production.__version__` must agree.

### Fixed
- `ref.agent_factory.runs` only asserted that the specimen ran and exited 0, so an auditor replaced it with
  `raise SystemExit(0)` and re-recording accepted it. The claim now loads the specimen in the sandbox and requires
  its documented behaviour: the registry holds exactly `CITADEL` and `DESTROYER`, the factory spawns the matching
  subclasses with the config it was given, each executes to its exact output line, the base class refuses to
  execute, and an unregistered name raises `KeyError`. Re-recorded with `manifest_registry --write` (only the
  recorded description of the assertion changed; no specimen and no hash). Mutation tests show a bare
  `SystemExit(0)`, an empty file, a print-only file, a changed output line, a removed registration and a base class
  that no longer refuses all fail the verifier and are refused by `--write`. Not asserted, on purpose:
  `initialize_full_agent_array()` raises `KeyError: 'AGENT_000'` as written (a defect in the specimen, left
  untouched because editing a specimen is a change to the answer key).
- `.gitignore` now lists `*.egg-info/`, `build/` and `dist/`, so the documented `pip install -e .` and a wheel build
  leave no untracked files.
- README, the `--help` epilog and `runtime.py` listed `ASSAY_LOG_LEVEL` values without `CRITICAL`, which
  `runtime.py` has always accepted. A test now compares the README list with the accepted set.
- The tag wording in this file and in the README: it said or implied that no tag exists. An older `v0.10.0` tag
  exists and matches no current version; tagging 0.11.x is the owner's decision.

## [0.11.0] - 2026-10-17 (not yet tagged)

Covers everything after the `v0.10.0` tag (2026-10-12) plus the hardening pass below.

### Added
- Console commands `assay-verify` and `assay-manifest` (`[project.scripts]`), and `python -m assay_production`.
  They need a checkout for the specimens and `MANIFEST.md`: `--root PATH`, `ASSAY_ROOT`, or run inside one.
- `--help` and `--version` on `assay-verify`, `assay-manifest` and `verify_manifest.py`.
- `assay_production.__version__`, single-sourced from `assay_production/_version.py` (read by `pyproject.toml`).
- Diagnostic logging through the standard `logging` module on stderr, level from `ASSAY_LOG_LEVEL`. Stdout is unchanged.
- README: a Security and limits section that states exactly what the CNS gate does not isolate; install, exit-code
  and logging documentation.
- A generated, verified summary example in the README (`ASSAY-SUMMARY-EXAMPLE` block) and a claim count in the
  status block, so the numbers in the README cannot drift from the verifier.
- Tests for typo'd flags, the console commands, the version, the README claims and the CNS pin.
- ruff and mypy configuration and CI steps; Python 3.13 in the CI matrix.
- Answer key: failure mode 3.6 (a test that cannot fail) and 3.7 (an unbacked status claim) (2026-10-14).
- Installable package, CI that proves the key with `--strict`, and the answer key offered as a CNS gate
  (`AssayKeyGate`) (#19, 2026-10-16).
- The gate reads the verifier summary through CNS's shared `cns.assay` row when the installed CNS has one (#20,
  2026-10-17).
- `STACK.md`: the role of ASSAY in the seven-repository circuit (2026-10-14).

### Changed
- Command lines are parsed with `argparse`. An unknown argument (for example `--stirct`) now exits 2 and checks
  nothing, instead of silently running the weaker non-strict check. Exit codes 0 (proven) and 1 (not proven) and the
  last-line `ASSAY-SUMMARY:` contract are unchanged.
- The optional `cns` extra is pinned to the full commit SHA of CNS v1.8.0, not a movable tag.
- `tests/test_consumers.py` honours `WARDEN_ROOT` and `SWIZZLE_ROOT` and finds a sibling checkout whatever its
  capitalisation (`Warden`, `warden`, `WARDEN`); it still skips cleanly when none exists.
- The Ghost baseline was rebuilt after Ghost's identity keys changed (2026-10-14).

### Fixed
- README: the passing-test count, the summary example (claims, entries, static checks), the description of CNS
  behaviour (the pinned CNS 1.8.0 has no `cns.assay`), and `STACK.md` calling the public CNS repository private.
- Unused imports and variables, and mypy errors, across the package and tests.

## [0.10.0] - 2026-10-12

The `v0.10.0` tag points at the end of this work (#18).

### Added
- The verifier proves the answer key instead of trusting it: every claim is run, the four copies of the key are
  compared, and every file under `specimens/` has a recorded SHA-256 (#16).
- A sandbox for running specimens: private temp per run, honest failure reasons, results a specimen cannot forge,
  output caps and time limits (#17).
- Sibling checkouts are found by the consumer tests (#18).

### Fixed
- README claims corrected (#18).

## Before 0.10.0 - 2026-08-19 to 2026-10-08

No tags before 0.10.0. In outline:
- 2026-08-19: the corpus is assembled from the GSA lineage (SECURE, UZTC, wrapper classes, resilience and SRE files).
- 2026-09-02: Apache-2.0 licence (#2); governance-stack cleanup (#3, #4); Ghost baseline (#6).
- 2026-09-07: from holding pen to specimen corpus, named TOUCHSTONE (#7); measured verdicts replace inherited
  prose, two of five were wrong (#8); the solvar pair was corrected (#9).
- 2026-10-05 to 2026-10-07: CNS-readiness catalogue; the MANIFEST answer key published as `registry.json` (#13).
- 2026-10-08: renamed from TOUCHSTONE to ASSAY (#15).
