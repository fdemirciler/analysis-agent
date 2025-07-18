// WebSocket connection
let ws;
let sessionId = null;
let fileUploaded = false;
let currentProcessingMessageId = null; // Track current processing message

// --- DOM Element References ---
const fileUploadInput = document.getElementById('file-upload');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');
const chatMessages = document.getElementById('chat-messages');
const themeToggle = document.getElementById('theme-toggle');
const themeIconLight = document.getElementById('theme-icon-light');
const themeIconDark = document.getElementById('theme-icon-dark');

const allowedFileTypes = [
    'text/csv',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
];

// Initialize WebSocket connection
function initWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    
    ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
        // The initial welcome message is now handled by DOMContentLoaded
    };
    
    ws.onclose = () => {
        addBotMessage("Connection lost. Attempting to reconnect...", "error");
        setTimeout(initWebSocket, 2000); // Try to reconnect
    };
    
    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        addBotMessage("Connection error. Please refresh the page.", "error");
    };
    
    ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        handleBackendMessage(message);
    };
}

// Handle incoming messages from the backend
function handleBackendMessage(message) {
    switch(message.type) {
        case 'session_created':
            sessionId = message.session_id;
            break;
            
        case 'processing_status':
            // Show processing status as a bot message with typing indicator
            const processingMessage = message.status || 'Processing...';
            addProcessingMessage(processingMessage);
            break;
            
        case 'file_processed':
            // Remove any processing message first
            removeProcessingMessage();
            fileUploaded = true;
            userInput.disabled = false;
            sendButton.disabled = false;
            const summary = message.profile_summary;
            const successMessage = `Successfully uploaded and processed "${summary.file_name}". It has ${summary.rows} rows and ${summary.columns} columns. You can now ask questions about the data.`;
            addBotMessage(successMessage, 'success');
            userInput.focus();
            break;
            
        case 'query_response':
            // Remove any processing message first
            removeProcessingMessage();
            addBotMessage(message.response);
            break;
            
        case 'error':
            // Remove any processing message first
            removeProcessingMessage();
            addBotMessage(`Error: ${message.message}`, 'error');
            break;
            
        default:
            console.log('Unknown message type:', message);
    }
}

// --- Theme Management ---
const applyTheme = (theme) => {
    if (theme === 'dark') {
        document.documentElement.classList.add('dark');
        themeIconLight.classList.add('hidden');
        themeIconDark.classList.remove('hidden');
    } else {
        document.documentElement.classList.remove('dark');
        themeIconLight.classList.remove('hidden');
        themeIconDark.classList.add('hidden');
    }
};

themeToggle.addEventListener('click', () => {
    const isDark = document.documentElement.classList.toggle('dark');
    const newTheme = isDark ? 'dark' : 'light';
    localStorage.setItem('theme', newTheme);
    applyTheme(newTheme);
});

const savedTheme = localStorage.getItem('theme');
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
const initialTheme = savedTheme || (prefersDark ? 'dark' : 'light');
applyTheme(initialTheme);


// --- Event Listeners ---
fileUploadInput.addEventListener('change', () => {
    if (fileUploadInput.files.length > 0) {
        handleFileUpload(fileUploadInput.files[0]);
    }
});

sendButton.addEventListener('click', sendMessage);
userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        e.preventDefault(); // Prevent form submission
        sendMessage();
    }
});


// --- Core Functions ---
function handleFileUpload(file) {
    if (!file) return;

    if (!allowedFileTypes.some(type => file.type === type || file.name.endsWith('.csv') || file.name.endsWith('.xls') || file.name.endsWith('.xlsx'))) {
        addBotMessage('Error: Invalid file type. Please upload a CSV or Excel file.', 'error');
        return;
    }

    const reader = new FileReader();
    
    reader.onload = (e) => {
        if (!ws || ws.readyState !== WebSocket.OPEN) {
            addBotMessage('Cannot upload file. WebSocket is not connected.', 'error');
            return;
        }
        
        addBotMessage(`Uploading "${file.name}"...`);
        
        // Add processing message for file upload
        addProcessingMessage('Processing your file...');
        
        ws.send(JSON.stringify({
            type: 'file_upload',
            file_name: file.name,
            data: e.target.result
        }));
    };
    
    reader.readAsDataURL(file);
}

function sendMessage() {
    const messageText = userInput.value.trim();
    if (messageText === '') return;

    if (!fileUploaded) {
        addBotMessage('Please upload and process a file before asking questions.', 'error');
        return;
    }

    addUserMessage(messageText);
    userInput.value = '';
    
    // Add immediate processing message
    addProcessingMessage('Analyzing your question...');
    
    ws.send(JSON.stringify({
        type: 'query',
        query: messageText
    }));
}

// --- UI Helper Functions ---
function addProcessingMessage(text) {
    // Remove any existing processing message first
    removeProcessingMessage();
    
    const messageId = 'processing-message-' + Date.now();
    currentProcessingMessageId = messageId;
    
    const iconSvg = `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-blue-500 animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
    </svg>`;
    
    const messageHtml = `
        <div id="${messageId}" class="message-fade-in flex items-start gap-2 sm:gap-3 processing-message">
            <div class="bg-slate-200 dark:bg-slate-600 p-2 rounded-full">${iconSvg}</div>
            <div class="bg-slate-100 dark:bg-slate-700 p-3 sm:p-4 rounded-lg max-w-xs sm:max-w-md lg:max-w-xl xl:max-w-2xl w-full">
                <p class="text-sm sm:text-base text-slate-700 dark:text-slate-200 flex items-center gap-2">
                    ${text}
                    <span class="typing-dots">
                        <span class="dot animate-bounce delay-0">.</span>
                        <span class="dot animate-bounce delay-100">.</span>
                        <span class="dot animate-bounce delay-200">.</span>
                    </span>
                </p>
            </div>
        </div>
    `;
    chatMessages.innerHTML += messageHtml;
    scrollToBottom();
}

function removeProcessingMessage() {
    if (currentProcessingMessageId) {
        const processingElement = document.getElementById(currentProcessingMessageId);
        if (processingElement) {
            processingElement.remove();
        }
        currentProcessingMessageId = null;
    }
}

function addUserMessage(text) {
    const messageHtml = `
        <div class="message-fade-in flex items-start gap-2 sm:gap-3 justify-end">
            <div class="bg-blue-500 text-white p-3 sm:p-4 rounded-lg max-w-xs sm:max-w-md lg:max-w-xl xl:max-w-2xl">
                <p class="text-sm sm:text-base">${text}</p>
            </div>
        </div>
    `;
    chatMessages.innerHTML += messageHtml;
    scrollToBottom();
}

function addBotMessage(text, type = 'info') {
    let iconSvg;
    let bgColor;
    let iconContainerBgColor = 'bg-slate-200 dark:bg-slate-600';

    switch(type) {
        case 'success':
            iconSvg = `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-green-600 dark:text-green-400" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" /></svg>`;
            bgColor = 'bg-green-100 dark:bg-green-900/30';
            break;
        case 'error':
            iconSvg = `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-red-600 dark:text-red-400" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" /></svg>`;
            bgColor = 'bg-red-100 dark:bg-red-900/30';
            break;
        default:
            iconSvg = `<svg height="14" stroke-linejoin="round" viewBox="0 0 16 16" width="14" class="h-5 w-5 text-slate-600 dark:text-slate-300" fill="currentColor">
                        <path d="M2.5 0.5V0H3.5V0.5C3.5 1.60457 4.39543 2.5 5.5 2.5H6V3V3.5H5.5C4.39543 3.5 3.5 4.39543 3.5 5.5V6H3H2.5V5.5C2.5 4.39543 1.60457 3.5 0.5 3.5H0V3V2.5H0.5C1.60457 2.5 2.5 1.60457 2.5 0.5Z" fill="currentColor"></path>
                        <path d="M14.5 4.5V5H13.5V4.5C13.5 3.94772 13.0523 3.5 12.5 3.5H12V3V2.5H12.5C13.0523 2.5 13.5 2.05228 13.5 1.5V1H14H14.5V1.5C14.5 2.05228 14.9477 2.5 15.5 2.5H16V3V3.5H15.5C14.9477 3.5 14.5 3.94772 14.5 4.5Z" fill="currentColor"></path>
                        <path d="M8.40706 4.92939L8.5 4H9.5L9.59294 4.92939C9.82973 7.29734 11.7027 9.17027 14.0706 9.40706L15 9.5V10.5L14.0706 10.5929C11.7027 10.8297 9.82973 12.7027 9.59294 15.0706L9.5 16H8.5L8.40706 15.0706C8.17027 12.7027 6.29734 10.8297 3.92939 10.5929L3 10.5V9.5L3.92939 9.40706C6.29734 9.17027 8.17027 7.29734 8.40706 4.92939Z" fill="currentColor"></path>
                    </svg>`;
            bgColor = 'bg-slate-100 dark:bg-slate-700';
    }

    const messageHtml = `
        <div class="message-fade-in flex items-start gap-2 sm:gap-3">
            <div class="${iconContainerBgColor} p-2 rounded-full">${iconSvg}</div>
            <div class="${bgColor} p-3 sm:p-4 rounded-lg max-w-xs sm:max-w-md lg:max-w-xl xl:max-w-2xl w-full">
                <p class="text-sm sm:text-base text-slate-700 dark:text-slate-200">${text}</p>
            </div>
        </div>
    `;
    chatMessages.innerHTML += messageHtml;
    scrollToBottom();
}

function scrollToBottom() {
    requestAnimationFrame(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    addBotMessage("Welcome! I'm your AI financial analyst. Please upload your financial data in CSV or Excel format to get started.");
    initWebSocket();
});