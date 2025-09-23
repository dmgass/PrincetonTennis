import pprint
import json

WEEKS = {
    "doubles/MON-3.5": {
        "09/22": ["Court 4", "Court 5"],
        "09/29": ["Court 4", "Court 5"],
        "10/06": ["Court 4", "Court 5"],
        "10/13": ["Court 4", "Court 5"],
        "10/20": ["Court 4", "Court 5"],
        "10/27": ["Court 4", "Court 5"],
        "11/03": ["Court 4", "Court 5"],
        "11/10": ["Court 4", "Court 5"],
        "11/17": ["Court 4", "Court 5"],
        "11/24": ["Court 4", "Court 5"],
        "12/01": ["Court 4", "Court 5"],
        "12/08": ["Court 4", "Court 5"],
        "12/15": ["Court 4", "Court 5"],
    },
    "doubles/MON-4.0": {
        "09/22": ["Court 6"],
        "09/29": ["Court 6"],
        "10/06": ["Court 6"],
        "10/13": ["Court 6"],
        "10/20": ["Court 6"],
        "10/27": ["Court 6"],
        "11/03": ["Court 6"],
        "11/10": ["Court 6"],
        "11/17": ["Court 6"],
        "11/24": ["Court 6"],
        "12/01": ["Court 6"],
        "12/08": ["Court 6"],
        "12/15": ["Court 6"],
    },
    "doubles/SUN-3.X": {
        "09/28": ["Court 5", "Court 6"],
        "10/05": ["Court 5", "Court 6"],
        "10/12": ["Court 5", "Court 6"],
        "10/19": ["Court 5", "Court 6"],
        "10/26": ["Court 5", "Court 6"],
        "11/02": ["Court 5", "Court 6"],
        "11/09": ["Court 5", "Court 6"],
        "11/16": ["Court 5", "Court 6"],
        "11/23": ["Court 5", "Court 6"],
        "12/07": ["Court 5", "Court 6"],
        "12/14": ["Court 5", "Court 6"],
        "12/21": ["Court 5", "Court 6"],
    },
    "singles/WED-3.X": {
        "09/24": ["Court 1", "Court 2", "Court 3"],
        "10/01": ["Court 1", "Court 2", "Court 3"],
        "10/08": ["Court 1", "Court 2", "Court 3"],
        "10/15": ["Court 1", "Court 2", "Court 3"],
        "10/22": ["Court 1", "Court 2", "Court 3"],
        "10/29": ["Court 1", "Court 2", "Court 3"],
        "11/05": ["Court 1", "Court 2", "Court 3"],
        "11/12": ["Court 1", "Court 2", "Court 3"],
        "11/19": ["Court 1", "Court 2", "Court 3"],
        "11/26": ["Court 1", "Court 2", "Court 3"],
        "12/03": ["Court 1", "Court 2", "Court 3"],
        "12/10": ["Court 1", "Court 2", "Court 3"],
        "12/17": ["Court 1", "Court 2", "Court 3"],
    },
    "singles/WED-4.0": {
        "09/24": ["Court 4", "Court 5", "Court 6"],
        "10/01": ["Court 4", "Court 5", "Court 6"],
        "10/08": ["Court 4", "Court 5", "Court 6"],
        "10/15": ["Court 4", "Court 5", "Court 6"],
        "10/22": ["Court 4", "Court 5", "Court 6"],
        "10/29": ["Court 4", "Court 5", "Court 6"],
        "11/05": ["Court 4", "Court 5", "Court 6"],
        "11/12": ["Court 4", "Court 5", "Court 6"],
        "11/19": ["Court 4", "Court 5", "Court 6"],
        "11/26": ["Court 4", "Court 5", "Court 6"],
        "12/03": ["Court 4", "Court 5", "Court 6"],
        "12/10": ["Court 4", "Court 5", "Court 6"],
        "12/17": ["Court 4", "Court 5", "Court 6"],
    },
}

for league, weeks in WEEKS.items():
    matches = {}
    entry = [["", ""], [None, None, True]] if "singles" in league else [["", "", "", ""]]
    for week, courts in weeks.items():
        week_matches = matches[week] = {}
        for court in courts:
            week_matches[court] = entry
        week_matches["off"] = []
        week_matches["requested_off"] = []
    with open(f"{league}/matches.py", "w") as handle:
        pprint.pprint(matches, handle)
