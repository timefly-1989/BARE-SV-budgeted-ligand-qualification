# Discovery-preserving allocation: numerical evidence, 2026-10-28

This release contains a newly locked public-activity allocation test and added
saved-score chemical controls. It does not claim a prospective wet-lab screen,
biological-family independence, statistical superiority, or strong-Q1 readiness.

The new test selected one assay from each of 28 input/provenance components,
using input hashes without examining query activities, and formed seven complete
four-assay campaigns. There are 888 support rows, 5,498 queries and 2,681 query
actives. The official FS-Mol classification labels are approximately balanced
few-shot QSAR labels, not naturally sparse HTS positives.

At the designated total budget 112, primary Morgan RF seed 11 gives
uniform 88/27, recycling 96/27, and global 99/13 (actives/discovered assays).
Both primary campaign-level Holm-adjusted p-values are 0.0625.
At quota 32, recycling recovers 632 versus uniform 654 while retaining all 28
baseline discoveries, demonstrating that protection does not ensure more recovery.
All 5,110 new policy values replay; 28 primary RF models refit from source with
maximum probability discrepancy 2.23e-16. The 2,252 saved qualification policy
values and all empirical Pareto points are retained without selecting a winner.
Thompson/UCB and ENS-style controls are declared finite-pool adaptations;
repeated-arm regret guarantees and original-code equivalence are not asserted.

## Source data and terms

FS-Mol: Megan Stanley et al., FS-Mol: A Few-Shot Learning Dataset of Molecules,
NeurIPS Datasets and Benchmarks 2021.
https://datasets-benchmarks-proceedings.neurips.cc/paper_files/paper/2021/hash/8d3bba7425e7c98c50f52ca1b52d3735-Abstract-round2.html
Official archive: https://api.figshare.com/v2/file/download/31345321
DOI: 10.6084/m9.figshare.16941100.v1
Bytes: 4,871,086,080; MD5: 0ad8f73db6bb8415b023538d514138dc;
SHA256: 528a9c4e8d74c4287acda79536eecbf91418d6d0ac2c55918b270d78c2333ebc.

The Figshare metadata and source README contain different licence notices
(CC BY 4.0 and CC BY-SA 3.0). Accordingly this release does not redistribute raw
SMILES, source structures, support or query row-level source activity records.
Obtain the original archive from its provider under the applicable source terms.
Frozen source-row identifiers permit exact reconstruction locally. Code retains
the repository's code licence; no blanket new licence is asserted for third-party
data. Existing LIT-PCBA/Bath materials remain in the earlier evidence release
under their original attribution and terms.

## Replay

Extract this ZIP and supply the official archive path:

```sh
uv run --no-project --python 3.12 --with-requirements experiments/50_discovery_allocation_20261028/requirements.txt python experiments/50_discovery_allocation_20261028/replay_public.py --archive /path/to/fsmol.tar --all --refit-primary
```

Use `--python 3.12` if the local uv version requires a separated argument.
The script restores labels into memory from official source rows, verifies the
frozen query-label hash, replays every new policy value, and refits the primary
scorer without cached model weights. Output checks and selected-key traces are
written under this extracted experiment directory. Raw source records are not
published by the script. Additional dependency-heavy representation/chemical
replays use the earlier public evidence archive; this package does not include
third-party model weights, planner stocks or reaction templates.

The as-locked evaluate.py driver encountered missing historical CatBoost/RF
columns after finishing development. finish_saved.py records this scope handling
without imputing scores; replay_public.py is the portable new-test entry point.
The initial unpinned RDKit parser incompatibility was resolved before score freeze
by using the original pinned RDKit 2023.9.6, without outcome-based graph exclusions.

Earlier evidence, fixed commit:
https://github.com/timefly-1989/BARE-SV-budgeted-ligand-qualification/tree/70ba1c1ed4e1bffa99bed909fe5d87cfa82c7987

The unsubmitted manuscript and the raw FS-Mol archive are not included here.
