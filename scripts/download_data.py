"""Verified, resumable public-data downloads. Run: python -m scripts.download_data."""
import json
import os
from datetime import date
from pathlib import Path

import requests
from huggingface_hub import HfApi, hf_hub_url

ROOT = Path("data/raw")
LIMIT = 20 * 1024**3

# Download only the files used by unify.py; large sources are streamed there.
HF = {
    "deepset_pi": ("deepset/prompt-injections", ["data/train-00000-of-00001-9564e8b05b4757ab.parquet", "data/test-00000-of-00001-701d16158af87368.parquet"], "apache-2.0", True),
    "safeguard_pi": ("xTRam1/safe-guard-prompt-injection", ["data/train-00000-of-00001.parquet", "data/test-00000-of-00001.parquet"], "unspecified", False),
    "jb_class": ("jackhhao/jailbreak-classification", ["balanced/jailbreak_dataset_train_balanced.csv", "balanced/jailbreak_dataset_test_balanced.csv"], "apache-2.0", True),
    "tensor_trust": ("qxcv/tensor-trust", ["benchmarks/extraction-robustness/v1/extraction_robustness_dataset.jsonl", "benchmarks/hijacking-robustness/v1/hijacking_robustness_dataset.jsonl", "detecting-extractions/v1/prompt_extraction_detection.jsonl"], "unspecified", False),
    "gandalf": ("Lakera/gandalf_ignore_instructions", ["data/train-00000-of-00001-ded53be747ff55cd.parquet", "data/validation-00000-of-00001-94481a2a09ff2fff.parquet", "data/test-00000-of-00001-bc92128b9288a6d1.parquet"], "mit", True),
    "wildjailbreak": ("allenai/wildjailbreak", ["train/train.tsv", "eval/eval.tsv"], "odc-by", False),
    "necent_merged": ("Necent/llm-jailbreak-prompt-injection-dataset", [f"data/train-0000{i}-of-00004.parquet" for i in range(4)], "mixed upstream", False),
    "mhj": ("ScaleAI/mhj", [], "cc-by-nc-4.0", False),
    "safemtdata": ("SafeMTData/SafeMTData", ["SafeMTData/Attack_600.json"], "mit", True),
    "red_queen": ("YifanJ/Red_Queen", ["Red_Queen_Attack.zip"], "unspecified", False),
    "tom_gibbs_multiturn": ("tom-gibbs/multi-turn_jailbreak_attack_datasets", ["Complete Harmful Dataset.csv", "Harmful Dataset.csv", "Semi-Benign Dataset.csv", "Completely-Benign Dataset.csv"], "mit", True),
    "wildguardmix": ("allenai/wildguardmix", ["train/wildguard_train.parquet", "test/wildguard_test.parquet"], "odc-by", False),
    "aegis2": ("nvidia/Aegis-AI-Content-Safety-Dataset-2.0", ["train.json", "validation.json", "test.json"], "cc-by-4.0", True),
    "beavertails": ("PKU-Alignment/BeaverTails", ["round0/30k/train.jsonl.gz"], "cc-by-nc-4.0", False),
    "toxicchat": ("lmsys/toxic-chat", ["data/0124/toxic-chat_annotation_train.csv", "data/0124/toxic-chat_annotation_test.csv"], "cc-by-nc-4.0", False),
    "or_bench": ("bench-llm/or-bench", ["or-bench-hard-1k.csv"], "cc-by-4.0", True),
    "ai4privacy": ("ai4privacy/open-pii-masking-500k-ai4privacy", ["data/validation/test.jsonl"], "CC-BY-4.0 + Llama Community License", False),
}
GH = {
    "jailbreak_llms": ("verazuo/jailbreak_llms", ["data/prompts/jailbreak_prompts_2023_12_25.csv", "data/prompts/regular_prompts_2023_12_25.csv"], "mit", True),
    "bipia": ("microsoft/BIPIA", ["benchmark/text_attack_test.json", "benchmark/code_attack_test.json"], "mit; source task restrictions", False),
    "injecagent": ("uiuc-kang-lab/InjecAgent", ["data/test_cases_dh_base.json", "data/test_cases_ds_base.json"], "mit", True),
    "agentdojo": ("ethz-spylab/agentdojo", [f"src/agentdojo/default_suites/v1/{x}/injection_tasks.py" for x in ("banking", "slack", "travel", "workspace")], "mit", True),
    "harmbench": ("centerforaisafety/HarmBench", ["data/behavior_datasets/harmbench_behaviors_text_test.csv"], "mit", True),
    "xstest": ("paul-rottger/exaggerated-safety", ["xstest_prompts.csv"], "cc-by-4.0", True),
    "injectionshield": ("mshahzaib7/injectionshield", ["DATA_CARD.md"], "mixed upstream", False),
    "smat26": ("Smat26/Roman-Urdu-Dataset", ["Dataset/Roman Urdu DataSet.csv"], "gpl-3.0", True),
    "erupd": ("bose9999/ERUPD-dataset", ["ERUPD_dataset.json"], "cc-by-4.0", True),
}
GH_REVISIONS = {
    "jailbreak_llms": "4f4031bf8be187f4478c7f94f42b08714722c12e",
    "bipia": "a004b69ec0dd446e0afd461d98cb5e96e120a5d0",
    "injecagent": "f19c9f2c79a41046eb13c03c51a24c567a8ffa07",
    "agentdojo": "089ed468cf3ed0322acc66b0211f26d9d90dbf60",
    "harmbench": "8e1604d1171fe8a48d8febecd22f600e462bdcdd",
    "xstest": "d7bb5bd738c1fcbc36edd83d5e7d1b71a3e2d84d",
    "injectionshield": "f1b8bdcb5bdc0e0d059ebdef8413332956a049b8",
    "smat26": "762ba24484024855798ef15d248e45f12a410de3",
    "erupd": "843d2071885b2db2715bc3146396964d576f4047",
}


def token_from_env():
    if "HF_TOKEN" in os.environ:
        return os.environ["HF_TOKEN"]
    path = Path(".env")
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("HF_TOKEN="):
                return line.partition("=")[2].strip().strip('"').strip("'")
    return None


def usage_bytes():
    return sum(p.stat().st_size for p in ROOT.rglob("*") if p.is_file())


def fetch(url, path, session, expected_size=None):
    if path.exists():
        return
    if expected_size and usage_bytes() + expected_size > LIMIT:
        raise RuntimeError("STOP: data/raw would exceed 20 GB")
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".part")
    with session.get(url, stream=True, timeout=120) as response:
        response.raise_for_status()
        size = int(response.headers.get("Content-Length", 0))
        if usage_bytes() + size > LIMIT:
            raise RuntimeError("STOP: data/raw would exceed 20 GB")
        with tmp.open("wb") as out:
            for chunk in response.iter_content(1024 * 1024):
                out.write(chunk)
                if usage_bytes() > LIMIT:
                    raise RuntimeError("STOP: data/raw exceeded 20 GB")
    tmp.replace(path)


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    token = token_from_env()
    session = requests.Session()
    session.headers["User-Agent"] = "pehredar-public-data/1"
    if token:
        session.headers["Authorization"] = f"Bearer {token}"
    api = HfApi(token=token)
    for name, (repo, files, license_name, redistributable) in HF.items():
        folder = ROOT / name
        try:
            old_meta = folder / "metadata.json"
            old = json.loads(old_meta.read_text(encoding="utf-8")) if old_meta.exists() else None
            info = api.dataset_info(repo, revision=old["revision"] if old else None, files_metadata=True)
            card = info.cardData or {}
            available = {f.rfilename: f for f in info.siblings}
            if any(f not in available for f in files):
                raise ValueError("requested file missing at verified revision")
            meta = {"source_url": f"https://huggingface.co/datasets/{repo}", "revision": info.sha,
                    "license": license_name, "card_license": card.get("license"), "gated": info.gated,
                    "redistributable": redistributable,
                    "download_date": old["download_date"] if old else str(date.today()), "files": files}
            folder.mkdir(parents=True, exist_ok=True)
            (folder / "metadata.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
            if name == "mhj":
                print(f"{name}: gated repository has no downloadable data files; manual action required")
                continue
            if name in {"safeguard_pi", "tensor_trust", "red_queen", "erupd"}:
                print(f"{name}: license is not established; metadata only")
                continue
            for file in files:
                fetch(hf_hub_url(repo, file, repo_type="dataset", revision=info.sha),
                      folder / file, session, available[file].size)
            print(f"{name}: ready")
        except requests.HTTPError as exc:
            if exc.response.status_code in (401, 403):
                print(f"{name}: access denied; accept terms at https://huggingface.co/datasets/{repo}")
            else:
                print(f"{name}: HTTP {exc.response.status_code}")
        except Exception as exc:
            if "20 GB" in str(exc):
                raise
            print(f"{name}: {type(exc).__name__}: {str(exc)[:150]}")
    for name, (repo, files, license_name, redistributable) in GH.items():
        folder = ROOT / name
        try:
            revision = GH_REVISIONS[name]
            old_meta = folder / "metadata.json"
            old = json.loads(old_meta.read_text(encoding="utf-8")) if old_meta.exists() else None
            meta = {"source_url": f"https://github.com/{repo}", "revision": revision, "license": license_name,
                    "redistributable": redistributable,
                    "download_date": old["download_date"] if old else str(date.today()), "files": files}
            folder.mkdir(parents=True, exist_ok=True)
            (folder / "metadata.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
            for file in files:
                url = f"https://raw.githubusercontent.com/{repo}/{revision}/{requests.utils.quote(file, safe='/')}"
                fetch(url, folder / file, session)
            print(f"{name}: ready")
        except Exception as exc:
            if "20 GB" in str(exc):
                raise
            print(f"{name}: {type(exc).__name__}: {str(exc)[:150]}")
    path = ROOT / "uci_roman_urdu"
    path.mkdir(parents=True, exist_ok=True)
    url = "https://archive.ics.uci.edu/static/public/458/roman+urdu+data+set.zip"
    try:
        fetch(url, path / "roman_urdu.zip", session)
        (path / "metadata.json").write_text(json.dumps({
            "source_url": "https://archive.ics.uci.edu/dataset/458/roman+urdu+data+set",
            "revision": "UCI dataset 458; file SHA-256 recorded in provenance",
            "license": "cc-by-4.0", "redistributable": True,
            "download_date": str(date.today()), "files": ["roman_urdu.zip"],
        }, indent=2) + "\n", encoding="utf-8")
        print("uci_roman_urdu: ready")
    except Exception as exc:
        print(f"uci_roman_urdu: {type(exc).__name__}: {str(exc)[:150]}")


if __name__ == "__main__":
    main()
