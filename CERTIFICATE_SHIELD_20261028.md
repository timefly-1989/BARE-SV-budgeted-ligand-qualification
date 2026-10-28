# Certificate-constrained allocation: sparse activity evidence (28 October 2026)

This numerical release accompanies a local manuscript revision. It does not
include or publish the unsubmitted manuscript. Runtime shielding and Bellman
recursion are established principles; no priority or journal-readiness claim is
made by this release.

Primary result: 16 constructed four-assay PCBA campaigns, 242,888 queries and
3,466 measured actives (1.426995%). At 2,048 checks, uniform / DPQR / global
recover 252 / 374 / 438; baseline discoveries lost are 0 / 0 / 15. Both two-test
Holm-adjusted campaign sign flips are 0.00537109375. Inference is conditional on
independent, sign-symmetric differences. All selected assays record NCGC as
their source; neither family nor laboratory independence is certified. Capped
query panels are not complete original HTS campaigns. Support cost is common
and excluded from the query budget. No new wet-lab or chemical qualification
outcomes were acquired. The earlier frozen FS-Mol primary p=.0625 is unchanged.

The new protocol, source hashes and parsing amendment precede query activity
export. The original protocol is preserved. The source CSV contains blank
records; a dated implementation correction preserves consistent source rows
without changing groups, caps, models, endpoints or comparisons.

## Source and replay

Download the original PCBA CSV from the DeepChem distribution:
https://deepchemdata.s3-us-west-1.amazonaws.com/datasets/pcba.csv.gz
SHA256 b429a13ff6310aabb2d5ae1f41ea9d9c025e2c73fbf733cea33a62b4f163db19
Original benchmark: Wu et al., Chemical Science 9 (2018), 513-530,
doi:10.1039/C7SC02664A. Assay descriptions: PubChem PUG REST, description/JSON.
Source assay/compound records retain provider attribution and terms. This
package redistributes scores and derived row mappings, not raw source SMILES
or row-level source activity labels. They are reconstructed from the source.

From the extracted package root:
```
uv run --no-project --python 3.12 --with-requirements experiments/51_certificate_shield_20261028/requirements.txt python experiments/51_certificate_shield_20261028/replay_public.py --archive /absolute/path/pcba.csv.gz --refit
uv run --no-project --python 3.12 --with-requirements experiments/51_certificate_shield_20261028/requirements.txt python experiments/51_certificate_shield_20261028/theory_checks.py
```
The first command replays all640 values and refits64 forests if --refit is set.
No checkpoint, planner stock/template or clinical/binding affinity claim is
included. Complete earlier FS-Mol and chemical evidence remains in prior releases.
