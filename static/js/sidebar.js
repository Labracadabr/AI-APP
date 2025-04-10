document.addEventListener('DOMContentLoaded', function () {

    const gameBtn = document.getElementById('gameBtn');
    const langToggle = document.getElementById('langToggle');
    const profileBtn = document.getElementById('profileBtn');
    const progressBtn = document.getElementById('progressBtn');
    const extraBtn = document.getElementById('extraBtn');

    profileBtn.addEventListener('click', function () {
        window.location.href = `/register`;
    });
    gameBtn.addEventListener('click', function () {
        window.location.href = `/draw`;
    });
    progressBtn.addEventListener('click', function () => {
        window.location.href = '/progress';
    });

});
