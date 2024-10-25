
import argparse

def check_schedule(group):
    players = {}
    num_matches = 0

    for filename in [f"unreported_matches_{group}.py", f"reported_matches_{group}.py"]:
        with open(filename) as handle:
            py = handle.read()

        for match in eval(py):
            try:
                date, court, (player1, _), (player2, _) = match
            except ValueError:
                continue

            num_matches += 1
            players.setdefault(player1, {})
            players.setdefault(player2, {})
            players[player1].setdefault(player2, 0)
            players[player2].setdefault(player1, 0)
            players[player1][player2] += 1
            players[player2][player1] += 1

    for player, opponents in sorted(players.items()):
        print(player)
        for opponent, count in sorted(opponents.items()):
            print(f"  {opponent}: {count}")

    print()

    for player, opponents in sorted(players.items()):
        print(f"{player}: {sum(opponents.values())}")

    print()
    print(f"total: {num_matches}")


parser = argparse.ArgumentParser()
parser.add_argument("group", choices=["3.5", "4.0"])

args = parser.parse_args()

check_schedule(args.group)
