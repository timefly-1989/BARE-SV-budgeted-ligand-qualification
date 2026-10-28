"""Fresh scoring and selection timings after the chemistry benchmark exits.

Frozen input matrices/weights are used. Timing output never changes original
scores, rankings or endpoints. GPU synchronization brackets MPS wall timings.
"""
import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import time,resource,json,importlib.util,importlib.metadata,sys,gc,hashlib
H=Path(__file__).resolve().parent;R=H.parents[1];EVENTS=[];CURRENT={}
def main():
    global CURRENT
    start=time.perf_counter();start_cpu=time.process_time();import numpy as np,pandas as pd,torch,joblib
    from tabicl import TabICLClassifier
    from catboost import CatBoostClassifier
    torch.set_num_threads(4)
    EVENTS.append(dict(cohort='shared',repeat=0,component='Imports',phase='scoring_dependency_import',wall_seconds=time.perf_counter()-start,self_cpu_seconds=time.process_time()-start_cpu))
    assert (H/'checks/fresh_chemistry.json').exists(),'Do not benchmark competing workloads concurrently'
    locked=json.loads((H/'scoring_measurement_plan.json').read_text())
    for p,v in locked['code_sha256'].items():assert hashlib.sha256((H/p).read_bytes()).hexdigest()==v
    t_device=time.perf_counter();c_device=time.process_time()
    if torch.backends.mps.is_available():torch.mps.synchronize()
    EVENTS.append(dict(cohort='shared',repeat=0,component='MPS',phase='MPS_device_initialization',wall_seconds=time.perf_counter()-t_device,self_cpu_seconds=time.process_time()-c_device))
    def sync():
        if torch.backends.mps.is_available():torch.mps.synchronize()
    def measure(phase,fn):
        sync();t=time.perf_counter();c=time.process_time();out=fn();sync()
        EVENTS.append(dict(**CURRENT,phase=phase,wall_seconds=time.perf_counter()-t,self_cpu_seconds=time.process_time()-c))
        pd.DataFrame(EVENTS).to_csv(H/'results/fresh_scoring_times.csv',index=False)
        return out
    p=R/'experiments/36_external_activity_benchmark_20261027/run_activity.py';spec=importlib.util.spec_from_file_location('activity_cost_helper',p);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);f=mod.foundation()
    CURRENT=dict(cohort='shared',repeat=0,component='CheMeleon')
    model,featurizer=measure('encoder_load',lambda:f.load_encoder(f.device()))
    cohorts=['37_independent_qualification_20261027','44_moad_allocation_test_20261027'];errors=[]
    state=joblib.load(R/'experiments/16_molecular_foundation_20261025/transforms/full_chemeleon.joblib')
    for cohort in cohorts:
        e=R/'experiments'/cohort;c=pd.read_csv(e/'data/candidates.csv');strings=sorted(set(c.smiles));old=np.load(e/'cache/embeddings.npy')
        assert json.loads((e/'cache/embedding_smiles.json').read_text())==strings
        for repeat in [1,2,3]:
            CURRENT=dict(cohort=cohort,repeat=repeat,component='CheMeleon')
            def encode():return np.concatenate([f.encode_batch(model,featurizer,strings[k:k+128]) for k in range(0,len(strings),128)])
            emb=measure('graph_featurization_and_encoding',encode);delta=float(np.max(np.abs(emb-old)));errors.append(dict(cohort=cohort,repeat=repeat,component='encoder',max_abs_difference=delta))
            measure('saved_scaler_PCA_transform',lambda:state['transform'].transform(state['scaler'].transform(emb)))
    del model;f.cleanup()
    # Route-prior feature inference includes three weight loads per call and
    # exact original descriptor normalization; prior-network training is offline.
    p=R/'experiments/37_independent_qualification_20261027/score_independent.py';sp=importlib.util.spec_from_file_location('original_scoring_cost',p);oldmod=importlib.util.module_from_spec(sp);sp.loader.exec_module(oldmod)
    for cohort in cohorts:
        e=R/'experiments'/cohort;frame=pd.read_csv(e/'data/features_before_outcomes.csv');fp=np.load(e/'data/fingerprints.npy');old=np.load(e/'data/prior.npy')
        for repeat in [1,2,3]:
            CURRENT=dict(cohort=cohort,repeat=repeat,component='Route prior')
            values=measure('prior_weights_and_inference',lambda:oldmod.prior(frame,fp));errors.append(dict(cohort=cohort,repeat=repeat,component='route_prior',max_abs_difference=float(np.max(np.abs(values-old)))))
    params=json.loads((R/'experiments/16_molecular_foundation_20261025/tabicl_params.json').read_text());params.update(random_state=11,model_path=str(R/'experiments/pretrained/tabicl-classifier-v2-20260212.ckpt'))
    for cohort in cohorts:
        e=R/'experiments'/cohort;z=np.load(e/'data/frozen_model_inputs.npz',allow_pickle=False);r=z['context_R_indices'];compact=z['compact_columns']
        specs=[('Route full',z['chemeleon_train55'],z['context_D_labels'],z['chemeleon_query55'],'chemeleon_route_full'),('Conditional compact',z['chemeleon_train55'][r][:,compact],z['context_joint_labels'][r],z['chemeleon_query55'][:,compact],'chemeleon_R_compact'),('Joint full',z['chemeleon_train55'],z['context_joint_labels'],z['chemeleon_query55'],'chemeleon_joint_full')]
        for component,x,y,q,cache in specs:
            cached=np.load(e/'cache'/(cache+'.npz'));old=cached['values']
            signature=hashlib.sha256(b''.join(str((v.shape,v.dtype)).encode()+np.ascontiguousarray(v).tobytes() for v in [x,np.asarray(y),q])).hexdigest()
            assert str(cached['input_signature'])==signature,(cohort,component)
            for repeat in [1,2,3]:
                CURRENT=dict(cohort=cohort,repeat=repeat,component=component)
                def initialize():
                    model=TabICLClassifier(**params);model.fit(x,y);return model
                model=measure('TFM_constructor_and_context_fit',initialize)
                values=measure('TFM_query_prediction',lambda:model.predict_proba(q)[:,list(model.classes_).index(1)])
                delta=float(np.max(np.abs(values-old)));assert delta<1e-4,(cohort,component,delta)
                errors.append(dict(cohort=cohort,repeat=repeat,component=component,max_abs_difference=delta))
                del model;f.cleanup();print('TFM',cohort,component,repeat,round(EVENTS[-1]['wall_seconds'],3),flush=True)
        q=z['classic_query279']
        for component in ['Conditional CatBoost','Joint RF']:
            CURRENT=dict(cohort=cohort,repeat=0,component=component)
            def load():
                if component=='Joint RF':return [joblib.load(e/'cache'/f'rf_{seed}.joblib') for seed in [11,23,37]]
                result=[]
                for target in ['route','R']:
                    target_models=[]
                    for seed in [11,23]:
                        model=CatBoostClassifier();model.load_model(str(e/'cache'/f'cat_{target}_{seed}.cbm'));target_models.append(model)
                    result.append(target_models)
                return result
            models=measure('archived_classical_model_load',load)
            for repeat in [1,2,3]:
                CURRENT=dict(cohort=cohort,repeat=repeat,component=component)
                def predict():
                    if component=='Joint RF':return np.mean([m.predict_proba(q)[:,1] for m in models],axis=0)
                    parts=[np.mean([m.predict_proba(q,thread_count=4)[:,1] for m in ms],axis=0) for ms in models];return parts[0]*parts[1]
                measure('archived_classical_query_prediction',predict)
            del models;gc.collect()
    sys.path.insert(0,str(R/'experiments/53_constrained_policy_audit_20261028'));from constrained import simulate
    algorithms=['uniform','recycling','global','shield_forecast4','shield_posterior','shield_UCB','shield_search32'];selections=[]
    for cohort in cohorts:
        e=R/'experiments'/cohort;d=pd.read_csv(e/'data/scores_before_outcomes.csv').merge(pd.read_csv(e/'data/independent_outcomes.csv'),on=['pocket_id','candidate_id']).sort_values(['pocket_id','candidate_id']);method='chemeleon_dual_full_compact'
        for B in [8,32]:
            canonical={}
            for algorithm in algorithms:
                out,ix,_=simulate(d[method],d.pocket_id,d.candidate_id,d.y,B,algorithm,11);canonical[algorithm]=(out,tuple(ix)) # one recorded warmup, excluded below
            jobs=[(rep,alg) for rep in range(1,6) for alg in algorithms];jobs.sort(key=lambda a:hashlib.sha256(str((cohort,B,*a)).encode()).hexdigest())
            for repeat,algorithm in jobs:
                CURRENT=dict(cohort=cohort,repeat=repeat,component=algorithm,B=B)
                out,ix,_=measure('selection_with_returned_label_replay',lambda:simulate(d[method],d.pocket_id,d.candidate_id,d.y,B,algorithm,11))
                assert tuple(ix)==canonical[algorithm][1];selections.append(dict(**CURRENT,C=out['C'],K=out['K'],baseline_lost=out['baseline_lost']))
    pd.DataFrame(errors).to_csv(H/'results/scoring_probability_differences.csv',index=False);pd.DataFrame(selections).to_csv(H/'results/repeated_selection_checks.csv',index=False)
    hardware=dict(device=f.device(),torch_threads=torch.get_num_threads(),MPS_synchronized=True,CPU_seconds_exclude_accelerator_work=True,versions={n:importlib.metadata.version(n) for n in ['numpy','pandas','torch','tabicl','chemprop','catboost','scikit-learn']})
    (H/'results/scoring_hardware.json').write_text(json.dumps(hardware,indent=2)+'\n');(H/'checks/fresh_scoring.json').write_text(json.dumps(dict(status='PASS',timing_records=len(EVENTS),predictions_replaced=False,new_training_or_model_selection=False,conditional_model_weights_frozen=True,selection_terminal_sets_repeat_exactly=True),indent=2)+'\n');print('SCORING_TIMING_COMPLETE',len(EVENTS),flush=True)
if __name__=='__main__':main()
