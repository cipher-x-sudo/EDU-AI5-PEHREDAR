"""Train/evaluate the English-only XLM-R v0 baseline on public data."""
import argparse, hashlib, json, random, statistics, time
from pathlib import Path
import torch
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModelForSequenceClassification, AutoTokenizer

ROOT = Path("data/processed")
BASE = "FacebookAI/xlm-roberta-base"
SEED = 42

def load(name):
    return [json.loads(x) for x in (ROOT / name).open(encoding="utf-8") if x.strip()]

def text(row):
    return row.get("text") or "\n".join(t["content"] for t in (row.get("turns") or []))

def encode(tokenizer, value):
    ids = tokenizer(value, add_special_tokens=True, truncation=False)["input_ids"]
    if len(ids) <= 512: return {"input_ids": ids, "attention_mask": [1]*len(ids)}
    keep = 510
    head, tail = keep // 2, keep - keep // 2
    ids = [ids[0]] + ids[1:1+head] + ids[-tail:] + [ids[-1]]
    return {"input_ids": ids, "attention_mask": [1]*len(ids)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--grad-accum", type=int, default=1)
    args = ap.parse_args()
    random.seed(SEED); torch.manual_seed(SEED)
    train = [r for r in load("train_public.jsonl") if r["lang"] == "en"]
    dev = [r for r in load("dev_public.jsonl") if r["lang"] == "en"]
    if args.smoke:
        attack_rows = [r for r in train if r["label"] == "attack"]
        benign_rows = [r for r in train if r["label"] == "benign"]
        train = attack_rows[:100] + benign_rows[:100]
    if not train or not dev: raise RuntimeError("English public train/dev data is empty")
    tokenizer = AutoTokenizer.from_pretrained(BASE)
    model = AutoModelForSequenceClassification.from_pretrained(BASE, num_labels=2,
        id2label={0:"benign",1:"attack"}, label2id={"benign":0,"attack":1})
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu"); model.to(device)
    use_fp16 = device.type == "cuda"
    class DS(Dataset):
        def __init__(self, rows): self.rows=rows
        def __len__(self): return len(self.rows)
        def __getitem__(self,i):
            r=self.rows[i]; x=encode(tokenizer,text(r)); x["labels"]=1 if r["label"]=="attack" else 0; return x
    def collate(items):
        labels=torch.tensor([x.pop("labels") for x in items])
        batch=tokenizer.pad(items,padding=True,return_tensors="pt"); batch["labels"]=labels; return batch
    loader=DataLoader(DS(train),batch_size=args.batch_size,shuffle=True,collate_fn=collate)
    counts=[sum(r["label"]==x for r in train) for x in ("benign","attack")]
    weights=torch.tensor([len(train)/(2*c) for c in counts],device=device)
    opt=torch.optim.AdamW(model.parameters(),lr=2e-5); start=time.perf_counter()
    steps = 0
    scaler = torch.amp.GradScaler("cuda", enabled=use_fp16)
    opt.zero_grad()
    for _ in range(2):
        model.train()
        for batch in loader:
            batch={k:v.to(device) for k,v in batch.items()}
            with torch.autocast(device_type="cuda", dtype=torch.float16, enabled=use_fp16):
                out=model(**{k:v for k,v in batch.items() if k!="labels"})
                loss = torch.nn.functional.cross_entropy(out.logits,batch["labels"],weight=weights) / args.grad_accum
            scaler.scale(loss).backward()
            if steps % args.grad_accum == args.grad_accum - 1:
                scaler.step(opt); scaler.update(); opt.zero_grad()
            steps += 1
            if steps % 50 == 0 or (args.smoke and steps == 20):
                vram = torch.cuda.max_memory_allocated()/2**30 if device.type == "cuda" else 0
                print(f"step={steps} loss={loss.item()*args.grad_accum:.4f} vram_gb={vram:.2f}", flush=True)
            if args.smoke and steps >= 20:
                break
        if args.smoke and steps >= 20:
            break
    model.eval()
    def score(rows):
        out=[]
        with torch.no_grad():
            for r in rows:
                st=time.perf_counter(); x=encode(tokenizer,text(r))
                b={k:torch.tensor([v]).to(device) for k,v in x.items()}
                risk=torch.softmax(model(**b).logits,dim=-1)[0,1].item()
                out.append({**r,"risk":risk,"latency_ms":(time.perf_counter()-st)*1000})
        return out
    scored=score(dev); candidates=sorted({0.5,*(r["risk"] for r in scored)})
    def f1(th):
        tp=sum(r["label"]=="attack" and r["risk"]>=th for r in scored); fp=sum(r["label"]=="benign" and r["risk"]>=th for r in scored); fn=sum(r["label"]=="attack" and r["risk"]<th for r in scored)
        return 2*tp/(2*tp+fp+fn) if tp+fp+fn else 0
    threshold=max(candidates,key=lambda x:(f1(x),x))
    dest=Path("models/clf_v0"); dest.mkdir(parents=True,exist_ok=True); model.save_pretrained(dest); tokenizer.save_pretrained(dest)
    report={"data_commit":"0746919","base_model":BASE,"base_revision":getattr(model.config,"_commit_hash",None),"dataset_sha256":hashlib.sha256((ROOT/"train_public.jsonl").read_bytes()).hexdigest(),"epochs":2,"max_length":512,"truncation":"head+tail","seed":SEED,"threshold":threshold,"train_count":len(train),"dev_count":len(dev),"device":str(device),"training_seconds":time.perf_counter()-start}
    (dest/"model_card.md").write_text("# Pehredar classifier v0\n\n"+json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))
if __name__=="__main__": main()
