// check for saved 'darkMode' in localStorage
let darkMode = localStorage.getItem('darkMode');

console.log(localStorage)

const enableDarkMode = () => {
    // 1. Add the class to the body
    // console.log(darkMode);
    var add_photo = document.getElementsByClassName('notification_screen')[0];
    add_photo.classList.add("notification_screen_dark");
    var v9_31 = document.getElementsByClassName('v9_31')[0];
    v9_31.classList.add("v9_31_dark");
    // 2. Update darkMode in localStorage
    localStorage.setItem('darkMode', 'enabled');
}

const disableDarkMode = () => {
    // 1. Remove the class from the body

    // console.log(darkMode);

    var add_photo = document.getElementsByClassName('photo_add_screen')[0];
    add_photo.classList.remove("photo_add_screen_dark");
    var v9_31 = document.getElementsByClassName('v9_31')[0];
    v9_31.classList.remove("v9_31_dark");
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