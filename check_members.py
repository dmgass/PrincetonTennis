
import argparse

UNIQUE_FIELDS = ("nickname", "phone", "email")
FIELDS = ("group",) + UNIQUE_FIELDS

def check_members(database):
    unique_values = {f: set() for f in UNIQUE_FIELDS}

    for name, info in database.items():
        assert tuple(info.keys()) == FIELDS, f"keys@{name}"
        for f in UNIQUE_FIELDS:
            assert info[f] not in unique_values[f], f"{f}@{name} not unique"
            unique_values[f].add(info[f])

def summarize_groups(season, database):
    groups = {}

    for name, info in database.items():
        for league, group in info["group"].items():
            if league.startswith(season):
                groups.setdefault(league, {}).setdefault(group, set()).add(name)

    for league in sorted(groups):
        for group in sorted(groups[league]):
            title = f"{league}-{group}"
            print(title)
            print("=" * len(title))
            for name in sorted(groups[league][group]):
                print(name)
            print()

parser = argparse.ArgumentParser()
parser.add_argument("season")

args = parser.parse_args()

with open("members.json") as handle:
    database = eval(handle.read())

check_members(database)
summarize_groups(args.season, database)