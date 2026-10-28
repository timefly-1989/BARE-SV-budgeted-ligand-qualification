# Measured computational cost, 29 October 2026

This archive contains derived numerical timing evidence and scripts. It adds no
independent efficacy campaign, no new labels for method selection and no primary
hypothesis test. Original rankings and chemical outcomes remain unchanged.
No unsubmitted manuscript, TOC graphic, SMILES, SDF, model weights, stocks or
individual external assay response records are included.

Audited historical records:1280 route tasks,20 conditional downstream tasks,
23 shared references and1280 cheap-input tasks (2605 source file hashes).
Fresh engineering measurements:8 hash-selected route inputs twice,20 archived
route-passed downstream inputs twice and23 references once (79 top-level calls,
309 component timing records). A separate synchronized scoring/allocator process
adds213 records. Serial chemistry uses Apple M5 Pro48GiB, VinaCPU1; internal
PoseBusters threads are retained. Timing failures/timeouts remain in summaries.
The random-input route sample contains no solved cases, so its latency does not
estimate successful routes. Downstream inputs are a conditional engineering set.

**Meaning of cost**:selected original task elapsed-time sums are NOT campaign
wall time or CPU-core hours. Parallel calls overlap. Shared input construction,
model loading, resident prediction and allocator overhead have separate scopes.
Actual task durations are joined only after policy selection, never supplied to
a selector. These unknown advance costs do not instantiate a known-cost budget
guarantee. No CPU-energy, monetary or wet-lab saving is inferred.

## Numerical reproduction without chemistry resources
From the extracted root:
```
uv run --no-project --python 3.12 --with-requirements requirements.txt python experiments/55_measured_computation_cost_20261029/verify_measurements.py
```
This reconstructs336 frozen-score policy values, route/downstream selected-task
sums and input-weighted latency profiles. It checks saved benchmark code hashes.
It does not reproduce a physical timing observation. `results/` gives raw and
summarized clocks, frozen repeat outcomes, package/hardware metadata and scoring
differences. `data/numerical_inputs.csv` has own-computed qualification labels,
fixed six-scorer probabilities and original task times, without structures.
`data/benchmark_case_ids.csv` sanitizes the original local case list; the
measurement plan's case hash refers to the unsanitized local list.

`benchmark_chemistry.py` and `benchmark_scoring.py` are the exact measurement
entry points for the original full research workspace; they require its frozen
original input paths, third-party model/stock resources and respective chemistry
and scoring environments. They are NOT standalone download-and-run chemistry
pipelines. `audit_recorded_costs.py` also expects original local logs. Those
files are included to expose timing scopes and code hashes. Licensed resources
are not republished. Source/candidate provenance remains with earlier archives.

Fresh chemistry versions:Python3.12.14, RDKit2023.9.6, AiZynthFinder4.4.1,
Meeko0.8.0, PoseBusters0.3.1, ONNXRuntime1.30.0. Scoring:PyTorch2.14.1,
TabICL2.2.0, Chemprop2.2.0, CatBoost1.2.8, scikit-learn1.6.1; MPS synchronization
brackets timers. CPU clocks exclude GPU work. Offline encoder pretraining,
historical prior/classical training and labelled-context acquisition are not
newly timed. Startup and resident inference are distinguished in the raw CSVs.

No previously published main branch or historical numerical release is replaced.
