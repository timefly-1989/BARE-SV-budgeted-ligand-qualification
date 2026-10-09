"""Independent read-only replay of saved scores, endpoints and reported summaries."""
from pathlib import Path
import hashlib
import json
import re

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
PROJECT = HERE
RESULTS = PROJECT / "experiments/04_completion/results"
KEYS = ["pocket_id", "candidate_id"]
PROP = json.loads((PROJECT / "project.json").read_text())["method_display"]
checks = []


def require(name, value):
    if not value:
        raise AssertionError(name)
    checks.append(name)


def replay(frame, columns, cohort):
    rows = []
    for pocket, part in frame.groupby("pocket_id", sort=False):
        y = part.y.to_numpy()
        ids = part.candidate_id.to_numpy(str)
        positives = int(y.sum())
        for name in columns:
            ranked = np.lexsort((ids, -part[name].to_numpy()))
            cumulative = np.cumsum(y[ranked])
            for budget in range(1, 41):
                recovered = int(cumulative[budget - 1])
                rows.append({"cohort": cohort, "method": name, "pocket_id": pocket, "budget": budget,
                             "C": recovered, "recall": recovered / positives if positives else np.nan,
                             "precision": recovered / budget, "f1": 2 * recovered / (budget + positives)})
    return pd.DataFrame(rows)


summary = pd.read_csv(RESULTS / "budget_summary.csv")
ablation_summary = pd.read_csv(RESULTS / "ablation_summary.csv")
main = []
fresh_effects = None
for cohort, directory in [("first48", "02_selection48"), ("later23", "03_confirmation23"), ("fresh16", "05_fresh16")]:
    data = PROJECT / "experiments" / directory / "data"
    outcomes = pd.read_csv(data / "outcomes.csv")
    proposed = pd.read_csv(data / "proposed_predictions.csv").rename(columns={"score": PROP})
    controls = pd.read_csv(data / "baseline_policy_scores.csv")
    names = [PROP] + [x for x in controls.columns if x not in KEYS]
    frame = outcomes.merge(proposed[KEYS + [PROP]], on=KEYS, validate="one_to_one").merge(controls, on=KEYS, validate="one_to_one")
    require(cohort + " complete candidate match", len(frame) == len(outcomes))
    require(cohort + " route-failure conjunction", frame.loc[frame.D.eq(0), "y"].eq(0).all())
    rebuilt = replay(frame, names, cohort)
    agg = rebuilt.groupby(["cohort", "method", "budget"]).agg(total_C=("C", "sum"), mean_C=("C", "mean"), recall=("recall", "mean"), precision=("precision", "mean"), f1=("f1", "mean")).reset_index()
    merged = agg.merge(summary[summary.cohort.eq(cohort)], on=["cohort", "method", "budget"], suffixes=("_new", "_saved"), validate="one_to_one")
    require(cohort + " all policies and budgets covered", len(merged) == len(agg))
    for column in ["total_C", "mean_C", "recall", "precision", "f1"]:
        require(cohort + " all-budget " + column, np.allclose(merged[column + "_new"], merged[column + "_saved"], atol=1e-12, rtol=0, equal_nan=True))
    row = agg[agg.method.eq(PROP) & agg.budget.eq(32)].iloc[0]
    main.append({"cohort": cohort, "candidates": len(frame), "pockets": frame.pocket_id.nunique(), "positives": int(frame.y.sum()), "C32": int(row.total_C), "macro_recall": float(row.recall)})
    if cohort == "fresh16":
        fresh_effects = rebuilt[rebuilt.budget.eq(32)].pivot(index="pocket_id", columns="method", values="C")
    ab = pd.read_csv(PROJECT / f"experiments/04_completion/data/{cohort}_ablation_predictions.csv")
    abnames = [x for x in ab if x not in KEYS and not x.startswith("raw_")]
    abframe = outcomes[KEYS + ["y"]].merge(ab, on=KEYS, validate="one_to_one")
    ar = replay(abframe, abnames, cohort)
    aa = ar.groupby(["cohort", "method", "budget"]).agg(total_C=("C", "sum"), mean_C=("C", "mean"), recall=("recall", "mean"), f1=("f1", "mean")).reset_index()
    am = aa.merge(ablation_summary[ablation_summary.cohort.eq(cohort)], on=["cohort", "method", "budget"], suffixes=("_new", "_saved"), validate="one_to_one")
    require(cohort + " ablation coverage", len(am) == len(aa))
    for column in ["total_C", "mean_C", "recall", "f1"]:
        require(cohort + " all-budget ablation " + column, np.allclose(am[column + "_new"], am[column + "_saved"], atol=1e-12, rtol=0, equal_nan=True))
    # Reconstruct the existing reliability bins directly from frozen utilities.
    score = frame[PROP].to_numpy()
    bins = np.minimum((np.clip(score, 0, 1) * 10).astype(int), 9)
    saved = pd.read_csv(RESULTS / f"{cohort}_reliability.csv")
    for item in saved.itertuples():
        selected = bins == item.bin
        require(f"{cohort} reliability bin {item.bin}", int(selected.sum()) == item.count and np.isclose(score[selected].mean(), item.mean_score, atol=1e-12) and np.isclose(frame.y.to_numpy()[selected].mean(), item.observed_rate, atol=1e-12))
    require(cohort + " reliability counts complete", saved["count"].sum() == len(frame))
    selected_parts = []
    for _, part in frame.groupby("pocket_id", sort=False):
        order = np.lexsort((part.candidate_id.to_numpy(str), -part[PROP].to_numpy()))
        selected_parts.append(part.iloc[order[:32]])
    selected = pd.concat(selected_parts)
    stages = np.select([selected.D.ne(1), selected.V.ne(1), selected.Q.ne(1)], ["route", "pose", "score"], default="qualified")
    partition = pd.Series(stages).value_counts().to_dict()
    saved_partition = pd.read_csv(RESULTS / "selected_failure_partition.csv")
    expected_partition = saved_partition[saved_partition.cohort.eq(cohort)].set_index("stage").selected_count.to_dict()
    require(cohort + " selected gate partition", partition == expected_partition)
    seed_summary = pd.read_csv(RESULTS / "seed_summary.csv")
    for seed in [11, 23, 37]:
        seed_scores = pd.read_csv(PROJECT / f"experiments/04_completion/data/{cohort}_seed{seed}.csv")
        seed_frame = outcomes[KEYS + ["y"]].merge(seed_scores, on=KEYS, validate="one_to_one")
        rebuilt_seed = replay(seed_frame, ["score"], cohort)
        seed_main = rebuilt_seed[rebuilt_seed.budget.eq(32)]
        seed_row = seed_summary[seed_summary.cohort.eq(cohort) & seed_summary.seed.eq(seed) & seed_summary.budget.eq(32)].iloc[0]
        require(f"{cohort} seed {seed}", np.allclose([seed_main.C.sum(), seed_main.C.mean(), seed_main.recall.mean()], [seed_row.total_C, seed_row.mean_C, seed_row.recall], atol=1e-12, rtol=0))

tests = pd.read_csv(RESULTS / "fresh_tests_joint26.csv")
for item in tests.itertuples():
    d = (fresh_effects[PROP] - fresh_effects[item.control]).to_numpy()
    nz = d[d != 0]
    sums = np.array([0.0])
    for value in nz:
        sums = np.r_[sums + value, sums - value]
    p = np.mean(np.abs(sums) >= abs(d.sum()) - 1e-12)
    rng = np.random.default_rng(20261007)
    boot = d[rng.integers(0, len(d), (10000, len(d)))].mean(axis=1)
    lo, hi = np.quantile(boot, [0.025, 0.975])
    require("fresh contrast " + item.control, np.allclose([d.mean(), p, lo, hi], [item.difference, item.p_raw, item.ci_low, item.ci_high], atol=1e-12, rtol=0))
family = json.loads((PROJECT / "experiments/00_protocol/joint_test_family.json").read_text())
raw = np.asarray(family["raw_p_values"])
require("frozen 26-contrast family", len(raw) == 26 and np.allclose(raw[family["displayed_indices"]], tests.p_raw, atol=1e-12))
order = np.argsort(raw)
adjusted = np.empty(len(raw))
last = 0
for index, position in enumerate(order):
    last = max(last, min(1, (len(raw) - index) * raw[position]))
    adjusted[position] = last
require("Holm adjustment", np.allclose(adjusted[family["displayed_indices"]], tests.p_holm_joint26, atol=1e-12))

timing = pd.read_csv(RESULTS / "repeated_latency.csv")
saved_timing = pd.read_csv(RESULTS / "latency_summary.csv")
for item in saved_timing.itertuples():
    values = timing[timing.method.eq(item.method)].seconds
    require("timing " + item.method, len(values) == item.count and np.allclose([values.median(), values.quantile(.25), values.quantile(.75)], [item.median, item.q25, item.q75], atol=1e-12))


expected_main = {"first48": 128, "later23": 36, "fresh16": 60}
require("fixed primary recovery totals", all(item["C32"] == expected_main[item["cohort"]] for item in main))
report = {"status": "PASS", "checks": len(checks), "check_names": checks, "main_endpoints": main,
          "scope": "Saved-score, endpoint and numerical analysis replay; no model fitting or chemical execution"}
(HERE / "numerical_replay_validation.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({"status": "PASS", "checks": len(checks), "main_endpoints": main}))
