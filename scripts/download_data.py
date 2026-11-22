"""Verified, pinned public dataset downloads. Raw files are never rewritten."""

import argparse
import json
import os
from datetime import date
from pathlib import Path

import requests
from huggingface_hub import HfApi, hf_hub_download

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
LIMIT_BYTES = 20 * 1024**3

# Only files whose IDs, cards, and research-use terms were checked are selected.
SOURCES = {
    "deepset_pi": ("hf", "deepset/prompt-injections", ["data/train-00000-of-00001-9564e8b05b4757ab.parquet", "data/test-00000-of-00001-701d16158af87368.parquet"], "apache-2.0", True),
    "jb_class": ("hf", "jackhhao/jailbreak-classification", ["default/jailbreak_dataset_train.csv", "default/jailbreak_dataset_test.csv"], "apache-2.0", True),
    "gandalf": ("hf", "Lakera/gandalf_ignore_instructions", ["data/train-00000-of-00001-ded53be747ff55cd.parquet", "data/validation-00000-of-00001-94481a2a09ff2fff.parquet", "data/test-00000-of-00001-bc92128b9288a6d1.parquet"], "mit", True),
    "safemtdata": ("hf", "SafeMTData/SafeMTData", ["SafeMTData/Attack_600.json", "SafeMTData/SafeMTData_1K.json"], "mit", True),
    "tom_gibbs_multiturn": ("hf", "tom-gibbs/multi-turn_jailbreak_attack_datasets", ["Complete Harmful Dataset.csv", "Harmful Dataset.csv", "Completely-Benign Dataset.csv", "Semi-Benign Dataset.csv"], "mit", True),
    "aegis2": ("hf", "nvidia/Aegis-AI-Content-Safety-Dataset-2.0", ["train.json", "validation.json", "test.json"], "cc-by-4.0", True),
    "beavertails": ("hf", "PKU-Alignment/BeaverTails", ["round0/30k/train.jsonl.gz"], "cc-by-nc-4.0", False),
    "toxicchat": ("hf", "lmsys/toxic-chat", ["data/0124/toxic-chat_annotation_train.csv", "data/0124/toxic-chat_annotation_test.csv"], "cc-by-nc-4.0", False),
    "or_bench": ("hf", "bench-llm/or-bench", ["or-bench-hard-1k.csv"], "cc-by-4.0", True),
    "ai4privacy": ("hf", "ai4privacy/open-pii-masking-500k-ai4privacy", ["data/validation/test.jsonl"], "other:cc-by-4.0+llama-community", False),
    "jailbreak_llms": ("gh", "verazuo/jailbreak_llms", ["data/prompts/jailbreak_prompts_2023_12_25.csv", "data/prompts/regular_prompts_2023_12_25.csv"], "mit", True),
    "bipia": ("gh", "microsoft/BIPIA", ["benchmark/text_attack_test.json", "benchmark/code_attack_test.json"], "mit; source task restrictions", False),
    "injecagent": ("gh", "uiuc-kang-lab/InjecAgent", ["data/test_cases_dh_base.json", "data/test_cases_ds_base.json"], "mit", True),
    "harmbench": ("gh", "centerforaisafety/HarmBench", ["data/behavior_datasets/harmbench_behaviors_text_test.csv"], "mit", True),
    "xstest": ("gh", "paul-rottger/exaggerated-safety", ["xstest_prompts.csv"], "cc-by-4.0", True),
    "injectionshield": ("gh", "mshahzaib7/injectionshield", ["DATA_CARD.md", "public/data/dataset_examples.json"], "mixed upstream", False),
    "agentdojo": ("gh", "ethz-spylab/agentdojo", [f"src/agentdojo/default_suites/v1/{part}/injection_tasks.py" for part in ("banking", "slack", "travel", "workspace")], "mit", True),
    "smat26": ("gh", "Smat26/Roman-Urdu-Dataset", ["Dataset/Roman Urdu DataSet.csv"], "gpl-3.0", True),
    "erupd": ("gh", "bose9999/ERUPD-dataset", ["ERUPD_dataset.json"], "cc-by-4.0", True),
    "uci_roman_urdu": ("url", "https://archive.ics.uci.edu/static/public/458/roman+urdu+data+set.zip", ["roman_urdu.zip"], "cc-by-4.0", True),
}

GITHUB_REVISIONS = {
    "jailbreak_llms": "4f4031bf8be187f4478c7f94f42b08714722c12e",
    "bipia": "a004b69ec0dd446e0afd461d98cb5e96e120a5d0",
    "injecagent": "f19c9f2c79a41046eb13c03c51a24c567a8ffa07",
    "harmbench": "8e1604d1171fe8a48d8febecd22f600e462bdcdd",
    "xstest": "d7bb5bd738c1fcbc36edd83d5e7d1b71a3e2d84d",
    "injectionshield": "f1b8bdcb5bdc0e0d059ebdef8413332956a049b8",
    "agentdojo": "089ed468cf3ed0322acc66b0211f26d9d90dbf60",
    "smat26": "762ba24484024855798ef15d248e45f12a410de3",
    "erupd": "843d2071885b2db2715bc3146396964d576f4047",
}

HF_REVISIONS = {
    "deepset_pi": "4f61ecb038e9c3fb77e21034b22511b523772cdd",
    "jb_class": "2f2ceeb39658696fd3f462403562b6eea5306287",
    "gandalf": "04737b65e90a6794ec227012e4a255a7def6344b",
    "safemtdata": "04af7bd0b6b6044e797e936d79674e348316b9b8",
    "tom_gibbs_multiturn": "e3b30257c4d6be5438ea19f0989ac82c24234fe4",
    "aegis2": "d86bb8bedff51d25ac834ab7838f1cc61acb7a2c",
    "beavertails": "8401fe609d288129cc684a9b3be6a93e41cfe678",
    "toxicchat": "29df8e4dba60e1f4af4b4075c0705c5b313548a8",
    "or_bench": "e36d8b80e81837c8a8f264bbb2a49f1b32c7e272",
    "ai4privacy": "506996d625ed970a0063432daf6007cf4a3a48e3",
}


def token_from_env() -> str | None:
    token = os.getenv("HF_TOKEN")
    if token:
        return token
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.startswith("HF_TOKEN="):
                return line.partition("=")[2].strip().strip("\"'")
    return None


def download(names: list[str], root: Path = RAW) -> dict:
    api = HfApi(token=token_from_env())
    session = requests.Session()
    report = {}
    existing_bytes = sum(p.stat().st_size for p in root.rglob("*") if p.is_file()) if root.exists() else 0
    if existing_bytes > LIMIT_BYTES:
        raise RuntimeError("Stopping: data/raw already exceeds 20 GB")
    for name in names:
        kind, source, files, expected_license, redistributable = SOURCES[name]
        folder = root / name
        metadata_path = folder / "metadata.json"
        if metadata_path.exists():
            old = json.loads(metadata_path.read_text(encoding="utf-8"))
            expected_revision = (HF_REVISIONS[name] if kind == "hf" else
                                 GITHUB_REVISIONS[name] if kind == "gh" else None)
            if expected_revision and old["revision"] != expected_revision:
                raise RuntimeError(f"Existing {name} revision differs; refusing to mix raw versions")
            if all((folder / path).exists() for path in files):
                if old["files"] != files:
                    old["files"] = files
                    metadata_path.write_text(json.dumps(old, indent=2) + "\n", encoding="utf-8")
                report[name] = {"status": "existing", "revision": old["revision"]}
                continue
        if kind == "hf":
            revision = HF_REVISIONS[name]
            info = api.dataset_info(source, revision=revision, files_metadata=True)
            card_license = (info.cardData or {}).get("license")
            actual_license = "other:cc-by-4.0+llama-community" if name == "ai4privacy" and card_license == "other" else card_license
            if actual_license != expected_license:
                report[name] = {"status": "skipped_license", "found": actual_license}
                continue
            index = {item.rfilename: item.size for item in info.siblings}
            if any(path not in index for path in files):
                report[name] = {"status": "missing_file", "revision": revision}
                continue
            if info.gated and not token_from_env():
                report[name] = {"status": "manual_access", "revision": revision}
                continue
            estimated = sum(index[path] or 0 for path in files if not (folder / path).exists())
            if any(index[path] is None for path in files if not (folder / path).exists()):
                raise RuntimeError(f"Cannot verify raw-data size before download: {name}")
            if existing_bytes + estimated > LIMIT_BYTES:
                raise RuntimeError(f"Stopping before 20 GB raw-data limit: {name}")
            selected = ["README.md", *files]
            for path in selected:
                destination = folder / path
                if destination.exists():
                    continue
                folder.mkdir(parents=True, exist_ok=True)
                hf_hub_download(source, path, repo_type="dataset", revision=revision,
                                local_dir=folder, token=token_from_env())
                existing_bytes += destination.stat().st_size
        elif kind == "gh":
            revision = GITHUB_REVISIONS[name]
            base = f"https://raw.githubusercontent.com/{source}/{revision}"
            for path in files:
                destination = folder / path
                if destination.exists():
                    continue
                response = session.get(f"{base}/{path}", timeout=120)
                response.raise_for_status()
                if existing_bytes + len(response.content) > LIMIT_BYTES:
                    raise RuntimeError(f"Stopping before 20 GB raw-data limit: {name}")
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(response.content)
                existing_bytes += len(response.content)
        else:
            revision = "UCI dataset 458"
            destination = folder / files[0]
            if not destination.exists():
                response = session.get(source, timeout=120)
                response.raise_for_status()
                if existing_bytes + len(response.content) > LIMIT_BYTES:
                    raise RuntimeError("Stopping before 20 GB raw-data limit")
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(response.content)
                existing_bytes += len(response.content)
        metadata = {
            "source_url": source if kind == "url" else
                f"https://huggingface.co/datasets/{source}" if kind == "hf" else f"https://github.com/{source}",
            "revision": revision, "license": expected_license,
            "redistributable": redistributable, "files": files,
            "download_date": date.today().isoformat(),
        }
        if metadata_path.exists():
            old = json.loads(metadata_path.read_text(encoding="utf-8"))
            if old["revision"] != revision:
                raise RuntimeError(f"Existing {name} revision differs; refusing to mix raw versions")
            metadata["download_date"] = old["download_date"]
        metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
        report[name] = {
            "status": "downloaded", "source": source, "revision": revision,
            "license": expected_license, "redistributable": redistributable,
            "files": files, "download_date": metadata["download_date"],
        }
    root.mkdir(parents=True, exist_ok=True)
    (root / "download_manifest.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("names", nargs="*")
    args = parser.parse_args()
    unknown = set(args.names) - SOURCES.keys()
    if unknown:
        parser.error(f"unknown dataset(s): {', '.join(sorted(unknown))}")
    selected = args.names or list(SOURCES)
    result = download(selected)
    for name, item in result.items():
        print(name, item["status"], item.get("revision", ""))
