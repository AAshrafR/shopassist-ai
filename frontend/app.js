// ShopAssist AI Frontend Application Logic

const API_BASE = window.location.origin;
const messagesContainer = document.getElementById("messagesContainer");
const chatForm = document.getElementById("chatForm");
const queryInput = document.getElementById("queryInput");
const backendStatus = document.getElementById("backendStatus");
const clearChatBtn = document.getElementById("clearChatBtn");

let sessionId = "session-" + Math.random().toString(36).substring(2, 9);

// Check backend connectivity on mount
async function checkBackendHealth() {
  try {
    const res = await fetch(`${API_BASE}/api/health`);
    if (res.ok) {
      const data = await res.json();
      backendStatus.innerHTML = `<span class="dot"></span> Online (${data.indexed_documents} chunks)`;
    } else {
      backendStatus.innerHTML = `<span class="dot" style="background:#ef4444;box-shadow:none;"></span> Status Error`;
    }
  } catch (err) {
    backendStatus.innerHTML = `<span class="dot" style="background:#ef4444;box-shadow:none;"></span> Offline`;
  }
}

// Convert simple markdown into clean HTML
function formatMarkdown(text) {
  if (!text) return "";
  let html = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  // Bold
  html = html.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  // Italic
  html = html.replace(/\*(.*?)\*/g, "<em>$1</em>");
  // Code
  html = html.replace(/`(.*?)`/g, "<code>$1</code>");
  // Linebreaks and paragraphs
  html = html.replace(/\n\n/g, "</p><p>");
  html = html.replace(/\n- (.*?)(?=(\n|$))/g, "<br>• $1");
  html = html.replace(/\n/g, "<br>");

  return `<p>${html}</p>`;
}

// Append message bubble to chat window
function appendMessage(sender, content, sources = [], toolCall = null, latencyMs = null) {
  const msgDiv = document.createElement("div");
  msgDiv.className = `message ${sender}`;

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = sender === "user" ? "👤" : "🤖";

  const bubble = document.createElement("div");
  bubble.className = "bubble";

  // Optional Tool Call badge
  if (toolCall) {
    const toolBadge = document.createElement("div");
    toolBadge.className = "tool-badge";
    const toolTitle = toolCall.tool_name === "order_lookup" ? "📦 Order Lookup Tool Executed" : "🎫 Support Ticket Tool Executed";
    toolBadge.innerHTML = `⚙️ <strong>${toolTitle}</strong>`;
    bubble.appendChild(toolBadge);
  }

  // Text content
  const contentDiv = document.createElement("div");
  contentDiv.innerHTML = formatMarkdown(content);
  bubble.appendChild(contentDiv);

  // Optional Sources tags
  if (sources && sources.length > 0) {
    const sourcesCard = document.createElement("div");
    sourcesCard.className = "sources-card";

    const header = document.createElement("div");
    header.className = "sources-header";
    header.innerHTML = `📚 Verified Sources (${sources.length})`;
    sourcesCard.appendChild(header);

    const tagsDiv = document.createElement("div");
    tagsDiv.className = "sources-tags";
    sources.forEach(src => {
      const tag = document.createElement("span");
      tag.className = "source-tag";
      tag.title = `File: ${src.source_file || 'Bitext KB'} | Score: ${src.relevance_score}`;
      tag.textContent = src.title;
      tagsDiv.appendChild(tag);
    });
    sourcesCard.appendChild(tagsDiv);
    bubble.appendChild(sourcesCard);
  }

  // Latency footer
  if (latencyMs !== null && latencyMs !== undefined) {
    const meta = document.createElement("div");
    meta.className = "latency-meta";
    meta.textContent = `Generated in ${latencyMs.toFixed(1)} ms`;
    bubble.appendChild(meta);
  }

  msgDiv.appendChild(avatar);
  msgDiv.appendChild(bubble);
  messagesContainer.appendChild(msgDiv);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Show typing indicator
function showTypingIndicator() {
  const typingDiv = document.createElement("div");
  typingDiv.className = "message bot";
  typingDiv.id = "typingIndicator";

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = "🤖";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.innerHTML = `
    <div class="typing-dots">
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
    </div>
  `;

  typingDiv.appendChild(avatar);
  typingDiv.appendChild(bubble);
  messagesContainer.appendChild(typingDiv);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function removeTypingIndicator() {
  const ind = document.getElementById("typingIndicator");
  if (ind) ind.remove();
}

// Send user inquiry to backend
async function handleUserQuery(userText) {
  if (!userText || !userText.trim()) return;

  const text = userText.trim();
  appendMessage("user", text);
  queryInput.value = "";
  showTypingIndicator();

  try {
    const res = await fetch(`${API_BASE}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: text,
        session_id: sessionId
      })
    });

    removeTypingIndicator();

    if (!res.ok) {
      appendMessage("bot", "⚠️ Sorry, an error occurred while communicating with the support engine.");
      return;
    }

    const data = await res.json();
    appendMessage("bot", data.answer, data.sources, data.tool_call, data.latency_ms);
  } catch (err) {
    removeTypingIndicator();
    appendMessage("bot", "⚠️ Unable to reach server. Please check your network connection.");
    console.error(err);
  }
}

// Form submission handler
chatForm.addEventListener("submit", (e) => {
  e.preventDefault();
  handleUserQuery(queryInput.value);
});

// Quick prompt chips
document.querySelectorAll(".chip").forEach(btn => {
  btn.addEventListener("click", () => {
    const prompt = btn.getAttribute("data-prompt");
    handleUserQuery(prompt);
  });
});

// Quick order lookup from sidebar
window.lookupOrderQuick = function(orderId) {
  handleUserQuery(`What is the status of order ${orderId}?`);
};

// Clear chat history
clearChatBtn.addEventListener("click", () => {
  messagesContainer.innerHTML = "";
  sessionId = "session-" + Math.random().toString(36).substring(2, 9);
  appendMessage("bot", "Chat history cleared. How can I assist you with your orders or policies today?");
});

// Initialize on page load
checkBackendHealth();
setInterval(checkBackendHealth, 30000);

