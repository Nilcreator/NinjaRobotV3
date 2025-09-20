
document.addEventListener('DOMContentLoaded', () => {
    // --- Element Selectors ---
    const movementsSelect = document.getElementById('movements-select');
    const expressionsSelect = document.getElementById('expressions-select');
    const emotionsSelect = document.getElementById('emotions-select');
    const distanceDisplay = document.getElementById('distance-display');
    const executeMovementBtn = document.getElementById('execute-movement-btn');
    const showExpressionBtn = document.getElementById('show-expression-btn');
    const playEmotionBtn = document.getElementById('play-emotion-btn');
    const setApiKeyBtn = document.getElementById('set-api-key-btn');
    const chatContainer = document.getElementById('chat-container');
    const logControls = document.getElementById('log-controls');
    const chatHistory = document.getElementById('chat-history');
    const chatInput = document.getElementById('chat-input');
    const chatSendBtn = document.getElementById('chat-send-btn');
    const micBtn = document.getElementById('mic-btn');
    const systemLog = document.getElementById('system-log');

    // --- State Variables ---
    let mediaRecorder;
    let voiceSocket;
    let isListening = false;

    // --- Generic API Call Functions ---
    async function fetchApi(endpoint, options = {}) {
        try {
            const response = await fetch(endpoint, options);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `API call failed`);
            }
            return await response.json();
        } catch (error) {
            console.error(`API Error for ${endpoint}:`, error);
            appendMessage('system-error', `Error: ${error.message}`);
            throw error;
        }
    }

    // --- UI & Data Loading ---
    async function populateSelect(select, endpoint, key) {
        try {
            const data = await fetchApi(`/api/${endpoint}`);
            select.innerHTML = '';
            data[key].forEach(item => {
                const option = document.createElement('option');
                option.value = item;
                option.textContent = item.charAt(0).toUpperCase() + item.slice(1);
                select.appendChild(option);
            });
        } catch (e) { console.error(`Failed to load ${key}.`); }
    }

    function appendMessage(sender, text) {
        const el = document.createElement('div');
        el.classList.add('chat-message', `chat-message-${sender}`);
        el.textContent = text;
        chatHistory.appendChild(el);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    function appendLog(text) {
        systemLog.textContent += `[${new Date().toLocaleTimeString()}] ${text}\n`;
        systemLog.scrollTop = systemLog.scrollHeight;
    }

    function showChatInterface(show) {
        if (show) {
            setApiKeyBtn.style.display = 'none';
            chatContainer.style.display = 'block';
            logControls.style.display = 'block';
            connectVoiceSocket();
        } else {
            setApiKeyBtn.style.display = 'block';
            chatContainer.style.display = 'none';
            logControls.style.display = 'none';
        }
    }

    // --- Voice Streaming Logic ---
    function connectVoiceSocket() {
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        voiceSocket = new WebSocket(`${wsProtocol}//${window.location.host}/ws/voice`);

        voiceSocket.onmessage = (event) => {
            const message = JSON.parse(event.data);
            switch (message.type) {
                case 'interim_transcript':
                case 'final_transcript':
                    chatInput.value = message.data;
                    break;
                case 'action':
                case 'response':
                    appendMessage('agent', message.data.response);
                    break;
                case 'log':
                    appendLog(message.data);
                    break;
                case 'error':
                    appendMessage('system-error', message.data);
                    break;
            }
        };

        voiceSocket.onerror = (err) => console.error('Voice WebSocket Error:', err);
        voiceSocket.onclose = () => console.log('Voice WebSocket closed.');
    }

    async function startListening() {
        if (isListening) return;
        if (window.location.protocol !== 'https:' && window.location.hostname !== 'localhost') {
            alert('Microphone access requires a secure (HTTPS) connection. This feature is disabled on HTTP.');
            return;
        }
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0 && voiceSocket && voiceSocket.readyState === WebSocket.OPEN) {
                    voiceSocket.send(event.data);
                }
            };
            mediaRecorder.onstart = () => {
                isListening = true;
                micBtn.classList.add('listening');
                chatInput.placeholder = 'Listening... Press mic again to stop.';
            };
            mediaRecorder.onstop = () => {
                isListening = false;
                micBtn.classList.remove('listening');
                chatInput.placeholder = 'Ask the robot to do something...';
                stream.getTracks().forEach(track => track.stop());
            };
            mediaRecorder.start(250);
        } catch (err) {
            console.error("Error accessing microphone:", err);
            appendMessage('system-error', `Could not access microphone: ${err.name}. Ensure you have granted permission and are on a secure (HTTPS) connection.`);
        }
    }

    function stopListening() {
        if (mediaRecorder && isListening) {
            mediaRecorder.stop();
        }
    }

    // --- Event Listeners ---
    executeMovementBtn.addEventListener('click', () => fetchApi(`/api/servos/movements/${movementsSelect.value}/execute`, { method: 'POST' }));
    showExpressionBtn.addEventListener('click', () => fetchApi(`/api/display/expressions/${expressionsSelect.value}`, { method: 'POST' }));
    playEmotionBtn.addEventListener('click', () => fetchApi(`/api/sound/emotions/${emotionsSelect.value}`, { method: 'POST' }));

    setApiKeyBtn.addEventListener('click', async () => {
        const apiKey = prompt('Please enter your Gemini API key:');
        if (apiKey && apiKey.trim()) {
            try {
                await fetchApi('/api/agent/set_api_key', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ api_key: apiKey })
                });
                showChatInterface(true);
                appendMessage('system-info', 'Ninja AI activated.');
            } catch (e) { /* Error handled in fetchApi */ }
        }
    });

    async function handleChatSend() {
        const message = chatInput.value.trim();
        if (!message) return;

        appendMessage('user', message);
        chatInput.value = '';

        try {
            const result = await fetchApi('/api/agent/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message })
            });
            if (result) {
                if (result.response) appendMessage('agent', result.response);
                if (result.log) appendLog(result.log);
            }
        } catch (error) {
            // Error is already logged by fetchApi and displayed in chat
        }
    }

    chatSendBtn.addEventListener('click', handleChatSend);
    chatInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') handleChatSend(); });

    micBtn.addEventListener('click', () => {
        if (isListening) {
            stopListening();
        } else {
            startListening();
        }
    });

    // --- Initialization ---
    async function init() {
        populateSelect(movementsSelect, 'servos/movements', 'movements');
        populateSelect(expressionsSelect, 'display/expressions', 'expressions');
        populateSelect(emotionsSelect, 'sound/emotions', 'emotions');
        
        try {
            const status = await fetchApi('/api/agent/status');
            showChatInterface(status.active);
        } catch (e) {
            showChatInterface(false);
        }

        // Distance sensor WebSocket
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const distanceSocket = new WebSocket(`${wsProtocol}//${window.location.host}/ws/distance`);
        distanceSocket.onmessage = (event) => {
            distanceDisplay.textContent = `${JSON.parse(event.data).distance_mm} mm`;
        };
        distanceSocket.onerror = () => distanceDisplay.textContent = 'Error';
        distanceSocket.onclose = () => distanceDisplay.textContent = 'Disconnected';
    }

    init();
});
