from schedule import Schedule

for group in ["3.5", "4.0"]:
    s = Schedule("SINGLES", group)
    s.reset_report_flags()
    s.save()
