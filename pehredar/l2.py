"""L2: language-routed classifier ensemble.

routed (default): en -> ProtectAI DeBERTa; roman_ur / mixed / ur / other -> Pehredar XLM-R v2.
deberta / v2: always that model. max: both models, attack if either is over its own threshold.
If the routed model failed to load, the other one is used (tag l2_fallback). If none is loaded,
score() raises L2Unavailable and the gateway fails closed (503).
Models are loaded once by load() at startup; torch/transformers are imported only there."""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

MODES = ("routed", "deberta", "v2", "max")
DEBERTA_NAME = "protectai/deberta-v3-base-prompt-injection-v2"
DEBERTA_THRESHOLD = 0.5


class L2Unavailable(RuntimeError):
    pass


@dataclass
class Scorer:
    threshold: float
    fn: Callable[[str], float]


@dataclass
class L2:
    models: dict[str, Scorer] = field(default_factory=dict)
    errors: dict[str, str] = field(default_factory=dict)
    load_seconds: dict[str, float] = field(default_factory=dict)
    device: str | None = None
    vram_gb: float | None = None

    def load(self, v2_dir: str) -> "L2":
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
        from .clf_text import encode
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.device = str(device)

        def deberta():
            tok = AutoTokenizer.from_pretrained(DEBERTA_NAME)
            model = AutoModelForSequenceClassification.from_pretrained(DEBERTA_NAME).to(device).eval()
            label = next(i for i, v in model.config.id2label.items() if v.upper() == "INJECTION")

            def fn(text):
                enc = {k: v.to(device) for k, v in tok(text, truncation=True, max_length=512, return_tensors="pt").items()}
                with torch.no_grad():
                    return torch.softmax(model(**enc).logits, dim=-1)[0, int(label)].item()
            return Scorer(DEBERTA_THRESHOLD, fn)

        def v2():
            path = Path(v2_dir)
            report = json.loads((path / "training_report.json").read_text(encoding="utf-8"))
            tok = AutoTokenizer.from_pretrained(path, local_files_only=True)
            model = AutoModelForSequenceClassification.from_pretrained(path, local_files_only=True).to(device).eval()
            version = int(report.get("encoder_version", 1))

            def fn(text):
                enc = tok.pad([encode(tok, text, version)], return_tensors="pt")
                enc = {k: v.to(device) for k, v in enc.items()}
                with torch.no_grad():
                    return torch.softmax(model(**enc).logits, dim=-1)[0, 1].item()
            return Scorer(float(report["threshold"]), fn)

        for name, loader in (("deberta", deberta), ("v2", v2)):
            started = time.perf_counter()
            try:
                self.models[name] = loader()
            except Exception as exc:  # a missing model must not stop the other one
                self.errors[name] = f"{type(exc).__name__}: {exc}"[:300]
            self.load_seconds[name] = round(time.perf_counter() - started, 2)
        if device.type == "cuda":
            self.vram_gb = round(torch.cuda.memory_allocated() / 2**30, 2)
        return self

    def status(self) -> dict:
        return {"loaded": sorted(self.models), "errors": self.errors, "load_seconds": self.load_seconds,
                "device": self.device, "vram_allocated_gb": self.vram_gb,
                "thresholds": {k: m.threshold for k, m in self.models.items()}}

    def score(self, text: str, lang: str, mode: str) -> dict:
        """Returns scores, which models ran, hit (any used model over its threshold), risk and tags.
        risk follows the old single-classifier rule: block_risk if hit, else the highest raw score."""
        if mode not in MODES:
            raise ValueError(f"unknown l2 mode {mode}")
        if not self.models:
            raise L2Unavailable("no L2 model loaded")
        wanted = ["deberta", "v2"] if mode == "max" else [mode] if mode in ("deberta", "v2") else \
                 ["deberta" if lang == "en" else "v2"]
        used = [m for m in wanted if m in self.models]
        tags = []
        if not used:
            used = sorted(self.models)[:1]
            tags.append(f"l2_fallback:{wanted[0]}->{used[0]}")
        elif len(used) < len(wanted):
            tags.append(f"l2_missing:{','.join(m for m in wanted if m not in self.models)}")
        scores, latency = {}, {}
        for m in used:
            started = time.perf_counter()
            scores[m] = self.models[m].fn(text)
            latency[m] = round((time.perf_counter() - started) * 1000, 3)
        hit = any(scores[m] >= self.models[m].threshold for m in used)
        return {"scores": scores, "used": used, "hit": hit, "tags": tags, "latency_ms": latency,
                "thresholds": {m: self.models[m].threshold for m in used}}


def from_env() -> L2 | None:
    """PEHREDAR_L2=1 enables L2; PEHREDAR_L2_V2_DIR points at the v2 model (default models/clf_v2_e2)."""
    if os.getenv("PEHREDAR_L2", "") != "1":
        return None
    return L2().load(os.getenv("PEHREDAR_L2_V2_DIR", "models/clf_v2_e2"))
