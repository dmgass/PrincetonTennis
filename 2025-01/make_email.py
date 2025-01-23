import argparse
from schedule import Schedule, SEASON

parser = argparse.ArgumentParser()
parser.add_argument("week")
parser.add_argument("group", choices=["3.5", "4.0"])
parser.add_argument("--league", choices=["SINGLES", "DOUBLES"], default="SINGLES")
parser.add_argument("--fmt", choices=["text", "html"], default="html")
args = parser.parse_args()

schedule = Schedule(args.league, args.group, args.week)

if args.fmt == "html":
    emails = [player.email for player in schedule.players.values()]
    emails.append('bjansen@princetonclub.net')
    if 'dan.gass@gmail.com' not in emails:
        emails.append('dan.gass@gmail.com')

    print(", ".join(emails))
    print("<br/>")
    print(f"Princeton Wednesday {args.group} Tennis Matches/Standings - {args.week}")
    print("<br/>")
    print("<br/>")

    if schedule.unreported_results:
        print("<h2>Unreported Matches</h2>")
        print("<br/>\n".join(schedule.unreported_results))

    if schedule.results_to_report:
        print("<h2>Recently Reported Matches</h2>")
        print("<br/>\n".join(schedule.results_to_report))

    print("<h2>Standings</h2>")
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
    print(f"https://github.com/dmgass/PrincetonTennis/tree/main/{SEASON}/{args.league}/{args.group}")

else:
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

    print("Standings")
    print("=========")
    print(schedule.get_standings("by_games", fmt="text"))
    print()
    print()

    print("Remaining Schedule")
    print("==================")
    print(schedule.make_table("text", args.week))
    print()
    print()
