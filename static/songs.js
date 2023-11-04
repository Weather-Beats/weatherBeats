

const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);
const location_param = urlParams.get('location');

if (location_param) {

    let doc_sel = document.querySelector(".content-list");

    const moodFromWeather = await fetch('/moodFromWeatherAPI?location=' + location_param);
    const data = await moodFromWeather.json();

    let row_data = "";

    for (let i of data.mood) {
        row_data += `
            <li> ${i} </li>
        `
    }

    doc_sel.innerHTML = row_data;

}

