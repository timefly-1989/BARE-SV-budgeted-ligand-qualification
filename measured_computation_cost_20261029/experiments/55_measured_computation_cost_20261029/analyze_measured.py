"""Cost summaries: measured work, serial profiles and synchronized scoring."""
from pathlib import Path
import json
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
H=Path(__file__).resolve().parent
def main():
    old=pd.read_csv(H/'data/recorded_candidate_costs.csv');cohort=pd.read_csv(H/'results/recorded_cohort_costs.csv');work=pd.read_csv(H/'results/measured_work_policy_replay.csv');raw=pd.read_csv(H/'results/fresh_component_times.csv');score=pd.read_csv(H/'results/fresh_scoring_times.csv')
    ids=['cohort','pocket_id','candidate_id'];profiles=[];case_values=[]
    for phase in ['reference_total','route_total','downstream_total','ligand_preparation','vina_score_only','vina_redocking','posebusters']:
        z=raw[raw.phase.eq(phase)]
        if phase not in ['reference_total','route_total','downstream_total']:z=z[z.candidate_id.ne('reference')]
        med=z.groupby(ids)[['wall_seconds','cpu_seconds']].median().reset_index()
        if med.empty:continue
        profiles.append(dict(phase=phase,cases=len(med),calls=len(z),wall_median=float(med.wall_seconds.median()),wall_min=float(med.wall_seconds.min()),wall_max=float(med.wall_seconds.max()),CPU_median=float(med.cpu_seconds.median())))
        med['phase']=phase;case_values.append(med)
    profiles=pd.DataFrame(profiles);profiles.to_csv(H/'results/chemistry_component_summary.csv',index=False);pd.concat(case_values).to_csv(H/'results/per_input_median_times.csv',index=False)
    repeat=pd.read_csv(H/'results/fresh_repeat_outcomes.csv');route=repeat[repeat.component.eq('route')].merge(old[ids+['D']],on=ids,suffixes=('_fresh','_archived'),validate='many_to_one');route['label_differs']=route.D_fresh.ne(route.D_archived);route.to_csv(H/'results/route_repeat_comparison.csv',index=False)
    # Recorded task work for the unchanged reference scores at the original
    # main candidate-count budget; a timing-aware ranking is never substituted.
    reference=work[work.method.eq('chemeleon_dual_full_compact')&work.B.eq(32)&work.algorithm.isin(['uniform','recycling','global'])].copy();reference.to_csv(H/'results/main_measured_work.csv',index=False)
    scoring=score.groupby(['cohort','component','phase'])[['wall_seconds','self_cpu_seconds']].agg(['median','min','max','count']).reset_index();scoring.columns=['_'.join(filter(None,v)) if isinstance(v,tuple) else v for v in scoring.columns];scoring.to_csv(H/'results/scoring_component_summary.csv',index=False)
    algorithms=score[score.phase.eq('selection_with_returned_label_replay')].groupby(['cohort','B','component'])[['wall_seconds','self_cpu_seconds']].median().reset_index();algorithms.to_csv(H/'results/selection_overhead_summary.csv',index=False)
    summary=dict(archived_candidates=len(old),archived_route_passed=int(old.D.sum()),archived_qualified=int(old.y.sum()),archived_total_route_task_hours=float(old.route_wall_seconds.sum()/3600),archived_total_downstream_task_minutes=float(old.downstream_wall_seconds.sum()/60),fresh_route_calls=int((raw.phase=='route_total').sum()),fresh_downstream_calls=int((raw.phase=='downstream_total').sum()),fresh_reference_calls=int((raw.phase=='reference_total').sum()),component_profiles=profiles.to_dict('records'),route_diagnostic_label_differences=int(route.label_differs.sum()),measured_work=reference.astype(object).where(pd.notna(reference),None).to_dict('records'),fresh_scoring_records=len(score),new_independent_efficacy_campaigns=0,known_actual_costs_used_online=False,new_confirmatory_tests=0)
    (H/'results/manuscript_numbers.json').write_text(json.dumps(summary,indent=2)+'\n')
    names={'37_independent_qualification_20261027':'CrossDocked','44_moad_allocation_test_20261027':'MOAD'};pol={'uniform':'Uniform','recycling':'DPQR','global':'Global'}
    for zh in [False,True]:
        caption=('冻结化学排序的实测任务耗时记账。当前参考评分器、每池配额32；CrossDocked/MOAD分别352/384次检查。逐任务墙钟时间从原始化学日志核对并按已选集合求和，不是独立运行各策略获得的活动墙钟时间或CPU核时；预验证输入与评分开销另行报告。' if zh else 'Measured-task work accounting for frozen chemical rankings. The reference scorer uses quota 32: 352/384 checks for CrossDocked/MOAD. Selected route and downstream elapsed times are audited from original task records. Their sums are not independently timed policy-campaign wall time or CPU-core time; shared input construction and scoring are reported separately.')
        lines=[r'\begin{table}[!htbp]\centering\small',r'\caption{'+caption+r'}\label{tab:measured-work}',r'\begin{tabular}{llrrrr}\toprule',('队列 & 策略 & 回收 & 丢失 & 路线任务小时 & 下游任务分钟' if zh else 'Cohort & Policy & Recovery & Loss & Route task h & Downstream min')+r'\\\midrule']
        for row in reference.itertuples():lines.append(f"{names[row.cohort]} & {pol[row.algorithm]} & {int(row.C)} & {int(row.baseline_lost)} & {row.route_task_sum_seconds/3600:.3f} & {row.downstream_task_sum_seconds/60:.2f}"+r'\\')
        lines += [r'\bottomrule\end{tabular}\end{table}'];(H/'tables'/('measured_work_zh.tex' if zh else 'measured_work.tex')).write_text('\n'.join(lines)+'\n')
        label={'reference_total':'Shared reference total','route_total':'Route total','downstream_total':'Conditional downstream total','ligand_preparation':'Ligand preparation','vina_score_only':'Vina score only','vina_redocking':'Vina redocking','posebusters':'PoseBusters'}
        lines=[r'\begin{table}[!htbp]\centering\small',r'\caption{'+('新串行化学成本测量，秒。路线和下游先逐输入取两次重复的中位数，再跨输入汇总；共享参照逐输入一次。下游仅包含原路线通过的20个条件工程样本。总调用与其内部子项重叠，不能相加；范围不是置信区间，失败及超时保留。' if zh else 'Fresh serial chemical measurements, seconds. Two repeats are first reduced to a median for each route/downstream input, then summarized across inputs; shared references have one run each. Downstream cases are the 20 archived route-passed engineering cases. Total calls overlap their internal components and must not be added; ranges are not confidence intervals. Failures and timeouts remain included.')+r'}\label{tab:si-real-components}',r'\begin{tabular}{lrrrr}\toprule',r'Component & Inputs/calls & Wall median & Wall range & CPU median\\\midrule']
        for row in profiles.itertuples():lines.append(f"{label[row.phase]} & {row.cases}/{row.calls} & {row.wall_median:.3f} & {row.wall_min:.3f}--{row.wall_max:.3f} & {row.CPU_median:.3f}"+r'\\')
        lines += [r'\bottomrule\end{tabular}\end{table}'];(H/'tables'/('real_components_zh.tex' if zh else 'real_components.tex')).write_text('\n'.join(lines)+'\n')
        lines=[r'\begin{table}[!htbp]\centering\small',r'\caption{'+('新分配器开销中位数，毫秒；一次预热后五次重复，包含初始化和已返回标签的数值回放，不执行化学验证。每个设置终止选择集合精确相同。' if zh else 'Fresh median allocator overhead, milliseconds: five repeats after one warmup, including policy initialization and returned-label numerical replay, with no chemical execution. Terminal selected sets match exactly within every setting.')+r'}\label{tab:si-real-selection}',r'\begin{tabular}{lrrrr}\toprule',r'Policy & CrossDocked 8 & CrossDocked 32 & MOAD 8 & MOAD 32\\\midrule']
        for algorithm in ['uniform','recycling','global','shield_forecast4','shield_posterior','shield_UCB','shield_search32']:
            vals=[]
            for e in names:
                for B in [8,32]:vals.append(1000*float(algorithms[algorithms.cohort.eq(e)&algorithms.B.eq(B)&algorithms.component.eq(algorithm)].iloc[0].wall_seconds))
            lines.append(algorithm.replace('_',r'\_')+' & '+' & '.join(f'{v:.2f}' for v in vals)+r'\\')
        lines += [r'\bottomrule\end{tabular}\end{table}'];(H/'tables'/('real_selection_zh.tex' if zh else 'real_selection.tex')).write_text('\n'.join(lines)+'\n')
        specs=[('CheMeleon','graph_featurization_and_encoding','Graph + encoding'),('CheMeleon','saved_scaler_PCA_transform','Saved scaler + PCA'),('Route prior','prior_weights_and_inference','Route-prior load + inference'),('Route full','TFM_constructor_and_context_fit','Route TFM setup'),('Route full','TFM_query_prediction','Route TFM prediction'),('Conditional compact','TFM_constructor_and_context_fit','Conditional TFM setup'),('Conditional compact','TFM_query_prediction','Conditional TFM prediction'),('Joint full','TFM_constructor_and_context_fit','Joint TFM setup'),('Joint full','TFM_query_prediction','Joint TFM prediction'),('Conditional CatBoost','archived_classical_model_load','Conditional CatBoost load'),('Conditional CatBoost','archived_classical_query_prediction','Conditional CatBoost prediction'),('Joint RF','archived_classical_model_load','Joint RF load'),('Joint RF','archived_classical_query_prediction','Joint RF prediction')]
        lines=[r'\begin{table}[!htbp]\centering\small',r'\caption{'+('新批量评分实测墙钟时间，秒。CrossDocked/MOAD分别为704/576条查询。设置与预测逐次独立计时；除模型加载一次外均为三次重复的中位数。相同冻结输入与模型；CPU经典模型仅用已有表征作查询预测，不包含重新拟合，因此不是训练成本比较。' if zh else 'Fresh batch scoring wall time, seconds, for 704/576 CrossDocked/MOAD queries. Setup and prediction are timed separately. Values are three-repeat medians, except classical model loading measured once. Inputs and models remain frozen. Classical prediction uses existing representations without refitting, so this is not a training-cost comparison.')+r'}\label{tab:si-real-scoring}',r'\begin{tabular}{lrr}\toprule',r'Component & CrossDocked & MOAD\\\midrule']
        for component,phase,label in specs:
            vals=[float(scoring[scoring.cohort.eq(c)&scoring.component.eq(component)&scoring.phase.eq(phase)].iloc[0].wall_seconds_median) for c in names]
            lines.append(label+' & '+' & '.join(f'{v:.4f}' for v in vals)+r'\\')
        lines += [r'\bottomrule\end{tabular}\end{table}'];(H/'tables'/('real_scoring_zh.tex' if zh else 'real_scoring.tex')).write_text('\n'.join(lines)+'\n')
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'svg.fonttype':'none'})
    fig,axes=plt.subplots(1,2,figsize=(9,3.7),layout='constrained');med=pd.concat(case_values)
    for k,(phase,label,color) in enumerate([('route_total','Route\n8 inputs','#007d82'),('downstream_total','Downstream\n20 conditional inputs','#66509a'),('reference_total','Reference\n23 inputs','#bf7833')]):
        z=med[med.phase.eq(phase)];offset=np.linspace(-.12,.12,len(z));axes[0].scatter(k+offset,z.wall_seconds,s=14,alpha=.7,color=color);axes[0].plot([k-.18,k+.18],[z.wall_seconds.median()]*2,color='black',lw=2);axes[1].scatter(z.wall_seconds,z.cpu_seconds,s=20,label=label.replace('\n',' '),color=color,alpha=.7)
    axes[0].set_xticks([0,1,2],['Route\n8 inputs','Downstream\n20 conditional','Reference\n23 inputs']);axes[0].set(ylabel='Per-input elapsed seconds (log scale)',yscale='log',title='A  Real serial task latency');mx=max(med.wall_seconds.max(),med.cpu_seconds.max());axes[1].plot([0,mx],[0,mx],ls='--',color='#999',lw=1);axes[1].set(xlabel='Elapsed seconds',ylabel='Self plus waited-child CPU seconds',title='B  Wall and CPU differ');axes[1].legend(frameon=False,fontsize=9)
    for ext in ['pdf','svg','png']:fig.savefig(H/'figures'/('measured_latency.'+ext),dpi=200)
    plt.close(fig);curves=pd.read_csv(H/'results/measured_work_curves.csv');fig,axes=plt.subplots(1,2,figsize=(9,3.5),layout='constrained')
    for ax,(cohort,name) in zip(axes,names.items()):
        for algorithm,color in [('uniform','#777'),('recycling','#007d82'),('global','#bf7833')]:
            z=curves[curves.cohort.eq(cohort)&curves.algorithm.eq(algorithm)];ax.step(z.selected_task_sum_seconds/3600,z.C,where='post',label=pol[algorithm],color=color)
        ax.set(title=name,xlabel='Selected task elapsed sum (h)',ylabel='Recovered qualified candidates');ax.legend(frameon=False,fontsize=10);ax.grid(alpha=.15)
    for ext in ['pdf','svg','png']:fig.savefig(H/'figures'/('recorded_work.'+ext),dpi=200)
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
