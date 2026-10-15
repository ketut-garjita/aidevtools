/**
 * Real-Time Customer Support Chat Widget Client
 */

(function () {
  // 1. Session Identity
  let customerId = localStorage.getItem("ecom_chat_customer_id");
  if (!customerId) {
    customerId = "cust_" + Math.random().toString(36).substring(2, 10);
    localStorage.setItem("ecom_chat_customer_id", customerId);
  }

  let customerName = localStorage.getItem("ecom_chat_customer_name") || "Guest Shopper";
  let activeConversationId = null;
  let socket = null;
  let isChatOpen = false;
  let unreadCount = 0;
  let typingTimer = null;
  let isCurrentlyTyping = false;
  let reconnectAttempts = 0;

  // 2. Inject Widget DOM
  const widgetHtml = `
    <div id="support-chat-container">
      <!-- Floating Launcher Button -->
      <button id="chat-launcher-btn" class="chat-launcher-btn" aria-label="Open Customer Support Chat">
        <svg id="launcher-icon-chat" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
        </svg>
        <svg id="launcher-icon-close" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display:none;">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
        <span id="chat-unread-badge" class="chat-launcher-badge" style="display: none;">0</span>
      </button>

      <!-- Chat Modal Window -->
      <div id="chat-window" class="chat-window" role="dialog" aria-modal="true" aria-label="Live Customer Support">
        <!-- Header -->
        <div class="chat-header">
          <div class="header-agent-info">
            <div class="agent-avatar">
              <span>CS</span>
              <span id="agent-status-indicator" class="agent-status-dot"></span>
            </div>
            <div class="header-text">
              <h3>Support Concierge</h3>
              <span id="agent-status-text" class="header-status-label">
                <span class="pulse-dot" style="width:6px; height:6px;"></span> Available Online
              </span>
            </div>
          </div>
          <div class="header-actions">
            <button id="chat-btn-minimize" class="icon-btn" aria-label="Minimize Chat">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="5" y1="12" x2="19" y2="12"></line></svg>
            </button>
          </div>
        </div>

        <!-- Quick Chips Bar -->
        <div class="quick-chips-bar">
          <button class="chip-btn" data-action="order" data-val="ORD-1001">📦 Track #ORD-1001</button>
          <button class="chip-btn" data-action="order" data-val="ORD-1002">🚚 Track #ORD-1002</button>
          <button class="chip-btn" data-action="faq" data-val="What is your return policy?">🔄 Return Policy</button>
          <button class="chip-btn" data-action="faq" data-val="How fast is express shipping?">⚡ Shipping Times</button>
          <button class="chip-btn" data-action="human">👤 Live Agent</button>
        </div>

        <!-- Message Body -->
        <div id="chat-messages" class="chat-messages" role="log" aria-live="polite"></div>

        <!-- Typing Indicator Container -->
        <div id="typing-indicator" class="typing-indicator-wrapper" style="display: none; margin: 0 1rem 0.5rem;">
          <span class="typing-dot"></span>
          <span class="typing-dot"></span>
          <span class="typing-dot"></span>
          <span style="font-size: 0.72rem; color: #94a3b8; margin-left: 0.4rem;">Agent is typing...</span>
        </div>

        <!-- Message Input Footer -->
        <form id="chat-input-form" class="chat-footer">
          <input 
            type="text" 
            id="chat-input-text" 
            class="chat-input" 
            placeholder="Type your question or #Order ID..." 
            autocomplete="off"
            maxlength="1000"
          />
          <button type="submit" id="chat-send-btn" class="chat-send-btn" aria-label="Send Message">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="22" y1="2" x2="11" y2="13"></line>
              <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
            </svg>
          </button>
        </form>
      </div>
    </div>
  `;

  document.body.insertAdjacentHTML("beforeend", widgetHtml);

  // DOM Elements
  const launcherBtn = document.getElementById("chat-launcher-btn");
  const launcherIconChat = document.getElementById("launcher-icon-chat");
  const launcherIconClose = document.getElementById("launcher-icon-close");
  const unreadBadge = document.getElementById("chat-unread-badge");
  const chatWindow = document.getElementById("chat-window");
  const btnMinimize = document.getElementById("chat-btn-minimize");
  const messagesBox = document.getElementById("chat-messages");
  const typingIndicator = document.getElementById("typing-indicator");
  const inputForm = document.getElementById("chat-input-form");
  const inputText = document.getElementById("chat-input-text");
  const agentStatusText = document.getElementById("agent-status-text");
  const agentStatusDot = document.getElementById("agent-status-indicator");

  // 3. WebSocket Connection Setup
  function initWebSocket() {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${window.location.host}/ws/chat`;

    socket = new WebSocket(wsUrl);

    socket.onopen = function () {
      reconnectAttempts = 0;
      // Initialize customer session
      socket.send(JSON.stringify({
        type: "customer_init",
        payload: {
          customerId: customerId,
          name: customerName
        }
      }));
    };

    socket.onmessage = function (event) {
      try {
        const data = JSON.parse(event.data);
        handleServerEvent(data.type, data.payload);
      } catch (err) {
        console.error("Error parsing WS message:", err);
      }
    };

    socket.onclose = function () {
      agentStatusText.innerHTML = `<span style="color:#ef4444;">Connecting...</span>`;
      agentStatusDot.classList.add("offline");
      // Exponential backoff
      reconnectAttempts++;
      const delay = Math.min(1000 * Math.pow(1.5, reconnectAttempts), 10000);
      setTimeout(initWebSocket, delay);
    };

    socket.onerror = function () {
      socket.close();
    };
  }

  // 4. Server Event Handling
  function handleServerEvent(type, payload) {
    switch (type) {
      case "session_ready":
        activeConversationId = payload.conversation.id;
        messagesBox.innerHTML = "";
        payload.conversation.messages.forEach(renderMessage);
        updateAgentPresence(payload.onlineAgents || 0);
        scrollToBottom();
        break;

      case "receive_message":
        renderMessage(payload);
        typingIndicator.style.display = "none";
        scrollToBottom();

        if (!isChatOpen && payload.sender !== "customer") {
          unreadCount++;
          unreadBadge.textContent = unreadCount;
          unreadBadge.style.display = "flex";
        }
        break;

      case "typing_status":
        if (payload.sender !== "customer") {
          typingIndicator.style.display = payload.isTyping ? "flex" : "none";
          if (payload.isTyping) scrollToBottom();
        }
        break;

      case "agent_presence":
        updateAgentPresence(payload.onlineAgents || 0);
        break;

      case "order_result":
        if (payload.found) {
          renderOrderCard(payload.order);
        }
        scrollToBottom();
        break;

      case "conversation_resolved":
        renderSystemNotice("This conversation has been marked as resolved by support. Feel free to send a message to start a new inquiry anytime!");
        scrollToBottom();
        break;
    }
  }

  function updateAgentPresence(count) {
    if (count > 0) {
      agentStatusDot.classList.remove("offline");
      agentStatusText.innerHTML = `<span class="pulse-dot" style="width:6px; height:6px;"></span> ${count} Agent${count > 1 ? "s" : ""} Online`;
    } else {
      agentStatusDot.classList.remove("offline");
      agentStatusText.innerHTML = `Automated Assistant (Live rep on call)`;
    }
  }

  // 5. Message Rendering
  function renderMessage(msg) {
    const isSelf = msg.sender === "customer";
    const bubble = document.createElement("div");
    bubble.className = `message-bubble ${msg.is_system ? "system" : isSelf ? "customer" : "agent"}`;

    const timeStr = msg.timestamp ? new Date(msg.timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : "";
    
    // Simple markdown link / bold parser for clean display
    let formattedText = escapeHtml(msg.text)
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\n/g, '<br/>');

    bubble.innerHTML = `
      <div class="message-sender">${msg.sender_name || (isSelf ? "You" : "Agent")}</div>
      <div class="message-content">${formattedText}</div>
      <div class="message-time">${timeStr}</div>
    `;

    messagesBox.appendChild(bubble);
  }

  function renderOrderCard(order) {
    const card = document.createElement("div");
    card.className = "chat-order-card";
    card.innerHTML = `
      <div class="card-order-header">
        <span>Order #${order.order_id}</span>
        <span class="card-order-status" style="background:${order.status_color}22; color:${order.status_color}; border: 1px solid ${order.status_color}44;">
          ${order.status}
        </span>
      </div>
      <div style="color: #94a3b8; font-size: 0.78rem; margin-bottom: 0.4rem;">
        🚚 <strong>${order.carrier}</strong> &bull; Tracking: ${order.tracking_number}
      </div>
      <div style="color: #e2e8f0; font-size: 0.78rem;">
        📅 Expected: <strong>${order.estimated_delivery}</strong>
      </div>
      <div style="font-size: 0.75rem; color: #a5b4fc; margin-top: 0.35rem; font-style: italic;">
        📍 ${order.last_update}
      </div>
    `;
    messagesBox.appendChild(card);
  }

  function renderSystemNotice(text) {
    const notice = document.createElement("div");
    notice.className = "message-bubble system";
    notice.innerHTML = `<div class="message-content">ℹ️ ${escapeHtml(text)}</div>`;
    messagesBox.appendChild(notice);
  }

  function scrollToBottom() {
    messagesBox.scrollTop = messagesBox.scrollHeight;
  }

  function escapeHtml(str) {
    return (str || "").replace(/[&<>"']/g, function (m) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[m];
    });
  }

  // 6. UI Interaction & Listeners
  function toggleChat(forceOpen) {
    isChatOpen = typeof forceOpen === "boolean" ? forceOpen : !isChatOpen;
    chatWindow.classList.toggle("open", isChatOpen);

    if (isChatOpen) {
      launcherIconChat.style.display = "none";
      launcherIconClose.style.display = "block";
      unreadCount = 0;
      unreadBadge.style.display = "none";
      setTimeout(() => inputText.focus(), 150);
      scrollToBottom();
    } else {
      launcherIconChat.style.display = "block";
      launcherIconClose.style.display = "none";
    }
  }

  launcherBtn.addEventListener("click", () => toggleChat());
  btnMinimize.addEventListener("click", () => toggleChat(false));

  // Form submission
  inputForm.addEventListener("submit", function (e) {
    e.preventDefault();
    const text = inputText.value.trim();
    if (!text || !socket || socket.readyState !== WebSocket.OPEN) return;

    // Check if input looks like an order ID query (e.g. #ORD-1001 or ORD-1001)
    const orderMatch = text.match(/#?(ORD-\d+|\b100\d\b)/i);

    // Send chat message
    socket.send(JSON.stringify({
      type: "send_message",
      payload: {
        conversationId: activeConversationId,
        sender: "customer",
        senderName: customerName,
        text: text
      }
    }));

    // If order number mentioned, trigger automatic simulated order lookup
    if (orderMatch) {
      socket.send(JSON.stringify({
        type: "order_query",
        payload: {
          conversationId: activeConversationId,
          orderId: orderMatch[0]
        }
      }));
    }

    // Reset typing status
    sendTyping(false);
    inputText.value = "";
  });

  // Typing emitter
  function sendTyping(isTyping) {
    if (isCurrentlyTyping !== isTyping && socket && socket.readyState === WebSocket.OPEN) {
      isCurrentlyTyping = isTyping;
      socket.send(JSON.stringify({
        type: "typing",
        payload: {
          conversationId: activeConversationId,
          sender: "customer",
          senderName: customerName,
          isTyping: isTyping
        }
      }));
    }
  }

  inputText.addEventListener("input", function () {
    sendTyping(true);
    clearTimeout(typingTimer);
    typingTimer = setTimeout(() => sendTyping(false), 2000);
  });

  // Quick Action Chips Listener
  document.querySelectorAll(".chip-btn").forEach(btn => {
    btn.addEventListener("click", function () {
      const action = this.getAttribute("data-action");
      const val = this.getAttribute("data-val");

      if (action === "order") {
        inputText.value = `Where is my order #${val}?`;
        inputForm.dispatchEvent(new Event("submit"));
      } else if (action === "faq") {
        inputText.value = val;
        inputForm.dispatchEvent(new Event("submit"));
      } else if (action === "human") {
        inputText.value = "I would like to speak to a customer support specialist.";
        inputForm.dispatchEvent(new Event("submit"));
      }
    });
  });

  // Expose helper to global window for demo order click tracking
  window.triggerOrderChat = function(orderId) {
    toggleChat(true);
    inputText.value = `Checking status for order #${orderId}`;
    inputForm.dispatchEvent(new Event("submit"));
  };

  // Start WebSocket
  initWebSocket();
})();
