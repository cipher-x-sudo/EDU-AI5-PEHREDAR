import json
from pathlib import Path
from evaluate import evaluate
sets={'dev_public':'dev_public.jsonl','external_eval':'external_eval.jsonl','indirect_eval':'indirect_eval.jsonl','overrefusal_eval':'overrefusal_eval.jsonl','benign_email_probe':'benign_email_probe.jsonl'}
models={'v0':'models/clf_v0','v1a_e1':'models/clf_v1_e1','v1a_e2':'models/clf_v1_e2','rules':None,'deberta':None}
def summarize(ps):
 tp=sum(p['label']=='attack' and p['risk']>=p.get('_threshold',.5) for p in ps); fn=sum(p['label']=='attack' and p['risk']<p.get('_threshold',.5) for p in ps); fp=sum(p['label']=='benign' and p['risk']>=p.get('_threshold',.5) for p in ps); tn=sum(p['label']=='benign' and p['risk']<p.get('_threshold',.5) for p in ps)
 return {'count':len(ps),'recall':tp/(tp+fn) if tp+fn else None,'fpr':fp/(fp+tn) if fp+tn else None,'f1':2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else None}
out={}
for m,d in models.items():
 out[m]={}; dev=evaluate(Path('data/processed/dev_public.jsonl'), 'rules' if m=='rules' else m if m=='deberta' else 'classifier', d)
 if m in ('rules','deberta'): th=.75 if m=='rules' else .5
 else:
  benign=sorted(p['risk'] for p in dev['predictions'] if p['label']=='benign'); th=benign[max(0,min(len(benign)-1,int(len(benign)*.98)))]
 out[m]['threshold']=th
 for name,f in sets.items():
  r=evaluate(Path('data/processed')/f,'rules' if m=='rules' else 'deberta' if m=='deberta' else 'classifier',d)
  for p in r['predictions']: p['_threshold']=th
  z={'overall':summarize(r['predictions']),'per_source':{}}
  for s in sorted(set(p.get('source','unknown') for p in r['predictions'])):
   q=[p for p in r['predictions'] if p.get('source','unknown')==s]; z['per_source'][s]=summarize(q)
  z['median_latency_ms']=r['median_latency_ms']; z['p95_latency_ms']=r['p95_latency_ms']; out[m][name]=z
Path('results/v1a_evaluation.json').write_text(json.dumps(out,indent=2),encoding='utf8')
