const statusEl = document.getElementById("statusData");
if (statusEl) {
    const labels = JSON.parse(statusEl.dataset.labels);
    const counts = JSON.parse(statusEl.dataset.counts);

    const ctx = document.getElementById("statusChart");

    new Chart(ctx, {
        type: "pie",
        data: {
            labels: labels,
            datasets: [{
                data: counts,
                backgroundColor: [
                    "#0d6efd",
                    "#ffc107",
                    "#198754",
                    "#dc3545"
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}
