document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.querySelector('form');
    const submitBtn = document.querySelector('button[type="submit"]');

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