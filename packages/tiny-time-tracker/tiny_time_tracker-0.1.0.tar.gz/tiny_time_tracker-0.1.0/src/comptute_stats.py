import json
from datetime import datetime, timedelta
from pathlib import Path


def compute_stats(dir: Path):
    total_duration = timedelta()
    for file_path in dir.glob("*.txt"):
        with open(file_path, "r") as f:
            for line in f:
                item = eval(line)
                try:
                    t = datetime.strptime(item["duration"], "%H:%M:%S.%f")
                except:
                    t = datetime.strptime(item["duration"], "%H:%M:%S")
                cur_dur = timedelta(
                    hours=t.hour,
                    minutes=t.minute,
                    seconds=t.second,
                    microseconds=t.microsecond,
                )
                total_duration += cur_dur
    total_hours = total_duration.days * 24 + total_duration.seconds / 60 / 60
    print(f"{dir.name} total duration {total_hours = :.2f}")


if __name__ == "__main__":
    dir = Path("./user-data/09-2023/")
    compute_stats(dir)
