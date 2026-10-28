# BARE-SV: budgeted ligand qualification — numerical archive

## 2026-10-27 stage-observable revision

The [new numerical evidence archive](stage_evidence_20261027.zip) retains
stage-eligible predictions, all 1,280 independent computational outcomes,
real-activity allocation results and negative mechanism screens.
See [scope and replay instructions](STAGE_EVIDENCE_20261027.md) and
[the archive SHA-256](STAGE_EVIDENCE_20261027.sha256).
This revision does not establish complete-method superiority; it preserves the
failed adaptation gates and tied independent primary contrasts.
The original numerical snapshot and its hashes below remain unchanged.


This repository contains the saved ranking scores, computational qualification labels, feature arrays, analysis summaries and numerical replay code for **Pre-verification representations for budgeted ligand qualification: information gains and transfer trade-offs** by Shuai Liu, Hui Li and Jin Qian (Taizhou University). Correspondence: Hui Li, lihui@tzu.edu.cn.

The complete directory structure is distributed in `numerical_archive.zip`. The portable entry-point scripts are also visible at the repository root for inspection. Extract the archive before running them; the file map below refers to the extracted directory.

The article evaluates a pre-verification representation with a frozen tabular in-context learner. The repository is a snapshot of the recorded experiments. It reproduces numerical analyses from saved scores and labels. Full model inference, chemical planning and independent pose verification require the original external resources and environments; these are not bundled here.

## Quick start

Python 3.11 is recommended. The numerical replay uses only NumPy and pandas.

```bash
git clone https://github.com/timefly-1989/BARE-SV-budgeted-ligand-qualification.git
cd BARE-SV-budgeted-ligand-qualification
python -m zipfile -e numerical_archive.zip numerical_archive
cd numerical_archive
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
python verify_archive.py
python replay_numerical_results.py
```

The replay checks all budgets 1–40, matched feature ablations, reliability bins, selected gate partitions, three ranking seeds, the frozen 26-contrast family with Holm adjustment, exact paired sign-flip tests, bootstrap intervals and repeated scoring times. The archived validation report records 108 passing checks. The script stops with an assertion if a reconstructed result differs.

## Recorded primary results

The budget is 32 allocations per pocket. The endpoint is joint **computational** route/pose/score qualification. It is not measured synthesis success or biological activity. Macro recall averages over positive-containing pockets; pooled counts have a different denominator.

| Cohort | Candidates | Pockets | Joint positives | Full representation recovered | Base representation recovered |
|---|---:|---:|---:|---:|---:|
| `first48` (selection) | 3,072 | 48 | 133 | 128 | 125 |
| `later23` (later reused cohort) | 1,472 | 23 | 36 | 36 | 36 |
| `fresh16` (new candidates scored before endpoint acquisition) | 1,428 | 16 | 72 | 60 | 61 |

The strongest reported control recovers 63/72 on `fresh16`. The full representation has no multiplicity-adjusted superiority on that cohort. The later reused cohort is not presented as an untouched prospective test.

## File map

| Path | Contents |
|---|---|
| `replay_numerical_results.py` | Portable replay of the published numerical comparisons |
| `verify_archive.py`, `SHA256SUMS.json` | Verify the archived file contents before replay |
| `numerical_replay_validation.json` | Results and names of the 108 archived checks |
| `experiments/02_selection48/data/` | Selection-cohort saved predictions, control scores and endpoint labels |
| `experiments/03_confirmation23/data/` | Later-cohort saved predictions, control scores and endpoint labels |
| `experiments/05_fresh16/` | Frozen policy, saved predictions and new-cohort endpoint labels |
| `experiments/04_completion/data/` | Matched ablations, seed scores and saved feature arrays |
| `experiments/04_completion/results/` | All-budget analyses, contrasts, reliability and timing summaries |
| `experiments/00_protocol/` | Original dated protocol and freeze/provenance records |
| `experiments/06_reporting/`, `experiments/07_historical_diagnostics/` | Additional saved reports and historical diagnostics |
| `replay/`, `replay_saved_scores.py` | Historical saved-score replay inputs and recipe |
| `scripts/`, `experiments/*/scripts/` | Original analysis and plotting source; some scripts require the full original project and optional dependencies |
| `figures/protein_pocket_effects/` | Pocket recovery, candidate ranks and provenance for the protein-pocket result figure |
| `project.json` | Original project metadata used by replay for exact method labels |

### Schema and interpretation

`pocket_id` and `candidate_id` identify records. Rankings sort descending utility and break ties lexicographically by candidate ID. In the endpoint files, `D`, `V`, `Q` are route, independent pose and score gates, respectively, and `y` is their joint endpoint. An upstream gate failure implies joint failure; downstream values need not be measured when the route gate fails. Utilities are used for ranking and are not assumed to be calibrated probabilities.

`first48`, `later23` and `fresh16` retain their original names for compatibility. Original protocol files describe the larger source project, including resources omitted from this numerical archive. Resource hashes establish provenance and do not imply that the corresponding checkpoints or chemistry resources are bundled. Plotting scripts referencing `manuscript.tex`, source structures or the original figures require that full project; the portable numerical replay is the independently checked entry point.

## Provenance and citation

The original ligand proposals come from the publicly released FLOWR archive: Cremer and Irwin, *FLOWR: Flow Matching for Structure-Aware De Novo, Interaction- and Fragment-Based Ligand Generation*, version v2 (2025), https://doi.org/10.5281/zenodo.15257565. Original molecular archives, model checkpoints, planner stocks and templates retain their original access and licensing conditions and are not redistributed here.

The `SHA256SUMS.json` manifest covers this numerical snapshot. `archive_provenance.json` separately records hashes of the copied numerical files. Original experimental scores and labels were not edited. AI assistance was used for code preparation, documentation and consistency checks; the authors are responsible for verification. No new experimental result is created by preparing this archive.

Please cite the repository and its specific commit when using these materials. `CITATION.cff` supplies author and archive metadata. A GitHub URL or commit is not a DOI, and no journal acceptance or publication is claimed. No new third-party licence is granted by this archive; consult the original resource licences for any external resource.

## Known-cost / bounded-retention numerical extension (29 October 2026)

`cost_retention_decisions_20261029.zip` provides the exact cost/loss-cap
certificate implementation, independent minimax verification, 4,500
research-exposed policy values, finite-panel value thresholds and a standalone
replay from official ToxCast/FS-Mol source files. It contains no unsubmitted
manuscript, TOC art, raw molecular structures or individual source activities.
Costs1/2/4 are synthetic input hashes, not measured assay/chemical times.
There is no new independent campaign or confirmatory test. Earlier locked
results remain unchanged. The archive README documents dependencies, scope,
source attribution and replay commands.

Archive SHA256: `c1ffe6dd1df9d0d41895d6ce33ddd91b0490e73625cc301a167ccc411a3bb590`.
