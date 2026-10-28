"""Finite-pool controls. Selectors see inputs and selected feedback only.

The UCB/TS controls use a declared pool-logit latent model. The conservative
variant protects frozen score sum, not realized reward. ENS-style search uses
a 32-candidate shortlist plus pool representatives and one-step batch completion;
it is not presented as the authors' complete ENS implementation.
"""
import numpy as np
from scipy.special import expit,logit

GRID=np.arange(-3,3.01,.5)
WEIGHTS=np.exp(-GRID**2/2);WEIGHTS/=WEIGHTS.sum()
CONTROLS=['uniform','global','recycling','latent_greedy','latent_TS','latent_UCB','score_conservative_UCB','ENS_style32']
CONTROLS += [kind+str(lam) for kind in ['forecast_','observed_'] for lam in [.25,1,4,16,64]]

class Policy:
    def __init__(self,score,pool,key,B,algorithm,seed=11):
        self.u=np.asarray(score,float);self.pool=np.asarray(pool,str);self.key=np.asarray(key,str)
        assert np.isfinite(self.u).all() and len(self.u)==len(self.pool)==len(self.key)
        self.names=sorted(set(self.pool));self.group=np.array([self.names.index(x) for x in self.pool])
        self.orders=[np.array(sorted(np.flatnonzero(self.group==j),key=lambda i:(-self.u[i],self.key[i])),int) for j in range(len(self.names))]
        self.uniform=np.concatenate([ix[:min(B,len(ix))] for ix in self.orders]);self.K=len(self.uniform)
        self.active=np.ones(len(self.u),bool);self.selected=[];self.hits=set();self.B=B;self.algorithm=algorithm
        self.rng=np.random.default_rng(seed);self.ptr=np.zeros(len(self.names),int);self.pilot=True;self.pilot_calls=0
        self.weight=np.tile(WEIGHTS,(len(self.names),1));self.likelihood=expit(logit(np.clip(self.u,1e-6,1-1e-6))[:,None]+GRID)
        self.nohit=np.ones(len(self.names));self.uniform_score=float(self.u[self.uniform].sum())
        self.latent=algorithm.startswith('latent_') or algorithm in ['score_conservative_UCB','ENS_style32']
    def tie(self,values,indices=None):
        ix=np.flatnonzero(self.active) if indices is None else np.asarray(indices,int)
        best=np.max(values[ix]);c=ix[values[ix]>=best-1e-12]
        return int(min(c,key=lambda i:(self.pool[i],self.key[i])))
    def mean(self): return np.einsum('ij,ij->i',self.likelihood,self.weight[self.group])
    @staticmethod
    def topsum(p,ix,n):
        if n<=0:return 0.
        v=p[ix]
        if len(v)<=n:return float(v.sum())
        return float(np.partition(v,len(v)-n)[-n:].sum())
    def action(self):
        a=self.algorithm;active=np.flatnonzero(self.active)
        if a=='uniform':return int(self.uniform[len(self.selected)])
        if a=='recycling' and self.pilot:
            eligible=[j for j,ix in enumerate(self.orders) if j not in self.hits and self.ptr[j]<min(self.B,len(ix))]
            if eligible:
                j=min(eligible,key=lambda j:(self.ptr[j],self.names[j]));return int(self.orders[j][self.ptr[j]])
            self.pilot=False
        p=self.u.copy()
        if a.startswith('forecast_'):p*=1+float(a.split('_')[1])*self.nohit[self.group]
        elif a.startswith('observed_'):p*=1+float(a.split('_')[1])*np.array([j not in self.hits for j in self.group])
        elif self.latent:
            p=self.mean()
            if a=='latent_TS':
                theta=[self.rng.choice(len(GRID),p=w) for w in self.weight];p=self.likelihood[np.arange(len(p)),np.array(theta)[self.group]]
            elif a in ['latent_UCB','score_conservative_UCB']:
                theta=np.array([min(len(GRID)-1,int(np.searchsorted(np.cumsum(w),.95))) for w in self.weight]);p=self.likelihood[np.arange(len(p)),theta[self.group]]
                if a=='score_conservative_UCB':
                    r=self.K-len(self.selected);rank=sorted(active,key=lambda i:(-self.u[i],self.pool[i],self.key[i]));top=set(rank[:r]);topr=float(self.u[rank[:r]].sum());toprm1=float(self.u[rank[:r-1]].sum())
                    spent=float(self.u[self.selected].sum());feasible=[i for i in active if spent+(topr if i in top else self.u[i]+toprm1)>=self.uniform_score-1e-10]
                    assert feasible
                    return self.tie(p,feasible)
            elif a=='ENS_style32' and self.K-len(self.selected)>1:
                shortlist=set(sorted(active,key=lambda i:(-p[i],self.pool[i],self.key[i]))[:32])
                for j in range(len(self.names)):
                    v=active[self.group[active]==j]
                    if len(v):
                        shortlist.add(self.tie(p,v));shortlist.add(int(min(v,key=lambda i:(abs(p[i]-.5),self.key[i]))))
                val=np.full(len(p),-np.inf);left=self.K-len(self.selected)-1
                for i in sorted(shortlist):
                    j=self.group[i];rest=active[active!=i];local=np.flatnonzero(self.group==j)
                    gains=[]
                    for y in [0,1]:
                        w=self.weight[j]*(self.likelihood[i] if y else 1-self.likelihood[i]);w/=w.sum()
                        pp=p.copy();pp[local]=self.likelihood[local]@w;gains.append(self.topsum(pp,rest,left))
                    val[i]=p[i]+(1-p[i])*gains[0]+p[i]*gains[1]
                return self.tie(val,sorted(shortlist))
        return self.tie(p)
    def reveal(self,i,y):
        assert self.active[i] and y in [0,1]
        j=self.group[i]
        if self.algorithm=='recycling' and self.pilot:
            assert i==self.orders[j][self.ptr[j]];self.ptr[j]+=1;self.pilot_calls+=1
        self.active[i]=False;self.selected.append(int(i));self.nohit[j]*=1-self.u[i]
        if y:self.hits.add(j)
        if self.latent:
            self.weight[j]*=self.likelihood[i] if y else 1-self.likelihood[i];self.weight[j]/=self.weight[j].sum()

def simulate(score,pool,key,y,B,algorithm,seed=11,trace=False):
    policy=Policy(score,pool,key,B,algorithm,seed);y=np.asarray(y,int)
    assert set(y)<=set([0,1]);events=[]
    for step in range(policy.K):
        i=policy.action();policy.reveal(i,int(y[i]))
        if trace:events.append(dict(step=step+1,index=i,y=int(y[i])))
    ix=np.array(policy.selected,int);baseline={policy.pool[i] for i in policy.uniform if y[i]};hits={policy.pool[i] for i in ix if y[i]}
    if algorithm=='recycling':assert baseline<=hits
    if algorithm=='score_conservative_UCB':assert policy.u[ix].sum()>=policy.uniform_score-1e-8
    return dict(K=policy.K,C=int(y[ix].sum()),coverage=len(hits),baseline_coverage=len(baseline),baseline_lost=len(baseline-hits),
        score_sum=float(policy.u[ix].sum()),pilot_calls=policy.pilot_calls if algorithm=='recycling' else None),ix,events
