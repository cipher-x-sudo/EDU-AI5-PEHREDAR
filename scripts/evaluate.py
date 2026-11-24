import argparse
import hashlib
import json
import statistics
import time
from functools import lru_cache
from pathlib import Path

from pehredar.classifier import score_classifier
from pehredar.dataset import load_jsonl
from pehredar.normalizer import normalize_text
from pehredar.rules import score_rules


@lru_cache(maxsize=1)
def load_deberta():
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    name = "protectai/deberta-v3-base-prompt-injection-v2"
    tokenizer = AutoTokenizer.from_pretrained(name)
    model = AutoModelForSequenceClassification.from_pretrained(name)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()
    label = next(index for index, value in model.config.id2label.items() if value.upper() == "INJECTION")
    return tokenizer, model, torch, int(label), device


def score_deberta(text: str) -> float:
    tokenizer, model, torch, label, device = load_deberta()
    encoded = tokenizer(text, truncation=True, max_length=512, return_tensors="pt")
    encoded = {k: v.to(device) for k, v in encoded.items()}
    with torch.no_grad():
        return torch.softmax(model(**encoded).logits, dim=-1)[0, label].item()


def evaluate(path: Path, detector: str = "rules", classifier_dir: str | None = None) -> dict:
    if detector not in {"rules", "deberta", "classifier", "combined"}:
        raise ValueError(f"Unknown detector: {detector}")
    if detector in {"classifier", "combined"} and not classifier_dir:
        raise ValueError("classifier_dir is required")
    rows = load_jsonl(path)
    texts = [normalize_text(r.input_text()) for r in rows]
    t0 = time.perf_counter()
    rule_scores = []
    tags_all = []
    for text in texts:
        risk, tags = score_rules(text)
        rule_scores.append(risk); tags_all.append(tags)
    scores_by = {"rules": rule_scores}
    thresholds = [0.75] * len(rows)
    if detector in {"classifier", "combined"}:
        if not Path(classifier_dir).exists():
            vals, clf_threshold = [], 0.5
            for text in texts:
                value, clf_threshold = score_classifier(text, classifier_dir)
                vals.append(value)
            scores_by["classifier"] = vals
            thresholds = [clf_threshold] * len(rows)
            # Continue with the same prediction and reporting path.
            classifier_loaded = True
        else:
            classifier_loaded = False
        if classifier_loaded:
            pass
        else:
            tokenizer, model, torch, clf_threshold, device = _load_classifier(classifier_dir)
            vals=[]
            for i in range(0, len(texts), 64):
                enc=tokenizer(texts[i:i+64], truncation=True, max_length=256, padding=True, return_tensors="pt")
                enc = {k: v.to(device) for k, v in enc.items()}
                with torch.no_grad(): vals.extend(torch.softmax(model(**enc).logits, dim=-1)[:,1].tolist())
            scores_by["classifier"] = vals
            if detector == "classifier": thresholds=[clf_threshold]*len(rows)
    if detector == "deberta":
        tokenizer, model, torch, label, device = load_deberta(); vals=[]
        for i in range(0, len(texts), 32):
            enc=tokenizer(texts[i:i+32], truncation=True, max_length=512, padding=True, return_tensors="pt")
            enc = {k: v.to(device) for k, v in enc.items()}
            with torch.no_grad(): vals.extend(torch.softmax(model(**enc).logits, dim=-1)[:,label].tolist())
        scores_by["deberta"] = vals; thresholds=[0.5]*len(rows)
    predictions=[]
    for i,row in enumerate(rows):
        if detector == "rules": risk=rule_scores[i]
        elif detector == "deberta": risk=scores_by["deberta"][i]
        elif detector == "classifier": risk=scores_by["classifier"][i]
        else:
            risk=max(rule_scores[i], 0.75 if scores_by["classifier"][i] >= thresholds[i] else scores_by["classifier"][i]); thresholds[i]=0.75
        predictions.append({"id":row.id,"lang":row.lang,"label":row.label,"prediction":"attack" if risk>=thresholds[i] else "benign","risk":risk,"scores":{k:v[i] for k,v in scores_by.items()},"tags":tags_all[i],"latency_ms":0.0})
    elapsed_ms=(time.perf_counter()-t0)*1000
    per=elapsed_ms/max(1,len(rows)); [p.update({"latency_ms":per}) for p in predictions]
    metrics={}
    def summarize(group):
        tp=sum(p["label"]=="attack" and p["prediction"]=="attack" for p in group); fn=sum(p["label"]=="attack" and p["prediction"]=="benign" for p in group); fp=sum(p["label"]=="benign" and p["prediction"]=="attack" for p in group); tn=sum(p["label"]=="benign" and p["prediction"]=="benign" for p in group)
        return {"count":len(group),"tp":tp,"fn":fn,"fp":fp,"tn":tn,"recall":tp/(tp+fn) if tp+fn else None,"false_positive_rate":fp/(fp+tn) if fp+tn else None,"f1":2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else None,"median_latency_ms":per if group else None,"p95_latency_ms":per if group else None}
    for language in ("en","ur","roman_ur","mixed"): metrics[language]=summarize([p for p in predictions if p["lang"]==language])
    by_source={}
    for source in sorted({r.source or "unknown" for r in rows}): by_source[source]=summarize([p for p,r in zip(predictions,rows) if (r.source or "unknown")==source])
    return {"input_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"detector":detector,"classifier_dir":classifier_dir,"deberta_scope":"English prompt injection only" if detector=="deberta" else None,"metrics":metrics,"per_source":by_source,"indirect_eval_source_scope":{s:("seen distribution" if s=="llmail" else "unseen") for s in by_source} if path.name=="indirect_eval.jsonl" else None,"median_latency_ms":per,"p95_latency_ms":per,"predictions":predictions}

@lru_cache(maxsize=1)
def _load_classifier(directory):
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    path=Path(directory)
    report_path = path / "training_report.json"
    if not report_path.exists():
        report_path = path / "model_card.md"
    raw = report_path.read_text(encoding="utf-8")
    if report_path.name == "model_card.md":
        raw = raw[raw.find("{"):]
    report = json.loads(raw)
    tokenizer=AutoTokenizer.from_pretrained(path,local_files_only=True); model=AutoModelForSequenceClassification.from_pretrained(path,local_files_only=True); device=torch.device("cuda" if torch.cuda.is_available() else "cpu"); model.to(device); model.eval(); return tokenizer,model,torch,float(report["threshold"]),device


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--detector", choices=("rules", "deberta", "classifier", "combined"), default="rules")
    parser.add_argument("--classifier-dir")
    args = parser.parse_args()
    report = evaluate(args.dataset, args.detector, args.classifier_dir)
    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
