import argparse
import json
import operator
import os
import pprint
import random
from texttable import Texttable

SEASON = "2025-09"

STYLE = 'style="border: 1px solid black"'

INJURED = {}

# billing skips injured for unplayed matches prior to this date
# (this can be used to resume billing for a just one injured player)
BILL_AFTER = '12/31'


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
        self.games_won = 0
        self.games_lost = 0
        self.matches_won = 0
        self.matches_lost = 0
        self.matches_tied = 0
        self.makeups_to_play = 0
        self.num_to_bill = 0

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

    @classmethod
    def make_table(cls, players, rank_name, fmt):
        rank_property = getattr(cls, "rank_" + rank_name).fget
        cells_property = getattr(cls, "cells_" + rank_name).fget

        header_row = getattr(cls, "header_" + rank_name)
        rows = [cells_property(player) for player in sorted(players.values(), key=rank_property)]

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
            self.nickname, 
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
            self.nickname, 
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
                self.nickname,
                f"{self.games_won / self.matches_played:0.1f}", 
                f"{self.games_lost / self.matches_played:0.1f}", 
            )
        
        return self.nickname, 0, 0

    @property
    def rank_by_name(self):
        return self.name

    @property
    def cells_by_name(self):
        return self.cells_by_match

    header_by_name = header_by_match


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

    def __init__(self, league, date=None):
        league_type, group = os.path.split(league)
        self.league_type = league_type.upper()
        self.matches_dir = league
        self.matches_filename = f"{self.matches_dir}/matches.py"
        self.players = self.get_players(self.league_type, group)
        self.subs = self.get_subs(self.league_type, group)
        self.weeks, self.unreported_results, self.results_to_report = self.load(date)

    def get_players(self, league_type, group):
        players = Players()

        for name, info in json.load(open("../members.json")).items():
            seasons = info['group']

            try:
                player_group = seasons[f"{SEASON}/{league_type}"]
            except KeyError:
                continue

            if player_group == group:
                players.add(name, info["nickname"], info["phone"], info["email"])

        players.reset(initialize_opponent_counts=True)

        return players

    def get_subs(self, league_type, group):
        league = f"{SEASON}/{league_type}/{group}"

        players = Players()

        for name, info in json.load(open("../members.json")).items():
            try:
                leagues = info['sub']
            except KeyError:
                continue

            if league in leagues:
                players.add(name, info["nickname"], info["phone"], info["email"])

        return players

    def load(self, this_weeks_date):
        with open(self.matches_filename) as handle:
            file_data = eval(handle.read())

        weeks = {}

        results_to_report = []
        unreported_results = []

        for date, data in file_data.items():
            weeks[date] = Week(date, data)

        for week in weeks.values():
            for name in week.requested_off:
                if name != "TBD":
                    self.players[name].num_off_weeks += 1

            for _court, match_data in week.matches.items():
                player_names, *score_data = match_data
                opponents = [self.players[n] for n in player_names if n and n != "TBD"]
                for opponent in opponents:
                    opponent.record_match(opponents)

                if opponents and score_data and score_data[0]:
                    if "TBD" in player_names:
                        continue
                    name1, name2 = player_names
                    player1 = self.players[name1]
                    player2 = self.players[name2]
                    (score1, score2, report), = score_data

                    bill = True

                    if score1 is None or score2 is None:
                        if name1 in INJURED or name2 in INJURED:
                            bill = week.date >= BILL_AFTER

                        if this_weeks_date and this_weeks_date > week.date:
                            unreported_results.append(f"{week.date}: {name1} v {name2}")
                            player1.makeups_to_play += 1
                            player2.makeups_to_play += 1

                    else:
                        max_score = max([score1, score2])

                        if max_score != 9:
                            loser_score = int(min([score1, score2]) * 9 / max_score)
                            
                            if score1 == max_score:
                                player1.games_won += 9
                                player2.games_won += loser_score
                                player1.games_lost += loser_score
                                player2.games_lost += 9
                            else:
                                player1.games_won += loser_score
                                player2.games_won += 9
                                player1.games_lost += 9
                                player2.games_lost += loser_score
                        else:
                            player1.games_won += score1
                            player2.games_won += score2
                            player1.games_lost += score2
                            player2.games_lost += score1

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

                        if report:
                            results_to_report.append(f"{week.date}: {result}")
                    if bill:
                        player1.num_to_bill += 1
                        player2.num_to_bill += 1

        return weeks, unreported_results, results_to_report
    
    def fill(self):
        for week in self.weeks.values():
            if "TBD" in week.requested_off:
                continue
            assert all(name in self.players for name in week.requested_off), week.requested_off
            available_names = list(set(self.players.keys()) - set(week.requested_off))
            random.shuffle(available_names)
            if self.league_type == "DOUBLES":
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

    def reset_report_flags(self):
        for week in self.weeks.values():
            for court, match_data in week.matches.items():
                player_names, *score_data = match_data
                if score_data[0] and None not in score_data[0]:
                    score_data[0][-1] = False

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

            if self.league_type == "SINGLES":
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
            if start_week and week.date < start_week:
                continue
            row = [week.date]
            for court in courts:
                try:
                    opponents = week.matches[court][0]
                except KeyError:
                    opponents = []
                row.append(", ".join(opponents))
            off = list(sorted(week.off))
            try:
                off.remove('Trung')
            except ValueError:
                pass
            row.append(", ".join(off))
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

    def get_standings(self, rank_name, fmt):
        return Player.make_table(self.players, rank_name, fmt)

def get_leagues():
    leagues = []
    for league_type in ["singles", "doubles"]:
        for name in os.listdir(league_type):
            possible_league = os.path.join(league_type, name)
            if os.path.isdir(possible_league):
                leagues.append(possible_league)

    return leagues


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("league", choices=get_leagues())
    parser.add_argument("--seed", default=0)
    args = parser.parse_args()

    random.seed(args.seed)

    schedule = Schedule(args.league)
    schedule.fill()
    schedule.save(backup=True)

    print(schedule.get_text_summary())

