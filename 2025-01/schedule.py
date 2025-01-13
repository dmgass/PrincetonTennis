import argparse
import json
import operator
import os
import pprint
import random
from texttable import Texttable

SEASON = "2025-01"

STYLE = 'style="border: 1px solid black"'

class Player:

    def __init__(self, name, nickname, phone, email):
        self.name = name
        self.nickname = nickname
        self.phone = phone
        self.email = email
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

    def add(self, name, nickname, phone, email):
        self[nickname] = Player(name, nickname, phone, email)

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
        self.off = list(sorted(data.pop("off")))
        self.requested_off = data.pop("requested_off")
        self.matches = data
        for court in data.keys():
            data[court][0] = list(sorted(data[court][0]))


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
                players.add(name, info["nickname"], info["phone"], info["email"])

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
            if self.league == "DOUBLES":
                available_players = list(
                    sorted(
                        list(self.players[n] for n in available_names), 
                        key=operator.attrgetter("priority")
                    ))
            else:
                available_players = list(
                    sorted(
                        list(self.players[n] for n in available_names), 
                        key=operator.attrgetter("num_matches")
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
                    if num_players == 2:
                        player1 = available_players.pop(0)
                        def rank(player):
                            return player1.opponent_counts[player]
                        candidates = list(sorted(available_players, key=rank))
                        player2 = candidates[0]
                        available_players.remove(player2)
                        players = [player1, player2]
                    else:
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
        lines = [self.make_table(fmt="text")]
        lines += [""]
        lines += [
            "Player Opponent Counts",
            "======================"
        ]
        for player in self.players.values():
            lines += [f"{player.name} ({player.num_matches} total)"]
            back_to_backs = {}

            if self.league == "SINGLES":
                last_opponent = None
                last_week = None
                for week in self.weeks.values():
                    for match_data in week.matches.values():
                        names = list(match_data[0])
                        if player.nickname in names:
                            names.remove(player.nickname)
                            opponent = names.pop()
                            if last_opponent == opponent:
                                back_to_backs[opponent] = f" {last_week} & {week.date}"
                            last_opponent = opponent
                    last_week = week.date

            for opponent, count in player.opponent_counts.items():
                lines += [f"  {opponent.nickname}: {count} {back_to_backs.get(opponent.nickname, '')}"]
            streaks = []
            off = []
            for week in self.weeks.values():
                if player.nickname in week.off:
                    off.append(week.date)
                elif off:
                    if len(off) > 1:
                        streaks.append("-".join(off))
                    off = []
            if streaks:
                lines += [",".join(streaks)]

            lines += [""]

        lines += [
            "Player Match Counts",
            "==================="
            ]
        for player in self.players.values():
            lines += [f"{player.num_matches} - {player.name}"]

        return "\n".join(lines)

    def make_table(self, fmt, start_week=None):
        lines = []

        courts = set()
        for week in self.weeks.values():
            for court in week.matches.keys():
                courts.add(court)

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

        if fmt == "html":
            lines = [
                '<table style="border: 1px solid black">',
                "".join(f"<th {STYLE}>{cell}</th>" for cell in rows[0]),
            ]
            for cells in rows[1:]:
                row_cells = "".join(f"<td {STYLE}>{cell}</td>" for cell in cells)
                lines += [f"<tr>{row_cells}<tr/>"]
            lines += ["</table>"]
        elif fmt == "text":
            table = Texttable()
            table.add_rows(rows)
            lines += [table.draw()]
        else:
            raise RuntimeError(f"Illegal format: {fmt}")

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

