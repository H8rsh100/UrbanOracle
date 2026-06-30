document.addEventListener('DOMContentLoaded', () => {
    
    // 1. Prediction Form Handler and Tabs
    const predictForm = document.getElementById('predictForm');
    const resultsGrid = document.getElementById('resultsGrid');
    const explainTabBtn = document.getElementById('explainTabBtn');
    const attributionList = document.getElementById('attributionList');

    const tabBtns = document.querySelectorAll('.tab-btn');
    
    function switchTab(tabId) {
        tabBtns.forEach(btn => {
            if (btn.getAttribute('data-tab') === tabId) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
        
        if (tabId === 'predictions') {
            document.getElementById('predictionsTab').style.display = 'block';
            document.getElementById('explainabilityTab').style.display = 'none';
        } else {
            document.getElementById('predictionsTab').style.display = 'none';
            document.getElementById('explainabilityTab').style.display = 'block';
        }
    }

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            switchTab(btn.getAttribute('data-tab'));
        });
    });

    predictForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(predictForm);
        const submitBtn = predictForm.querySelector('button');
        submitBtn.innerHTML = '<div class="spinner"></div> Predicting...';
        submitBtn.disabled = true;
        
        // Reset tabs state on new prediction
        explainTabBtn.style.display = 'none';
        switchTab('predictions');

        try {
            // Show Lottie animation while predicting
            resultsGrid.innerHTML = `
                <div style="display: flex; justify-content: center; align-items: center; height: 100%; min-height: 250px;">
                    <dotlottie-player src="/static/img/loading.lottie" background="transparent" speed="1" style="width: 200px; height: 200px;" loop autoplay></dotlottie-player>
                </div>
            `;
            
            // Enforce a minimum 3-second display of the Lottie animation
            const [response] = await Promise.all([
                fetch('/predict', { method: 'POST', body: formData }),
                new Promise(resolve => setTimeout(resolve, 3000))
            ]);
            
            const data = await response.json();
            resultsGrid.innerHTML = '';
            
            if (data.status === 'success') {
                for (const [modelName, score] of Object.entries(data.predictions)) {
                    let isRisk = modelName === 'Risk Score';
                    let formattedScore = isRisk ? score.toFixed(2) : (score * 100).toFixed(2) + '%';
                    
                    let valueClass = '';
                    if (!isRisk) {
                        valueClass = score > 0.5 ? 'value-high' : 'value-low';
                    }

                    const item = document.createElement('div');
                    item.className = 'result-item';
                    item.innerHTML = `
                        <span class="result-name">${modelName}</span>
                        <span class="result-value ${valueClass}">${formattedScore}</span>
                    `;
                    resultsGrid.appendChild(item);
                }

                // Render explainability
                attributionList.innerHTML = '';
                if (data.attributions && Object.keys(data.attributions).length > 0) {
                    explainTabBtn.style.display = 'inline-block';
                    for (const [feat, val] of Object.entries(data.attributions)) {
                        const row = document.createElement('div');
                        row.className = 'attribution-row';
                        
                        const percentage = Math.min(Math.abs(val) * 250, 100); // Scale up for visual representation
                        const colorClass = val >= 0 ? 'bar-high' : 'bar-low';
                        const sign = val >= 0 ? '+' : '-';
                        const valText = `${sign}${(Math.abs(val) * 100).toFixed(1)}%`;
                        
                        row.innerHTML = `
                            <div class="attribution-header">
                                <span class="attribution-name">${feat}</span>
                                <span class="attribution-val ${val >= 0 ? 'value-high' : 'value-low'}">${valText}</span>
                            </div>
                            <div class="attribution-bar-bg">
                                <div class="attribution-bar ${colorClass}" style="width: ${percentage}%"></div>
                            </div>
                        `;
                        attributionList.appendChild(row);
                    }
                }
            } else {
                resultsGrid.innerHTML = `<p class="placeholder-text value-high">Error: ${data.message}</p>`;
            }
        } catch (error) {
            resultsGrid.innerHTML = `<p class="placeholder-text value-high">Network error occurred.</p>`;
        } finally {
            submitBtn.textContent = 'Run Prediction';
            submitBtn.disabled = false;
        }
    });

    // 2. Load Analytics Chart
    fetch('/analytics')
        .then(res => res.json())
        .then(data => {
            if (data.error) return;
            
            const labels = [];
            const accuracies = [];
            const f1s = [];

            for (const [model, metrics] of Object.entries(data)) {
                if (metrics.Accuracy !== undefined) {
                    labels.push(model);
                    accuracies.push(metrics.Accuracy);
                    f1s.push(metrics['F1-Score']);
                }
            }

            const ctx = document.getElementById('comparisonChart').getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Accuracy',
                            data: accuracies,
                            backgroundColor: 'rgba(0, 229, 255, 0.7)',
                            borderColor: '#00e5ff',
                            borderWidth: 1
                        },
                        {
                            label: 'F1 Score',
                            data: f1s,
                            backgroundColor: 'rgba(0, 230, 118, 0.7)',
                            borderColor: '#00e676',
                            borderWidth: 1
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { labels: { color: '#f0f2f5' } }
                    },
                    scales: {
                        y: { 
                            beginAtZero: true, 
                            max: 1,
                            ticks: { color: '#a0aab2' },
                            grid: { color: 'rgba(255,255,255,0.1)' }
                        },
                        x: {
                            ticks: { color: '#a0aab2' },
                            grid: { display: false }
                        }
                    }
                }
            });
        });

    // 3. Load MLP History Curves
    fetch('/history')
        .then(res => res.json())
        .then(data => {
            if (data.error) return;
            
            const epochs = Array.from({length: data.loss.length}, (_, i) => i + 1);

            // Loss Chart
            const lossCtx = document.getElementById('lossChart').getContext('2d');
            new Chart(lossCtx, {
                type: 'line',
                data: {
                    labels: epochs,
                    datasets: [
                        {
                            label: 'Train Loss',
                            data: data.loss,
                            borderColor: '#ff1744',
                            tension: 0.4
                        },
                        {
                            label: 'Val Loss',
                            data: data.val_loss,
                            borderColor: '#ff5252',
                            borderDash: [5, 5],
                            tension: 0.4
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { labels: { color: '#f0f2f5' } } },
                    scales: {
                        y: { ticks: { color: '#a0aab2' }, grid: { color: 'rgba(255,255,255,0.1)' } },
                        x: { ticks: { color: '#a0aab2' }, grid: { display: false }, title: {display: true, text: 'Epoch', color: '#a0aab2'} }
                    }
                }
            });

            // Accuracy Chart
            const accCtx = document.getElementById('accuracyChart').getContext('2d');
            new Chart(accCtx, {
                type: 'line',
                data: {
                    labels: epochs,
                    datasets: [
                        {
                            label: 'Train Accuracy',
                            data: data.accuracy,
                            borderColor: '#00e676',
                            tension: 0.4
                        },
                        {
                            label: 'Val Accuracy',
                            data: data.val_accuracy,
                            borderColor: '#69f0ae',
                            borderDash: [5, 5],
                            tension: 0.4
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { labels: { color: '#f0f2f5' } } },
                    scales: {
                        y: { ticks: { color: '#a0aab2' }, grid: { color: 'rgba(255,255,255,0.1)' } },
                        x: { ticks: { color: '#a0aab2' }, grid: { display: false }, title: {display: true, text: 'Epoch', color: '#a0aab2'} }
                    }
                }
            });
        });

    // 4. Initialize Hotspot Map
    // Center of Chicago
    const map = L.map('map').setView([41.8781, -87.6298], 11);
    
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 20
    }).addTo(map);

    fetch('/hotspot')
        .then(res => res.json())
        .then(data => {
            if (!data.length) return;
            
            // Find max size to scale circles
            const maxSize = Math.max(...data.map(d => d.size));

            data.forEach(spot => {
                // Calculate radius based on size relative to max
                const radius = (spot.size / maxSize) * 2000 + 500;
                
                L.circle([spot.lat, spot.lng], {
                    color: '#ff1744',
                    fillColor: '#ff1744',
                    fillOpacity: 0.5,
                    radius: radius
                }).addTo(map)
                .bindPopup(`<b>Hotspot ID: ${spot.id}</b><br>Incidents Clustered: ${spot.size}`);
            });
        });
});
