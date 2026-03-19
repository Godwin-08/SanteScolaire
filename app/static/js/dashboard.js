document.addEventListener('DOMContentLoaded', function() {
    // Récupération des données injectées dans le DOM par Jinja2
    const dataContainer = document.getElementById('chart-data');
    const pieLabels = JSON.parse(dataContainer.dataset.pieLabels);
    const pieValues = JSON.parse(dataContainer.dataset.pieValues);
    const jourLabels = JSON.parse(dataContainer.dataset.jourLabels);
    const jourValues = JSON.parse(dataContainer.dataset.jourValues);

    // Configuration globale
    Chart.defaults.font.family = "'Inter', 'Segoe UI', sans-serif";
    Chart.defaults.color = '#636e72'; // Texte sombre pour le mode clair

    // 1. Graphique Circulaire (Pie Chart) - Motifs ou Médecins selon le rôle
    const pieCanvas = document.getElementById('pieChart');
    if (pieCanvas) {
        const pieCtx = pieCanvas.getContext('2d');
        new Chart(pieCtx, {
            type: 'doughnut',
            data: {
                labels: pieLabels,
                datasets: [{
                    data: pieValues,
                    backgroundColor: [
                        '#10ac84', '#1dd1a1', '#4a69bd', '#ff6b6b', '#feca57', '#5f27cd'
                    ],
                    borderWidth: 4,
                    borderColor: '#ffffff', // Couleur du fond de la carte pour l'espacement
                    hoverOffset: 20
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            font: { size: 12, weight: '600' }
                        }
                    }
                }
            }
        });
    }

    // 2. Graphique de l'activité
    const jourCtx = document.getElementById('jourChart').getContext('2d');
    const gradient = jourCtx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, '#1a2a6c');
    gradient.addColorStop(1, 'rgba(197, 160, 89, 0.2)');

    new Chart(jourCtx, {
        type: 'bar',
        data: {
            labels: jourLabels,
            datasets: [{
                label: 'Consultations',
                data: jourValues,
                backgroundColor: gradient,
                borderRadius: 10,
                barThickness: 25
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.05)' }, ticks: { stepSize: 1 } },
                x: { grid: { display: false } }
            }
        }
    });

    // 3. Gestion de l'impression du rapport (Graphique en barres)
    const printBtn = document.getElementById('printReportBtn');
    if (printBtn) {
        printBtn.addEventListener('click', function() {
            const canvas = document.getElementById('jourChart');
            if (!canvas) return;
            
            const win = window.open('', 'Print', 'height=600,width=800');
            if (win) {
                win.document.write(`
                    <html>
                        <head>
                            <title>Rapport Hebdomadaire - SanteScolaire</title>
                            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
                            <style>
                                body { padding: 40px; font-family: 'Segoe UI', sans-serif; }
                                .header { text-align: center; margin-bottom: 40px; border-bottom: 2px solid #10ac84; padding-bottom: 20px; }
                                h2 { color: #2d3436; font-weight: bold; margin-top: 10px; }
                                .logo-container { display: flex; align-items: center; justify-content: center; margin-bottom: 15px; }
                                .brand-logo {
                                    width: 50px; height: 50px;
                                    background: linear-gradient(135deg, #10ac84 0%, #1dd1a1 100%);
                                    color: white; border-radius: 12px;
                                    display: flex; align-items: center; justify-content: center;
                                    font-size: 1.5rem; margin-right: 15px;
                                }
                            </style>
                        </head>
                        <body>
                            <div class="header">
                                <div class="logo-container">
                                    <div class="brand-logo"><i class="fas fa-heartbeat"></i></div>
                                    <h1 class="text-primary fw-bold m-0">SanteScolaire</h1>
                                </div>
                                <h2>Rapport d'Activité Hebdomadaire</h2>
                                <p class="text-muted">Généré le ${new Date().toLocaleDateString()} à ${new Date().toLocaleTimeString()}</p>
                            </div>
                            <div class="text-center">
                                <img src="${canvas.toDataURL()}" style="max-width: 100%; max-height: 500px;">
                            </div>
                            <script>
                                window.onload = function() { window.print(); }
                            </script>
                        </body>
                    </html>
                `);
                win.document.close();
            }
        });
    }
});