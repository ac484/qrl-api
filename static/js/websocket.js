// WebSocket connection for real-time updates
let ws = null;
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;
const reconnectDelay = 3000;

function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    
    console.log('Connecting to WebSocket:', wsUrl);
    ws = new WebSocket(wsUrl);
    
    ws.onopen = function() {
        console.log('WebSocket connected');
        reconnectAttempts = 0;
        updateConnectionStatus(true);
    };
    
    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        console.log('WebSocket message:', data);
        handleWebSocketMessage(data);
    };
    
    ws.onerror = function(error) {
        console.error('WebSocket error:', error);
        updateConnectionStatus(false);
    };
    
    ws.onclose = function() {
        console.log('WebSocket disconnected');
        updateConnectionStatus(false);
        
        // Attempt to reconnect
        if (reconnectAttempts < maxReconnectAttempts) {
            reconnectAttempts++;
            console.log(`Reconnecting... (attempt ${reconnectAttempts}/${maxReconnectAttempts})`);
            setTimeout(connectWebSocket, reconnectDelay);
        } else {
            console.error('Max reconnection attempts reached. Please refresh the page.');
        }
    };
}

function handleWebSocketMessage(data) {
    const updateTime = document.querySelector('.refresh-info');
    const now = new Date().toLocaleString('zh-TW', { 
        year: 'numeric', 
        month: '2-digit', 
        day: '2-digit', 
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit' 
    });
    
    if (data.type === 'update') {
        // Update price if changed
        if (data.price) {
            const priceElements = document.querySelectorAll('.balance-value');
            if (priceElements.length > 0) {
                // Update current price (assuming it's in the price card)
                console.log('Updated price:', data.price);
            }
        }
        
        // Update bot status if changed
        if (data.bot_status) {
            const statusBadge = document.querySelector('.status-badge');
            if (statusBadge) {
                statusBadge.textContent = data.bot_status;
                statusBadge.className = 'status-badge status-' + data.bot_status.toLowerCase();
            }
        }
        
        // Update daily trades if changed
        if (data.daily_trades !== undefined) {
            console.log('Daily trades:', data.daily_trades);
        }
        
        // Update last update time
        if (updateTime) {
            const timeText = updateTime.textContent.replace(/最後更新:.*/, `最後更新: ${now}`);
            updateTime.innerHTML = updateTime.innerHTML.replace(/最後更新:.*?(?=<|$)/, `最後更新: ${now}`);
        }
    } else if (data.type === 'trade_executed') {
        console.log('Trade executed:', data.result);
        // Reload page on trade execution to show updated data
        setTimeout(() => location.reload(), 1000);
    } else if (data.type === 'status_change') {
        console.log('Status changed:', data.new_status);
        // Reload page on status change
        setTimeout(() => location.reload(), 500);
    }
}

function updateConnectionStatus(connected) {
    const indicator = document.querySelector('.auto-refresh');
    if (indicator) {
        indicator.style.color = connected ? '#48bb78' : '#f56565';
        indicator.title = connected ? 'WebSocket 已連接' : 'WebSocket 已斷線';
    }
}

// Connect when page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', connectWebSocket);
} else {
    connectWebSocket();
}

// Fallback: reload page every 5 minutes if WebSocket fails
setTimeout(function() {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        console.log('WebSocket not connected, reloading page...');
        location.reload();
    }
}, 300000); // 5 minutes
