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
                        '#10ac84', '#0984e3', '#6c5ce7', '#fdcb6e', '#e17055', '#00cec9'
                    ],
                    borderWidth: 3,
                    borderColor: '#ffffff',
                    hoverOffset: 12
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '68%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 14,
                            usePointStyle: true,
                            boxWidth: 8,
                            font: { size: 11, weight: '600' }
                        }
                    },
                    tooltip: {
                        backgroundColor: '#0f172a',
                        titleFont: { size: 12, weight: '700' },
                        padding: 10,
                        cornerRadius: 8
                    }
                }
            }
        });
    }

    // 2. Graphique de l'activité (7 jours réels)
    const jourCanvas = document.getElementById('jourChart');
    if (jourCanvas) {
        const jourCtx = jourCanvas.getContext('2d');
        const gradient = jourCtx.createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, 'rgba(16, 172, 132, 0.85)');
        gradient.addColorStop(1, 'rgba(16, 172, 132, 0.12)');

        new Chart(jourCtx, {
            type: 'bar',
            data: {
                labels: jourLabels,
                datasets: [{
                    label: 'Visites / Consultations',
                    data: jourValues,
                    backgroundColor: gradient,
                    borderColor: '#10ac84',
                    borderWidth: 1.5,
                    borderRadius: 8,
                    borderSkipped: false,
                    maxBarThickness: 38
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#0f172a',
                        titleFont: { size: 12, weight: '700' },
                        padding: 10,
                        cornerRadius: 8,
                        callbacks: {
                            label: function(context) {
                                const v = context.parsed.y;
                                return ` ${v} consultation${v > 1 ? 's' : ''}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(0, 0, 0, 0.04)', drawBorder: false },
                        ticks: { stepSize: 1, precision: 0, font: { weight: '600', size: 11 } }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { font: { weight: '600', size: 11 } }
                    }
                }
            }
        });
    }

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