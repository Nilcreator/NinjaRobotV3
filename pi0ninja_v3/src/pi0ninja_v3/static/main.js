document.addEventListener('DOMContentLoaded', () => {
    const movementsSelect = document.getElementById('movements-select');
    const expressionsSelect = document.getElementById('expressions-select');
    const emotionsSelect = document.getElementById('emotions-select');
    const distanceDisplay = document.getElementById('distance-display');

    const executeMovementBtn = document.getElementById('execute-movement-btn');
    const showExpressionBtn = document.getElementById('show-expression-btn');
    const playEmotionBtn = document.getElementById('play-emotion-btn');

    // --- Data Loading Functions ---
    async function populateSelect(selectElement, endpoint, dataKey) {
        try {
            const response = await fetch(`/api/${endpoint}`);
            const data = await response.json();
            selectElement.innerHTML = ''; // Clear existing options
            data[dataKey].forEach(item => {
                const option = document.createElement('option');
                option.value = item;
                option.textContent = item.charAt(0).toUpperCase() + item.slice(1);
                selectElement.appendChild(option);
            });
        } catch (error) {
            console.error(`Failed to load ${dataKey}:`, error);
        }
    }

    // --- API Call Functions ---
    async function postCommand(endpoint) {
        try {
            const response = await fetch(`/api/${endpoint}`, { method: 'POST' });
            if (!response.ok) {
                throw new Error(`API call failed with status ${response.status}`);
            }
            const result = await response.json();
            console.log(result);
        } catch (error) {
            console.error(`Failed to execute command for ${endpoint}:`, error);
        }
    }

    // --- Event Listeners ---
    executeMovementBtn.addEventListener('click', () => {
        const selectedMovement = movementsSelect.value;
        if (selectedMovement) {
            postCommand(`servos/movements/${selectedMovement}/execute`);
        }
    });

    showExpressionBtn.addEventListener('click', () => {
        const selectedExpression = expressionsSelect.value;
        if (selectedExpression) {
            postCommand(`display/expressions/${selectedExpression}`);
        }
    });

    playEmotionBtn.addEventListener('click', () => {
        const selectedEmotion = emotionsSelect.value;
        if (selectedEmotion) {
            postCommand(`sound/emotions/${selectedEmotion}`);
        }
    });

    // --- WebSocket for Distance Sensor ---
    function setupDistanceWebSocket() {
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const ws = new WebSocket(`${wsProtocol}//${window.location.host}/ws/distance`);

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            distanceDisplay.textContent = `${data.distance_mm} mm`;
        };

        ws.onerror = (error) => {
            console.error('WebSocket Error:', error);
            distanceDisplay.textContent = 'Error';
        };

        ws.onclose = () => {
            console.log('Distance WebSocket closed. Attempting to reconnect in 3 seconds...');
            distanceDisplay.textContent = 'Disconnected';
            setTimeout(setupDistanceWebSocket, 3000);
        };
    }

    // --- Initialization ---
    function init() {
        populateSelect(movementsSelect, 'servos/movements', 'movements');
        populateSelect(expressionsSelect, 'display/expressions', 'expressions');
        populateSelect(emotionsSelect, 'sound/emotions', 'emotions');
        
        setupDistanceWebSocket();
    }

    init();
});