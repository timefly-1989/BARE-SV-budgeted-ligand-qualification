# Stage-observable ligand qualification: numerical evidence, 2026-10-27

Authors: Shuai Liu, Hui Li, Jin Qian, Taizhou University.

This version provides saved predictions, computational outcomes, complete activity
policy results, negative mechanism screens and numerical replay for the revised
study. The primary independent comparisons tie; neither new development
adaptation passes its prespecified continuation rule. No journal acceptance,
method originality certification, or statistically established superiority is claimed.

## Reproduce

Use Python 3.12 and `pip install -r requirements.txt`, then run:

```
python replay_stage_evidence.py
python replay/replay_adapters.py
python experiments/45_activity_allocation_20261027/replay_activity.py
```

The first command verifies file hashes and reproduces qualification counts,
independent allocation values and exact power sensitivities. The second refits
all 20 stage calibrators and repeats nested kernel selection and all 60 outer
policy values from numerical-only inputs. The third replays all 1,470 saved
activity-policy results. No pretrained neural model is fitted by these commands.

## Scope and provenance

The 704 CrossDocked-source and 576 MOAD-source outcomes were acquired after the
corresponding predictions/policies were frozen. Both computational populations
contain few positive pools. Original freeze records retain their timestamps and
hashes. D=0 establishes joint failure; unobserved downstream values remain missing.
Earlier development/history and LIT-PCBA analyses are research-exposed reanalyses.
Inference/fitting seeds are not independent biological replicates.

The activity experiment uses published activity labels, not inferred D/V/Q.
Its allocation replay does not validate the complete dual-context qualification
pipeline against experimental activity. The FS-Mol material here is an input
readiness audit only: no FS-Mol test prediction or activity evaluation was run.
Assay count is not certified independent target-family count.

Molecular structures, raw assay archives, pretrained checkpoints, planner stocks,
templates and external fitted neural resources are not redistributed. Official
source URLs/checksums and dependency records are retained. Full source-chemistry
execution and encoder inference need those resources and the complete project.
Stored covariate matrices and excluded-row indices reproduce the added adapter
fits; re-auditing chemical exclusions from structures requires the original inputs.

## Rights and citation

This archive does not assign a new blanket licence to third-party datasets or
models. Resource-specific original terms apply. See experiment36/NOTICE.txt for
LIT-PCBA and Bath source attribution; imported Bath score summaries retain
CC-BY-SA 4.0 attribution. Raw FS-Mol data are omitted; the Figshare deposit and
code README have different licence notices recorded by the readiness audit.
The authors must resolve source terms before raw-data redistribution.

Please cite this exact repository version and archive SHA-256. A commit URL is
not a DOI. No Zenodo DOI has been minted for this revision.
