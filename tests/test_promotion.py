from pehredar.promotion import Counts, LANGUAGES, promotion_gate


def test_regressing_candidate_is_rejected():
    old = {lang: Counts(8, 2, 1, 9) for lang in LANGUAGES}
    new = {lang: Counts(9, 1, 1, 9) for lang in LANGUAGES}
    new["roman_ur"] = Counts(9, 1, 2, 8)
    passed, reasons = promotion_gate(old, new)
    assert not passed
    assert "roman_ur: false-positive rate rose" in reasons


def test_improvement_with_no_regression_passes():
    old = {lang: Counts(8, 2, 1, 9) for lang in LANGUAGES}
    new = dict(old)
    new["roman_ur"] = Counts(9, 1, 1, 9)
    assert promotion_gate(old, new) == (True, [])
