document.addEventListener('DOMContentLoaded', function() {
    // Éléments du DOM
    const searchInput = document.getElementById('search');
    const grid = document.getElementById('studentGrid');
    const emptyState = document.getElementById('emptyState');
    const resultCount = document.getElementById('resultCount');
    const countDisplay = document.getElementById('count');

    if (searchInput) {
        // Fonction utilitaire Debounce (attend la fin de la frappe)
        const debounce = (func, wait) => {
            let timeout;
            return function(...args) {
                clearTimeout(timeout);
                timeout = setTimeout(() => func.apply(this, args), wait);
            };
        };

        // Écouteur optimisé sur la barre de recherche
        searchInput.addEventListener('input', debounce(function(e) {
            const term = e.target.value.toLowerCase().trim();
            const cards = document.querySelectorAll('.student-card');
            let visibleCount = 0;

            if (term.length > 0) {
                // Filtrage des cartes élèves
                cards.forEach(card => {
                    const name = card.getAttribute('data-name').toLowerCase();
                    const id = card.getAttribute('data-id').toString().toLowerCase();
                    
                    // Recherche par nom ou ID
                    if (name.includes(term) || id.includes(term)) {
                        card.classList.remove('d-none');
                        visibleCount++;
                    } else {
                        card.classList.add('d-none');
                    }
                });

                // Gestion de l'affichage (Grille vs État vide)
                if (visibleCount > 0) {
                    grid.classList.remove('d-none');
                    emptyState.classList.add('d-none');
                    resultCount.classList.remove('d-none');
                    countDisplay.innerText = visibleCount;
                } else {
                    grid.classList.add('d-none');
                    emptyState.classList.remove('d-none');
                    resultCount.classList.add('d-none');
                }
            } else {
                // Si recherche vide, on remet l'état initial
                // Vérification : Si des filtres URL sont actifs, on ne cache pas la grille
                const urlParams = new URLSearchParams(window.location.search);
                if (urlParams.has('classe') || urlParams.has('avec_rdv')) {
                    cards.forEach(card => card.classList.remove('d-none')); // Réaffiche tout
                    grid.classList.remove('d-none');
                    emptyState.classList.add('d-none');
                    resultCount.classList.remove('d-none');
                    countDisplay.innerText = cards.length;
                } else {
                    grid.classList.add('d-none');
                    emptyState.classList.remove('d-none');
                    resultCount.classList.add('d-none');
                }
            }
        }, 300)); // Délai de 300ms
    }
});

// Fonction de tri alphabétique des cartes
function sortCards() {
    const grid = document.getElementById('studentGrid');
    const cards = Array.from(document.getElementsByClassName('student-card'));
    if (cards.length === 0) return;

    // Tri basé sur l'attribut data-name
    cards.sort((a, b) => {
        return a.getAttribute('data-name').localeCompare(b.getAttribute('data-name'));
    });

    grid.innerHTML = ""; 
    cards.forEach(card => grid.appendChild(card));
}