document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.querySelector('form');
    const submitBtn = document.querySelector('button[type="submit"]');
    const roleSelect = document.getElementById('roleSelect');
    const prenomGroup = document.getElementById('prenomGroup');
    const prenomInput = document.getElementById('userPrenom');

    const togglePrenomField = () => {
        if (!roleSelect || !prenomGroup || !prenomInput) return;
        const isAdmin = roleSelect.value === 'admin';
        prenomInput.required = !isAdmin;
        prenomInput.disabled = isAdmin;
        prenomGroup.classList.toggle('d-none', isAdmin);
        if (isAdmin) prenomInput.value = '';
    };

    if (roleSelect) {
        roleSelect.addEventListener('change', togglePrenomField);
        togglePrenomField();
    }

    if (loginForm && submitBtn) {
        loginForm.addEventListener('submit', function(e) {
            // Si le formulaire est valide, on active l'état de chargement
            if (loginForm.checkValidity()) {
                const originalWidth = submitBtn.offsetWidth;
                
                // On fige la largeur pour éviter que le bouton ne rétrécisse
                submitBtn.style.width = `${originalWidth}px`;
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i>';
                
                // Sécurité : Réactiver après 8s si le serveur ne répond pas
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = 'VÉRIFIER L\'ACCÈS';
                }, 8000);
            }
            loginForm.classList.add('was-validated');
        });
    }
});