"""
Solution for automatically generating EOD reports from List of Sessions
csv exports
"""
__author__ = 'Isaac'

import csv
import re
from datetime import datetime, timedelta

EXAMPLE = 'C:/Users/Isaac/Projects/python-list-of-sessions/los_export.csv'

class ListOfSessions(object):

    def __init__(self, csv_file):
        rows = []
        with open(csv_file) as raw_file:
            rows = [row for row in csv.reader(raw_file)]
        self.rows = self.__preprocess(rows)

    def generate_report(self):
        """Generate the end of day report from object data"""
        segments = self.__split_by_unique_value('segment', self.rows)
        for row_dicts in segments.itervalues():
            row_dicts = self.__split_by_unique_value('stage', row_dicts)

        return segments

    def __iter__(self):
        """Allow iteration over list of sessions, returns row dicts"""
        return iter(self.rows)

    # TODO: Split QA and review fields to determine session duration
    def __preprocess(self, rows):
        """Fix the dodgy csv output by list of sessions and convert
        data types. Converts integers, durations, and boolean values
        based on strings in row fields.
        """
        # Fix malformed rows due to commas in rec name field
        fixed_rows = []
        for row in rows:
            if len(row) > 12:
                offset = len(row) - 7
                rec_name = ''.join(row[4:offset])
                fixed = row[:4] + [rec_name] + row[offset:]
                fixed_rows.append(fixed)
            else:
                fixed_rows.append(row)

        # Convert data types
        converted_rows = []
        for row in converted_rows:
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
            converted_rows.append(new)

        # Turn into a dict
        row_dicts = []
        headers = map(lambda h: h.lower().replace(' ', '_'), rows[0])
        for row in rows[1:]:
            row_dict = {h: v for h, v in zip(headers, row)}
            row_dicts.append(row_dict)

        # Determine segment for each row
        for row_dict in row_dicts:
            customer = row_dict['customer']
            if '@transcribeme.com' in customer:
                if 'srt' in customer:
                    row_dict['segment'] = 'srt'
                elif 'spanish' in customer:
                    row_dict['segment'] = 'spanish'
                else:
                    row_dict['segment'] = 'b2b'
            else:
                row_dict['segment'] = 'b2c'

        # Determine stage for each row
        # TODO: This will have to change when I break up QA and Review fields
        for row_dict in row_dicts:
            if not row_dict['is_finished?']:
                row_dict['stage'] = 'transcribing'
            else:
                if not row_dict['qa']:
                    row_dict['stage'] = 'ready_for_qa'
                elif 'Expires' in row_dict['qa']:
                    row_dict['stage'] = 'qa_in_progress'
                else:
                    if not row_dict['review']:
                        row_dict['stage'] = 'ready_for_review'
                    elif 'Expires' in row_dict['review']:
                        row_dict['stage'] = 'review_in_progress'
                    else:
                        row_dict['stage'] = 'completed'

        return row_dicts

    def __sum_durations(self, row_dicts):
        """Given a list of row dicts, return total duration as timedelta"""
        durations = [row['duration'] for row in row_dicts]
        total = reduce(lambda x, y: x + y, durations)

        return total

    def __split_by_unique_value(self, field, row_dicts):
        """Split a list of row dicts by unique value in field"""
        out = {}
        for row in row_dicts:
            value = row[field]
            if value not in out.keys():
                out[value] = [row]
            else:
                out[value] += [row]

        return out