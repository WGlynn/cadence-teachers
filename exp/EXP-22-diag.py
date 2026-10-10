"""EXP-22 diagnostic: trace parent vs label-taught child through test trips, in-context."""
import os,importlib.util,numpy as np,cadence as cd
s=importlib.util.spec_from_file_location('e22','EXP-22_generation_chains.py');e22=importlib.util.module_from_spec(s);s.loader.exec_module(e22)
from key_door import corridor,observe,KINDS,INTERACT,CHEST
e19,e20=e22.e19,e22.e20
f=e19.make_brain(e19.POINT,60_001,None,True); e20.teach(f,e19.interleave("A"*300,"B"*300),np.random.default_rng(3001))
pp=f.save(os.path.join(e19.TMP,'p.npz'))
c=e19.make_brain(e19.POINT,70_101,None,True); e22.teach_by_labels(c,pp,300,np.random.default_rng(4101))
cp=c.save(os.path.join(e19.TMP,'c.npz'))
for name,p in (('parent',pp),('child',cp)):
    b=cd.Brain.load(p); rng=np.random.default_rng(1)
    print(name,'cold labels',e22.labels(p))
    for t in range(2):
        holding=False; seq=[]
        for cell in corridor(2,15,2,rng):
            a=int(b.act(observe(cell,holding,True),greedy=True)[0]); seq.append(f"{KINDS[cell][:2]}{'+' if holding else ''}:{'I' if a else '.'}")
            if a==INTERACT and cell==CHEST and not holding: holding=True
        b.reset(); print(' ',' '.join(seq))
