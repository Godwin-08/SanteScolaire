// Scripts spécifiques au dossier médical

document.addEventListener('DOMContentLoaded', function() {
    const printBtn = document.getElementById('printBtn');
    
    if (printBtn) {
        printBtn.addEventListener('click', function() {
            // On peut ajouter ici des actions avant l'impression (ex: masquer certains éléments)
            window.print();
        });
    }
});