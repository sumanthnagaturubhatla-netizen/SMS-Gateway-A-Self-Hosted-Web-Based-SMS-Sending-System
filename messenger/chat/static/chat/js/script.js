// ============================================
// SMS Gateway — JavaScript Controller
// ============================================

// === CSRF Token Helper ===
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// === Toast Notification System ===
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    const icons = {
        success: '✅',
        error: '❌',
        info: 'ℹ️'
    };

    toast.innerHTML = `
        <span class="toast-icon">${icons[type] || icons.info}</span>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    // Auto dismiss after 4 seconds
    setTimeout(() => {
        toast.classList.add('toast-out');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// === Relative Time Formatting ===
function timeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);

    if (seconds < 10) return 'just now';
    if (seconds < 60) return `${seconds}s ago`;

    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;

    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;

    const days = Math.floor(hours / 24);
    if (days < 7) return `${days}d ago`;

    return date.toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'short',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// === Status Badge Renderer ===
function renderStatusBadge(status) {
    const statusLower = (status || 'pending').toLowerCase();
    return `<span class="status-badge status-${statusLower}">${status}</span>`;
}

// === Truncate Message ===
function truncateMessage(msg, maxLen = 50) {
    if (!msg) return '';
    return msg.length > maxLen ? msg.substring(0, maxLen) + '...' : msg;
}

// === Character Count ===
const messageInput = document.getElementById('message');
const charCountEl = document.getElementById('charCount');
const smsCountEl = document.getElementById('smsCount');

if (messageInput) {
    messageInput.addEventListener('input', () => {
        const len = messageInput.value.length;
        charCountEl.textContent = len;

        // Calculate SMS parts (160 chars per SMS, 153 for multi-part)
        let parts = 1;
        if (len > 160) {
            parts = Math.ceil(len / 153);
        }
        smsCountEl.textContent = `(${parts} SMS)`;

        // Color warning if over 160
        if (len > 160) {
            charCountEl.style.color = '#fdcb6e';
        } else {
            charCountEl.style.color = '';
        }
    });
}

// === AJAX Form Submission ===
const smsForm = document.getElementById('smsForm');
const sendBtn = document.getElementById('sendBtn');

if (smsForm) {
    smsForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Show loading state
        const btnText = sendBtn.querySelector('.btn-text');
        const btnLoader = sendBtn.querySelector('.btn-loader');
        btnText.style.display = 'none';
        btnLoader.style.display = 'flex';
        sendBtn.disabled = true;

        try {
            const formData = new FormData(smsForm);

            const response = await fetch('', {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]') ? document.querySelector('[name=csrfmiddlewaretoken]').value : getCookie('csrftoken')
                },
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                showToast(data.message || 'SMS queued successfully!', 'success');

                // Clear form
                smsForm.reset();
                charCountEl.textContent = '0';
                smsCountEl.textContent = '(1 SMS)';

                // Refresh history immediately
                fetchSMSHistory();
            } else {
                showToast(data.error || 'Failed to send SMS.', 'error');
            }
        } catch (err) {
            console.error('Submit error:', err);
            showToast('Network error. Please try again.', 'error');
        } finally {
            // Reset button state
            btnText.style.display = 'flex';
            btnLoader.style.display = 'none';
            sendBtn.disabled = false;
        }
    });
}

// === SMS History Polling ===
let previousData = null;

async function fetchSMSHistory() {
    try {
        const response = await fetch('/api/sms-history/');
        if (!response.ok) throw new Error('Failed to fetch');

        const data = await response.json();
        updateHistoryTable(data);
        updateHistoryCount(data.length);
    } catch (err) {
        console.error('History fetch error:', err);
    }
}

function updateHistoryTable(smsList) {
    const tbody = document.getElementById('smsTableBody');
    if (!tbody) return;

    if (!smsList || smsList.length === 0) {
        tbody.innerHTML = `
            <tr class="empty-state">
                <td colspan="4">
                    <div class="empty-icon">📭</div>
                    <p>No messages yet. Send your first SMS!</p>
                </td>
            </tr>
        `;
        return;
    }

    // Check if data actually changed to avoid unnecessary DOM updates
    const newDataStr = JSON.stringify(smsList);
    if (newDataStr === previousData) return;
    previousData = newDataStr;

    const rows = smsList.map((sms, index) => {
        const isNew = index === 0 && !previousData; // first load won't animate
        return `
            <tr class="${isNew ? 'row-new' : ''}">
                <td>${escapeHTML(sms.receiver_number)}</td>
                <td><span class="msg-preview" title="${escapeHTML(sms.message)}">${escapeHTML(truncateMessage(sms.message))}</span></td>
                <td>${renderStatusBadge(sms.status)}</td>
                <td class="time-cell">${timeAgo(sms.created_at)}</td>
            </tr>
        `;
    });

    tbody.innerHTML = rows.join('');
}

function updateHistoryCount(count) {
    const el = document.getElementById('historyCount');
    if (el) {
        el.textContent = `${count} message${count !== 1 ? 's' : ''}`;
    }
}

// === HTML Escaping ===
function escapeHTML(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

// === Connection Status ===
const connectionStatusEl = document.getElementById('connectionStatus');

async function checkConnection() {
    try {
        const response = await fetch('/api/adb-status/', { method: 'GET' });
        if (!response.ok) {
            setConnectionStatus('disconnected', 'API Error');
            return;
        }
        
        const data = await response.json();
        if (!data.adb_installed) {
            setConnectionStatus('disconnected', 'ADB Not Found');
        } else if (!data.device_connected) {
            setConnectionStatus('disconnected', 'USB Disconnected');
        } else if (data.ready && data.device_info) {
            setConnectionStatus('connected', `${data.device_info.model}`);
        } else {
            setConnectionStatus('disconnected', 'Not Ready');
        }
    } catch (err) {
        console.error('Connection check error:', err);
        setConnectionStatus('disconnected', 'Server Offline');
    }
}

function setConnectionStatus(state, text) {
    if (!connectionStatusEl) return;
    connectionStatusEl.className = `connection-status ${state}`;
    const textEl = connectionStatusEl.querySelector('.status-text');
    if (textEl) textEl.textContent = text;
}

// === Initialize ===
document.addEventListener('DOMContentLoaded', () => {
    // Initial fetch
    fetchSMSHistory();
    checkConnection();

    // Poll history every 5 seconds
    setInterval(fetchSMSHistory, 5000);

    // Check connection every 30 seconds
    setInterval(checkConnection, 30000);

    // === Clear History ===
    const clearHistoryBtn = document.getElementById('clearHistoryBtn');
    if (clearHistoryBtn) {
        clearHistoryBtn.addEventListener('click', async () => {
            if (!confirm('Are you sure you want to clear all message history? This cannot be undone.')) {
                return;
            }

            clearHistoryBtn.disabled = true;
            try {
                const response = await fetch('/api/clear-history/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]') ? document.querySelector('[name=csrfmiddlewaretoken]').value : getCookie('csrftoken')
                    }
                });
                const data = await response.json();
                if (data.success) {
                    showToast(data.message || 'History cleared successfully.', 'success');
                    previousData = null; // force table redraw
                    fetchSMSHistory();   // refresh UI
                } else {
                    showToast(data.error || 'Failed to clear history.', 'error');
                }
            } catch (err) {
                console.error('Clear history error:', err);
                showToast('Network error. Please try again.', 'error');
            } finally {
                clearHistoryBtn.disabled = false;
            }
        });
    }

    console.log('📩 SMS Gateway loaded successfully!');
});