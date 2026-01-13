document.addEventListener('DOMContentLoaded', function () {
    const toggles = document.querySelectorAll('.toggle-password');

    toggles.forEach(function (toggle) {
        const targetId = toggle.getAttribute('data-target');
        const input = document.getElementById(targetId);

        if (!input) {
            return;
        }

        toggle.addEventListener('click', function () {
            const isPassword = input.getAttribute('type') === 'password';
            input.setAttribute('type', isPassword ? 'text' : 'password');
            toggle.classList.toggle('fa-eye');
            toggle.classList.toggle('fa-eye-slash');
        });
    });
});