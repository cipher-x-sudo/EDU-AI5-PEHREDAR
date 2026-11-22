import os
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, model_validator


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


class Policy(BaseModel):
    tenant: str = "default"
    thresholds: Thresholds = Field(default_factory=Thresholds)


def load_policy() -> Policy:
    path = Path(os.getenv("PEHREDAR_POLICY_PATH", Path(__file__).resolve().parent.parent / "config" / "policy.yaml"))
    return Policy.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")) or {})
