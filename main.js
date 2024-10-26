import { $, CalButton, Manager } from "./manager.js"

const manager = new Manager();

manager.update()

function butttonSuccessAnimation(btn, success) {
    btn.classList.remove('btn-secondary');

    let btnclass;
    if (success) {
        btnclass = "btn-success"
    } else {
        btnclass = "btn-danger"
    }
    btn.classList.add(btnclass);

    // After 3 seconds, revert the button back to the original color
    setTimeout(() => {
        btn.classList.remove(btnclass);
        btn.classList.add('btn-secondary');
    }, 3000)
}

// implement the buttons
$('.week').addEventListener('click', () => manager.changeView("week") );
$('.month').addEventListener('click', () => manager.changeView("month") );
$('.multi-week').addEventListener('click', () => manager.changeView("multi-week") );
$('.next').addEventListener('click', () => manager.next() );
$('.prev').addEventListener('click', () => manager.prev() );
$('.today').addEventListener('click', () => manager.today() );
$('.allOn').addEventListener('click', () => manager.toggleAll(true) );
$('.allOff').addEventListener('click', () => manager.toggleAll(false) );
$('.syncbtn').addEventListener('click', () =>  sync() )


// implement the sync button functionality and animation
async function sync() {
    let syncbtn = $('.syncbtn')
    syncbtn.disable = true
    syncbtn.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Syncing ...`;
    try {
        await fetch("http://localhost:5000/caldav/sync")
            .then(response => {
                return response.text()
            }).then(text => {
                let ret = JSON.parse(text)
                console.log("ret:", ret)
            })
        butttonSuccessAnimation(syncbtn, true)
    } catch (error) {
        console.log("Could not finisch update: " + error)
        butttonSuccessAnimation(syncbtn, false)
    } finally {
        syncbtn.disable = false
        syncbtn.innerHTML = 'Sync';
        manager.update()
    }
}

//init sync of calendars
async function init_calendars() {
    console.debug("Fetching calendars")
    await fetch("http://localhost:5000/caldav/calendars")
        .then(response => {
            return response.text()
        }).then(text => {
            let cals = JSON.parse(text)
            console.debug("Calendars loaded: ", cals)
            manager.addCals(cals)
        })
}

function fetch_events() {
    console.debug("Fetching events")
    fetch("http://localhost:5000/caldav/events").then(response => {
        return response.text()
    }).then(text => {
            let events = JSON.parse(text)
            console.debug("Events loaded: ", events)

            manager.addEvents(events)
        })
}

init_calendars().then(() => {
    fetch_events()
})
