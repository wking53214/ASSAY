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

## [0.11.1] - 2026-10-17 (not yet tagged)

Cleanup after an independent audit of 0.11.0.

### Changed
- CI: every GitHub Action is pinned by full commit SHA with its tag in a comment (`actions/checkout` v4.2.2,
  `actions/setup-python` v5.6.0), and a test guards it.
- CI: the `consumers` job checks SWIZZLE and WARDEN out at the tested set (full SHAs). The comments say what is
  true of each commit: its own version file, and how far it is past that repository's last tag.

### Fixed
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
