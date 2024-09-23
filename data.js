import { $, createCalButton, CalButton, Manager } from "./utils.js"

const manager = new Manager();

// export const update = function() {
//     $('.range').innerHTML = tuiCal.renderRange.start
// }

// const update = manager.update
function update() {}

update()

var weekButton = $('.week');
weekButton.addEventListener('click', function () {
    manager.changeView("week");
});
var weekButton = $('.month');
weekButton.addEventListener('click', function () {
    manager.changeView("month");
});
var weekButton = $('.multi-week');
weekButton.addEventListener('click', function () {
    manager.changeView("multi-week");
});

var nextButton = $('.next');
nextButton.addEventListener('click', function () {
    manager.next();
});

var prevButton = $('.prev');
prevButton.addEventListener('click', function () {
    manager.prev();
});

var all_off_button = $('.all_off');
all_off_button.addEventListener('click', function () {
    manager.toggleAll(false);
});

var all_on_button = $('.all_on');
all_on_button.addEventListener('click', function () {
    manager.toggleAll(true);
});

async function init_calendars() {
    await fetch("http://localhost:5000/caldav/calendars")
        .then(response => {
            return response.text()
        }).then(text => {
            let cals = JSON.parse(text)
            manager.addCals(cals)
        })
}

function fetch_events() {
    fetch("http://localhost:5000/caldav/events").then(response => {
        return response.text()
    }).then(text => {
            let events = JSON.parse(text)
            console.log(events)
            manager.addEvents(events)
        })
}

init_calendars().then(() => {
    fetch_events()
})
