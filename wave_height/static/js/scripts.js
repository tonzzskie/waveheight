// Toggle the sidebar visibility
function togglePanel() {
    const panel = document.getElementById("marineDataPanel");
    panel.style.right = (panel.style.right === "0px") ? "-400px" : "0px";
}

// Initialize the map
function initMap() {
    const map = L.map('leafletMap').setView([11.654916, 124.265899], 5);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap'
    }).addTo(map);

    // Handle map click event
    map.on('click', function(e) {
        const lat = e.latlng.lat.toFixed(6);
        const lng = e.latlng.lng.toFixed(6);

        // Fetch updated data based on clicked location
        fetch(`/fetch_data?latitude=${lat}&longitude=${lng}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error(data.error);
                } else {
                    updateSidebar(data); // Display new data in the sidebar
                    logInteraction(lat, lng, data); // Log the interaction
                }
            })
            .catch(error => console.error('Error fetching data:', error));
    });
}

// Update the sidebar with new data
function updateSidebar(data) {
    document.getElementById('latValue').textContent = data.info_data.latitude;
    document.getElementById('lonValue').textContent = data.info_data.longitude;
    document.getElementById('timezone').textContent = data.info_data.timezone;
    document.getElementById('elevation').textContent = `${data.info_data.elevation} meters`;

    // Update the charts
    updateCharts(data.hourly_data.hourly);
}

let waveHeightChart, waveDirectionChart, wavePeriodChart; // Store chart instances

// Initialize or update charts with new data
function updateCharts(hourlyData) {
    const labels = hourlyData.time.map(time => new Date(time).toLocaleString());
    const waveHeightData = hourlyData.wave_height;
    const waveDirectionData = hourlyData.wave_direction;
    const wavePeriodData = hourlyData.wave_period;

    // Destroy existing charts if they exist to prevent overlaying
    if (waveHeightChart) waveHeightChart.destroy();
    if (waveDirectionChart) waveDirectionChart.destroy();
    if (wavePeriodChart) wavePeriodChart.destroy();

    // Wave Height Chart
    waveHeightChart = new Chart(document.getElementById('waveHeightChart').getContext('2d'), {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Wave Height (m)',
                data: waveHeightData,
                borderColor: 'blue',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            scales: {
                x: { display: false },  // Hide x-axis labels
                y: { title: { display: true, text: 'Height (m)' }}
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        title: function(tooltipItems) {
                            return tooltipItems[0].label;
                        }
                    }
                }
            }
        }
    });

    // Wave Direction Chart
    waveDirectionChart = new Chart(document.getElementById('waveDirectionChart').getContext('2d'), {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Wave Direction (°)',
                data: waveDirectionData,
                borderColor: 'green',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            scales: {
                x: { display: false },  // Hide x-axis labels
                y: { title: { display: true, text: 'Direction (°)' }}
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        title: function(tooltipItems) {
                            return tooltipItems[0].label;
                        }
                    }
                }
            }
        }
    });

    // Wave Period Chart
    wavePeriodChart = new Chart(document.getElementById('wavePeriodChart').getContext('2d'), {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Wave Period (s)',
                data: wavePeriodData,
                borderColor: 'red',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            scales: {
                x: { display: false },  // Hide x-axis labels
                y: { title: { display: true, text: 'Period (s)' }}
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        title: function(tooltipItems) {
                            return tooltipItems[0].label;
                        }
                    }
                }
            }
        }
    });

}

function logInteraction(latitude, longitude, data) {
    // Check if user is logged in by examining the session
    // if (!document.body.classList.contains("logged-in")) {
    //     alert("Please log in to save interactions.");
    //     return;
    // }

    fetch('/log_interaction', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ latitude: latitude, longitude: longitude, data: data })
    })
    .then(response => response.json())
    .then(responseData => {
        if (responseData.status === "success") {
            console.log("Interaction logged successfully.");
        } else if (responseData.error) {
            alert(responseData.error);
        }
    })
    .catch(error => console.error('Error logging interaction:', error));
}

// Call initMap() after the page loads
window.onload = initMap;
