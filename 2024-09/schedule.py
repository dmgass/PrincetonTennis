import argparse
import json
import operator
import pprint
import random
from texttable import Texttable

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
            set(p.name for p in players.values()) -
            set(p.name for p in self.players_scheduled)
        ))


class Schedule:

    def __init__(self):
        self.players = Players()

        for name, info in json.load(open("../members.json")).items():
            seasons = info['group']

            try:
                group = seasons[SEASON]
            except KeyError:
                continue

            if group == args.group:
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
            self.weeks.append(Week(date, courts[args.group]))

        prescheduled = PRESCHEDULED[args.group]

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
            for court in week_courts[args.group]:
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

parser = argparse.ArgumentParser()
parser.add_argument("group", choices=["3.5", "4.0"])
parser.add_argument("--seed", default=0)
args = parser.parse_args()

seed = args.seed

while 1:
    random.seed(seed)

    schedule = Schedule()
    try:
        schedule.do()
        break # bypass retry, temporarily just try once
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
        matches.append([week.date, court, (player1.nickname, None), (player2.nickname, None)])
    matches.append([week.date, "off", week.get_players_off(schedule.players)])

with open(f"unreported_matches_{args.group}.py", "w") as handle:
    pprint.pprint(matches, handle)

with open(f"reported_matches_{args.group}.py", "w") as handle:
    handle.write('[]')
