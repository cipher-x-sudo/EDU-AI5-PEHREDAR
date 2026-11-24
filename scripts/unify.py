"""Unify downloaded public datasets. Run: python -m scripts.unify."""
import ast
import csv
import gzip
import hashlib
import json
import os
import random
import re
import unicodedata
import zipfile
from datetime import date
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

from pehredar.output_guard import PII_PATTERNS, SECRET_PATTERNS

RAW, OUT = Path("data/raw"), Path("data/processed")
FILES = ("injection_train", "multiturn", "indirect_eval", "harm",
         "overrefusal_eval", "pii_eval", "external_eval", "urdu_benign",
         "extraction_eval", "translation_pairs")
COUNTS = defaultdict(Counter)
POOL = []
OUTPUT = defaultdict(list)
SEEN = set()
MAX_PROMPT = 12_000
PII_EXEMPT_EVAL = {"injecagent", "bipia", "agentdojo"}
ROMAN = {"hai", "nahi", "kya", "mujhe", "aur", "karo", "bhai", "yaar"}
ENGLISH = {"the", "is", "are", "what", "how", "please", "can", "you", "to", "of"}


@lru_cache
def source_metadata(name):
    path = RAW / name / "metadata.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def norm(text):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", text).casefold()).strip()


def near_hash(text):
    collapsed = re.sub(r"[\W_]+", " ", norm(text), flags=re.UNICODE).strip()
    return hashlib.sha256(collapsed.encode()).hexdigest()


def redact_pii(text):
    for pattern in PII_PATTERNS + SECRET_PATTERNS:
        text = pattern.sub("[REDACTED]", text)
    return text


def group(text):
    value = re.sub(r"\b\d+\b", "#", unicodedata.normalize("NFKC", text))
    value = re.sub(r"\b[A-Z][a-z]+\b", "<name>", value)
    value = norm(value)
    return hashlib.sha256(value.encode()).hexdigest()[:20]


def lang(text):
    words = re.findall(r"[a-z]+", text.casefold())
    arabic = len(re.findall(r"[\u0600-\u06ff]", text))
    if arabic > len(text) * .2:
        return "ur" if len(words) < 3 else "mixed"
    if not words:
        return "other"
    ru_words = {w for w in words if w in ROMAN}
    ru = len(ru_words) / len(words)
    en = sum(w in ENGLISH for w in words) / len(words)
    # A few English words in names, addresses, or email text must not create a
    # mixed label; require at least two distinct Roman Urdu markers.
    if len(ru_words) >= 2 and ru > .2 and en > .2:
        return "mixed"
    return "roman_ur" if len(ru_words) >= 2 and ru > .2 else "en"


def source_lang(name, text):
    detected = lang(text)
    if name in {"smat26", "uci_roman_urdu", "erupd"} and detected == "en":
        return "roman_ur"
    return detected


def rows(name):
    folder = RAW / name
    if not (folder / "metadata.json").exists():
        return
    meta = json.loads((folder / "metadata.json").read_text(encoding="utf-8"))
    for rel in meta["files"]:
        path = folder / rel
        if not path.exists():
            continue
        if path.suffix == ".parquet":
            import pyarrow.parquet as pq
            for batch in pq.ParquetFile(path).iter_batches(batch_size=2048):
                for row in batch.to_pylist():
                    yield rel, row
        elif path.suffix in (".csv", ".tsv"):
            with path.open(encoding="utf-8-sig", errors="replace", newline="") as stream:
                reader = csv.reader(stream) if name == "smat26" else csv.DictReader(
                    stream, delimiter="\t" if path.suffix == ".tsv" else ","
                )
                for row in reader:
                    yield rel, row
        elif path.suffix in (".json", ".jsonl", ".gz"):
            stream = gzip.open(path, "rt", encoding="utf-8") if path.suffix == ".gz" else path.open(encoding="utf-8")
            with stream as f:
                if path.suffix == ".jsonl" or path.suffix == ".gz":
                    for line in f:
                        yield rel, json.loads(line)
                else:
                    data = json.load(f)
                    for row in data if isinstance(data, list) else [data]:
                        yield rel, row


def add(file, name, text, label, kind, original, usage="train", turns=None, extra=None):
    COUNTS[name]["downloaded"] += 1
    if not isinstance(text, str):
        COUNTS[name]["unclear"] += 1
        return False
    text = text.strip()
    if (len(text) < 3 or
            (turns is None and len(text) > MAX_PROMPT) or
            (turns is not None and any(len(turn["content"]) > MAX_PROMPT for turn in turns))):
        COUNTS[name]["length"] += 1
        return False
    response = (extra or {}).get("response")
    has_pii = any(p.search(value) for value in (text, response)
                  if isinstance(value, str) for p in PII_PATTERNS + SECRET_PATTERNS)
    if file != "pii_eval" and has_pii:
        if file == "indirect_eval" and name in PII_EXEMPT_EVAL:
            COUNTS[name]["pii_exempt"] += 1
        else:
            COUNTS[name]["pii"] += 1
            return False
    detected_lang = source_lang(name, text)
    if file == "injection_train" and detected_lang == "other":
        COUNTS[name]["lang_other"] += 1
        return False
    key = norm(text)
    if key in SEEN:
        COUNTS[name]["duplicate"] += 1
        return False
    SEEN.add(key)
    meta = source_metadata(name)
    record = {"id": f"{name}-{COUNTS[name]['downloaded']}", "text": text, "lang": detected_lang,
              "label": label, "type": kind, "source": name, "split_group": group(text),
              "usage": usage, "redistributable": meta.get("redistributable", False),
              "license": meta.get("license", "synthetic"), "turns": turns, "orig_label": original}
    if extra:
        record.update(extra)
    (POOL if file == "injection_train" else OUTPUT[file]).append(record)
    COUNTS[name]["kept"] += 1
    return True


def mapped(name, row, field, label, attack_values, benign_values, kind, file="injection_train", usage="train", extra=None):
    value = row.get(label)
    if value in attack_values:
        mapped_label, mapped_kind = "attack", kind
    elif value in benign_values:
        mapped_label, mapped_kind = "benign", "none"
    else:
        COUNTS[name]["unclear"] += 1
        OUTPUT["unclear_" + name].append({"row": row, "reason": f"unrecognized {label}"})
        return
    add(file, name, row.get(field), mapped_label, mapped_kind, value, usage, extra=extra)


def capped_sample(groups, limit, denominator, seed=42, multiple=1, preserve_keys=()):
    """Largest deterministic sample with no group above 1/denominator."""
    rng = random.Random(seed)
    choices = {key: list(values) for key, values in groups.items() if values}
    for key, values in choices.items():
        if key not in preserve_keys:
            rng.shuffle(values)
    maximum = min(limit, sum(map(len, choices.values())))
    size = next((n for n in range(maximum - maximum % multiple, 0, -multiple)
                 if sum(min(len(values), n // denominator)
                        for values in choices.values()) >= n), 0)
    cap = size // denominator
    selected = []
    for index in range(cap):
        for key in sorted(choices):
            if index < len(choices[key]) and len(selected) < size:
                selected.append(choices[key][index])
    return selected


def main():
    COUNTS.clear()
    POOL.clear()
    OUTPUT.clear()
    SEEN.clear()
    source_metadata.cache_clear()
    OUT.mkdir(parents=True, exist_ok=True)
    for name, field, label, attack, benign, kind in [
        ("deepset_pi", "text", "label", {1}, {0}, "injection"),
        ("safeguard_pi", "text", "label", {1}, {0}, "injection"),
        ("jb_class", "prompt", "type", {"jailbreak"}, {"benign"}, "jailbreak"),
    ]:
        for rel, row in rows(name) or []:
            usage = "secondary_eval" if "test" in rel else "train"
            mapped(name, row, field, label, attack, benign, kind,
                   file="injection_train" if usage == "train" else "external_eval", usage=usage)
    for name in ("jailbreak_llms",):
        for rel, row in rows(name) or []:
            label = "benign" if "regular" in rel else "attack"
            add("injection_train", name, row.get("prompt"), label,
                "none" if label == "benign" else "jailbreak", row.get("jailbreak", label))
    # Diverse benign email corpus. The source card is recorded in PROVENANCE.md;
    # rows are redacted and capped before global balancing.
    enron_seen = 0
    for _, row in rows("enron") or []:
        if enron_seen >= 2000:
            break
        subject = row.get("subject") or row.get("Subject")
        body = row.get("body") or row.get("Body") or row.get("text") or row.get("content")
        if not isinstance(body, str):
            continue
        if not subject:
            match = re.search(r"(?im)^Subject:\s*(.+)$", body)
            subject = match.group(1).strip() if match else "Message"
        text = redact_pii(f"Subject: {str(subject).strip()}\nBody: {body.strip()[:1500]}")
        if add("injection_train", "enron", text, "benign", "none", "email", extra={"email_format": True}):
            enron_seen += 1
    # Normal English user instructions are hard benign negatives.
    dolly_seen = 0
    for _, row in rows("dolly") or []:
        if dolly_seen >= 5000:
            break
        text = row.get("instruction") or row.get("context")
        if isinstance(text, str) and text.strip():
            if add("injection_train", "dolly", text, "benign", "none", "first_user_turn",
                   extra={"hard_negative": True}):
                dolly_seen += 1
    oasst_seen = 0
    for _, row in rows("oasst1") or []:
        if oasst_seen >= 5000:
            break
        if str(row.get("lang", "en")).lower() not in {"en", "english"}:
            continue
        text = row.get("text") or row.get("message")
        if isinstance(text, str) and text.strip() and str(row.get("role", "prompter")).lower() in {"prompter", "user"}:
            if add("injection_train", "oasst1", text, "benign", "none", "first_user_turn",
                   extra={"hard_negative": True}):
                oasst_seen += 1
    for _, row in rows("spml") or []:
        system, prompt = row.get("System Prompt"), row.get("User Prompt")
        if not isinstance(system, str) or not isinstance(prompt, str):
            COUNTS["spml"]["unclear"] += 1
            continue
        mapped("spml", {"text": prompt.strip(),
                        "label": row.get("Prompt injection")}, "text", "label",
               {"1", 1}, {"0", 0}, "injection",
               extra={"contextual": True, "system_prompt": system.strip(),
                      "hard_negative": row.get("Prompt injection") in {"0", 0}})
    llmail_counts = Counter()
    llmail_train_groups = set()
    for rel, row in rows("llmail") or []:
        if llmail_counts["train"] >= 2000 and llmail_counts["eval"] >= 2000:
            break
        subject, body = row.get("subject"), row.get("body")
        if not isinstance(subject, str) or not isinstance(body, str):
            COUNTS["llmail"]["unclear"] += 1
            continue
        text = f"Subject: {subject.strip()}\nBody: {body.strip()}"
        clean = redact_pii(text)
        if clean != text:
            COUNTS["llmail"]["pii_redacted"] += 1
        text = clean
        if llmail_counts["train"] < 2000:
            if add("injection_train", "llmail", text, "attack", "injection",
                   row.get("scenario", "submission")):
                llmail_counts["train"] += 1
                llmail_train_groups.add(group(text))
        elif group(text) not in llmail_train_groups and add("indirect_eval", "llmail", text, "attack", "injection",
                 row.get("scenario", "submission"), "eval_only"):
            llmail_counts["eval"] += 1
    hack_candidates = defaultdict(list)
    hack_order = {}
    hack_seen = set()
    for _, row in rows("hackaprompt") or []:
        if not {"user_input", "expected_completion"} <= row.keys():
            raise ValueError("HackAPrompt file schema differs from expected user_input/expected_completion")
        goal = row.get("expected_completion")
        if not isinstance(goal, str) or not goal.strip():
            COUNTS["hackaprompt"]["unclear"] += 1
            continue
        goal = norm(goal)
        prompt = row.get("user_input")
        if not isinstance(prompt, str):
            COUNTS["hackaprompt"]["unclear"] += 1
            continue
        key = near_hash(prompt)
        if key in hack_seen:
            COUNTS["hackaprompt"]["near_duplicate"] += 1
            continue
        if len(hack_candidates[goal]) >= 2000:
            COUNTS["hackaprompt"]["goal_cap"] += 1
            continue
        if add("injection_train", "hackaprompt", prompt,
               "attack", "injection", row.get("level"), extra={"goal": goal}):
            hack_seen.add(key)
            hack_candidates[goal].append(POOL[-1])
    if hack_candidates:
        chosen = capped_sample(hack_candidates, 5000, 5)
        hack_order = {row["id"]: index for index, row in enumerate(chosen)}
        chosen_ids = {row["id"] for row in chosen}
        excluded = [row for values in hack_candidates.values() for row in values
                    if row["id"] not in chosen_ids]
        COUNTS["hackaprompt"]["goal_cap"] += len(excluded)
        COUNTS["hackaprompt"]["kept"] -= len(excluded)
        SEEN.difference_update(norm(row["text"]) for row in excluded)
        POOL[:] = [row for row in POOL if row["source"] != "hackaprompt" or row["id"] in chosen_ids]
    wild_counts = Counter()
    for rel, row in rows("wildjailbreak") or []:
        data_type = row.get("data_type")
        if data_type not in {"adversarial_harmful", "adversarial_benign"}:
            continue
        if wild_counts[data_type] >= 8000:
            continue
        text = row.get("adversarial")
        label = "attack" if data_type == "adversarial_harmful" else "benign"
        if add("injection_train", "wildjailbreak", text, label,
               "jailbreak" if label == "attack" else "none", data_type,
               extra={"hard_negative": label == "benign"}):
            wild_counts[data_type] += 1
    for _, row in rows("gandalf") or []:
        add("injection_train", "gandalf", row.get("text"), "attack", "extraction", "password extraction")
    wildguard_count = 0
    for rel, row in rows("wildguardmix") or []:
        if "train" not in rel or wildguard_count >= 3000:
            break
        if not {"prompt", "prompt_harm_label", "adversarial"} <= row.keys():
            raise ValueError("WildGuardMix train schema requires prompt, prompt_harm_label, adversarial")
        # Harm pool only: as injection attacks these teach "harmful topic = attack";
        # harmful content is the Qwen3Guard judge's job (v2 data change).
        if row.get("adversarial") is True and row.get("prompt_harm_label") == "harmful":
            if add("harm", "wildguardmix", row.get("prompt"), "attack", "harm",
                   "adversarial_harmful", "train", extra={"response": row.get("response")}):
                wildguard_count += 1
    for rel, row in rows("tensor_trust") or []:
        if "detecting-extractions" in rel:
            add("extraction_eval", "tensor_trust", row.get("llm_output"), "attack", "extraction", row.get("is_extraction"), "eval_only")
        else:
            add("injection_train", "tensor_trust", row.get("attack"), "attack",
                "extraction" if "extraction" in rel else "injection", rel)
    for rel, row in rows("safemtdata") or []:
        if "SafeMTData_1K" in rel:
            turns = [turn for turn in row.get("conversations", [])
                     if isinstance(turn, dict) and turn.get("role") in {"user", "assistant"}
                     and isinstance(turn.get("content"), str)]
        else:
            turns = [{"role": "user", "content": x} for x in row.get("multi_turn_queries", []) if isinstance(x, str)]
        text = "\n".join(x["content"] for x in turns)
        if turns:
            add("multiturn", "safemtdata", text, "attack", "jailbreak",
                row.get("category", "actor attack"), turns=turns)
    for rel, row in rows("tom_gibbs_multiturn") or []:
        try:
            turns = ast.literal_eval(row["Multi-turn conversation"])
        except (ValueError, SyntaxError, KeyError):
            COUNTS["tom_gibbs_multiturn"]["unclear"] += 1
            continue
        if not isinstance(turns, list) or not all(isinstance(t, dict) and t.get("role") in {"user", "assistant", "system"} and isinstance(t.get("content"), str) for t in turns):
            COUNTS["tom_gibbs_multiturn"]["unclear"] += 1
            continue
        text = "\n".join(t["content"] for t in turns)
        if "Harmful" in rel:
            label, kind = "attack", "jailbreak"
        else:
            label, kind = "benign", "none"
        add("multiturn", "tom_gibbs_multiturn", text, label, kind, rel, turns=turns)
    for name in ("aegis2", "beavertails", "toxicchat", "wildguardmix"):
        for rel, row in rows(name) or []:
            if name == "wildguardmix" and "test" not in rel:
                continue
            if name == "beavertails" and COUNTS[name]["downloaded"] >= 10000:
                break
            if name == "aegis2":
                value = row.get("prompt_label")
                if value not in ("safe", "unsafe"):
                    COUNTS[name]["unclear"] += 1
                    continue
                text, response = row.get("prompt"), row.get("response")
                label = "attack" if value == "unsafe" else "benign"
            elif name == "beavertails":
                value = row.get("is_safe")
                text, response = row.get("prompt"), row.get("response")
                label = "benign" if value else "attack"
            elif name == "toxicchat":
                value = row.get("toxicity")
                text, response = row.get("user_input"), row.get("model_output")
                jailbreaking = row.get("jailbreaking")
                label = "attack" if str(value) == "1" or str(jailbreaking) == "1" else "benign"
            else:
                value = row.get("prompt_harm_label")
                text, response = row.get("prompt"), row.get("response")
                label = "attack" if value == "harmful" else "benign" if value == "unharmful" else None
            if label is None:
                COUNTS[name]["unclear"] += 1
                continue
            if label == "benign" and (
                (name == "aegis2" and value == "safe")
                or (name == "toxicchat" and str(value) == "0"
                    and str(row.get("jailbreaking")) == "0")
            ):
                add("injection_train", name, text, "benign", "none", value,
                    "train", extra={"response": response})
            else:
                add("harm", name, text, label, "harm" if label == "attack" else "none",
                    value, "eval_only" if "test" in rel else "train",
                    extra={"response": response})
    for rel, row in rows("xstest") or []:
        if row.get("label") == "safe":
            mapped("xstest", row, "prompt", "label", set(), {"safe"}, "harm",
                   "overrefusal_eval", "eval_only")
    for rel, row in rows("or_bench") or []:
        add("overrefusal_eval", "or_bench", row.get("prompt"), "benign", "none", row.get("category"), "eval_only")
    for rel, row in rows("harmbench") or []:
        add("harm", "harmbench", row.get("Behavior"), "attack", "harm", "behavior", "eval_only")
    for rel, row in rows("ai4privacy") or []:
        add("pii_eval", "ai4privacy", row.get("source_text"), "attack", "pii", "pii", "eval_only",
            extra={"masked_text": row.get("masked_text")})
        if COUNTS["ai4privacy"]["kept"] >= 5000:
            break
    for i, text in enumerate(("CNIC 00000-0000000-0", "Mobile 0300-0000000", "IBAN PK00FAKE0000000000000000"), 1):
        add("pii_eval", "synthetic", text, "attack", "pii", "synthetic", "eval_only")
    for rel, row in rows("smat26") or []:
        text = row[0] if row else None
        if text:
            add("urdu_benign", "smat26", text, "benign", "none", "sentiment", "train")
    uci = RAW / "uci_roman_urdu" / "roman_urdu.zip"
    if uci.exists():
        with zipfile.ZipFile(uci) as archive:
            candidates = [p for p in archive.namelist() if p.lower().endswith(".csv")]
            if candidates:
                import io
                with archive.open(candidates[0]) as stream:
                    for row in csv.reader(io.TextIOWrapper(stream, encoding="utf-8", errors="replace")):
                        if row:
                            add("urdu_benign", "uci_roman_urdu", row[0], "benign", "none", "sentiment")
    for rel, row in rows("erupd") or []:
        add("translation_pairs", "erupd", row.get("Roman Urdu"), "benign", "none",
            "English/Roman Urdu pair", "eval_only", extra={"english": row.get("English")})
    for rel, row in rows("bipia") or []:
        if isinstance(row, dict):
            for key, values in row.items():
                if isinstance(values, list):
                    for value in values:
                        if isinstance(value, str):
                            add("indirect_eval", "bipia", value, "attack", "injection", key, "eval_only")
    for rel, row in rows("injecagent") or []:
        add("indirect_eval", "injecagent", row.get("Tool Response"),
            "attack", "injection", row.get("Attack Type"), "eval_only")
    for name in list(OUTPUT):
        OUTPUT[name].sort(key=lambda r: r.get("id", ""))
    frozen = Path("data/frozen_test/human_v1.jsonl")
    if os.getenv("PEHREDAR_SKIP_FROZEN") == "1":
        frozen = Path("__sealed_human_set_not_read__")
    if frozen.exists():
        held_out = {norm(json.loads(line)["text"]) for line in frozen.read_text(encoding="utf-8").splitlines() if line.strip()}
        POOL[:] = [row for row in POOL if norm(row["text"]) not in held_out]
        for file, records in OUTPUT.items():
            OUTPUT[file] = [row for row in records if row["usage"] != "train" or norm(row["text"]) not in held_out]
    attacks_by_source = defaultdict(list)
    benign = []
    for row in POOL:
        if row["label"] == "attack":
            attacks_by_source[row["source"]].append(row)
        else:
            benign.append(row)
    if hack_order:
        attacks_by_source["hackaprompt"].sort(key=lambda row: hack_order[row["id"]])
    attacks = capped_sample(attacks_by_source, len(benign) * 2 // 3, 4,
                            multiple=20, preserve_keys={"hackaprompt"})
    benign_needed = len(attacks) * 3 // 2
    rng = random.Random(42)
    hard = [row for row in benign if row.get("hard_negative") or
            re.search(r"\b(?:instructions|system|password|ignore)\b", row["text"], re.I)]
    hard_ids = {row["id"] for row in hard}
    easy = [row for row in benign if row["id"] not in hard_ids]
    rng.shuffle(hard); rng.shuffle(easy)
    # Apply the benign source cap after hard-negative prioritization. When the
    # cap itself causes a shortfall, solve for the largest self-consistent
    # final size so no source exceeds 35% of the rows actually selected.
    available = Counter(row["source"] for row in hard + easy)
    low, high = 0, benign_needed
    while low < high:
        candidate_total = (low + high + 1) // 2
        cap = int(candidate_total * .35)
        capacity = sum(min(count, cap) for count in available.values())
        if capacity >= candidate_total:
            low = candidate_total
        else:
            high = candidate_total - 1
    final_benign_target = low
    max_per_source = int(final_benign_target * .35)
    selected_benign, source_counts = [], Counter()
    for candidate in hard + easy:
        if len(selected_benign) >= final_benign_target:
            break
        source = candidate["source"]
        if source_counts[source] >= max_per_source:
            continue
        selected_benign.append(candidate)
        source_counts[source] += 1
    if len(selected_benign) < benign_needed:
        print(f"WARNING: benign shortfall {benign_needed - len(selected_benign)} rows after 35% source caps")
    OUTPUT["injection_train"] = sorted(attacks + selected_benign, key=lambda row: row["id"])
    train_texts = {norm(row["text"]) for row in OUTPUT["injection_train"]}
    for file, records in list(OUTPUT.items()):
        if file != "injection_train":
            OUTPUT[file] = [
                row for row in records
                if row.get("usage") not in {"eval_only", "secondary_eval"}
                or norm(row["text"]) not in train_texts
            ]
    for name, records in OUTPUT.items():
        with (OUT / (name + ".jsonl")).open("w", encoding="utf-8") as stream:
            for record in records:
                stream.write(json.dumps(record, ensure_ascii=True, default=str) + "\n")
    stats = ["# Public data statistics", "", "File | Label | Type | Lang | Source | Rows", "---|---|---|---|---|---:"]
    for file, records in sorted(OUTPUT.items()):
        counts = Counter((r.get("label"), r.get("type"), r.get("lang"), r.get("source")) for r in records)
        for key, count in sorted(counts.items()):
            stats.append(f"{file} | {' | '.join(str(x) for x in key)} | {count}")
    for row in OUTPUT["injection_train"]:
        COUNTS[row["source"]]["selected_train"] += 1
    stats += ["", "## Filtering by source", "",
              "Source | Scanned | Kept before balancing | Final classifier | Duplicate | Near duplicate | PII dropped | PII redacted | PII exempt in synthetic eval | Length | Other language | Unclear | Goal cap",
              "---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:"]
    for name, count in sorted(COUNTS.items()):
        stats.append(f"{name} | {count['downloaded']} | {count['kept']} | {count['selected_train']} | "
                     f"{count['duplicate']} | {count['near_duplicate']} | {count['pii']} | "
                     f"{count['pii_redacted']} | {count['pii_exempt']} | "
                     f"{count['length']} | {count['lang_other']} | {count['unclear']} | {count['goal_cap']}")
    labels = Counter(r["label"] for r in OUTPUT["injection_train"])
    attack_sources = Counter(r["source"] for r in OUTPUT["injection_train"] if r["label"] == "attack")
    benign_sources = Counter(r["source"] for r in OUTPUT["injection_train"] if r["label"] == "benign")
    stats += ["", "## Final classifier source shares", "",
              "Label | Source | Rows | Share", "---|---|---:|---:"]
    for label, counts in (("attack", attack_sources), ("benign", benign_sources)):
        total = labels[label]
        for source, count in sorted(counts.items()):
            stats.append(f"{label} | {source} | {count} | {count / total:.2%}")
    ratio = labels["benign"] / labels["attack"] if labels["attack"] else 0
    stats += ["", f"Classifier training pool: {labels['attack']} attack, {labels['benign']} benign.",
              f"Actual benign/attack ratio: {ratio:.4f}; target: 1.5000.",
              "Every attack source is capped at 25% of final attacks; every benign source is capped at 35% of final benign rows after hard-negative-first selection.",
              "PII exemption applies only to synthetic indirect-evaluation sources: injecagent, bipia, agentdojo.",
              f"Raw directory size: {sum(p.stat().st_size for p in RAW.rglob('*') if p.is_file()) / 1024**3:.3f} GiB."]
    (Path("data") / "STATS.md").write_text("\n".join(stats) + "\n", encoding="utf-8")
    provenance = [
        "# Public dataset provenance", "",
        f"Generated {date.today()}. Revisions are immutable Hub or GitHub commit hashes unless noted.",
        "Rows downloaded counts source rows scanned by the unifier; rows kept are before the final classifier balancing step.",
        "Raw and processed files remain outside Git.", "",
        "Name | Source URL | Revision | Download date | License | Rows downloaded | Rows kept | Usage | Redistributable | Notes",
        "---|---|---|---|---|---:|---:|---|---|---",
    ]
    notes = {
        "safeguard_pi": "Card does not state a license; skipped pending rights confirmation.",
        "tensor_trust": "Card does not state a license; skipped pending rights confirmation.",
        "red_queen": "Official GitHub/HF source; no explicit dataset license; skipped.",
        "mhj": "Gated; repository has no accessible data file until approval. Nonredistributable.",
        "wildjailbreak": "ODC-By card; access granted. Adversarial harmful and benign rows capped at 8,000 each before global balancing.",
        "wildguardmix": "ODC-By card; access granted. Adversarial harmful train rows (capped at 3,000) go to the harm pool only, not injection_train (v2).",
        "hackaprompt": "MIT card; access granted. Maximum 5,000 training rows and 20% per goal after near-deduplication.",
        "spml": "MIT card; label depends on paired system prompt. Both system and user text retained together.",
        "llmail": "MIT card; Phase2 only. Subject and body joined; PII redacted before deduplication; first 2,000 accepted for training, next 2,000 for indirect evaluation.",
        "necent_merged": "Gated; access denied. Mixed upstream licenses require per-source review.",
        "injectionshield": "Only 3 display examples and summary metrics in repository; benchmark folders are placeholders. No usable full benchmark rows. Never train.",
        "agentdojo": "Task GOAL definitions are not injected payloads; no eval rows extracted. Synthetic indirect-eval PII exemption applies if payloads become available.",
        "bipia": "Only text/code attack lists, no licensed WebQA/Summarization contexts. Synthetic indirect-eval PII exemption.",
        "injecagent": "Synthetic indirect-eval PII exemption; matched rows retained and counted in STATS.md.",
        "erupd": "English/Roman Urdu translation pairs, not attacks.",
        "ai4privacy": "CC BY 4.0 plus Llama Community License terms; marked nonredistributable conservatively.",
        "beavertails": "30k train first 10,000 rows only. Noncommercial and nonredistributable.",
        "toxicchat": "Latest 0124 config. Noncommercial and nonredistributable.",
        "uci_roman_urdu": "UCI dataset 458; overlaps Smat26 and is deduplicated.",
        "dolly": "CC BY-SA 3.0; first instruction field used as English benign hard negatives.",
        "oasst1": "Apache-2.0; English prompter/user messages used as benign hard negatives.",
        "enron": "Apache-2.0 card on the pinned mirror; formatted as Subject/Body, truncated and PII-redacted.",
    }
    for folder in sorted(RAW.iterdir()):
        path = folder / "metadata.json"
        if not path.exists():
            continue
        meta = json.loads(path.read_text(encoding="utf-8"))
        name = folder.name
        count = COUNTS[name]
        usage = ", ".join(sorted({r["usage"] for records in OUTPUT.values()
                                  for r in records if r.get("source") == name})) or "skipped"
        revision = meta["revision"]
        if name == "uci_roman_urdu":
            revision = "sha256:" + hashlib.sha256((folder / "roman_urdu.zip").read_bytes()).hexdigest()
        provenance.append(
            f"{name} | {meta['source_url']} | `{revision}` | {meta['download_date']} | {meta['license']} | "
            f"{count['downloaded']} | {count['kept']} | {usage} | "
            f"{str(meta['redistributable']).lower()} | {notes.get(name, '—')}"
        )
    provenance.append(
        "ruwv_nsr | https://data.mendeley.com/datasets/v5jfhsvtmd/5 | unavailable | "
        "not downloaded | unverified | 0 | 0 | skipped | false | Manual Mendeley download and license review required."
    )
    provenance += [
        "", "## Manual actions for the team", "",
        "- WildJailbreak, WildGuardMix, and HackAPrompt access was verified on 2026-11-23; rerun the downloader when refreshing the pinned revisions.",
        "- https://huggingface.co/datasets/Necent/llm-jailbreak-prompt-injection-dataset — click **Accept**, then check every upstream source license before unifying.",
        "- https://huggingface.co/datasets/ScaleAI/mhj — provide requested contact information and click **Accept**; obtain the actual dataset files from the maintainers.",
        "- https://data.mendeley.com/datasets/v5jfhsvtmd/5 — download RUwV-NSR and confirm its dataset license.",
        "- https://huggingface.co/datasets/xTRam1/safe-guard-prompt-injection — obtain an explicit dataset license from the maintainer.",
        "- https://huggingface.co/datasets/qxcv/tensor-trust — obtain an explicit dataset license from the maintainer.",
        "- https://huggingface.co/datasets/YifanJ/Red_Queen — obtain an explicit dataset license from the maintainer.",
        "- https://github.com/mshahzaib7/injectionshield — obtain the full benchmark rows from its maintainers for external evaluation; the repository has only 3 display examples.",
        "", "## Run", "",
        "Run `docker compose --profile data run --rm data python -m scripts.download_data` and then `docker compose --profile data run --rm data python -m scripts.unify`.",
        "The downloader skips files already present and stops before `data/raw/` exceeds 20 GB.",
        "Unification rebuilds processed files from raw inputs and excludes any exact or normalized frozen-test text from training.",
    ]
    (Path("data") / "PROVENANCE.md").write_text("\n".join(provenance) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
