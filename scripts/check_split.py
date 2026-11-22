import argparse
from pathlib import Path

from pehredar.dataset import assert_disjoint, load_jsonl


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check train/test group and near-duplicate leakage")
    parser.add_argument("train", type=Path)
    parser.add_argument("test", type=Path)
    arguments = parser.parse_args()
    assert_disjoint(load_jsonl(arguments.train), load_jsonl(arguments.test))
    print("No group or near-duplicate overlap detected.")
