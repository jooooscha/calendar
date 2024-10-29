import app.db as db
import sqlite3
from datetime import datetime, timedelta
import caldav
import os
import app.db as db
from app.event_helper import *
import caldav.elements.ical # for calendarColor

def init(sync=False):
    global calendar_list
    global event_map

    db.init()

    if sync:
        sync_data()

def sync_data():
    """ Drops tables and refills them from dav """

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
        return {"error": "No calendars found"}, 404
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


                        # Handle reoccuring events
                        if component.get("rrule"):
                            rrule = component.get("rrule").to_ical().decode()

                            # handle exclusion dates
                            exdates = []
                            exdate_list = component.get("exdate")
                            if exdate_list is not None:
                                if not isinstance(exdate_list, list):
                                    exdate_list = [ exdate_list ]

                                for exdate in exdate_list:
                                    exdate_list = exdate.dts
                                    exdate_list = [ d.dt for d in exdate_list ]
                                    exdates += (exdate_list)

                            occurrences = process_rrule(rrule, start)
                            for occ in occurrences:

                                if exdate_list and occ in exdate_list:
                                    # if date is in exdate_list, we skip it
                                    continue

                                # only load dates 10 years into the future
                                if occ.year > datetime.now().year + 10:
                                    continue

                                # TODO: fix this ugly .date() thing:

                                # event start, not start of this repetition
                                # we calculate that later with the diff
                                start_date = start.date() if isinstance(start, datetime) else start
                                diff = occ.date() - start_date if isinstance(occ, datetime) else occ - start_date

                                start = start + diff
                                end = end + diff

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
                                    exdates=component.get("exdate"),
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
                                exdates=component.get("exdate"),
                                conn=conn,
                                commit=False,
                                close=False,
                            )

            conn.commit()
            conn.close()
    print("DB data updated")
