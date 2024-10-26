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
from app.event_helper import *
from zoneinfo import ZoneInfo
import sqlite3

# remove ctrl+c traceback
import signal
import sys
signal.signal(signal.SIGINT, lambda x, y: sys.exit(0))

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


            # Add calendar to DB (if not exists)
            color = cal.get_property(caldav.elements.ical.CalendarColor())
            db.add_cal(cal.id, cal.name, color, visible=True)

            # only connect once for all events
            conn = sqlite3.connect('calendars.db')


            # go through all events
            print(f"{cal} has {len(cal.events())} events")
            for event in cal.events():
                for component in event.icalendar_instance.walk():
                    if component.name == "VEVENT":

                        endDate = component.get("dtend")

                        start = component.get("dtstart").dt
                        if endDate and endDate.dt:
                            end = endDate.dt
                        else:
                            end = start

                        match component.get("dtstart").params.get("value"):
                            case "DATE":
                                category = "allday"

                                # for some reason, nextcloud stores the end date for all-day events as the n+1 date
                                # therefore, we descrease the end date by one
                                end = end - timedelta(days=1)

                            case _:
                                category = "time"

                        exdates = [] # TODO: implement excluded dates

                        #  exdate_list = component.get("exdate")
                        #  if exdate_list is not None:
                        #      for exdate in exdate_list:
                        #          exdates.append(exdate.dts[0].dt)

                        # Handle reoccuring events
                        if component.get("rrule"):
                            rrule = component.get("rrule").to_ical().decode()

                            occurrences = process_rrule(rrule, start)
                            for occ in occurrences:
                                if occ.year > datetime.now().year + 10:
                                    continue

                                # event start, not start of this repetition
                                # we calculate that later with the diff
                                start = start.date() if isinstance(start, datetime) else start
                                diff = occ.date() - start if isinstance(occ, datetime) else occ - start

                                try:
                                    start = start + diff
                                    end = end + diff
                                except:
                                    breakpoint()

                                db.add_event(
                                    id=component.get("uid"),
                                    calendar_id=cal.id,
                                    title=component.get("summary"),
                                    body=component.get("description"),
                                    start=start.isoformat(),
                                    end=end.isoformat(),
                                    location=component.get("location"),
                                    read_only=True,
                                    category=category,
                                    rrule=rrule,
                                    exdates=exdates,
                                    conn=conn,
                                    commit=False,
                                    close=False,
                                )
                        else:
                            rrule = ""

                            db.add_event(
                                id=component.get("uid"),
                                calendar_id=cal.id,
                                title=component.get("summary"),
                                body=component.get("description"),
                                start=start.isoformat(),
                                end=end.isoformat(),
                                location=component.get("location"),
                                read_only=True,
                                category=category,
                                rrule=rrule,
                                exdates=exdates,
                                conn=conn,
                                commit=False,
                                close=False,
                            )

            conn.commit()
            conn.close()
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
        occurrences = process_rrule(row["rrule"], start)

        breakpoint()

        for o in occurrences:
            events.append(event_to_dict(row, new_start=o))
    else:
        events.append([ event_to_dict(row) ])
    return events

@app.route('/caldav/calendars')
def get_calendars():
    data = db.get_calendars()
    print("Calendars in DB", len(data))
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
    print("Events requested")
    data = db.get_events()

    #  events = [ row) for row in data ]

    events = data
    #  breakpoint()

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
        ret = { "error": False, }
    else:
        ret = { "error": True, }
    return jsonify(ret)



def main():
    print("Connect to DAV")
    init(sync=True)
    print("Running server...")
    app.run(debug=True)

if __name__ == '__main__':
    main()
