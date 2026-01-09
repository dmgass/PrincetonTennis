
import argparse

UNIQUE_FIELDS = ("phone", "email")
FIELDS = ("group", "nickname") + UNIQUE_FIELDS

def check_member_nicknames(database, season, league):
    unique_values = set()
    group_key = f"{season}/{league}"
    for name, info in database.items():
        if group_key in info["group"]:
            nickname = info["nickname"]
            assert info["nickname"] not in unique_values, f"{nickname}@{name} not unique"
            unique_values.add(nickname)

def check_members(database):
    unique_values = {f: set() for f in UNIQUE_FIELDS}

    for name, info in database.items():
        fields = list(info)
        if "sub" in fields:
            fields.remove("sub")
        assert tuple(fields) == FIELDS, f"keys@{name}\n{fields}\n{FIELDS}"
        for f in UNIQUE_FIELDS:
            assert info[f] not in unique_values[f], f"{f}@{name} not unique"
            unique_values[f].add(info[f])

def summarize_groups(season, database):
    groups = {}

    for name, info in database.items():
        for league, group in info["group"].items():
            if league.startswith(season):
                groups.setdefault(league, {}).setdefault(group, set()).add(f"{name} - {info['nickname']}")

    for league in sorted(groups):
        for group in sorted(groups[league]):
            group_names = groups[league][group]
            title = f"{league}-{group} ({len(group_names)})"
            print(title)
            print("=" * len(title))
            for name in sorted(group_names):
                print(name)
            print()

parser = argparse.ArgumentParser()
parser.add_argument("season")

args = parser.parse_args()

with open("members.json") as handle:
    database = eval(handle.read())

check_members(database)
check_member_nicknames(database, args.season, "DOUBLES")
check_member_nicknames(database, args.season, "SINGLES")
summarize_groups(args.season, database)