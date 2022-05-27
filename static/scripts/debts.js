let darkMode = localStorage.getItem('darkMode');

console.log(localStorage)


const enableDarkMode = () => {
    var background = document.getElementsByClassName('background')[0];
    background.classList.add("background_dark");

    var debtors = document.getElementsByClassName('debtors')[0];
    debtors.classList.add("debtors_dark");

    var debts = document.getElementsByClassName('debts')[0];
    debts.classList.add("debts_dark");
    localStorage.setItem('darkMode', 'enabled');
}


const disableDarkMode = () => {
    var background = document.getElementsByClassName('background')[0];
    background.classList.remove("background_dark");

    var debtors = document.getElementsByClassName('debtors')[0];
    debtors.classList.remove("debtors_dark");

    var debts = document.getElementsByClassName('debts')[0];
    debts.classList.remove("debts_dark");
    localStorage.setItem('darkMode', null);
}


if (darkMode === 'enabled') {
    enableDarkMode();

}