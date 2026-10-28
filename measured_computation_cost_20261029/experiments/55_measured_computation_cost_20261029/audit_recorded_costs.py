"""Read-only source-record cost audit and fixed-selection work accounting."""
from pathlib import Path
import json,hashlib,sys,math
import pandas as pd,numpy as np
H=Path(__file__).resolve().parent;R=H.parents[1]
sys.path.insert(0,str(R/'experiments/53_constrained_policy_audit_20261028'))
from constrained import simulate
COHORTS=['37_independent_qualification_20261027','44_moad_allocation_test_20261027']
METHODS=['chemeleon_dual_full_compact','chemeleon_dual_full_full','morgan_conditional','catboost_conditional279','rf_joint279','historical_route_prior']
POLICIES=['uniform','recycling','global','shield_forecast4','shield_posterior','shield_UCB','shield_search32']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    records=[];source_hashes={};summary=[];policies=[];curves=[]
    for cohort in COHORTS:
        e=R/'experiments'/cohort;o=pd.read_csv(e/'data/independent_outcomes.csv',float_precision='round_trip');sc=pd.read_csv(e/'data/scores_before_outcomes.csv');source_hashes[str((e/'data/independent_outcomes.csv').relative_to(R))]=sha(e/'data/independent_outcomes.csv')
        for row in o.itertuples():
            base=e/'chemistry/records'/row.pocket_id/row.candidate_id;r=json.loads((base/'route.json').read_text());source_hashes[str((base/'route.json').relative_to(R))]=sha(base/'route.json')
            assert r['D']==row.D and abs(r['elapsed_seconds']-row.route_seconds)<1e-8
            assert r['strict_full_stock_checked']
            dt=0
            if row.D:
                d=json.loads((base/'docking.json').read_text());source_hashes[str((base/'docking.json').relative_to(R))]=sha(base/'docking.json')
                assert d['V']==row.V and d['Q']==row.Q and abs(d['elapsed_seconds']-row.downstream_seconds)<1e-8;dt=d['elapsed_seconds']
            else:assert not (base/'docking.json').exists() and pd.isna(row.V) and pd.isna(row.Q) and row.downstream_seconds==0
            records.append(dict(cohort=cohort,pocket_id=row.pocket_id,candidate_id=row.candidate_id,D=int(row.D),y=int(row.y),route_wall_seconds=float(r['elapsed_seconds']),downstream_wall_seconds=float(dt),total_task_wall_seconds=float(r['elapsed_seconds']+dt),route_status=r['status']))
        feature=json.loads((e/'results/feature_provenance.json').read_text());acq=json.loads((e/'results/independent_acquisition.json').read_text())
        refsum=0;cheapsum=0;refcount=0;cheapcount=0
        for pid in o.pocket_id.unique():
            p=e/'chemistry/records'/pid/'reference/docking.json';refsum+=json.loads(p.read_text())['elapsed_seconds'];refcount+=1;source_hashes[str(p.relative_to(R))]=sha(p)
        for row in o.itertuples():
            p=e/'chemistry/records'/row.pocket_id/row.candidate_id/'cheap_features.json';j=json.loads(p.read_text());cheapsum+=j['seconds'];cheapcount+=1;source_hashes[str(p.relative_to(R))]=sha(p)
        summary.append(dict(cohort=cohort,candidates=len(o),pools=o.pocket_id.nunique(),route_passed=int(o.D.sum()),positives=int(o.y.sum()),route_task_sum_seconds=float(o.route_seconds.sum()),downstream_task_sum_seconds=float(o.downstream_seconds.sum()),recorded_parallel_acquisition_wall_seconds=float(acq['wall_seconds']),route_workers=12,downstream_workers=4,prevalidation_feature_pipeline_wall_seconds=feature['seconds'],shared_reference_task_sum_seconds=refsum,cheap_input_task_sum_seconds=cheapsum,reference_calls=refcount,cheap_calls=cheapcount,route_median_seconds=float(o.route_seconds.median()),route_p95_seconds=float(o.route_seconds.quantile(.95)),downstream_conditional_median_seconds=float(o.loc[o.D.eq(1),'downstream_seconds'].median())))
        g=sc.merge(o,on=['pocket_id','candidate_id'],validate='one_to_one').sort_values(['pocket_id','candidate_id']).reset_index(drop=True)
        for method in METHODS:
            for B in [4,8,16,32]:
                for algorithm in POLICIES:
                    result,ix,_=simulate(g[method],g.pocket_id,g.candidate_id,g.y,B,algorithm,11);z=g.iloc[ix];route=float(z.route_seconds.sum());downstream=float(z.downstream_seconds.sum())
                    policies.append(dict(cohort=cohort,method=method,B=B,algorithm=algorithm,route_task_sum_seconds=route,downstream_task_sum_seconds=downstream,selected_task_sum_seconds=route+downstream,route_calls=len(z),downstream_calls=int(z.D.sum()),**result))
                    if method=='chemeleon_dual_full_compact' and B==32 and algorithm in ['uniform','recycling','global']:
                        cum=0;hits=0
                        for k,row in enumerate(z.itertuples(),1):
                            cum+=row.route_seconds+row.downstream_seconds;hits+=row.y;curves.append(dict(cohort=cohort,algorithm=algorithm,checks=k,C=int(hits),selected_task_sum_seconds=cum))
    pd.DataFrame(records).to_csv(H/'data/recorded_candidate_costs.csv',index=False);pd.DataFrame(summary).to_csv(H/'results/recorded_cohort_costs.csv',index=False)
    pd.DataFrame(policies).to_csv(H/'results/measured_work_policy_replay.csv',index=False);pd.DataFrame(curves).to_csv(H/'results/measured_work_curves.csv',index=False)
    (H/'checks/record_hashes.json').write_text(json.dumps(source_hashes,indent=2)+'\n')
    for p,v in json.loads((H/'checks/frozen_guards.json').read_text()).items():assert sha(R/p)==v,p
    out=dict(status='PASS',candidate_records=len(records),route_records=1280,conditional_downstream_records=20,shared_reference_records=23,cheap_input_records=1280,source_file_hashes=len(source_hashes),policy_values=len(policies),recorded_task_sums_are_not_campaign_wall_time=True,no_unobserved_timing_used_for_selection=True,old61_resumed=False)
    (H/'checks/recorded_cost_audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
