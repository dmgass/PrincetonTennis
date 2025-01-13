import argparse
from texttable import Texttable
from schedule import Schedule, SEASON

parser = argparse.ArgumentParser()
parser.add_argument("week")
parser.add_argument("group", choices=["3.5", "4.0"])
parser.add_argument("--league", choices=["SINGLES", "DOUBLES"], default="SINGLES")
parser.add_argument("--fmt", choices=["text", "html"], default="html")
args = parser.parse_args()

schedule = Schedule(args.league, args.group)
blank_line = "" if args.fmt == "text" else "<br/>"

emails = [player.email for player in schedule.players.values()]
emails.append('bjansen@princetonclub.net')
if 'dan.gass@gmail.com' not in emails:
    emails.append('dan.gass@gmail.com')

print(", ".join(emails))
print(blank_line)
print(f"Princeton Wednesday {args.group} Tennis Matches/Standings - {args.week}")
print(blank_line)
print(blank_line)
print(schedule.make_table(args.fmt, args.week))
print(blank_line)
print(blank_line)

if args.fmt == "html":
    contacts = [f"{player.name}: {player.phone}" for player in schedule.players.values()]
    print("<h2>Contact Info</h2>")
    print("<br/>\n".join(contacts) + "<br/>")
    print("<br/>")
    print("<br/>")
    print(f"https://github.com/dmgass/PrincetonTennis/tree/main/{SEASON}/{args.league}/{args.group}")

"""
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
    print("<br/>\n".join(contact_info) + "<br/>)
    print("<br/>")
    print("<br/>")
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
"""