"""Resumable Ollama translation pilot for public training rows."""
import csv, json, os, re, time, random
from pathlib import Path
import requests

ROOT=Path("data/processed"); OUT=ROOT/"translated.jsonl"; REVIEW=ROOT/"translation_review.csv"
MODEL="richardyoung/qwen3-8b-abliterated:Q4_K_M"; HOST=os.getenv("OLLAMA_HOST","http://ollama:11434")
EXAMPLES=json.loads(Path("scripts/translation_examples.json").read_text(encoding="utf-8"))

def rows():
    return [json.loads(x) for x in (ROOT/"train_public.jsonl").open(encoding="utf-8") if x.strip()]
def valid(value, lang, original):
    if not isinstance(value,str) or not (len(original)*.5 <= len(value) <= len(original)*2): return False
    urdu=bool(re.search(r"[\u0600-\u06ff]",value)); latin=len(re.findall(r"[A-Za-z]",value))
    if lang=="ur" and not urdu: return False
    if lang=="roman_ur" and urdu: return False
    if lang=="roman_ur" and latin and len(re.findall(r"\b(?:the|and|is|are|what|how|please)\b",value,re.I))>max(2,latin//20): return False
    if lang=="mixed" and (latin < 3 or latin > len(value)*.9): return False
    return not any(x in value.lower() for x in ("@", "cnic", "iban"))
def call(original):
    prompt="/no_think\nReturn JSON with keys roman_ur, ur, mixed. Preserve intent and target exactly. "+json.dumps({"text":original,"examples":EXAMPLES},ensure_ascii=False)
    payload={"model":MODEL,"messages":[{"role":"user","content":prompt}],"stream":False,"think":False,
             "format":"json","options":{"temperature":0.3,"num_ctx":4096,"num_predict":1024}}
    last=None
    for attempt in range(3):
        try:
            r=requests.post(HOST+"/api/chat",json=payload,timeout=180); r.raise_for_status()
            return json.loads(r.json()["message"]["content"])
        except Exception as exc:
            last=exc
            if attempt < 2: time.sleep(1)
    raise last
def main():
    existing={json.loads(x)["orig_id"] for x in OUT.open(encoding="utf-8")} if OUT.exists() else set()
    source=rows(); attacks=[r for r in source if r["label"]=="attack"]; benign=[r for r in source if r["label"]=="benign"]
    random.Random(42).shuffle(attacks); random.Random(43).shuffle(benign)
    chosen=attacks[:100]+benign[:100]; chosen.sort(key=lambda r:r["id"]); passed=failed=0; durations=[]
    warm=time.perf_counter(); call("Reply with JSON keys roman_ur, ur, mixed for: hello")
    print(f"WARMUP_SECONDS {time.perf_counter()-warm:.2f}", flush=True)
    with OUT.open("a",encoding="utf-8") as out:
      for r in chosen:
        if r["id"] in existing: continue
        st=time.perf_counter()
        try:
          result=call(r["text"]); good=True
          for lang in ("roman_ur","ur","mixed"):
            if not valid(result.get(lang),lang,r["text"]): good=False
          if not good: raise ValueError("validation failed")
          for lang in ("roman_ur","ur","mixed"):
            out.write(json.dumps({"id":f"translated-{r['id']}-{lang}","text":result[lang],"lang":lang,"label":r["label"],"type":r["type"],"source":"translated","orig_id":r["id"],"split_group":r["split_group"],"usage":"train"},ensure_ascii=False)+"\n")
          passed+=1
        except Exception as e:
          failed+=1; print(f"FAILED {r['id']}: {type(e).__name__}: {e}", flush=True)
        durations.append(time.perf_counter()-st)
        n=passed+failed
        if n and n % 10 == 0:
          rate=n/sum(durations); eta=(200-n)/rate if rate else 0
          print(f"PROGRESS done={n} failed={failed} rows_per_min={rate*60:.2f} eta_seconds={eta:.1f}", flush=True)
    allrows=[json.loads(x) for x in OUT.open(encoding="utf-8") if x.strip()]
    sample=random.Random(44).sample(allrows,min(50,len(allrows)))
    with REVIEW.open("w",newline="",encoding="utf-8") as f:
      w=csv.writer(f); w.writerow(["orig_id","original","lang","translation","reviewer","verdict","note"])
      for x in sample:
        original=next((r["text"] for r in source if r["id"]==x["orig_id"]),""); w.writerow([x["orig_id"],original,x["lang"],x["text"],"","",""])
    print(json.dumps({"attempted":passed+failed,"passed":passed,"failed":failed,"validation_rate":passed/(passed+failed) if passed+failed else 0,"seconds_per_row":sum(durations)/len(durations) if durations else 0,"pilot_stopped":True}))
if __name__=="__main__": main()
