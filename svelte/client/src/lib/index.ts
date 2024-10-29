// place files you want to import through the `$lib` alias in this folder.


// load events from server
export async function fetch_events() {
  console.debug("Fetching events")

  return await fetch("http://localhost:5000/caldav/events").then(response => {
    return response.text()
  }).then(text => {
    let events = JSON.parse(text)
    console.debug("Events loaded: ", events)
    return events;
  })

}

// load calenars from server
export async function fetch_calendars() {
  console.debug("Fetching cals")

  return await fetch("http://localhost:5000/caldav/calendars").then(response => {
    return response.text()
  }).then(text => {
    let cals = JSON.parse(text)
    console.debug("Cals loaded: ", cals)
    return cals;
  })
}
