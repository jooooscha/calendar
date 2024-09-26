export const $ = function (selector) {
    return document.querySelector(selector);
}

export class Manager {
    constructor() {
        // create calendar objec
        this.tuiCal = new tui.Calendar('#calendar', {
            defaultView: 'month', // Can be 'day', 'week', or 'month'
            useCreationPopup: true, // Enable popup for creating events
            useDetailPopup: true, // Enable popup for event details
            useFormPopup: true,
            isReadOnly: true,
            usageStatistics: false,
            month: {
                visibleWeeksCount: 5,
                startDayOfWeek: 1,
                narrowWeekend: false,
                visibleEventCount: 6,
            },
            week: {
                startDayOfWeek: 1,
                taskView: ["task"],
            },
            calendars: [
                // {
                //     id: '1',
                //     name: 'Personal Calendar',
                //     backgroundColor: '#9e5fff',
                //     borderColor: '#9e5fff',
                // }
            ],
        });

        this.cals = {}
    }
    next() {
        this.tuiCal.next(); // move to next moneth/week (depends on context)
        this.update()
    }
    prev() {
        this.tuiCal.prev(); // move to prev month/week (depens on context)
        this.update()
    }
    today() {
        this.tuiCal.today();
        this.update()
    }
    changeView(view) { // change view to month, week, multi-week
        if (view == "week") {
            this.tuiCal.changeView("week");
        } else if (view == "month") {
            this.tuiCal.changeView("month");
            this.tuiCal.setOptions({
                month: {
                    visibleWeeksCount: 0,
                },
            });
        } else if (view == "multi-week") {
            this.tuiCal.changeView("month");
            this.tuiCal.setOptions({
                month: {
                    visibleWeeksCount: 5,
                },
            });
        }
        this.update()
    }
    update() { // update text and stuff
        let d = this.tuiCal.renderRange.start;
        let date = new Date(d)
        const options = {
          weekday: 'long',  // Full weekday name (e.g., Monday)
          day: 'numeric',   // Numeric day (e.g., 23)
          month: 'long',    // Full month name (e.g., September)
          year: 'numeric'   // Full year (e.g., 2024)
        };

        const formattedDate = date.toLocaleDateString('en-GB', options);
        $('.date').innerHTML = formattedDate
    }
    addCals(cals) { // add a new calendar to tuiCAl
        this.tuiCal.setCalendars(cals)
        for (let cal of cals) {
            let id = cal.id;
            let tuiCal = this.tuiCal
            const callback = function(b) {
                // hide calendar
                tuiCal.setCalendarVisibility(cal.id, b)
            }
            let button = new CalButton(
                cal.id,
                cal.name,
                cal.visible,
                cal.backgroundColor,
                callback
            );
            this.cals[id] = button
            button.addSelfToList()
        }
    }
    addEvents(events) { // add new events to the calendar
        this.tuiCal.createEvents(events)
    }
    toggleAll(bool) { // toggle all clalendars
        fetch("http://localhost:5000/caldav/toggle_all/" + bool)
            .then(response => {
                return response.text()
            })

        for (let id in this.cals) {
            let cal = this.cals[id]
            this.tuiCal.setCalendarVisibility(cal.id, bool)
        }
        let cals = $("#calendar-list").children
        for (let cal of cals) {
            cal.children[0].checked = bool
        }
    }
}

export class CalButton {
    constructor(id, name, checked, color, onclickCallback) {
        this.id = id;
        this.name = name;
        this.checked = checked;
        this.callback = onclickCallback;
        this.color = color
    }

    addSelfToList() {
        let id = this.id
        let callback = this.callback

        // let calItem = document.createElement("div");

        // calItem.classList.add("calItem")

        // let circle = document.createElement("div");
        // circle.classList.add("circle")
        // circle.style.backgroundColor = this.color;
        // calItem.appendChild(circle)

        let label = document.createElement("label")
        label.classList.add("btn")
        // label.classList.add("btn-primary")
        label.classList.add("calendarBtnLabel")
        label.setAttribute("for", "button-" + id)
        label.textContent = this.name
        label.style.backgroundColor = this.color;

        let r = parseInt(this.color.substring(1, 3), 16);
        let g = parseInt(this.color.substring(3, 5), 16);
        let b = parseInt(this.color.substring(5, 7), 16);
        let luminance = 0.299 * r + 0.587 * g + 0.114 * b;
        let textColor = luminance > 176 ? '#202020' : '#eeeeee';

        label.style.color = textColor;

        let checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.classList.add("btn-check")
        checkbox.id = "button-" + id
        checkbox.setAttribute("autocomplete", "off")
        checkbox.checked = this.checked;
        label.style.opacity = this.checked ? 1 : 0.5;
        checkbox.onclick = function(event) {
            event.preventDefault()
            // toggle calendar in backend and call callback
            fetch("http://localhost:5000/caldav/toggle/" + id)
                .then(resp => resp.text())
                .then(v => {
                    v = JSON.parse(v)
                    this.checked = v.visible
                    label.style.opacity = v.visible ? 1 : 0.5;
                    callback(v.visible)
                })
        }
        // calItem.appendChild(checkbox)

        $("#calendar-list").appendChild(checkbox);
        $("#calendar-list").appendChild(label);
    }
}
