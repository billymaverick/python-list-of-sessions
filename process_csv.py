"""
Solution for automatically generating EOD reports from List of Sessions
csv exports
"""
__author__ = 'Isaac'

import csv
import re
from datetime import timedelta

EXAMPLE = 'C:/Users/Isaac/Projects/python-list-of-sessions/los_export.csv'
LEN_REGEX = re.compile("\d+:\d+:\d+")


def sum_durations(records):
    """Given a list of record hashes, return their total duration in seconds"""
    durations = [record['duration'] for record in records]
    total = reduce(lambda x, y: x + y, durations)

    return total


def convert_types(rows):
    """Attempt to convert data of various types"""
    # TODO: Possible unicode problems?
    out = []

    for row in rows:
        new = []
        for string in row:
            # Convert durations, in the format hh:mm:ss
            if re.match("^\d+:\d+:\d+$", string):
                h, m, s = map(int, string.split(':'))
                duration = timedelta(hours=h, minutes=m, seconds=s)
                new.append(duration)
            # Convert integers
            elif re.match("^\d+$", string):
                new.append(int(string))
            # Convert "yes" or "no" to True or False
            elif re.match("^yes$", string, re.IGNORECASE):
                new.append(True)
            elif re.match("^no$", string, re.IGNORECASE):
                new.append(False)
            # No matches for conversion
            else:
                new.append(string)
        out.append(new)

    return out


def convert_csv(rows):
    """Convert list of csv rows into a dictionary"""
    headers = map(lambda h: h.lower().replace(' ', '_'), rows[0])
    out = []

    for row in rows[1:]:
        row_dict = {h: v for h, v in zip(headers, row)}
        out.append(row_dict)

    return out


def fix_rows(rows):
    """Fix rows malformed due to commas in recording name field"""
    # TODO: Magic numbers
    out = []

    for row in rows:
        if len(row) > 12:
            offset = len(row) - 7
            rec_name = ''.join(row[4:offset])
            fixed = row[:4] + [rec_name] + row[offset:]
            out.append(fixed)
        else:
            out.append(row)

    return out


def load_csv(filename):
    """Slurp all rows in given filename into list"""
    out = []
    with open(filename) as csv_file:
        out = [row for row in csv.reader(csv_file)]

    return out