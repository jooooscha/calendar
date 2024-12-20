from dateutil.rrule import rrulestr
from datetime import datetime
from dateutil.tz import UTC

def process_rrule(rrule, start) -> list[datetime]:
    """ Processes the rrule and returns all dates on which the event should occur """

    #  rrule_str = f"RRULE:{rrule}"
    #  rule_string = f"DTSTART:{start}\n{rrule_str}"

    try:
        rule = rrulestr(rrule, dtstart=start)
    except: # TODO:
        #  breakpoint()
        return [ start ]
    occurrences = list(rule)
    return occurrences


def event_to_dict(row: dict) -> dict:

    return {
        "id": row["id"],
        "calendarId": row["calendarId"],
        "title": row["title"],
        "body": row["body"],
        "start": row["start"],
        "end": row["start"],
        "location": row["location"],
        "isReadOnly": row["isReadOnly"],
        "category": row["category"],
    }
