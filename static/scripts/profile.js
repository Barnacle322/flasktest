// check for saved 'darkMode' in localStorage
let darkMode = localStorage.getItem('darkMode');

console.log(localStorage)

const enableDarkMode = () => {
    // 1. Add the class to the body
    // console.log(darkMode);

    var background = document.getElementsByClassName('background')[0];
    background.classList.add("background_dark");
    var logout_button = document.getElementsByClassName('logout_button')[0];
    logout_button.classList.add("logout_button_dark");
    var notifications_button = document.getElementsByClassName('notifications_button')[0];
    notifications_button.classList.add("notifications_button_dark");
    try {
        var white_margin = document.getElementsByClassName('white_margin')[0];
        white_margin.classList.add("black_margin");
    } catch (error) {
        //pass
    }

    try {
        var house = document.getElementsByClassName('house')[0];
        house.classList.add("house_dark");
    } catch (error) {
        //pass
    }

    try {
        var house_name_plate = document.getElementsByClassName('house_name_plate')[0];
        house_name_plate.classList.add("house_name_plate_dark");
    } catch (error) {
        //pass
    }

    var add_field = document.getElementsByClassName('add_field')[0];
    add_field.classList.add("add_field_dark");
    var top_bar = document.getElementsByClassName('top_bar')[0];
    top_bar.classList.add("top_bar_dark");
    var name = document.getElementsByClassName('name')[0];
    name.classList.add("name_dark");
    // 2. Update darkMode in localStorage
    localStorage.setItem('darkMode', 'enabled');
}

const disableDarkMode = () => {
    // 1. Remove the class from the body

    // console.log(darkMode);

    var background = document.getElementsByClassName('background')[0];
    background.classList.remove("background_dark");
    var logout_button = document.getElementsByClassName('logout_button')[0];
    logout_button.classList.remove("logout_button_dark");
    var notifications_button = document.getElementsByClassName('notifications_button')[0];
    notifications_button.classList.remove("notifications_button_dark");
    try {
        var white_margin = document.getElementsByClassName('white_margin')[0];
        white_margin.classList.remove("black_margin");
    } catch (error) {
        //pass
    }
    try {
        var house = document.getElementsByClassName('house')[0];
        house.classList.remove("house_dark");
    } catch (error) {
        //pass
    }

    try {
        var house_name_plate = document.getElementsByClassName('house_name_plate')[0];
        house_name_plate.classList.remove("house_name_plate_dark")
    } catch (error) {
        //pass
    }
    var add_field = document.getElementsByClassName('add_field')[0];
    add_field.classList.remove("add_field_dark");
    var top_bar = document.getElementsByClassName('top_bar')[0];
    top_bar.classList.remove("top_bar_dark");
    var name = document.getElementsByClassName('name')[0];
    name.classList.remove("name_dark");
    // 2. Update darkMode in localStorage 
    localStorage.setItem('darkMode', null);
}

// If the user already visited and enabled darkMode
// start things off with it on
if (darkMode === 'enabled') {
    // console.log(darkMode);
    var button = document.getElementById('switch-button');
    button.checked = true;
    enableDarkMode();

}

function myFunction() {
    darkMode = localStorage.getItem('darkMode');
    // console.log(darkMode);

    // if it not current enabled, enable it
    if (darkMode !== 'enabled') {
        enableDarkMode();
        // if it has been enabled, turn it off  
    } else {
        disableDarkMode();
    }
}