import pprint
import json

WEEKS = {
    "doubles/MON-3.5": {
        "01/05": ["Court 4", "Court 5"],
        "01/12": ["Court 4", "Court 5"],
        "01/19": ["Court 4", "Court 5"],
        "01/26": ["Court 4", "Court 5"],
        "02/02": ["Court 4", "Court 5"],
        "02/09": ["Court 4", "Court 5"],
        "02/16": ["Court 4", "Court 5"],
        "02/23": ["Court 4", "Court 5"],
        "03/02": ["Court 4", "Court 5"],
        "03/09": ["Court 4", "Court 5"],
        "03/16": ["Court 4", "Court 5"],
        "03/23": ["Court 4", "Court 5"],
        "04/13": ["Court 4", "Court 5"],
        "04/20": ["Court 4", "Court 5"],
    },
    "doubles/MON-4.0": {
        "09/22": ["6pm Court 6", "7:30pm Court 6"],
        "01/05": ["6pm Court 6", "7:30pm Court 6"],
        "01/12": ["6pm Court 6", "7:30pm Court 6"],
        "01/19": ["6pm Court 6", "7:30pm Court 6"],
        "01/26": ["6pm Court 6", "7:30pm Court 6"],
        "02/02": ["6pm Court 6", "7:30pm Court 6"],
        "02/09": ["6pm Court 6", "7:30pm Court 6"],
        "02/16": ["6pm Court 6", "7:30pm Court 6"],
        "02/23": ["6pm Court 6", "7:30pm Court 6"],
        "03/02": ["6pm Court 6", "7:30pm Court 6"],
        "03/09": ["6pm Court 6", "7:30pm Court 6"],
        "03/16": ["6pm Court 6", "7:30pm Court 6"],
        "03/23": ["6pm Court 6", "7:30pm Court 6"],
        "04/13": ["6pm Court 6", "7:30pm Court 6"],
        "04/20": ["6pm Court 6", "7:30pm Court 6"],
    },
    "singles/WED-3.X": {
        "01/07": ["Court 1", "Court 2"],
        "01/14": ["Court 1", "Court 2"],
        "01/21": ["Court 1", "Court 2"],
        "01/28": ["Court 1", "Court 2"],
        "02/04": ["Court 1", "Court 2"],
        "02/11": ["Court 1", "Court 2"],
        "02/18": ["Court 1", "Court 2"],
        "02/25": ["Court 1", "Court 2"],
        "03/04": ["Court 1", "Court 2"],
        "03/11": ["Court 1", "Court 2"],
        "03/18": ["Court 1", "Court 2"],
        "03/25": ["Court 1", "Court 2"],
        "04/01": ["Court 1", "Court 2"],
        "04/08": ["Court 1", "Court 2"],
    },
    "singles/WED-4.0": {
        "01/07": ["Court 4", "Court 5", "Court 6"],
        "01/14": ["Court 4", "Court 5", "Court 6"],
        "01/21": ["Court 4", "Court 5", "Court 6"],
        "01/28": ["Court 4", "Court 5", "Court 6"],
        "02/04": ["Court 4", "Court 5", "Court 6"],
        "02/11": ["Court 4", "Court 5", "Court 6"],
        "02/18": ["Court 4", "Court 5", "Court 6"],
        "02/25": ["Court 4", "Court 5", "Court 6"],
        "03/04": ["Court 4", "Court 5", "Court 6"],
        "03/11": ["Court 4", "Court 5", "Court 6"],
        "03/18": ["Court 4", "Court 5", "Court 6"],
        "03/25": ["Court 4", "Court 5", "Court 6"],
        "04/01": ["Court 4", "Court 5", "Court 6"],
        "04/08": ["Court 4", "Court 5", "Court 6"],
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
