"""Fresh serial timing runs; original scientific records are read-only.

Calls the original qualification code in new record directories. Instrumentation
wraps existing calls without changing their arguments, seeds or checks. Timing
replicates are diagnostics and never replace original frozen labels.
"""
import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import time,resource,json,hashlib,importlib.util,importlib.metadata,threading,subprocess,sys,platform
H=Path(__file__).resolve().parent;R=H.parents[1]
EVENTS=[];CURRENT={};PEAK=0;STOP=False
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def cpu():
    x=resource.getrusage(resource.RUSAGE_CHILDREN)
    return time.process_time(),x.ru_utime+x.ru_stime
def measure(phase,fn):
    t=time.perf_counter();a,b=cpu();status='completed'
    try:return fn()
    except BaseException:status='error';raise
    finally:
        c,d=cpu();EVENTS.append(dict(**CURRENT,phase=phase,wall_seconds=time.perf_counter()-t,self_cpu_seconds=c-a,child_cpu_seconds=d-b,cpu_seconds=c-a+d-b,status=status))
def main():
    global PEAK,STOP,CURRENT
    plan=json.loads((H/'measurement_plan.json').read_text())
    for n,v in plan['code_sha256'].items():assert sha(H/n)==v,n
    for n,v in json.loads((H/'checks/frozen_guards.json').read_text()).items():assert sha(R/n)==v,n
    CURRENT=dict(cohort='shared',pocket_id='',candidate_id='',repeat=0)
    def imports():
        global pd,np,psutil,acq,vc
        import pandas as pd,numpy as np,psutil
        spec=importlib.util.spec_from_file_location('acq_cost_benchmark',R/'experiments/37_independent_qualification_20261027/acquire_independent.py')
        acq=importlib.util.module_from_spec(spec);spec.loader.exec_module(acq);vc=acq.vc
    measure('dependency_import',imports)
    def monitor():
        global PEAK
        root=psutil.Process()
        while not STOP:
            total=0
            for p in [root]+root.children(recursive=True):
                try:total+=p.memory_info().rss
                except psutil.Error:pass
            PEAK=max(PEAK,total);time.sleep(.05)
    thread=threading.Thread(target=monitor,daemon=True);thread.start()
    def context(cohort,repeat):
        root=H/'benchmark'/('shared' if repeat==0 else 'repeat_'+str(repeat))/cohort;root.mkdir(exist_ok=True,parents=True)
        source=R/'experiments'/cohort/'chemistry';link=root/'pools'
        if not link.exists():link.symlink_to((source/'pools').resolve(),target_is_directory=True)
        raw=root/'raw';raw.mkdir(exist_ok=True);link=raw/'aizynth'
        if not link.exists():link.symlink_to((R/'experiments/05_fresh16/chemistry/raw/aizynth').resolve(),target_is_directory=True)
        vc.ROOT=root;vc.VINA=R/'experiments/05_fresh16/chemistry/bin/vina'
        return root
    cohorts=plan['cohorts'];context(cohorts[0],0)
    # Hash all resources before timing initialization; this is a fresh process,
    # not a claim that the operating-system page cache is cold.
    resources=json.loads((R/'experiments/37_independent_qualification_20261027/checks/chemistry_environment.json').read_text())['resource_sha256']
    for p,v in resources.items():assert sha(R/p)==v
    measure('planner_and_full_stock_initialization',acq.route_init)
    candidates={k:pd.read_csv(R/'experiments'/k/'data/candidates.csv') for k in cohorts}
    cases=pd.read_csv(H/'data/benchmark_cases.csv')
    # Instrument nonoverlapping inner docking components. Total-call timing
    # contains these components and must not be added to them again.
    original_prepare=vc.prepare_ligand;original_vina=vc.vina_command;original_bust=vc.PoseBusters.bust
    vc.prepare_ligand=lambda *a,**kw:measure('ligand_preparation',lambda:original_prepare(*a,**kw))
    def vina(*a,**kw):return measure('vina_score_only' if kw.get('score_only',False) else 'vina_redocking',lambda:original_vina(*a,**kw))
    vc.vina_command=vina
    def bust(self,*a,**kw):return measure('posebusters',lambda:original_bust(self,*a,**kw))
    vc.PoseBusters.bust=bust
    # Shared references: one fresh measurement for all 23 original input pools.
    for cohort in cohorts:
        context(cohort,0)
        for pid in sorted(candidates[cohort].pocket_id.unique()):
            CURRENT=dict(cohort=cohort,pocket_id=pid,candidate_id='reference',repeat=0)
            dest=vc.ROOT/'records'/pid/'reference'/'docking.json';assert not dest.exists()
            out=measure('reference_total',lambda:vc.dock_one({'pocket_id':pid},True))
            print('REFERENCE',cohort,pid,out['status'],round(EVENTS[-1]['wall_seconds'],3),flush=True)
    # Two fresh passes; reverse the input order on the second pass to expose
    # within-process order effects rather than reporting only the best pass.
    diagnostics=[]
    for repeat in [1,2]:
        for cohort in cohorts:
            root=context(cohort,repeat)
            for pid in sorted(candidates[cohort].pocket_id.unique()):
                ref=root/'records'/pid/'reference';ref.parent.mkdir(exist_ok=True,parents=True)
                ref.symlink_to((H/'benchmark/shared'/cohort/'records'/pid/'reference').resolve(),target_is_directory=True)
            route=cases[cases.cohort.eq(cohort)&cases.benchmark_group.eq('route_input_hash')].sort_values('h',ascending=repeat==1)
            for row in route.to_dict('records'):
                CURRENT=dict(cohort=cohort,pocket_id=row['pocket_id'],candidate_id=row['candidate_id'],repeat=repeat)
                assert not (root/'records'/row['pocket_id']/row['candidate_id']/'route.json').exists()
                out=measure('route_total',lambda:acq.route_one(row));diagnostics.append(dict(**CURRENT,component='route',D=out['D'],status=out['status']))
                print('ROUTE',repeat,cohort,row['candidate_id'],out['status'],round(EVENTS[-1]['wall_seconds'],3),flush=True)
                pd.DataFrame(EVENTS).to_csv(H/'results/fresh_component_times.csv',index=False)
            downstream=cases[cases.cohort.eq(cohort)&cases.benchmark_group.eq('archived_route_passed_downstream')].sort_values('h',ascending=repeat==1)
            for row in downstream.to_dict('records'):
                CURRENT=dict(cohort=cohort,pocket_id=row['pocket_id'],candidate_id=row['candidate_id'],repeat=repeat)
                assert not (root/'records'/row['pocket_id']/row['candidate_id']/'docking.json').exists()
                out=measure('downstream_total',lambda:vc.dock_one(row));diagnostics.append(dict(**CURRENT,component='downstream',V=out['V'],Q=out['Q'],status=out['status']))
                print('DOWNSTREAM',repeat,cohort,row['candidate_id'],out['status'],round(EVENTS[-1]['wall_seconds'],3),flush=True)
                pd.DataFrame(EVENTS).to_csv(H/'results/fresh_component_times.csv',index=False)
    STOP=True;thread.join(timeout=1)
    pd.DataFrame(EVENTS).to_csv(H/'results/fresh_component_times.csv',index=False);pd.DataFrame(diagnostics).to_csv(H/'results/fresh_repeat_outcomes.csv',index=False)
    for n,v in json.loads((H/'checks/frozen_guards.json').read_text()).items():assert sha(R/n)==v,n
    hardware=dict(cpu=subprocess.check_output(['sysctl','-n','machdep.cpu.brand_string'],text=True).strip(),memory_bytes=int(subprocess.check_output(['sysctl','-n','hw.memsize'],text=True)),logical_cpus=os.cpu_count(),platform=platform.platform(),python=sys.version,peak_process_tree_RSS_MiB=PEAK/2**20,thread_environment={k:os.environ[k] for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS']},versions={k:importlib.metadata.version(k) for k in ['numpy','pandas','rdkit','aizynthfinder','meeko','posebusters','onnxruntime','psutil']},resource_sha256=resources)
    (H/'results/chemistry_hardware.json').write_text(json.dumps(hardware,indent=2)+'\n')
    out=dict(status='PASS',fresh_route_calls=16,fresh_downstream_calls=40,fresh_shared_reference_calls=23,records=len(EVENTS),serial_single_task_driver=True,Vina_cpu=1,PoseBusters_archived_default_threading=True,cold_OS_cache_claim=False,previous_endpoints_replaced=False,old61_resumed=False)
    (H/'checks/fresh_chemistry.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
if __name__=='__main__':main()
