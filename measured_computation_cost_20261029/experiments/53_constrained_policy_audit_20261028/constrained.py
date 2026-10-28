"""Matched certificate proposals. Only reveal() receives a selected source label."""
from pathlib import Path
import sys,numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'50_discovery_allocation_20261028'))
from policies import Policy,simulate as previous_simulate

ALGORITHMS=['uniform','recycling','shield_fixed','shield_forecast4','shield_observed4','shield_posterior','shield_UCB','shield_search32','pilot_posterior']
class ConstrainedPolicy(Policy):
    def __init__(self,score,pool,key,B,algorithm,seed=11):
        super().__init__(score,pool,key,B,'latent_greedy' if algorithm in ['shield_posterior','shield_UCB','shield_search32','pilot_posterior'] else 'global',seed)
        self.proposal=algorithm;self.is_baseline=np.zeros(len(self.u),bool);self.is_baseline[self.uniform]=True
        self.restricted_steps=0;self.free_steps=0;self.search_evaluations=0
    def obligations(self):return self.active & self.is_baseline & ~np.isin(self.group,list(self.hits))
    def action(self):
        O=self.obligations();r=self.K-len(self.selected);h=int(O.sum());assert h<=r
        allowed=np.flatnonzero(self.active if h<r else O)
        self.free_steps+=int(h<r);self.restricted_steps+=int(h==r)
        a=self.proposal
        if a=='pilot_posterior' and h:
            # A fixed-prefix pilot barrier, followed by unrestricted posterior ranking.
            choices=[]
            for order in self.orders:
                pending=order[O[order]]
                if len(pending):choices.append((int(np.flatnonzero(order==pending[0])[0]),str(self.pool[pending[0]]),int(pending[0])))
            return min(choices)[2]
        q=self.mean() if self.latent else self.u.copy()
        if a=='shield_forecast4':q*=1+4*self.nohit[self.group]
        elif a=='shield_observed4':q*=1+4*np.array([g not in self.hits for g in self.group])
        elif a=='shield_UCB':
            theta=np.array([min(len(w)-1,int(np.searchsorted(np.cumsum(w),.95))) for w in self.weight]);q=self.likelihood[np.arange(len(q)),theta[self.group]]
        elif a=='shield_search32' and r>1 and len(allowed)>1:
            shortlist=set(sorted(allowed,key=lambda i:(-q[i],self.pool[i],self.key[i]))[:32])
            for j in range(len(self.names)):
                v=allowed[self.group[allowed]==j]
                if len(v):
                    shortlist.add(self.tie(q,v));shortlist.add(int(min(v,key=lambda i:(abs(q[i]-.5),self.key[i]))))
            values=np.full(len(q),-np.inf)
            for i in sorted(shortlist):
                j=self.group[i];rest=self.active.copy();rest[i]=False;local=np.flatnonzero(self.active&(self.group==j));tail=[]
                for y in [0,1]:
                    w=self.weight[j]*(self.likelihood[i] if y else 1-self.likelihood[i]);w/=w.sum();pp=q.copy();pp[local]=self.likelihood[local]@w
                    obligation=O.copy();obligation[i]=False
                    if y:obligation[self.group==j]=False
                    free=r-1-int(obligation.sum());assert free>=0
                    tail.append(float(pp[obligation].sum())+self.topsum(pp,np.flatnonzero(rest&~obligation),free))
                values[i]=q[i]+(1-q[i])*tail[0]+q[i]*tail[1];self.search_evaluations+=1
            return self.tie(values,sorted(shortlist))
        return self.tie(q,allowed)

def simulate(score,pool,key,y,B,algorithm,seed=11):
    if algorithm in ['uniform','recycling','global']:return previous_simulate(score,pool,key,y,B,algorithm,seed)
    p=ConstrainedPolicy(score,pool,key,B,algorithm,seed);y=np.asarray(y,int)
    for _ in range(p.K):
        i=p.action();p.reveal(i,int(y[i]));assert int(p.obligations().sum())<=p.K-len(p.selected)
    ix=np.asarray(p.selected,int);base={p.pool[i] for i in p.uniform if y[i]};hits={p.pool[i] for i in ix if y[i]};assert base<=hits
    return dict(K=p.K,C=int(y[ix].sum()),coverage=len(hits),baseline_coverage=len(base),baseline_lost=0,score_sum=float(p.u[ix].sum()),restricted_steps=p.restricted_steps,free_steps=p.free_steps,search_evaluations=p.search_evaluations),ix,[]

def hindsight_value(group,baseline,state,remaining,y):
    """Exact label-informed optimum over universally admissible action paths.

    It uses complete labels ONLY for a retrospective upper bound, never ranking.
    The escape/no-escape formula is independently checked by exhaustive search.
    """
    group=np.asarray(group);state=np.asarray(state);y=np.asarray(y);active=state<0;hits=set(group[state==1]);O=active&np.asarray(baseline,bool)&~np.isin(group,list(hits));h=int(O.sum());assert h<=remaining
    escape=remaining>h or any(int((O&(group==j)).sum())>=2 and bool(y[O&(group==j)].sum()) for j in set(group))
    if not escape:return int(y[O].sum())
    unavoidable_zero=sum(int((O&(group==j)).sum()) for j in set(group) if not bool(y[active&(group==j)].sum()))
    return min(int(y[active].sum()),remaining-unavoidable_zero)
