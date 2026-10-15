/**
 * Real-Time Support Agent Dashboard Client
 */

(function () {
  let agentId = "agent_" + Math.random().toString(36).substring(2, 6);
  let agentName = "Sarah Jenkins";
  let socket = null;
  let conversations = [];
  let activeConvId = null;
  let currentFilter = "all";
  let cannedResponses = [];
  let typingTimer = null;
  let isAgentTyping = false;

  // DOM Elements
  const queueList = document.getElementById("queue-list");
  const queueCountBadge = document.getElementById("queue-count-badge");
  const canvasTitle = document.getElementById("canvas-title");
  const canvasSubtitle = document.getElementById("canvas-subtitle");
  const canvasMessages = document.getElementById("canvas-messages");
  const canvasInputBar = document.getElementById("canvas-input-bar");
  const agentInput = document.getElementById("agent-input");
  const btnAgentSend = document.getElementById("btn-agent-send");
  const btnResolveChat = document.getElementById("btn-resolve-chat");
  const typingBanner = document.getElementById("agent-typing-banner");
  const cannedBar = document.getElementById("canned-macros-bar");
  const tabBtns = document.querySelectorAll(".tab-btn");

  // Context Pane Elements
  const contextCustId = document.getElementById("context-cust-id");
  const contextConvId = document.getElementById("context-conv-id");
  const contextStatus = document.getElementById("context-status");
  const orderSearchInput = document.getElementById("order-search-input");
  const btnOrderSearch = document.getElementById("btn-order-search");
  const orderDetailsBox = document.getElementById("order-details-box");

  // 1. WebSocket Setup
  function initAgentSocket() {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${window.location.host}/ws/chat`;

    socket = new WebSocket(wsUrl);

    socket.onopen = function () {
      socket.send(JSON.stringify({
        type: "agent_join",
        payload: {
          agentId: agentId,
          agentName: agentName
        }
      }));
    };

    socket.onmessage = function (event) {
      try {
        const data = JSON.parse(event.data);
        handleAgentEvent(data.type, data.payload);
      } catch (err) {
        console.error("Agent WS Error:", err);
      }
    };

    socket.onclose = function () {
      setTimeout(initAgentSocket, 3000);
    };
  }

  // 2. Handle Server Events
  function handleAgentEvent(type, payload) {
    switch (type) {
      case "agent_ready":
        conversations = payload.conversations || [];
        cannedResponses = payload.cannedResponses || [];
        renderCannedMacros();
        renderQueue();
        if (conversations.length > 0 && !activeConvId) {
          selectConversation(conversations[0].id);
        }
        break;

      case "queue_update":
        conversations = payload.conversations || [];
        renderQueue();
        if (activeConvId) {
          const current = conversations.find(c => c.id === activeConvId);
          if (current) updateContextPane(current);
        }
        break;

      case "receive_message":
        if (payload.conversation_id === activeConvId) {
          renderCanvasMessage(payload);
          scrollToCanvasBottom();
        }
        // Update local conversation list message cache
        const targetConv = conversations.find(c => c.id === payload.conversation_id);
        if (targetConv) {
          targetConv.messages.push(payload);
          targetConv.updated_at = payload.timestamp;
          renderQueue();
        }
        break;

      case "typing_status":
        if (payload.conversationId === activeConvId && payload.sender === "customer") {
          typingBanner.textContent = payload.isTyping ? "Customer is typing a message..." : "";
        }
        break;

      case "conversation_resolved":
        if (payload.conversationId === activeConvId) {
          btnResolveChat.style.display = "none";
          canvasInputBar.style.opacity = "0.5";
        }
        break;
    }
  }

  // 3. Render Conversation Queue
  function renderQueue() {
    let filtered = conversations.filter(c => {
      if (currentFilter === "all") return true;
      return c.status === currentFilter;
    });

    queueCountBadge.textContent = filtered.length;
    queueList.innerHTML = "";

    if (filtered.length === 0) {
      queueList.innerHTML = `<div style="padding: 1.5rem; text-align: center; color: #64748b; font-size: 0.85rem;">No conversations found in '${currentFilter}'.</div>`;
      return;
    }

    filtered.forEach(conv => {
      const item = document.createElement("div");
      item.className = `queue-item ${conv.id === activeConvId ? "active" : ""}`;

      const lastMsg = conv.messages && conv.messages.length > 0 ? conv.messages[conv.messages.length - 1] : null;
      const snippet = lastMsg ? lastMsg.text : "New session started";
      const timeStr = conv.updated_at ? new Date(conv.updated_at * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : "";

      item.innerHTML = `
        <div class="queue-item-header">
          <span class="customer-name">${escapeHtml(conv.customer_name || "Shopper")}</span>
          <span class="queue-time">${timeStr}</span>
        </div>
        <div class="queue-snippet">${escapeHtml(snippet)}</div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.25rem;">
          <span class="queue-status-tag tag-${conv.status}">${conv.status}</span>
          <span style="font-size: 0.7rem; color: #64748b;">${conv.messages ? conv.messages.length : 0} msgs</span>
        </div>
      `;

      item.addEventListener("click", () => selectConversation(conv.id));
      queueList.appendChild(item);
    });
  }

  // 4. Select Conversation
  function selectConversation(convId) {
    activeConvId = convId;
    const conv = conversations.find(c => c.id === convId);
    if (!conv) return;

    renderQueue();
    updateContextPane(conv);

    canvasTitle.textContent = `${conv.customer_name || "Shopper"}`;
    canvasSubtitle.textContent = `Conversation ID: ${conv.id} • Customer: ${conv.customer_id}`;
    
    // Status button
    if (conv.status === "resolved") {
      btnResolveChat.style.display = "none";
      canvasInputBar.style.opacity = "0.5";
    } else {
      btnResolveChat.style.display = "block";
      canvasInputBar.style.opacity = "1";
    }

    // Auto-claim conversation if still queued
    if (conv.status === "queued" && socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({
        type: "assign_agent",
        payload: {
          conversationId: conv.id,
          agentId: agentId,
          agentName: agentName
        }
      }));
    }

    // Render messages
    canvasMessages.innerHTML = "";
    (conv.messages || []).forEach(renderCanvasMessage);
    scrollToCanvasBottom();
  }

  function renderCanvasMessage(msg) {
    const isAgent = msg.sender === "agent";
    const bubble = document.createElement("div");
    bubble.className = `message-bubble ${msg.is_system ? "system" : isAgent ? "customer" : "agent"}`;
    bubble.style.alignSelf = msg.is_system ? "flex-start" : isAgent ? "flex-end" : "flex-start";

    const senderTitle = msg.sender_name || (isAgent ? agentName : "Customer");
    const timeStr = msg.timestamp ? new Date(msg.timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : "";

    let formattedText = escapeHtml(msg.text)
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\n/g, '<br/>');

    bubble.innerHTML = `
      <div class="message-sender">${escapeHtml(senderTitle)}</div>
      <div class="message-content" style="${isAgent ? 'background: #6366f1; color: #fff;' : ''}">
        ${formattedText}
      </div>
      <div class="message-time">${timeStr}</div>
    `;

    canvasMessages.appendChild(bubble);
  }

  function scrollToCanvasBottom() {
    canvasMessages.scrollTop = canvasMessages.scrollHeight;
  }

  // 5. Canned Responses Macros
  function renderCannedMacros() {
    cannedBar.innerHTML = `<span style="font-size:0.75rem; color:#9ca3af; font-weight:600;">Quick Macros:</span>`;
    cannedResponses.forEach(macro => {
      const chip = document.createElement("button");
      chip.className = "macro-chip";
      chip.textContent = macro.title;
      chip.title = macro.text;
      chip.addEventListener("click", () => {
        agentInput.value = macro.text;
        agentInput.focus();
      });
      cannedBar.appendChild(chip);
    });
  }

  // 6. Send Agent Message
  function handleSendMessage() {
    const text = agentInput.value.trim();
    if (!text || !activeConvId || !socket || socket.readyState !== WebSocket.OPEN) return;

    socket.send(JSON.stringify({
      type: "send_message",
      payload: {
        conversationId: activeConvId,
        sender: "agent",
        senderName: agentName,
        text: text
      }
    }));

    agentInput.value = "";
    sendAgentTyping(false);
  }

  btnAgentSend.addEventListener("click", handleSendMessage);
  agentInput.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  });

  // Typing state
  function sendAgentTyping(isTyping) {
    if (isAgentTyping !== isTyping && socket && socket.readyState === WebSocket.OPEN && activeConvId) {
      isAgentTyping = isTyping;
      socket.send(JSON.stringify({
        type: "typing",
        payload: {
          conversationId: activeConvId,
          sender: "agent",
          senderName: agentName,
          isTyping: isTyping
        }
      }));
    }
  }

  agentInput.addEventListener("input", function () {
    sendAgentTyping(true);
    clearTimeout(typingTimer);
    typingTimer = setTimeout(() => sendAgentTyping(false), 2000);
  });

  // Resolve chat button
  btnResolveChat.addEventListener("click", async function () {
    if (!activeConvId) return;
    try {
      const resp = await fetch(`/api/conversations/${activeConvId}/resolve`, { method: "POST" });
      if (resp.ok) {
        btnResolveChat.style.display = "none";
        canvasInputBar.style.opacity = "0.5";
      }
    } catch (err) {
      console.error("Resolve error:", err);
    }
  });

  // Filter tabs
  tabBtns.forEach(btn => {
    btn.addEventListener("click", function () {
      tabBtns.forEach(b => b.classList.remove("active"));
      this.classList.add("active");
      currentFilter = this.getAttribute("data-filter");
      renderQueue();
    });
  });

  // 7. Context Pane & Order Lookup
  function updateContextPane(conv) {
    contextCustId.textContent = conv.customer_id || "guest";
    contextConvId.textContent = conv.id;
    contextStatus.innerHTML = `<span class="queue-status-tag tag-${conv.status}">${conv.status}</span>`;
  }

  async function performOrderSearch(orderId) {
    if (!orderId) return;
    try {
      orderDetailsBox.innerHTML = `<em>Searching database...</em>`;
      const res = await fetch(`/api/orders/${encodeURIComponent(orderId)}`);
      if (res.ok) {
        const data = await res.json();
        const o = data.order;
        let itemsHtml = (o.items || []).map(i => `<li>${i.name} (${i.qty}x) - <strong>${i.price}</strong></li>`).join("");
        orderDetailsBox.innerHTML = `
          <div style="font-weight: 700; color: #818cf8; margin-bottom: 0.35rem;">${o.order_id} &bull; ${o.customer_name}</div>
          <div>Status: <span style="color:${o.status_color}; font-weight:700;">${o.status}</span></div>
          <div>Carrier: <strong>${o.carrier}</strong> (${o.tracking_number})</div>
          <div>ETA: ${o.estimated_delivery}</div>
          <div style="margin-top: 0.5rem; font-weight:600;">Items:</div>
          <ul style="padding-left: 1.1rem; margin-top: 0.2rem;">${itemsHtml}</ul>
          <div style="margin-top: 0.5rem; font-weight:700; color:#fff;">Total: ${o.total}</div>
        `;
      } else {
        orderDetailsBox.innerHTML = `<span style="color:#ef4444;">Order '${orderId}' not found in records.</span>`;
      }
    } catch (err) {
      orderDetailsBox.innerHTML = `<span style="color:#ef4444;">Error fetching order details.</span>`;
    }
  }

  btnOrderSearch.addEventListener("click", () => performOrderSearch(orderSearchInput.value.trim()));
  orderSearchInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") performOrderSearch(orderSearchInput.value.trim());
  });

  function escapeHtml(str) {
    return (str || "").replace(/[&<>"']/g, function (m) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[m];
    });
  }

  // Initialize
  initAgentSocket();
})();
