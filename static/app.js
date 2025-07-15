// WebSocket connection
let ws;
let sessionId = null;
let fileUploaded = false;

// DOM elements
const fileInput = document.getElementById('fileInput');
const uploadButton = document.getElementById('uploadButton');
const fileInfo = document.getElementById('fileInfo');
const chatMessages = document.getElementById('chatMessages');
const queryInput = document.getElementById('queryInput');
const sendButton = document.getElementById('sendButton');
const statusBar = document.getElementById('statusBar');

// Initialize WebSocket connection
function initWebSocket() {
    // Use window location to build WebSocket URL
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    
    ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
        updateStatus('Connected');
    };
    
    ws.onclose = () => {
        updateStatus('Disconnected');
        setTimeout(initWebSocket, 2000); // Try to reconnect
    };
    
    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        updateStatus('Connection error');
    };
    
    ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        handleMessage(message);
    };
}

// Handle incoming messages
function handleMessage(message) {
    switch(message.type) {
        case 'session_created':
            sessionId = message.session_id;
            updateStatus('Session established');
            break;
            
        case 'processing_status':
            updateStatus(message.status);
            break;
            
        case 'file_processed':
            fileUploaded = true;
            displayFileInfo(message.profile_summary);
            addSystemMessage('File processed successfully. You can now ask questions about your data.');
            break;
            
        case 'query_response':
            addAssistantMessage(message.response);
            break;
            
        case 'error':
            updateStatus('Error');
            addSystemMessage(`Error: ${message.message}`, true);
            break;
            
        default:
            console.log('Unknown message type:', message);
    }
}

// Update status bar
function updateStatus(status) {
    statusBar.textContent = status;
}

// Display file information
function displayFileInfo(profileSummary) {
    fileInfo.innerHTML = `
        <strong>File:</strong> ${profileSummary.file_name}<br>
        <strong>Rows:</strong> ${profileSummary.rows}<br>
        <strong>Columns:</strong> ${profileSummary.columns}<br>
        <strong>Time periods:</strong> ${profileSummary.periods.join(', ')}
    `;
}

// Add message to chat
function addUserMessage(text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user-message';
    messageDiv.textContent = text;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addAssistantMessage(text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant-message';
    messageDiv.innerHTML = formatMessage(text);
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addSystemMessage(text, isError = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = isError ? 'message system-message error' : 'message system-message';
    messageDiv.textContent = text;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Format message with Markdown-like syntax
function formatMessage(text) {
    // Convert line breaks
    text = text.replace(/\n/g, '<br>');
    
    // Bold text
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Italic text
    text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // Convert bullet points
    text = text.replace(/- (.*?)(?=<br>|$)/g, '• $1');
    
    return text;
}

// Upload file
uploadButton.addEventListener('click', () => {
    if (!fileInput.files[0]) {
        addSystemMessage('Please select a file first', true);
        return;
    }
    
    const file = fileInput.files[0];
    const reader = new FileReader();
    
    reader.onload = (e) => {
        if (!sessionId) {
            addSystemMessage('Waiting for session to be established...', true);
            return;
        }
        
        addSystemMessage(`Uploading file: ${file.name}`);
        
        ws.send(JSON.stringify({
            type: 'file_upload',
            file_name: file.name,
            data: e.target.result
        }));
    };
    
    reader.readAsDataURL(file); // Use base64 encoding for file data
});

// Send query
sendButton.addEventListener('click', sendQuery);
queryInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendQuery();
    }
});

function sendQuery() {
    const query = queryInput.value.trim();
    if (!query) return;
    
    if (!fileUploaded) {
        addSystemMessage('Please upload a file first', true);
        return;
    }
    
    addUserMessage(query);
    
    ws.send(JSON.stringify({
        type: 'query',
        query: query
    }));
    
    queryInput.value = '';
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    addSystemMessage('Welcome to the Financial Data Analyst. Please upload a financial dataset to begin.');
    initWebSocket();
});