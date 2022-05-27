let darkMode = localStorage.getItem('darkMode');

console.log(localStorage)


const enableDarkMode = () => {
    var v9_31 = document.getElementsByClassName('v9_31')[0];
    v9_31.classList.add("v9_31_dark");

    var invite_user_screen = document.getElementsByClassName('invite_user_screen')[0];
    invite_user_screen.classList.add("invite_user_screen_dark");
    localStorage.setItem('darkMode', 'enabled');
}


const disableDarkMode = () => {
    var v9_31 = document.getElementsByClassName('v9_31')[0];
    v9_31.classList.remove("v9_31_dark");

    var invite_user_screen = document.getElementsByClassName('invite_user_screen')[0];
    invite_user_screen.classList.remove("invite_user_screen_dark");
    localStorage.setItem('darkMode', null);
}


if (darkMode === 'enabled') {
    enableDarkMode();

}