import argparse
import json
import operator
import os
import pprint
import random
from texttable import Texttable

SEASON = "2025-01"

class Player:

    def __init__(self, name, nickname):
        self.name = name
        self.nickname = nickname
        self.possible_opponents = []
        self.num_matches = 0
        self.opponent_counts = {}
        self.num_off_weeks = 0

    @property
    def priority(self):
        return self.num_matches - self.num_off_weeks

    def record_match(self, opponents):
        self.num_matches += 1
        for opponent in opponents:
            if opponent is self:
                continue
            self.opponent_counts[opponent] += 1
            try:
                self.possible_opponents.remove(opponent)
            except ValueError:
                pass

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
        self[nickname] = Player(name, nickname)

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

    def __init__(self, date, data):
        self.date = date
        self.off = data.pop("off")
        self.requested_off = data.pop("requested_off")
        self.matches = data
        
    @property
    def xis_available(self):
        return len(self.matches) < len(self.courts)

    def xassign_match(self, player1, player2):
        self.players_scheduled += [player1, player2]
        self.matches.append((player1, player2))
        player1.record_match(player2)
        player2.record_match(player1)
        return f"{self.date} {player1.name} {player2.name}"

    def xget_players_off(self, players):
        return ", ".join(sorted(
            set(p.name for p in players.values()) -
            set(p.name for p in self.players_scheduled)
        ))


class Schedule:

    def __init__(self, league, group):
        self.league = league
        self.matches_dir = f"{league.lower()}/{group}"
        self.matches_filename = f"{self.matches_dir}/matches.py"
        self.players = self.get_players(league, group)
        self.weeks = self.load()

    def get_players(self, league, group):
        players = Players()

        for name, info in json.load(open("../members.json")).items():
            seasons = info['group']

            try:
                player_group = seasons[f"{SEASON}/{league}"]
            except KeyError:
                continue

            if player_group == group:
                players.add(name, info["nickname"])

        players.reset(initialize_opponent_counts=True)

        return players

    def load(self):
        with open(self.matches_filename) as handle:
            file_data = eval(handle.read())

        weeks = {}

        for date, data in file_data.items():
            weeks[date] = Week(date, data)

        for week in weeks.values():
            for name in week.requested_off:
                self.players[name].num_off_weeks += 1

            for _court, match_data in week.matches.items():
                player_names, *score_data = match_data
                opponents = [self.players[n] for n in player_names if n]
                for opponent in opponents:
                    opponent.record_match(opponents)

                if score_data:
                    (score1, score2, reported), = score_data
                    # TODO

        return weeks
    
    def fill(self):
        for week in self.weeks.values():
            assert all(name in self.players for name in week.requested_off), week.requested_off
            available_names = list(set(self.players.keys()) - set(week.requested_off))
            random.shuffle(available_names)
            available_players = list(
                sorted(
                    list(self.players[n] for n in available_names), 
                    key=operator.attrgetter("priority")
                ))


            matches = {}
            off = list(self.players)
            for court, match_data in week.matches.items():
                player_names, *score_data = match_data
                if all(player_names):
                    for name in player_names:
                        off.remove(name)
                    matches[court] = match_data
                else:
                    assert not week.off, f"week {week.date}: off should be empty"
                    num_players = len(player_names)
                    assert len(available_players) >= num_players, f"np: {num_players} available_players"
                    players = available_players[:num_players]
                    available_players = available_players[num_players:]
                    for player in players:
                        player.record_match(players)
                        off.remove(player.nickname)

                    matches[court] = [[player.nickname for player in players]] + score_data

            week.matches = matches
            week.off = off

    def save(self, backup=False):
        if backup:
            filenames = os.listdir(self.matches_dir)
            backups = sorted(n for n in filenames if n.startswith("matches_"))
            if backups:
                number = int(backups[-1].split('.')[0].split('_')[1]) + 1
            else:
                number = 0
            backup_name = f"{self.matches_dir}/matches_{number:03}.py"

            os.rename(self.matches_filename, backup_name)

        matches = {}
        for week in self.weeks.values():
            week_data = week.matches.copy()
            week_data["off"] = week.off
            week_data["requested_off"] = week.requested_off
            matches[week.date] = week_data

        with open(self.matches_filename, "w") as handle:
            pprint.pprint(matches, handle)

    def get_text_summary(self):
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
        for week in self.weeks.values():
            for court in week.matches.keys():
                courts.add(court)

        table = Texttable()
        rows = [["Week"] + list(sorted(courts)) + ["Off"]]
        for week in self.weeks.values():
            row = [week.date]
            for court in courts:
                try:
                    opponents = week.matches[court][0]
                except KeyError:
                    opponents = []
                row.append(", ".join(opponents))
            row.append(", ".join(week.off))
            rows.append(row)
        table.add_rows(rows)
        lines += [table.draw()]
        return "\n".join(lines)

    def xget_available_weeks(self, player):
         return [
             week for week in self.weeks 
             if week.is_available and (week.date not in player.off) and (player not in week.players_scheduled)
             ]

    def xcreate_match(self):
        for player in self.players.in_least_scheduled_order:
            available_weeks = self.get_available_weeks(player)
            for opponent in player.opponents_by_least_scheduled:
                for week in available_weeks:
                    if week.date not in opponent.off and opponent not in week.players_scheduled:
                        if player.nickname > opponent.nickname:
                            player, opponent = opponent, player
                        return week.assign_match(player, opponent)

        return None

    def xdo(self):
        num_matches = sum([len(week.courts) for week in self.weeks])
        num_preloaded = sum([len(week.matches) for week in self.weeks])

        for match_number in range(num_preloaded + 1, num_matches + 1):
            match = self.create_match()

            if not match:
                self.players.reset()
                match = self.create_match()

            if not match:
                raise RuntimeError()

    def xget_summary(self):
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("league", choices=["SINGLES", "DOUBLES"])
    parser.add_argument("group", choices=["3.5", "4.0"])
    parser.add_argument("--seed", default=0)
    args = parser.parse_args()

    random.seed(args.seed)

    schedule = Schedule(args.league, args.group)
    schedule.fill()
    schedule.save(backup=True)

    print(schedule.get_text_summary())

