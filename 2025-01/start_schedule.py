import pprint
import json

SINGLES_WEEKS = {
    "01/15": {"3.5": ["Court 1", "Court 2", "Court 3"], "4.0": ["Court 4", "Court 5", "Court 6"]},
    "01/22": {"3.5": ["Court 1", "Court 2", "Court 3"], "4.0": ["Court 4", "Court 5", "Court 6"]},
    "01/29": {"3.5": ["Court 1", "Court 2", "Court 3"], "4.0": ["Court 4", "Court 5", "Court 6"]},
    "02/05": {"3.5": ["Court 1", "Court 2", "Court 3"], "4.0": ["Court 4", "Court 5", "Court 6"]},
    "02/12": {"3.5": ["Court 1", "Court 2", "Court 3"], "4.0": ["Court 4", "Court 5", "Court 6"]},
    "02/19": {"3.5": ["Court 1", "Court 2", "Court 3"], "4.0": ["Court 4", "Court 5", "Court 6"]},
    "02/26": {"3.5": ["Court 1", "Court 2", "Court 3"], "4.0": ["Court 4", "Court 5", "Court 6"]},
    "03/05": {"3.5": ["Court 1", "Court 2", "Court 3"], "4.0": ["Court 4", "Court 5", "Court 6"]},
    "03/12": {"3.5": ["Court 1", "Court 2", "Court 3"], "4.0": ["Court 4", "Court 5", "Court 6"]},
    "03/19": {"3.5": ["Court 1", "Court 2", "Court 3"], "4.0": ["Court 4", "Court 5", "Court 6"]},
    "04/02": {"3.5": ["Court 1", "Court 2", "Court 3"], "4.0": ["Court 4", "Court 5", "Court 6"]},
    "04/09": {"3.5": ["Court 1", "Court 2", "Court 3"], "4.0": ["Court 4", "Court 5", "Court 6"]},
    "04/16": {"3.5": ["Court 1", "Court 2", "Court 3"], "4.0": ["Court 4", "Court 5", "Court 6"]},
    "04/23": {"3.5": ["Court 1", "Court 2", "Court 3"], "4.0": ["Court 4", "Court 5", "Court 6"]},
    "04/30": {"3.5": ["Court 1", "Court 2", "Court 3"], "4.0": ["Court 4", "Court 5", "Court 6"]},
    "05/07": {"3.5": ["Court 1", "Court 2", "Court 3"], "4.0": ["Court 4", "Court 5", "Court 6"]},
}

DOUBLES_WEEKS = {
    "01/13": {"3.5": ["7:30 Court 4", "7:30 Court 5"], "4.0": ["6:00 Court 6", "7:30 Court 6"]},
    "01/20": {"3.5": ["7:30 Court 4", "7:30 Court 5"], "4.0": ["6:00 Court 6", "7:30 Court 6"]},
    "01/27": {"3.5": ["7:30 Court 4", "7:30 Court 5"], "4.0": ["6:00 Court 6", "7:30 Court 6"]},
    "02/03": {"3.5": ["7:30 Court 4", "7:30 Court 5"], "4.0": ["6:00 Court 6", "7:30 Court 6"]},
    "02/10": {"3.5": ["7:30 Court 4", "7:30 Court 5"], "4.0": ["6:00 Court 6", "7:30 Court 6"]},
    "02/17": {"3.5": ["7:30 Court 4", "7:30 Court 5"], "4.0": ["6:00 Court 6", "7:30 Court 6"]},
    "02/24": {"3.5": ["7:30 Court 4", "7:30 Court 5"], "4.0": ["6:00 Court 6", "7:30 Court 6"]},
    "03/03": {"3.5": ["7:30 Court 4", "7:30 Court 5"], "4.0": ["6:00 Court 6", "7:30 Court 6"]},
    "03/10": {"3.5": ["7:30 Court 4", "7:30 Court 5"], "4.0": ["6:00 Court 6", "7:30 Court 6"]},
    "03/17": {"3.5": ["7:30 Court 4", "7:30 Court 5"], "4.0": ["6:00 Court 6", "7:30 Court 6"]},
    "03/31": {"3.5": ["7:30 Court 4", "7:30 Court 5"], "4.0": ["6:00 Court 6", "7:30 Court 6"]},
    "04/07": {"3.5": ["7:30 Court 4", "7:30 Court 5"], "4.0": ["6:00 Court 6", "7:30 Court 6"]},
    "04/14": {"3.5": ["7:30 Court 4", "7:30 Court 5"], "4.0": ["6:00 Court 6", "7:30 Court 6"]},
    "04/21": {"3.5": ["7:30 Court 4", "7:30 Court 5"], "4.0": ["6:00 Court 6", "7:30 Court 6"]},
    "04/28": {"3.5": ["7:30 Court 4", "7:30 Court 5"], "4.0": ["6:00 Court 6", "7:30 Court 6"]},
    "05/05": {"3.5": ["7:30 Court 4", "7:30 Court 5"], "4.0": ["6:00 Court 6", "7:30 Court 6"]},
}

for league in ["singles", "doubles"]:
    matches = {}
    for group in ["3.5", "4.0"]:
        weeks = SINGLES_WEEKS if league == "singles" else DOUBLES_WEEKS
        entry = [["", ""], [None, None, True]] if league == "singles" else [["", "", "", ""]]
        for week in weeks.keys():
            week_matches = matches[week] = {}
            for court in weeks[week][group]:
                week_matches[court] = entry
            week_matches["off"] = []
            week_matches["requested_off"] = []
        with open(f"{league}/{group}/matches.py", "w") as handle:
            pprint.pprint(matches, handle)
