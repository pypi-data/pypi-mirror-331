import argparse
import time
from itertools import groupby
from pathlib import Path
from typing import Iterable

import orjson
from typing_extensions import ParamSpec

parser = argparse.ArgumentParser()
parser.add_argument("--data-dir", type=Path)


def load_jsonl(f_path: Path):
    data = []
    with open(f_path, "rb") as f:
        for line in f:
            data.append(orjson.loads(line))

    return data


def aggregate_duration(records: Iterable):
    tasks_duration = dict()
    records = sorted(list(records), key=lambda x: x["task"])
    for elem, group in groupby(records, key=lambda x: x["task"]):
        group_duration = sum([itm["duration"] for itm in group])
        tasks_duration[elem] = group_duration
    return tasks_duration


def aggregate(data_dir: Path):
    key_func = lambda x: x["client"]
    # collection of all records for given month
    reccords = []
    for f_path in data_dir.glob("*.txt"):
        reccords.extend(load_jsonl(f_path))

    print()
    print(f"Aggregate for month {data_dir.name}")
    print()
    print(f"{'client':<40} {'duration'}")
    print("-" * 10)
    reccords = sorted(reccords, key=key_func)
    for client, entries in groupby(reccords, key=key_func):
        tasks_duration = aggregate_duration(entries)
        total_duration = sum(tasks_duration.values()) / 60 / 60
        # entries is consumed now
        print(f"{client:<40} {total_duration:.3f}")
        for task, dur in tasks_duration.items():
            print(f"{task:>40} {dur / 60 / 60:.3f}")
        print()
        print()


def main():
    args = parser.parse_args()
    aggregate(args.data_dir)


if __name__ == "__main__":
    main()
