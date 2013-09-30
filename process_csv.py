"""
Solution for automatically generating EOD reports from List of Sessions
csv exports
"""
__author__ = 'Isaac'

import csv
import re
from datetime import timedelta
from collections import namedtuple

EXAMPLE = 'C:/Users/Isaac/Projects/python-list-of-sessions/los_export.csv'

class Records(dict):
    """Subclass of dict to allow setting extra attributes"""
    pass


def generate_eod_report(records):
    """Generate end of day report from list of sessions csv export"""
    segments = split_records_by_segment(records)
    stages_per_seg = {k: split_records_by_stage(v) for k, v in segments.iteritems()}
    report_str = """
    {}

    - Transcribing - {}
    - Ready for QA - {}
    - QA in progress - {}
    - Ready for review - {}
    - Review in progress {}
    """
    for segment in stages_per_seg:
        pass


def split_records_by_segment(records):

    records_by_segment = {'b2b': [], 'b2c': [], 'spanish': [], 'srt': []}
    for record in records:
        customer = record['customer']
        if '@transcribeme.com' in customer:
            if 'srt' in customer:
                records_by_segment['srt'].append(record)
            elif 'spanish' in customer:
                records_by_segment['spanish'].append(record)
            else:
                records_by_segment['b2b'].append(record)
        else:
            records_by_segment['b2c'].append(record)

    return records_by_segment


def split_records_by_stage(records):
    """Divide records according to what stage of processing they're at"""
    records_by_stage = {'transcribing': [], 'ready_for_qa': [],
                        'qa_in_progress': [], 'ready_for_review': [],
                        'review_in_progress': [], 'completed': []}
    for record in records:
        if not record['is_finished?']:
            records_by_stage['transcribing'].append(record)
        elif record['is_finished?'] and not record['qa']:
            records_by_stage['ready_for_qa'].append(record)
        elif 'Expires' in record['qa']:
            records_by_stage['qa_in_progress'].append(record)
        elif 'Submitted' in record['qa'] and not record['review']:
            records_by_stage['ready_for_review'].append(record)
        elif 'Expires' in record['review']:
            records_by_stage['review_in_progress'].append(record)
        else:
            records_by_stage['completed'].append(record)

    return records_by_stage


def split_by_unique_value(field, records):
    """Split a list of records into sublists by common field"""
    out = Records()
    out.field = field # Allows checking which field was split on
    for record in records:
        value = record[field]
        if value not in out.keys():
            out[value] = [record]
        else:
            out[value].append(record)

    return out


def load_and_process(filename):
    """Create a list of formatted record hashes from given file"""
    # TODO: These function names are confusing as fuck
    raw = load_csv(filename)
    fixed = fix_rows(raw)
    type_converted = convert_types(fixed)

    return convert_csv(type_converted)


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


def partition(predicate, iterable):
    match = []
    no_match = []
    for item in iterable:
        if predicate(item):
            match.append(item)
        else:
            no_match.append(item)

    return match, no_match