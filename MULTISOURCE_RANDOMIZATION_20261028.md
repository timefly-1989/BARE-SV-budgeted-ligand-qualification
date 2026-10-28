# External-provider randomized algorithmic replay (28 October 2026)

Nine documented ToxCast assay-provider/platform categories, 66 endpoints,
64 fixed query libraries, 32 within-provider randomized pairs. These are not
64 independent biological/laboratory replicates or a random sample of labs.
Response-positive calls include toxicology responses; they are not therapeutic
binding or route/pose/docking qualification. Existing public measurements were
replayed, with no new wet-lab acquisition.

Protocol and actual random assignment were saved before support-label fitting
and query evaluation. They were not redrawn or tuned. Input-only availability
rules determine library counts and selected endpoints without activity signs.
There are 16,325 support and 64,639 query records, with 7,072 response positives
(10.9408%). Query feedback/budget is never shared between libraries or trials.

Two predeclared virtual trials use the SAME64 libraries, independently assigned
within32 pairs for each trial. Assigned recovery: DPQR1932 vs uniform1634,
7424 checks each; source-balanced estimate1.25347 perendpoint. Assigned discovery
loss: DPQR0 vs global30, 7424 checks each. Exact TWO-SIDED Fisher SHARP-null
p-values after Holm correction: .005823077633976936 and .0000019073486328125.
These tests use the actual fair-bit assignment mechanism, not independent or
sign-symmetric potential outcomes. They do NOT test the weak zero-average-effect
null and do not justify unseen-provider or laboratory-population inference.

Full counterfactual replay at14848 checks: uniform3265 / DPQR3876 / global4044.
All416 baseline endpoint-library discoveries are preserved by DPQR; pooling
loses67. Each provider has a positive fixed-panel recovery contrast. Stronger
unconstrained controls recover more; no overall SOTA or journal-readiness claim.
Whole-provider campaigns are secondary and not the same-budget operating point.
The earlier NCGC and FS-Mol frozen outcomes/groupings are not redefined.

## Source and reproducibility

Archived MoleculeNet/DeepChem CSV (NOT a claim to current EPA invitrodb):
https://deepchemdata.s3-us-west-1.amazonaws.com/datasets/toxcast_data.csv.gz
SHA256 02c8b96da666884a13746e4891fc10b4f81f51fa14e0060df1db7da0223b46c6
EPA provenance:
https://www.epa.gov/system/files/documents/2022-12/ToxCast%20Assay%20Platform%20Descriptions%2008112017.pdf
SHA256 b10236c58f4796be0b1ac2c676fb7624fd6aa28ee7ee349c534d29a7ee845393
Wu etal., MoleculeNet, Chemical Science2018, doi10.1039/C7SC02664A.
Ding, A Paradox from Randomization-Based Causal Inference, Statistical Science
32(3):331-345,2017, doi10.1214/16-STS571, clarifies sharp vs weak nulls.

Provider data retain original attribution and terms. This numerical package
excludes raw SMILES, individual source activity labels and the unsubmitted
manuscript. Canonical-key/source-row mappings and derived predictions permit
reconstruction from the official archive. Assigned outcomes are library-level
counts, not individual source labels.

From extracted root:
```
uv run --no-project --python 3.12 --with-requirements experiments/52_multisource_randomized_20261028/requirements.txt python experiments/52_multisource_randomized_20261028/replay_public.py --archive /absolute/path/toxcast_data.csv.gz --refit
uv run --no-project --python 3.12 --with-requirements experiments/52_multisource_randomized_20261028/requirements.txt python experiments/52_multisource_randomized_20261028/randomization_checks.py
```
This reconstructs source labels by canonical graph, replays2632 policy values,
128 assigned-policy outcomes and both exact tests, and optionally refits66 RFs.
The protocol/prepare/fit/evaluate files have once-only guards and should NOT be
rerun over frozen evidence. Replay does not create new random assignments.
