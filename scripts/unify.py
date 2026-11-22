"""Unify downloaded public datasets. Run: python -m scripts.unify."""
import ast
import csv
import gzip
import hashlib
import json
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
ROMAN = {"hai", "nahi", "kya", "mujhe", "aur", "karo", "bhai", "yaar"}
ENGLISH = {"the", "is", "are", "what", "how", "please", "can", "you", "to", "of"}


@lru_cache
def source_metadata(name):
    path = RAW / name / "metadata.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def norm(text):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", text).casefold()).strip()


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
    ru = sum(w in ROMAN for w in words) / len(words)
    en = sum(w in ENGLISH for w in words) / len(words)
    if ru > .2 and en > .2:
        return "mixed"
    return "roman_ur" if ru > .2 else "en"


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
            import pandas as pd
            for batch in pd.read_parquet(path).to_dict("records"):
                yield rel, batch
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
        return
    text = text.strip()
    if not 3 <= len(text) <= 4000:
        COUNTS[name]["length"] += 1
        return
    response = (extra or {}).get("response")
    if file != "pii_eval" and any(p.search(value) for value in (text, response) if isinstance(value, str) for p in PII_PATTERNS + SECRET_PATTERNS):
        COUNTS[name]["pii"] += 1
        return
    detected_lang = source_lang(name, text)
    if file == "injection_train" and detected_lang == "other":
        COUNTS[name]["lang_other"] += 1
        return
    key = norm(text)
    if key in SEEN:
        COUNTS[name]["duplicate"] += 1
        return
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


def main():
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
    wild_counts = Counter()
    for rel, row in rows("wildjailbreak") or []:
        data_type = row.get("data_type")
        if data_type not in {"adversarial_harmful", "adversarial_benign"}:
            continue
        if wild_counts[data_type] >= 15000:
            continue
        text = row.get("adversarial")
        label = "attack" if data_type == "adversarial_harmful" else "benign"
        add("injection_train", "wildjailbreak", text, label,
            "jailbreak" if label == "attack" else "none", data_type)
        wild_counts[data_type] += 1
    for _, row in rows("gandalf") or []:
        add("injection_train", "gandalf", row.get("text"), "attack", "extraction", "password extraction")
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
                label = "attack" if str(value) == "1" else "benign"
            else:
                value = row.get("prompt_harm_label")
                text, response = row.get("prompt"), row.get("response")
                label = "attack" if value == "harmful" else "benign" if value == "unharmful" else None
            if label is None:
                COUNTS[name]["unclear"] += 1
                continue
            add("harm", name, text, label, "harm" if label == "attack" else "none", value,
                "eval_only" if "test" in rel else "train", extra={"response": response})
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
    rng = random.Random(42)
    attack = [r for r in POOL if r["label"] == "attack"]
    benign = [r for r in POOL if r["label"] == "benign"]
    rng.shuffle(attack)
    rng.shuffle(benign)
    attack_sources = Counter(r["source"] for r in attack)
    cap = max(1, sum(attack_sources.values()) // max(3, len(attack_sources)))
    selected, sources = [], Counter()
    for row in attack:
        if sources[row["source"]] < cap:
            selected.append(row)
            sources[row["source"]] += 1
    while selected and max(sources.values()) > len(selected) * .35:
        source = max(sources, key=sources.get)
        index = next(i for i, row in enumerate(selected) if row["source"] == source)
        selected.pop(index)
        sources[source] -= 1
    selected += benign[:len(selected)]
    OUTPUT["injection_train"] = sorted(selected, key=lambda r: r["id"])
    frozen = Path("data/frozen_test/human_v1.jsonl")
    if frozen.exists():
        held_out = {norm(json.loads(line)["text"]) for line in frozen.read_text(encoding="utf-8").splitlines() if line.strip()}
        for file, records in OUTPUT.items():
            OUTPUT[file] = [row for row in records if row["usage"] != "train" or norm(row["text"]) not in held_out]
    for name, records in OUTPUT.items():
        with (OUT / (name + ".jsonl")).open("w", encoding="utf-8") as stream:
            for record in records:
                stream.write(json.dumps(record, ensure_ascii=True, default=str) + "\n")
    stats = ["# Public data statistics", "", "File | Label | Type | Lang | Source | Rows", "---|---|---|---|---|---:"]
    for file, records in sorted(OUTPUT.items()):
        counts = Counter((r.get("label"), r.get("type"), r.get("lang"), r.get("source")) for r in records)
        for key, count in sorted(counts.items()):
            stats.append(f"{file} | {' | '.join(str(x) for x in key)} | {count}")
    stats += ["", "## Filtering by source", "", "Source | Downloaded | Kept before balancing | Duplicate | PII | Length | Other language | Unclear", "---|---:|---:|---:|---:|---:|---:|---:"]
    for name, count in sorted(COUNTS.items()):
        stats.append(f"{name} | {count['downloaded']} | {count['kept']} | {count['duplicate']} | {count['pii']} | {count['length']} | {count['lang_other']} | {count['unclear']}")
    labels = Counter(r["label"] for r in OUTPUT["injection_train"])
    stats += ["", f"Classifier training pool: {labels['attack']} attack, {labels['benign']} benign.",
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
        "wildjailbreak": "Gated; access denied.",
        "wildguardmix": "Gated; access denied.",
        "necent_merged": "Gated; access denied. Mixed upstream licenses require per-source review.",
        "injectionshield": "Benchmark only; repository does not contain the benchmark rows. Never train.",
        "agentdojo": "Task GOAL definitions are available, but they are objectives rather than injected payloads; raw definitions only.",
        "bipia": "Only text/code attack lists, no licensed WebQA/Summarization contexts.",
        "erupd": "English/Roman Urdu translation pairs, not attacks.",
        "ai4privacy": "CC BY 4.0 plus Llama Community License terms; marked nonredistributable conservatively.",
        "beavertails": "30k train first 10,000 rows only. Noncommercial and nonredistributable.",
        "toxicchat": "Latest 0124 config. Noncommercial and nonredistributable.",
        "uci_roman_urdu": "UCI dataset 458; overlaps Smat26 and is deduplicated.",
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
        "- https://huggingface.co/datasets/allenai/wildjailbreak — click **Accept** on the dataset page, then rerun downloads.",
        "- https://huggingface.co/datasets/allenai/wildguardmix — click **Accept** on the dataset page, then rerun downloads.",
        "- https://huggingface.co/datasets/Necent/llm-jailbreak-prompt-injection-dataset — click **Accept**, then check every upstream source license before unifying.",
        "- https://huggingface.co/datasets/ScaleAI/mhj — provide requested contact information and click **Accept**; obtain the actual dataset files from the maintainers.",
        "- https://data.mendeley.com/datasets/v5jfhsvtmd/5 — download RUwV-NSR and confirm its dataset license.",
        "- https://huggingface.co/datasets/xTRam1/safe-guard-prompt-injection — obtain an explicit dataset license from the maintainer.",
        "- https://huggingface.co/datasets/qxcv/tensor-trust — obtain an explicit dataset license from the maintainer.",
        "- https://huggingface.co/datasets/YifanJ/Red_Queen — obtain an explicit dataset license from the maintainer.",
        "- https://github.com/mshahzaib7/injectionshield — obtain the benchmark rows from its maintainers for external evaluation.",
        "", "## Run", "",
        "Install `huggingface_hub`, `pandas`, `pyarrow`, and `requests` in the project's Python environment, then run `python -m scripts.download_data` and `python -m scripts.unify`.",
        "The downloader skips files already present and stops before `data/raw/` exceeds 20 GB.",
        "Unification rebuilds processed files from raw inputs and excludes any exact or normalized frozen-test text from training.",
    ]
    (Path("data") / "PROVENANCE.md").write_text("\n".join(provenance) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
