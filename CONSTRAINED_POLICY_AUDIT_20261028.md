# Matched certificate-policy and hindsight audit, 28 October 2026

Research-exposed extension of frozen public-activity evaluations. No new wet-lab,
source-label acquisition, confirmatory test or provider-population inference.
This archive does not publish the unsubmitted manuscript or its TOC artwork.

All4337 policy values use the same exact baseline-discovery certificate. New
proposals: shielded forecast/observed coverage(weight4), posterior mean/UCB,
certificate-aware one-step search(top32 plus pool representatives), and a
pilot-then-posterior barrier. ToxCast quotas1/4/8/16/32/64; FS-Mol RF/CatBoost/
active-neighbour seed11 at1/4/8/16/32. Search stops at32 by design. All losses of
particular baseline discoveries are zero. Static shielding matches DPQR in all
489 cases. There is no universally highest-recovery proposal across settings.

ToxCast quota32: DPQR3876; forecast/observed3859; posterior3820; UCB3812;
search3821; pilot-posterior3820. Exact admissible-path hindsight ceiling6954,
unconstrained label-known ceiling6986. DPQR is not near the oracle: gap3078.
FS-Mol RF quota32: shielded UCB671 vs static632, same discovery certificate.
These are retrospective comparisons, not newly locked superiority evidence.

The oracle maximizes realized recovery on paths whose EVERY action admits a
universally protected continuation. Full labels are used only offline. Its
escape/no-escape formula is independently checked on43632 feasible history/
quota/table cases and1088 root cases. Exact joint-model Bellman optimization,
including an explicit2-state witness(2.4 versus optimal pilot-first2.0), separates
information and execution barriers. This is not a claim to invent shielding or
Bellman's principle. Another independent full-world/batch enumeration checks
174 posterior histories and422 lookahead candidate values.

## Source data and replay

FS-Mol official archive: https://ndownloader.figshare.com/files/31345321
Dataset DOI10.6084/m9.figshare.16941100.v1; Stanley etal., NeurIPS2021.
ToxCast archived MoleculeNet file:
https://deepchemdata.s3-us-west-1.amazonaws.com/datasets/toxcast_data.csv.gz
SHA256 02c8b96da666884a13746e4891fc10b4f81f51fa14e0060df1db7da0223b46c6
Wu etal., Chemical Science2018, doi10.1039/C7SC02664A.
The ToxCast response calls include toxicity, not therapeutic binding or DVQ.
Provider terms and attribution remain applicable. No raw SMILES or individual
source responses are redistributed; derived scores and source-row mappings are.

From extracted root:
```
uv run --no-project --python 3.12 --with-requirements experiments/53_constrained_policy_audit_20261028/requirements.txt python experiments/53_constrained_policy_audit_20261028/replay_public.py --toxcast /path/toxcast_data.csv.gz --fsmol /path/fsmol.tar
uv run --no-project --python 3.12 --with-requirements experiments/53_constrained_policy_audit_20261028/requirements.txt python experiments/53_constrained_policy_audit_20261028/oracle_checks.py
uv run --no-project --python 3.12 --with-requirements experiments/53_constrained_policy_audit_20261028/requirements.txt python experiments/53_constrained_policy_audit_20261028/search_checks.py
```
The replay reconstructs source labels, verifies all4337 values and489 oracles.
The acquisition/audit runner run_audit.py expects locally reconstructed source
labels; replay_public.py is the public verification entry point. Frozen prior
primary tests, scores and random assignments are neither rerun nor replaced.
