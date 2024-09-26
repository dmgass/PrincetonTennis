import pprint

for group in ["3.5", "4.0"]:
    unreported_filename = f"unreported_matches_{group}.py"
    reported_filename = f"reported_matches_{group}.py"
    
    with open(unreported_filename) as handle:
        unreported = eval(handle.read())

    with open(reported_filename) as handle:
        reported = eval(handle.read())

    new_unreported = []

    for match in unreported:
        try:
            date, court, (name1, score1), (name2, score2) = match

        except ValueError:
            # must be off week, keep it
            new_unreported.append(match)
            continue

        if None in (score1, score2):
            # not scored yet, keep it
            new_unreported.append(match)
            continue

        reported.append(match)
 
    with open(unreported_filename, "w") as handle:
        pprint.pprint(new_unreported, handle)

    with open(reported_filename, "w") as handle:
        pprint.pprint(reported, handle)

