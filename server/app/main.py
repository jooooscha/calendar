import caldav
import caldav.elements.ical # for calendarColor
from flask import Flask, jsonify
from dataclasses import dataclass, asdict
import random
import json
import app.db as db
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from dateutil.rrule import rrulestr

# remove ctrl+c traceback
import signal
import sys
signal.signal(signal.SIGINT, lambda x, y: sys.exit(0))

DATEFORMAT = "%Y-%m-%dT%H:%M"

load_dotenv()

app = Flask(__name__)

def sync_data():

    print("dropping old data")
    db.purge()

    print("Starting data sync")
    # CalDAV server details
    url = os.getenv('SERVER_URL')
    username = os.getenv("USER")
    password = os.getenv("PASSWORD")

    # Connect to the CalDAV server
    try:
        client = caldav.DAVClient(url, username=username, password=password)
    except:
        print("Could not login to DAV client")
        return 404
    principal = client.principal()
    calendars = principal.calendars()

    if not calendars:
        print("No calendars found")
        return jsonify({"error": "No calendars found"}), 404
    else:
        print(f"Found {len(calendars)} calendars")
        for cal in calendars:
            print(f"syncing {cal}")

            if cal.name != "TESTCAL": # TODO: remove
                continue

            color = cal.get_property(caldav.elements.ical.CalendarColor())
            db.add_cal(cal.id, cal.name, color, visible=True)

            print(f"{cal} has {len(cal.events())} events")
            for event in cal.events():
                for component in event.icalendar_instance.walk():
                    if component.name == "VEVENT":

                        #  print(component.get("rrule"))
                        #  print(component.get("exdate"))
                        #  breakpoint()

                        endDate = component.get("dtend")

                        start = component.get("dtstart").dt.strftime(DATEFORMAT)
                        if endDate and endDate.dt:
                            end = endDate.dt.strftime(DATEFORMAT)
                        else:
                            end = start

                        match component.get("dtstart").params.get("value"):
                            case "DATE":
                                category = "allday"

                                # for some reason, nextcloud stores the end date for all-day events as the n+1 date
                                # therefore, we descrease the end date by one
                                fixedend = datetime.strptime(end, DATEFORMAT) - timedelta(days=1)
                                end = fixedend.strftime(DATEFORMAT)

                            case _:
                                category = "time"

                        exdates = []
                        exdate_list = component.get("exdate")
                        if exdate_list is not None:
                            for exdate in exdate_list:
                                exdates.append(exdate.dts[0].dt)

                        if component.get("rrule"):
                            print(component.get("rrule"))
                            rrule = component.get("rrule").to_ical().decode()
                        else:
                            rrule = ""

                        db.add_event(
                            id=component.get("uid"),
                            calendar_id=cal.id,
                            title=component.get("summary"),
                            body=component.get("description"),
                            start=start,
                            end=end,
                            location=component.get("location"),
                            read_only=True,
                            category=category,
                            rrule=rrule,
                            exdates=exdates
                        )
    print("DB data updated")

def init(sync=False):
    global calendar_list
    global event_map

    db.init()

    if sync:
        sync_data()

def assemble_events(row):
    events = []
    start = row["start"]
    if row["rrule"]:
        # handle rrule
        rrule = row["rrule"]
        rrule_str = f"RRULE:{rrule}"
        # Create a string combining the DTSTART and RRULE
        rule_string = f"DTSTART:{start}\n{rrule_str}"
        # Parse the rrule
        rule = rrulestr(rule_string)
        occurrences = list(rule)

        for o in occurrences:
            events.append(
                {
                    "id": row["id"],
                    "calendarId": row["calendarId"],
                    "title": row["title"],
                    "body": row["body"],
                    "start": row["start"],
                    "end": row["end"],
                    "location": row["location"],
                    "isReadOnly": row["isReadOnly"],
                    "category": row["category"],
                }
            )
    else:
        events.append([
            {
                "id": row["id"],
                "calendarId": row["calendarId"],
                "title": row["title"],
                "body": row["body"],
                "start": row["start"],
                "end": row["end"],
                "location": row["location"],
                "isReadOnly": row["isReadOnly"],
                "category": row["category"],
            }
        ])
    return events

@app.route('/caldav/calendars')
def get_calendars():
    data = db.get_calendars()
    cals = [
        {
            "id": r[0],
            "visible": r[1],
            "name": r[2],
            "backgroundColor": r[3],
        }
        for r in data
    ]

    return jsonify(cals)

@app.route('/caldav/events')
def get_caldav_events():
    data = db.get_events()

    events = []
    for row in data:
        events.append(assemble_events(row))

    print(events)
    return events



@app.route('/caldav/toggle/<cal_id>')
def toggle_calendar(cal_id):
    visible = db.get_visible(cal_id)
    db.set_visible(cal_id, not visible)
    ret = {
        "error": False,
        "visible": not visible,
    }
    return jsonify(ret)

@app.route('/caldav/toggle_all/<state>')
def toggle_calendar_all(state):
    state = True if state == "true" else False
    db.set_visibility_all(state)
    ret = {
        "error": False,
    }
    return jsonify(ret)

@app.route('/caldav/sync')
def sync_calendar():
    x = sync_data()
    if x is None:
        ret = {
            "error": False,
        }
    else:
        ret = {
            "error": True,
        }
    return jsonify(ret)



def main():
    print("Connect to DAV")
    init(False)
    print("Running server...")
    app.run(debug=True)

if __name__ == '__main__':
    main()
