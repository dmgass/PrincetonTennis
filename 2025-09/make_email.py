import argparse
import os
from schedule import Schedule, SEASON, get_leagues

parser = argparse.ArgumentParser()
parser.add_argument("week")
parser.add_argument("league", choices=get_leagues())
parser.add_argument("--fmt", choices=["text", "html"], default="html")
args = parser.parse_args()

schedule = Schedule(args.league, args.week)

DAYS = {
    'SUN': 'Sunday',
    'MON': 'Monday',
    'TUE': 'Tuesday',
    'WED': 'Wednesday',
    'THU': 'Thursday',
    'FRI': 'Friday',
    'SAT': 'Saturday'
}

league_type, league = os.path.split(args.league)
day, group = league.split('-')
title = 'Schedule/Records' if league_type == 'singles' else 'Schedule'

if args.fmt == "html":
    emails = [player.email for player in schedule.players.values()]
    emails.append('bjansen@princetonclub.net')
    if 'dan.gass@gmail.com' not in emails:
        emails.append('dan.gass@gmail.com')

    print(", ".join(emails))
    print("<br/>")
    print(f"Princeton {DAYS[day]} {group} {league_type.title()} Tennis {title} - {args.week}")
    print("<br/>")
    print("<br/>")

    if league_type == 'singles':
        if schedule.unreported_results:
            print("<h2>Unreported Matches</h2>")
            print("<br/>\n".join(schedule.unreported_results))

        if schedule.results_to_report:
            print("<h2>Recently Reported Matches</h2>")
            print("<br/>\n".join(schedule.results_to_report))

        print("<h2>Records</h2>")
        print(schedule.get_standings("by_games", fmt="html"))

        print("<h2>Remaining Schedule</h2>")

    print(schedule.make_table("html", args.week))
    print("<br/>")
    print("<br/>")

    contacts = [f"{player.name}: {player.phone}" for player in schedule.players.values()]
    print("<h2>Contact Info</h2>")
    print("<br/>\n".join(contacts) + "<br/>")
    print("<br/>")
    print("<br/>")

    subs = [f"{sub.name}: {sub.phone}" for sub in schedule.subs.values()]
    if subs:
        print("<h2>Subs</h2>")
        print("<br/>\n".join(subs) + "<br/>")
        print("<br/>")
        print("<br/>")

    print(f"https://github.com/dmgass/PrincetonTennis/tree/main/{SEASON}/{args.league}")

else:
    if league_type == 'singles':
        if schedule.unreported_results:
            print("Unreported Matches")
            print("==================")
            for line in schedule.unreported_results:
                print(line)
            print()
            print()

        if schedule.results_to_report:
            print("Recently Reported Matches")
            print("=========================")
            for line in schedule.results_to_report:
                print(line)
            print()
            print()

        print("Records")
        print("=========")
        print(schedule.get_standings("by_games", fmt="text"))
        print()
        print()

        print("Remaining Schedule")
        print("==================")

    print(schedule.make_table("text", args.week))
    print()
    print()

    print("Matches to Bill")
    print("===============")
    for player in schedule.players.values():
        print(f"{player.name}: {player.num_to_bill}")
    print()
    print()
