// Ajoute une nouvelle ligne de prescription
function addRow() {
    const container = document.getElementById('prescription-container');
    const rows = document.querySelectorAll('.prescription-row');
    
    // On clone la première ligne existante
    const newRow = rows[0].cloneNode(true);
    
    // On vide les champs texte du clone pour une nouvelle saisie
    newRow.querySelectorAll('input').forEach(input => {
        input.value = '';
    });
    
    container.appendChild(newRow);
    
    // UX : Focus automatique sur le premier champ de la nouvelle ligne
    const firstInput = newRow.querySelector('input');
    if (firstInput) firstInput.focus();
}

// Supprime une ligne de prescription
function removeRow(btn) {
    const row = btn.closest('.prescription-row');
    const rows = document.querySelectorAll('.prescription-row'); // Compte total actuel
    
    // Vérifier si la ligne contient des données
    let hasData = false;
    row.querySelectorAll('input').forEach(input => {
        if (input.value.trim() !== '') hasData = true;
    });

    if (rows.length > 1) {
        // Si des données sont présentes, on demande confirmation
        if (!hasData || confirm("Voulez-vous supprimer cette ligne de prescription ?")) {
            row.remove();
        }
    } else {
        btn.closest('.prescription-row').querySelectorAll('input').forEach(input => input.value = '');
    }
}

// Gestion de la disponibilité des médecins (AJAX)
document.addEventListener('DOMContentLoaded', function() {
    const medecinSelect = document.querySelector('select[name="id_medecin_rdv"]');
    const dateInput = document.querySelector('input[name="date_rdv"]');
    
    if (medecinSelect && dateInput) {
        // Création de l'élément pour afficher les messages de feedback
        const feedbackDiv = document.createElement('div');
        feedbackDiv.className = 'mt-2 small';
        dateInput.parentNode.appendChild(feedbackDiv);

        function checkAvailability() {
            const medecinId = medecinSelect.value;
            const fullDate = dateInput.value; // Format: YYYY-MM-DDTHH:MM
            
            if (!medecinId || !fullDate) {
                feedbackDiv.innerHTML = '';
                return;
            }

            const dateJour = fullDate.split('T')[0]; // YYYY-MM-DD
            const timeHeure = fullDate.split('T')[1]; // HH:MM

            // Appel AJAX vers le backend
            fetch(`/api/creneaux_occupes/${medecinId}/${dateJour}`)
                .then(response => response.json())
                .then(data => {
                    // data est un tableau d'heures occupées ex: ['09:00', '10:15']
                    let html = '';
                    
                    // 1. Vérification du conflit direct
                    if (data.includes(timeHeure)) {
                        html += `<div class="text-danger fw-bold mb-1"><i class="fas fa-times-circle me-1"></i>Attention : Le créneau de ${timeHeure} est déjà réservé !</div>`;
                    } else {
                        html += `<div class="text-success fw-bold mb-1"><i class="fas fa-check-circle me-1"></i>Le créneau de ${timeHeure} est libre.</div>`;
                    }

                    // 2. Affichage de la liste des créneaux pris pour info
                    if (data.length > 0) {
                        html += `<div class="text-muted fst-italic">Heures indisponibles ce jour : ${data.join(', ')}</div>`;
                    } else {
                        html += `<div class="text-muted fst-italic">Aucun autre rendez-vous ce jour-là.</div>`;
                    }
                    
                    feedbackDiv.innerHTML = html;
                })
                .catch(err => console.error("Erreur vérification dispo:", err));
        }

        // Écouteurs d'événements sur les changements
        medecinSelect.addEventListener('change', checkAvailability);
        dateInput.addEventListener('change', checkAvailability);
        dateInput.addEventListener('input', checkAvailability); // Pour réagir pendant la saisie
    }
});