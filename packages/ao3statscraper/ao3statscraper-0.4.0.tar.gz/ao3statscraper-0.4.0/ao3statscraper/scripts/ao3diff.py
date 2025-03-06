#!/usr/bin/env python3

import argparse
import os
import datetime


def _parse_diff_args():
    """
    Setup argument parser and read cmdline args.
    """

    parser = argparse.ArgumentParser(
        prog="ao3diff.py",
        description="Show the diff between your current stats and a date in the past.",
        epilog="""
The program will require you to log in to your AO3 account.
Note that the program can only show you the diff in stats based on snapshots
fetched and stored using `ao3get`. If there is no snapshot at the time
interval you would like to see, then the program will try and find the closest
date it can.
Also note that while this program still fetches you current stats, it will
never write them down. Please use `ao3get` to store snapshots instead.
""",
    )

    parser.add_argument(
        "-d",
        "--day",
        action="store_true",
        default=False,
        dest="day",
        help="Show the diff from the stats a day ago.",
    )
    parser.add_argument(
        "-w",
        "--week",
        action="store_true",
        default=False,
        dest="week",
        help="Show the diff from the stats a week ago. This is the default running mode.",
    )
    parser.add_argument(
        "-m",
        "--month",
        action="store_true",
        default=False,
        dest="month",
        help="Show the diff from the stats a month ago.",
    )
    parser.add_argument(
        "-y",
        "--year",
        action="store_true",
        default=False,
        dest="year",
        help="Show the diff from the stats a year ago.",
    )
    parser.add_argument(
        "date",
        nargs="?",
        default="None",
        help="Show the diff from the stats compared to DATE in the format YYYY-MM-DD",
    )

    args = parser.parse_args()

    return args


def ao3diff():
    from ..configuration import Config
    from ..statsdata import (
        WorkStatsData,
        TotStatsData,
        get_timestamp_from_filename,
        get_dump_file_list,
    )
    from ..scrape import UserSession

    args = _parse_diff_args()
    conf = Config()

    now = datetime.datetime.now()

    diff = None

    if args.date != "None":
        try:
            y, m, d = args.date.split("-")
        except ValueError:
            print(f"'{args.date}' has invalid date format. Provide as YYYY-MM-DD.")
            quit()

        then = datetime.datetime(
            year=int(y),
            month=int(m),
            day=int(d),
            hour=now.hour,
            minute=now.minute,
            second=now.second,
        )
        diff = now - then

    else:
        if args.day:
            diff = datetime.timedelta(days=1)
        elif args.week:
            diff = datetime.timedelta(days=7)
        elif args.month:
            diff = datetime.timedelta(days=30)
        elif args.year:
            diff = datetime.timedelta(days=365)

        else:
            # Default running mode
            diff = datetime.timedelta(days=7)

    if diff is None:
        raise ValueError("How did we get here?")

    # Get and check list of dump files.
    tsfiles = get_dump_file_list(conf, TotStatsData)
    wsfiles = get_dump_file_list(conf, WorkStatsData)

    if len(tsfiles) == 0:
        print("Error: Found no total stats files.")
        quit()
    if len(tsfiles) == 1:
        print("Error: Found only 1 total stats file.")
        quit()
    if len(wsfiles) == 0:
        print("Error: Found no work stats files.")
        quit()
    if len(wsfiles) == 1:
        print("Error: Found only 1 work stats file.")
        quit()

    snaptimes = [get_timestamp_from_filename(TotStatsData, tf) for tf in tsfiles]

    timediffs = [abs(now - st) for st in snaptimes]

    # find snapshot closest to the one you want displayed.
    index = 0
    minval = datetime.timedelta().max
    for i, dt in enumerate(timediffs):
        ddt = abs(dt - diff)
        if ddt < minval:
            minval = ddt
            index = i

    # Fetch new data
    session = UserSession(conf)
    ts_new, ws_new = session.get_stats(conf)

    tsfile = tsfiles[index]
    wsfile = wsfiles[index]
    ts_old = TotStatsData(conf, source=tsfile)
    ws_old = WorkStatsData(conf, source=wsfile)

    ts_new.diff(ts_old)
    changes = ws_new.diff(ws_old)

    t = ts_old.timestamp
    print(
        f"Changes compared to {t.year:04d}-{t.month:02d}-{t.day:02d} {t.hour:02d}:{t.minute:02d}:{t.second:02d}"
    )

    return


if __name__ == "__main__":
    ao3diff()
