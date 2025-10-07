from schedule import Schedule

for group in ["WED-3.X", "WED-4.0"]:
    s = Schedule(f"singles/{group}")
    s.reset_report_flags()
    s.save()
