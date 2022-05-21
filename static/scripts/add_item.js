// check for saved 'darkMode' in localStorage
let darkMode = localStorage.getItem('darkMode');

console.log(localStorage)

const enableDarkMode = () => {
    // 1. Add the class to the body
    // console.log(darkMode);
    var add_photo = document.getElementsByClassName('item_add_screen')[0];
    add_photo.classList.add("item_add_screen_dark");
    var v9_31 = document.getElementsByClassName('v9_31')[0];
    v9_31.classList.add("v9_31_dark");
    var photo_input = document.getElementsByClassName('name_input')[0];
    photo_input.classList.add("name_input_dark");

    var description_input = document.getElementsByClassName('description_input')[0];
    description_input.classList.add("description_input_dark");

    var address_input = document.getElementsByClassName('address_input')[0];
    address_input.classList.add("address_input_dark");
    // var login = document.getElementsByClassName('login')[0];
    // login.classList.add("login_dark");
    var title = document.getElementsByClassName('title')[0];
    title.classList.add("title_dark");
    // 2. Update darkMode in localStorage
    localStorage.setItem('darkMode', 'enabled');
}

const disableDarkMode = () => {
    // 1. Remove the class from the body

    // console.log(darkMode);

    var add_photo = document.getElementsByClassName('house_add_screen')[0];
    add_photo.classList.remove("house_add_screen_dark");
    var v9_31 = document.getElementsByClassName('v9_31')[0];
    v9_31.classList.remove("v9_31_dark");
    var photo_input = document.getElementsByClassName('name_input')[0];
    photo_input.classList.remove("name_input_dark");
    var description_input = document.getElementsByClassName('description_input')[0];
    description_input.classList.remove("description_input_dark");

    var address_input = document.getElementsByClassName('address_input')[0];
    address_input.classList.remove("address_input_dark");
    // var login = document.getElementsByClassName('login')[0];
    // login.classList.remove("login_dark");
    var title = document.getElementsByClassName('title')[0];
    title.classList.remove("title_dark");
    // 2. Update darkMode in localStorage 
    localStorage.setItem('darkMode', null);
}

// If the user already visited and enabled darkMode
// start things off with it on
if (darkMode === 'enabled') {
    // console.log(darkMode);
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