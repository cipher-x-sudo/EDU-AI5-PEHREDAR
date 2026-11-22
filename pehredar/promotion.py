from dataclasses import dataclass

LANGUAGES = ("en", "ur", "roman_ur", "mixed")


@dataclass(frozen=True)
class Counts:
    tp: int
    fn: int
    fp: int
    tn: int

    @property
    def recall(self) -> float | None:
        return self.tp / (self.tp + self.fn) if self.tp + self.fn else None

    @property
    def fpr(self) -> float | None:
        return self.fp / (self.fp + self.tn) if self.fp + self.tn else None


def promotion_gate(old: dict[str, Counts], new: dict[str, Counts]) -> tuple[bool, list[str]]:
    reasons = []
    improved = False
    for language in LANGUAGES:
        prior = old.get(language)
        candidate = new.get(language)
        if prior is None or candidate is None or prior.recall is None or prior.fpr is None:
            reasons.append(f"{language}: missing evaluation counts")
            continue
        if candidate.tp + candidate.fn != prior.tp + prior.fn or candidate.fp + candidate.tn != prior.fp + prior.tn:
            reasons.append(f"{language}: test sample counts changed")
            continue
        if candidate.recall is None or candidate.fpr is None:
            reasons.append(f"{language}: missing candidate rates")
            continue
        if candidate.recall < prior.recall:
            reasons.append(f"{language}: recall regressed")
        if candidate.fpr > prior.fpr:
            reasons.append(f"{language}: false-positive rate rose")
        if candidate.recall > prior.recall:
            improved = True
    if not improved:
        reasons.append("no language improved recall")
    return not reasons, reasons
