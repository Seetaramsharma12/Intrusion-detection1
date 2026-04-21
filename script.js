const API_URL = 'http://localhost:5000';

// Initialize Chart
const ctx = document.getElementById('trafficChart').getContext('2d');
const trafficChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Requests/sec',
            data: [],
            borderColor: '#58a6ff',
            backgroundColor: 'rgba(88, 166, 255, 0.1)',
            tension: 0.4,
            fill: true
        }]
    },
    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true,
                grid: { color: '#30363d' },
                ticks: { color: '#8b949e' }
            },
            x: {
                grid: { display: false },
                ticks: { color: '#8b949e' }
            }
        },
        plugins: {
            legend: { labels: { color: '#c9d1d9' } }
        }
    }
});

function updateStats() {
    fetch(`${API_URL}/stats`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('total-requests').textContent = data.total_requests;
            document.getElementById('threats-blocked').textContent = data.threats_blocked;
            document.getElementById('active-threats').textContent = data.active_threats;

            updateLogTable(data.history);
        })
        .catch(err => console.error("Error fetching stats:", err));
}

function updateLogTable(history) {
    const tbody = document.querySelector('#log-table tbody');
    tbody.innerHTML = ''; // Clear current

    history.forEach(log => {
        const row = document.createElement('tr');
        row.className = log.action === 'Blocked' ? 'log-row-blocked' : 'log-row-allowed';

        row.innerHTML = `
            <td>${log.timestamp}</td>
            <td>${log.ip}</td>
            <td>${log.type}</td>
            <td><strong>${log.action}</strong></td>
            <td>${log.details}</td>
        `;
        tbody.appendChild(row);
    });
}

function simulateTraffic(type) {
    // Generate random payload based on type
    let payload = {};
    if (type === 'normal') {
        payload = {
            packet_size: Math.random() * 200 + 400, // 400-600
            duration: Math.random() * 2,
            request_rate: Math.floor(Math.random() * 20),
            protocol_type: Math.random() > 0.8 ? 1 : 0 // Mostly TCP
        };
    } else {
        // DDoS / Attack profile
        payload = {
            packet_size: Math.random() * 1000 + 1500, // Large packets
            duration: Math.random() * 10 + 5,
            request_rate: Math.floor(Math.random() * 200 + 100), // High rate
            protocol_type: 2 // ICMP/Other
        };
    }

    fetch(`${API_URL}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
        .then(res => res.json())
        .then(data => {
            console.log("Simulation result:", data);
            // Chart update logic (mocking real-time feed for the specific request)
            addToChart(payload.request_rate);
            updateStats();
        })
        .catch(err => console.error("Error simulating traffic:", err));
}

function addToChart(rate) {
    const now = new Date().toLocaleTimeString();
    trafficChart.data.labels.push(now);
    trafficChart.data.datasets[0].data.push(rate);

    if (trafficChart.data.labels.length > 20) {
        trafficChart.data.labels.shift();
        trafficChart.data.datasets[0].data.shift();
    }
    trafficChart.update();
}

// Event Listeners
document.getElementById('btn-simulate-normal').addEventListener('click', () => {
    // Simulate a burst of 5 normal requests
    for (let i = 0; i < 5; i++) {
        setTimeout(() => simulateTraffic('normal'), i * 200);
    }
});

document.getElementById('btn-simulate-ddos').addEventListener('click', () => {
    // Simulate a burst of attacks
    for (let i = 0; i < 10; i++) {
        setTimeout(() => simulateTraffic('ddos'), i * 100);
    }
});

// Poll stats every 2 seconds
setInterval(updateStats, 2000);
