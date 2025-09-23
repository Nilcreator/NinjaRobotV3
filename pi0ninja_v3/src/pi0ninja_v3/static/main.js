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
    const systemLog = document.getElementById('system-log');
    const micButton = document.getElementById('micButton');

    // --- Voice Recording Variables ---
    let isRecording = false;
    let mediaRecorder;
    let audioChunks = [];
    let silenceTimer;
    let maxRecordingTimer;
    let audioContext;
    let analyser;
    let dataArray;
    let source;

    // --- Generic API Call Functions ---
    async function fetchApi(endpoint, options = {}) {
        try {
            const response = await fetch(endpoint, options);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `API call failed`);
            }
            // For file uploads, the response might not be JSON
            if (options.body instanceof FormData) {
                return response.json(); 
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
        } else {
            setApiKeyBtn.style.display = 'block';
            chatContainer.style.display = 'none';
            logControls.style.display = 'none';
        }
    }

    // --- Voice Recording Functions ---
    async function sendAudioToServer(audioBlob) {
        const formData = new FormData();
        formData.append('audio_file', audioBlob, 'voice_command.webm');

        appendMessage('user', '[Sending voice command...]');

        try {
            const result = await fetchApi('/api/agent/chat_voice', {
                method: 'POST',
                body: formData
            });
            if (result) {
                const userMessages = chatHistory.getElementsByClassName('chat-message-user');
                const lastUserMessage = userMessages[userMessages.length - 1];
                if (lastUserMessage && lastUserMessage.textContent === '[Sending voice command...]') {
                    // The backend doesn't have the transcription, so we remove the placeholder
                    lastUserMessage.remove();
                }
                if (result.response) appendMessage('agent', result.response);
                if (result.log) appendLog(result.log);
            }
        } catch (error) {
            const userMessages = chatHistory.getElementsByClassName('chat-message-user');
            const lastUserMessage = userMessages[userMessages.length - 1];
            if (lastUserMessage && lastUserMessage.textContent === '[Sending voice command...]') {
                lastUserMessage.textContent = '[Error sending voice command]';
            }
        }
    }

    function stopRecording() {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
            mediaRecorder.stop();
        }
        clearTimeout(silenceTimer);
        clearTimeout(maxRecordingTimer);
        micButton.classList.remove('recording');
        isRecording = false;
        if (audioContext && audioContext.state !== 'closed') {
            audioContext.close();
        }
    }

    function detectSilence() {
        if (!isRecording || !analyser) return;

        analyser.getByteTimeDomainData(dataArray);
        const slice = dataArray.slice(0, analyser.frequencyBinCount);
        const sum = slice.reduce((acc, val) => acc + Math.abs(val - 128), 0);
        const avg = sum / slice.length;

        if (avg < 2.5) { // Silence threshold - may need tuning
            if (!silenceTimer) {
                silenceTimer = setTimeout(stopRecording, 3000); // 3 seconds of silence
            }
        } else {
            clearTimeout(silenceTimer);
            silenceTimer = null;
        }
        requestAnimationFrame(detectSilence);
    }

    async function startRecording() {
        if (isRecording) return;

        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            isRecording = true;
            micButton.classList.add('recording');
            audioChunks = [];

            mediaRecorder = new MediaRecorder(stream);

            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                if (audioBlob.size > 0) {
                    sendAudioToServer(audioBlob);
                }
                stream.getTracks().forEach(track => track.stop());
            };

            audioContext = new AudioContext();
            source = audioContext.createMediaStreamSource(stream);
            analyser = audioContext.createAnalyser();
            analyser.fftSize = 2048;
            const bufferLength = analyser.frequencyBinCount;
            dataArray = new Uint8Array(bufferLength);
            source.connect(analyser);
            detectSilence();

            mediaRecorder.start();

            maxRecordingTimer = setTimeout(stopRecording, 30000); // 30 seconds max

        } catch (err) {
            console.error('Error accessing microphone:', err);
            appendMessage('system-error', `Microphone access denied: ${err.message}`);
            isRecording = false;
            micButton.classList.remove('recording');
        }
    }

    function handleMicClick() {
        if (isRecording) {
            stopRecording();
        } else {
            startRecording();
        }
    }

    // --- Event Listeners ---
    executeMovementBtn.addEventListener('click', () => fetchApi(`/api/servos/movements/${movementsSelect.value}/execute`, { method: 'POST' }));
    showExpressionBtn.addEventListener('click', () => fetchApi(`/api/display/expressions/${expressionsSelect.value}`, { method: 'POST' }));
    playEmotionBtn.addEventListener('click', () => fetchApi(`/api/sound/emotions/${emotionsSelect.value}`, { method: 'POST' }));
    micButton.addEventListener('click', handleMicClick);

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
