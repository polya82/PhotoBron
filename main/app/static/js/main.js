document.addEventListener('DOMContentLoaded', () => {
    const burger = document.getElementById('burger-menu');
    const nav = document.getElementById('nav-menu');

    if (burger && nav) {
        burger.addEventListener('click', () => {
            nav.classList.toggle('active');
        });
    }
});