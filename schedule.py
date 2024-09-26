import json
import operator
import pprint
import random
from texttable import Texttable

seed = 3

GROUP = "4.0"

SEASON = "2024-09"

WEEKS = {
    "09/18": {"3.5": [1], "4.0": [4, 5, 6]},
    "09/25": {"3.5": [1, 2], "4.0": [3, 4, 5, 6]},
    "10/02": {"3.5": [1, 2, 3], "4.0": [4, 5, 6]}, 
    "10/09": {"3.5": [1, 2, 3], "4.0": [4, 5, 6]}, 
    "10/16": {"3.5": [1, 2, 3], "4.0": [4, 5, 6]},
    "10/23": {"3.5": [1, 2, 3], "4.0": [4, 5, 6]}, 
    "10/30": {"3.5": [1, 2], "4.0": [3, 4, 5, 6]}, 
    "11/06": {"3.5": [1, 2], "4.0": [3, 4, 5, 6]},
    "11/13": {"3.5": [1, 2, 3], "4.0": [4, 5, 6]}, 
    "11/20": {"3.5": [1, 2, 3], "4.0": [4, 5, 6]}, 
    "12/04": {"3.5": [1, 2], "4.0": [3, 4, 5, 6]},
    "12/11": {"3.5": [1, 2, 3], "4.0": [4, 5, 6]},
}

PRESCHEDULED = {
    "4.0": {"09/18": [("Dan Gass", "Matt Huth"), ("Brian Berner", "Trevor Holwell"), ("Dan DeMuro", "Eric Groncki")]},
    "3.5": {"09/18": [("Randy Lee", "Samer Alanani")]}
}

OFF = {
    "09/25": ["Dan Gass"],
    "10/16": ["Nhan Vu"],
    "10/30": ["Nhan Vu"],
}

print(f"3.5 matches: {sum([len(v['3.5']) for v in WEEKS.values()])}")
print(f"4.0 matches: {sum([len(v['4.0']) for v in WEEKS.values()])}")

class Player:

    def __init__(self, name, nickname):
        self.name = name
        self.off = set()
        self.nickname = nickname
        self.possible_opponents = []
        self.num_matches = 0
        self.opponent_counts = {}

    def record_match(self, opponent):
        self.num_matches += 1
        self.opponent_counts[opponent] += 1
        self.possible_opponents.remove(opponent)

    @property
    def opponents_by_least_scheduled(self):
        def against_self(opponent):
            return opponent.opponent_counts[self]
        opponents = list(self.possible_opponents)
        random.shuffle(opponents)
        opponents = sorted(opponents, key=against_self)
        return sorted(opponents, key=operator.attrgetter("num_matches"))



class Players(dict):

    def add(self, name, nickname):
        self[name] = Player(name, nickname)

    @property
    def in_least_scheduled_order(self):
        players = list(self.values())
        random.shuffle(players)
        return sorted(players, key=operator.attrgetter("num_matches"))

    def reset(self, initialize_opponent_counts=False):
        for player in self.values():
            player.possible_opponents = [p for p in self.values() if p is not player]

        if initialize_opponent_counts:
            for player in self.values():
                player.opponent_counts = {p: 0 for p in self.values() if p is not player}


class Week:

    def __init__(self, date, courts):
        self.date = date
        self.matches = []
        self.courts = courts
        self.players_scheduled = []
        
    @property
    def is_available(self):
        return len(self.matches) < len(self.courts)

    def assign_match(self, player1, player2):
        self.players_scheduled += [player1, player2]
        self.matches.append((player1, player2))
        player1.record_match(player2)
        player2.record_match(player1)
        return f"{self.date} {player1.name} {player2.name}"

    def get_players_off(self, players):
        return ", ".join(sorted(
            set(p.nickname for p in players.values()) -
            set(p.nickname for p in self.players_scheduled)
        ))




class Schedule:

    def __init__(self):
        self.players = Players()

        for name, info in json.load(open("members.json")).items():
            seasons = info['group']

            try:
                group = seasons[SEASON]
            except KeyError:
                continue

            if group == GROUP:
                self.players.add(name, info["nickname"])

        for date, names in OFF.items():
            for n in names:
                try:
                    player = self.players[n]
                except KeyError:
                    pass
                else:
                    player.off.add(date)

        self.players.reset(initialize_opponent_counts=True)

        self.weeks = []
        for date, courts in WEEKS.items():
            self.weeks.append(Week(date, courts[GROUP]))

        prescheduled = PRESCHEDULED[GROUP]

        for week in self.weeks:
            try:
                matches = prescheduled[week.date]
            except KeyError:
                continue

            for name1, name2 in matches:
                week.assign_match(self.players[name1], self.players[name2])

    def get_available_weeks(self, player):
         return [
             week for week in self.weeks 
             if week.is_available and (week.date not in player.off) and (player not in week.players_scheduled)
             ]

    def create_match(self):
        for player in self.players.in_least_scheduled_order:
            available_weeks = self.get_available_weeks(player)
            for opponent in player.opponents_by_least_scheduled:
                for week in available_weeks:
                    if week.date not in opponent.off and opponent not in week.players_scheduled:
                        if player.nickname > opponent.nickname:
                            player, opponent = opponent, player
                        return week.assign_match(player, opponent)

        return None

    def do(self):
        num_matches = sum([len(week.courts) for week in self.weeks])
        num_preloaded = sum([len(week.matches) for week in self.weeks])

        for match_number in range(num_preloaded + 1, num_matches + 1):
            match = self.create_match()

            if not match:
                self.players.reset()
                match = self.create_match()

            if not match:
                raise RuntimeError()

    def get_summary(self):
        lines = []
        for player in self.players.values():
            lines += [player.name]
            for opponent, count in player.opponent_counts.items():
                lines += [f"  {opponent.nickname}: {count}"]
            lines += [""]

        for player in self.players.values():
            lines += [f"{player.nickname} {player.num_matches}"]
        lines += [""]

        courts = set()
        for _date, week_courts in WEEKS.items():
            for court in week_courts[GROUP]:
                courts.add(court)

        table = Texttable()
        rows = [["Week"] + list(sorted(courts)) + ["Off"]]
        for week in self.weeks:
            assignments = dict(zip(week.courts, [f"{p1.nickname} v {p2.nickname}" for p1, p2 in week.matches]))
            matches = [assignments.get(court, "") for court in courts]
            rows += [[week.date] + matches[:len(courts)] + [week.get_players_off(self.players)]]
        table.add_rows(rows)
        lines += [table.draw()]
        return "\n".join(lines)

    @property
    def as_html(self):
        lines = []

        # lines += ['<table style="border: 1px solid black">']
        # for player in players:
        #     row_cells = [
        #         f"<td {STYLE}>{player.nickname}</td>",
        #         f"<td {STYLE}>{player.name}</td>",
        #         ]
        #     lines += [f"<tr>{''.join(row_cells)}<tr/>"]
        # lines += ["</table>"]
        # lines += ["<br/>"]

        for player in players:
            lines += [f"{player.nickname}: {player.name} {player.telephone}<br/>"]
        lines += ["<br/>"]

        lines += ['<table style="border: 1px solid black">']
        row_cells = [f"<th {STYLE}>Week</th>"]
        row_cells += [f"<th {STYLE}>{cell}</th>" for cell in courts]
        row_cells += [f"<th {STYLE}>Off</th>"]
        lines += [f"<tr>{''.join(row_cells)}<tr/>"]

        for week in self.weeks:
            row_cells = [f"<th {STYLE}>{week.date}</th>"]
            for p1, p2 in week.matches:
                if p1.nickname > p2.nickname:
                    p1, p2 = p2, p1
                row_cells += [f"<td {STYLE}>{p1.nickname} v {p2.nickname}</td>"]
            row_cells += [f"<td {STYLE}>{week.get_players_off(self.players)}</td>"]
            lines += [f"<tr>{''.join(row_cells)}<tr/>"]

        if args.playoffs:
            row_cells = [f"<th {STYLE}>{args.playoffs}</th>"]
            row_cells += [f"<td {STYLE}>TBD</td>"] * (len(courts) + 1)
            lines += [f"<tr>{''.join(row_cells)}<tr/>"]

        lines += ["</table>"]
        return "\n".join(lines)

    @property
    def as_code(self):
        lines = ["PLAYERS = ["]
        for player in players:
            lines += [f'    {player.varname} := Player("{player.name}", "{player.nickname}", "{player.telephone}"),']
        lines += ["]", ""]

        lines += ["SEASON = {"]
        for week in self.weeks:
            lines += [f'    "{week.date}": ' + "{"]
            for court, (p1, p2) in zip(courts, week.matches):
                if p1.name > p2.name:
                    p1, p2 = p2, p1
                lines += [f'        "{court}": {{{p1.varname}: None, {p2.varname}: None}},']
            lines += ["    },"]
        lines += ["}"]
        return "\n".join(lines)

while 1:
    random.seed(seed)

    schedule = Schedule()
    try:
        schedule.do()
    except RuntimeError:
        seed += 1
        break
    except KeyboardInterrupt:
        print(f"seed={seed}")
        break
    else:
        print(f"seed={seed}")
        break

print(schedule.get_summary())

matches = []
for week in schedule.weeks:
    for court, (player1, player2) in zip(week.courts, week.matches):
        matches.append([week.date, court, (player1.name, None), (player2.name, None)])
    matches.append([week.date, "off", week.get_players_off(schedule.players)])

with open(f"unreported_matches_{GROUP}.py", "w") as handle:
    # json.dump(matches, handle, indent=2)
    pprint.pprint(matches, handle)

with open(f"reported_matches_{GROUP}.py", "w") as handle:
    handle.write('[]')

# if args.html:
#     assert not args.code
#     print(schedule.as_html)
# elif args.code:
#     print(schedule.as_code)
# else:
#     print(schedule.get_summary())
