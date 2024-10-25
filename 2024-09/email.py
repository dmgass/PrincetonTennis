import argparse
import json
from texttable import Texttable

SEASON = '2024-09'

STYLE = 'style="border: 1px solid black"'

MEMBERS = json.load(open("../members.json"))

PLAYOFFS = ["12/18"]

class Player:

    def __init__(self, name):
        self.name = name
        self.matches_won = 0
        self.matches_lost = 0
        self.matches_tied = 0
        self.makeups_to_play = 0
        self.games_won = 0
        self.games_lost = 0

    def __str__(self):
        return self.name

    @classmethod
    def make_table(cls, rank_name, fmt):
        rank_property = getattr(cls, "rank_" + rank_name).fget
        cells_property = getattr(cls, "cells_" + rank_name).fget

        header_row = getattr(cls, "header_" + rank_name)
        rows = [cells_property(player) for player in sorted(PLAYERS.values(), key=rank_property)]

        match fmt:
            case "text":
                table = Texttable()
                table.add_rows([header_row] + rows)
                return table.draw()

            case "html":
                lines = [
                    '<table style="border: 1px solid black">',
                    "".join(f"<th {STYLE}>{cell}</th>" for cell in header_row),
                ]
                for cells in rows:
                    row_cells = "".join(f"<td {STYLE}>{cell}</td>" for cell in cells)
                    lines += [f"<tr>{row_cells}<tr/>"]
                lines += ["</table>"]
                return "\n".join(lines)

            case _:
                raise RuntimeError(f"invalid format {fmt!r}")

    @property
    def matches_played(self):
        return self.matches_won + self.matches_tied + self.matches_lost

    @property
    def rank_by_match(self):
        return (
            -self.matches_won, 
            -self.matches_tied, 
            #self.matches_lost, 
            -self.games_won, 
            self.games_lost, 
            self.name,
        )

    @property
    def rank_by_games(self):
        return (
            -self.games_won, 
            self.games_lost, 
            -self.matches_won, 
            -self.matches_tied, 
            self.matches_lost, 
            self.name,
        )

    header_by_match = (
        "Player", "Won", "Tied", "Lost", "Games Won", "Games Lost", "Makeups")

    header_by_games = (
        "Player", "Games Won", "Games Lost", "Matches Won", "Matches Tied", "Matches Lost", "Makeups")

    @property
    def cells_by_match(self):
        return (
            self.name, 
            self.matches_won, 
            self.matches_tied, 
            self.matches_lost, 
            self.games_won, 
            self.games_lost, 
            self.makeups_to_play if self.makeups_to_play else "",
        )

    @property
    def cells_by_games(self):
        return (
            self.name, 
            self.games_won, 
            self.games_lost, 
            self.matches_won, 
            self.matches_tied, 
            self.matches_lost, 
            self.makeups_to_play if self.makeups_to_play else "",
        )

    @property
    def rank_by_avg_games(self):
        if self.matches_played:
            return (
                -(self.games_won / self.matches_played), 
                self.games_lost / self.matches_played, 
                self.name
            )
        
        return 0, 0, self.name

    header_by_avg_games = ("Player", "Avg Games Won", "Avg Games Lost")

    @property
    def cells_by_avg_games(self):
        if self.matches_played:
            return (
                self.name,
                f"{self.games_won / self.matches_played:0.1f}", 
                f"{self.games_lost / self.matches_played:0.1f}", 
            )
        
        return self.name, 0, 0

    @property
    def rank_by_name(self):
        return self.name

    @property
    def cells_by_name(self):
        return self.cells_by_match

    header_by_name = header_by_match

parser = argparse.ArgumentParser()
parser.add_argument("week")
parser.add_argument("group", choices=["3.5", "4.0"])
parser.add_argument("--html", action="store_true")
args = parser.parse_args()

PLAYERS = {}

for name, info in MEMBERS.items():
    group_info = info['group']

    try:
        group = group_info[SEASON]
    except KeyError:
        continue

    if group == args.group:
        nickname = info['nickname']
        PLAYERS[nickname] = Player(nickname)

new_results = []
unreported_matches = []
schedule = {}

def read_matches(filename):
    with open(filename) as handle:
        match_text = handle.read()
    
    for match in eval(match_text):
        if len(match) == 3:
            date, court, names = match
            assert court == "off"
            if date >= args.week:
                this_weeks_schedule = schedule.setdefault(date, {})
                assert court not in this_weeks_schedule
                if names:
                    names =", ".join(name.strip() for name in names.split(','))
                this_weeks_schedule[court] = names
            continue

        date, court, (name1, score1), (name2, score2) = match

        player1 = PLAYERS[name1]
        player2 = PLAYERS[name2]
        scores = {score1, score2}

        this_weeks_schedule = schedule.setdefault(date, {})
        assert court not in this_weeks_schedule
        this_weeks_schedule[court] = f"{name1} v {name2}"

        if None in scores:
            if date < args.week:
                unreported_matches.append(f"{date}: {name1} v {name2}")
                player1.makeups_to_play += 1
                player2.makeups_to_play += 1
        else:
            max_score = max(scores)

            if max_score > 9:
                adjustment = max_score - 9
            else:
                adjustment = 0

            player1.games_won += score1 - adjustment
            player2.games_won += score2 - adjustment
            player1.games_lost += score2 - adjustment
            player2.games_lost += score1- adjustment

            if score1 == score2:
                player1.matches_tied += 1
                player2.matches_tied += 1
                result = f"{name1} tied {name2} {score1} to {score2}"

            elif score1 > score2:
                player1.matches_won += 1
                player2.matches_lost += 1
                result = f"{name1} beat {name2} {score1} to {score2}"

            else:
                player2.matches_won += 1
                player1.matches_lost += 1
                result = f"{name2} beat {name1} {score2} to {score1}"

            if 'unreported' in filename:
                new_results.append(f"{date}: {result}")


read_matches(f"unreported_matches_{args.group}.py")
read_matches(f"reported_matches_{args.group}.py")

def make_schedule_table(fmt):
    courts = set()
    for _date, matches in schedule.items():
        for court, _match in matches.items():
            courts.add(court)

    header_row = [""] + list(sorted(courts))
    rows = []

    for date, matches in sorted(schedule.items()):
        if date < args.week:
            continue
        cells = [date]
        for court in header_row[1:]:
            try:
                cells.append(matches[court])
            except KeyError:
                cells.append("")
        rows.append(cells)

    playoff_courts = ['PLAYOFF'] * (len(courts) - 1)
    for date in PLAYOFFS:
        rows.append([date] + playoff_courts + [""])

    match fmt:
        case "text":
            table = Texttable()
            table.add_rows([header_row] + rows)
            return table.draw()

        case "html":
            lines = [
                '<table style="border: 1px solid black">',
                "".join(f"<th {STYLE}>{cell}</th>" for cell in header_row),
            ]
            for cells in rows:
                row_cells = "".join(f"<td {STYLE}>{cell}</td>" for cell in cells)
                lines += [f"<tr>{row_cells}<tr/>"]
            lines += ["</table>"]
            return "\n".join(lines)

        case _:
            raise RuntimeError(f"invalid format {fmt!r}")

contact_info = []
for name, member in MEMBERS.items():
    try:
        group = member['group'][SEASON]
    except KeyError:
        continue

    if group == args.group:
        contact_info.append(f"{name}: {member['phone']}")

print(f"Princeton Wednesday {args.group} Tennis Matches/Standings - {args.week}")
print()
print()

if args.html:
    if unreported_matches:
        print("<h2>Unreported Matches</h2>")
        print("<br/>\n".join(unreported_matches))

    if new_results:
        print("<h2>Recently Reported Matches</h2>")
        print("<br/>\n".join(new_results))
              
    print("<h2>Standings</h2>")
    print(Player.make_table("by_games", fmt="html"))

    print("<h2>Remaining Schedule</h2>")
    print(make_schedule_table(fmt="html"))

    print("<h2>Contact Info</h2>")
    print("<br/>\n".join(contact_info))
    print("<br/>\n")
    print("<br/>\n")
    print(f"https://github.com/dmgass/PrincetonTennis/tree/main/{SEASON}")

else:
    print("Unreported Matches")
    print("==================")
    for line in unreported_matches:
        print(line)
    print()
    print()

    print("Recently Reported Matches")
    print("=========================")
    for line in new_results:
        print(line)
    print()
    print()

    print("Standings")
    print("=================")
    print(Player.make_table("by_games", fmt="text"))
    print()
    print()

    print("Remaining Schedule")
    print("==================")
    print(make_schedule_table(fmt="text"))
    print()
    print()
