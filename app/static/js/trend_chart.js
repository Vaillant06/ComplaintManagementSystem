const trendEl = document.getElementById("trendData");
if (trendEl) {
    const labels = JSON.parse(trendEl.dataset.labels);
    const counts = JSON.parse(trendEl.dataset.counts);

    const ctx = document.getElementById("trendChart");

    new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [{
                label: "Complaints per Day",
                data: counts,
                borderColor: "#0d6efd",
                backgroundColor: "rgba(13,110,253,0.3)",
                tension: 0.25,
                fill: true
            }]
        },
        options: {
            responsive: true,
            scales: { y: { beginAtZero: true} }
        }
    });
}
