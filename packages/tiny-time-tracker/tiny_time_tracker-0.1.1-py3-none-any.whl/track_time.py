import argparse
import datetime
from dataclasses import dataclass, field
from pathlib import Path
from pprint import pprint

import orjson

DATA_DIR = Path("./user-data")
DATA_DIR.mkdir(exist_ok=True)

@dataclass
class Entry:
    start_time: datetime.datetime
    end_time: datetime.datetime
    duration: float = field(init=False)
    client: str
    task: str

    def __post_init__(self):
        duration = self.end_time - self.start_time
        self.duration = duration.total_seconds()

    def __repr__(self):
        return f"task: {self.task}, time spent: {self.duration/60/60:.3f} hours"


def append_to_file(f_name, data):
    with open(f_name, "ab") as f:
        print(data)
        entry = orjson.dumps(
            data, option=orjson.OPT_OMIT_MICROSECONDS | orjson.OPT_APPEND_NEWLINE
        )
        f.write(entry)


def main(f_name, **kwargs):
    start_time = datetime.datetime.now()
    try:
        while True:
            pass
    except KeyboardInterrupt as e:
        end_time = datetime.datetime.now()

        entry = Entry(
            start_time=start_time,
            end_time=end_time,
            client=kwargs.get("client"),
            task=kwargs.get("task"),
        )
        append_to_file(f_name, entry)


def manual(f_name, **kwargs):
    assert kwargs["duration"] is not None
    if (date_str := kwargs.get("date")) is not None:
        start_time = datetime.datetime.strptime(date_str, "%d-%m-%Y")
    else:
        start_time = datetime.datetime.now()
    end_time = start_time + datetime.timedelta(hours=kwargs["duration"])

    entry = Entry(
        start_time=start_time,
        end_time=end_time,
        client=kwargs.get("client"),
        task=kwargs.get("task"),
    )
    append_to_file(f_name, entry)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("client", nargs="?", default="research", type=str)
    parser.add_argument("task", nargs="?", default="tts", type=str)
    parser.add_argument(
        "--date", type=str, help="date of activity. Example: 07-10-2023"
    )
    parser.add_argument(
        "--duration", type=float, help="duration in hours. Fractionals are accepted"
    )
    args = parser.parse_args()

    if args.date is not None:
        date = datetime.datetime.strptime(args.date, "%d-%m-%Y")
    else:
        date = datetime.date.today()

    date_str = date.strftime("%d-%m-%Y")
    month_str = date.strftime("%m-%Y")

    month_dir = DATA_DIR / month_str
    month_dir.mkdir(exist_ok=True)

    f_name = month_dir / f"{date_str}.txt"

    if args.duration is not None:
        print("Adding task in a manual mode")
        manual(f_name, **args.__dict__)
        exit()
    main(f_name, **args.__dict__)
