document.addEventListener('DOMContentLoaded', function() {
    const toggles = document.querySelectorAll('[data-toggle-password]');

    toggles.forEach(function(btn) {
        const targetId = btn.getAttribute('data-target');
        if (!targetId) {
            return;
        }
        const input = document.getElementById(targetId);
        if (!input) {
            return;
        }

        btn.addEventListener('click', function() {
            const isPassword = input.type === 'password';
            input.type = isPassword ? 'text' : 'password';
            btn.setAttribute('aria-pressed', String(isPassword));

            const icon = btn.querySelector('i');
            const label = btn.querySelector('span');

            if (icon) {
                icon.classList.toggle('fa-eye', !isPassword);
                icon.classList.toggle('fa-eye-slash', isPassword);
            }
            if (label) {
                label.textContent = isPassword ? 'Masquer' : 'Afficher';
            }
        });
    });
});
