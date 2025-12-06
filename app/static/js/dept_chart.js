const el = document.getElementById("deptData");
if (el) {
    const labels = JSON.parse(el.dataset.labels);
    const counts = JSON.parse(el.dataset.counts);

    const ctx = document.getElementById("deptChart");

    new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Complaints per Department",
                data: counts,
                backgroundColor: [
                    '#6610F2', '#20C997', '#FFC107', '#DC3545'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: { y: { beginAtZero: true } }
        }
    });
}
