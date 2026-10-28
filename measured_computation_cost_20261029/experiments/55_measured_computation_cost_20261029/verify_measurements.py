"""Numerical verification from sanitized fixed inputs; never reruns chemistry."""
from pathlib import Path
import sys,json,hashlib
import numpy as np,pandas as pd
H=Path(__file__).resolve().parent;R=H.parents[1]
sys.path.insert(0,str(H.parent/'53_constrained_policy_audit_20261028'))
from constrained import simulate

def main():
    x=pd.read_csv(H/'data/numerical_inputs.csv');saved=pd.read_csv(H/'results/measured_work_policy_replay.csv');n=0
    for row in saved.itertuples():
        d=x[x.cohort.eq(row.cohort)].sort_values(['pocket_id','candidate_id']).reset_index(drop=True)
        out,ix,_=simulate(d[row.method],d.pocket_id,d.candidate_id,d.y,row.B,row.algorithm,11)
        z=d.iloc[ix]
        for key in ['C','K','coverage','baseline_coverage','baseline_lost']:assert out[key]==getattr(row,key),(row.cohort,row.algorithm,key)
        for key,value in [('route_task_sum_seconds',z.route_wall_seconds.sum()),('downstream_task_sum_seconds',z.downstream_wall_seconds.sum()),('selected_task_sum_seconds',z.total_task_wall_seconds.sum())]:assert np.isclose(value,getattr(row,key),rtol=0,atol=1e-7),(row.algorithm,key)
        assert len(z)==row.route_calls and int(z.D.sum())==row.downstream_calls;n+=1
    raw=pd.read_csv(H/'results/fresh_component_times.csv');profiles=pd.read_csv(H/'results/chemistry_component_summary.csv')
    for p in profiles.itertuples():
        q=raw[raw.phase.eq(p.phase)]
        if p.phase not in ['route_total','downstream_total','reference_total']:q=q[q.candidate_id.ne('reference')]
        med=q.groupby(['cohort','pocket_id','candidate_id'])[['wall_seconds','cpu_seconds']].median()
        assert len(med)==p.cases and len(q)==p.calls
        assert np.isclose(med.wall_seconds.median(),p.wall_median)
        assert np.isclose(med.cpu_seconds.median(),p.CPU_median)
    assert len(raw)==309 and len(pd.read_csv(H/'results/fresh_scoring_times.csv'))==213
    for f in ['measurement_plan.json','scoring_measurement_plan.json','analysis_plan.json']:
        for name,sha in json.loads((H/f).read_text())['code_sha256'].items():assert hashlib.sha256((H/name).read_bytes()).hexdigest()==sha,name
    assert (raw[['wall_seconds','self_cpu_seconds','child_cpu_seconds','cpu_seconds']]>=0).all().all()
    assert np.allclose(raw.self_cpu_seconds+raw.child_cpu_seconds,raw.cpu_seconds,atol=1e-8)
    assert np.isfinite(saved.selected_task_sum_seconds).all()
    result=dict(status='PASS',candidate_rows=len(x),policy_values=n,chemistry_timing_records=len(raw),scoring_timing_records=213,profiles_reconstructed=True,physical_timing_repetition_not_claimed=True,no_times_passed_to_selector=True)
    (H/'checks/numerical_verification.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
if __name__=='__main__':main()
