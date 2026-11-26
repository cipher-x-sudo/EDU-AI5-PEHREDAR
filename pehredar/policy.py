import os
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator


class Thresholds(BaseModel):
    warn: float = Field(0.45, ge=0, le=1)
    judge_low: float = Field(0.30, ge=0, le=1)
    block: float = Field(0.75, ge=0, le=1)

    @model_validator(mode="after")
    def ordered(self):
        if self.warn >= self.block:
            raise ValueError("warn must be lower than block")
        if self.judge_low >= self.block:
            raise ValueError("judge_low must be lower than block")
        return self


class L2Policy(BaseModel):
    # routed: en -> DeBERTa, other languages -> the XLM-R classifier; deberta / xlmr: one model; max: both
    mode: Literal["routed", "deberta", "xlmr", "max"] = "routed"
    # Threshold for the XLM-R (non-English) path; None = the model's training_report.json threshold.
    # Must match the model in PEHREDAR_L2_XLMR_DIR (chosen on dev, see results/clf_v3_recal.md).
    xlmr_threshold: float | None = Field(default=None, gt=0, lt=1)

    @field_validator("mode", mode="before")
    @classmethod
    def legacy_v2(cls, value):
        return "xlmr" if value == "v2" else value  # policies stored before the rename


class JudgePolicy(BaseModel):
    # An XLM-R score under its threshold goes to the L3 judge only if it is >= xlmr_floor
    # (0 = always, as before; 1 = never). Below the floor it is capped under judge_low (allow).
    xlmr_floor: float = Field(0.0, ge=0, le=1)
    # Judge "unsafe" blocks only if a category is in this list (None = any category); otherwise warn.
    # "controversial" always warns.
    block_categories: list[str] | None = None


class Policy(BaseModel):
    tenant: str = "default"
    thresholds: Thresholds = Field(default_factory=Thresholds)
    l2: L2Policy = Field(default_factory=L2Policy)
    judge: JudgePolicy = Field(default_factory=JudgePolicy)


def load_policy() -> Policy:
    path = Path(os.getenv("PEHREDAR_POLICY_PATH", Path(__file__).resolve().parent.parent / "config" / "policy.yaml"))
    return Policy.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")) or {})
