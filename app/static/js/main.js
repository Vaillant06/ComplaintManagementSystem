setTimeout(() => {
    let alerts = document.querySelectorAll('.flash-messages');
    alerts.forEach(alert => {
        alert.remove();
    });
}, 3000);
