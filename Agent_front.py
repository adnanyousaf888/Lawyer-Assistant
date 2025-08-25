# app.py
import uuid, json, requests, datetime as dt, re
import streamlit as st

# ----------------------------- #
# Config
# ----------------------------- #
DEFAULT_API_URL = "https://agentx123.app.n8n.cloud/webhook/23ee85b0-c920-490b-8f47-6a6d3f24db90/chat"
APP_TITLE = "IBT Smart Wakeel"

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🧑‍⚖️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ----------------------------- #
# Global styles (centered layout, compact bubbles, fixed chat input)
# ----------------------------- #
st.markdown("""
<style>
/* Center column width */
.maxw { max-width: 840px; margin: 0 auto; }

/* Keep some top room */
.main { padding-top: .75rem; }

/* Hero */
.hero        { text-align:center; margin: 0 auto 8px auto; }
.hero-title  { font-weight: 800; font-size: 2.2rem; letter-spacing:.2px; }
.hero-subtle { opacity:.70; font-size:.95rem; margin-top:.25rem }

/* Chips area (wrapper stays centered with .maxw) */
#chipbar { margin: 12px auto 6px auto; max-width: 840px; }
#chipbar .stButton>button {
  border-radius: 12px;
  padding: 10px 12px;
  font-size: .92rem;
  text-align: left;
  border: 1px solid rgba(255,255,255,.15);
  background: rgba(255,255,255,.06);
  transition: all .2s ease;
  color: inherit;
  width: 100%;
  box-shadow: 0 2px 6px rgba(0,0,0,.10);
}
#chipbar .stButton>button:hover {
  border-color: rgba(59,130,246,.40);
  background: rgba(59,130,246,.12);
  box-shadow: 0 6px 16px rgba(59,130,246,.22);
}
#chipbar .stButton>button:active { transform: scale(.985); }

/* Hint under chips */
.askline { text-align:center; opacity:.7; font-size:.95rem; margin: 10px auto 6px auto; }

/* Chat bubbles */
.bubble-wrap { max-width: 840px; margin: 6px auto; }
.bubble-user, .bubble-assistant {
  padding: 11px 14px;
  border-radius: 16px;
  margin: 6px 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-size: 0.95rem;
}

/* --- Unified type rhythm ------------------------------------ */
/* Everything inside bubbles follows the same line-height and block margins */
.bubble-user, 
.bubble-user * ,
.bubble-assistant, 
.bubble-assistant * {
  line-height: 1.38;               /* single rhythm for all text inside bubbles */
}

/* Paragraphs: spacing only, no left padding */
.bubble-user p,
.bubble-assistant p {
  margin: 0.40rem 0;
  padding-left: 0;                 /* remove indent on <p> */
}

/* Lists: add the indent */
.bubble-user ul,
.bubble-assistant ul,
.bubble-user ol,
.bubble-assistant ol {
  margin: 0.40rem 0;
  padding-left: 1.25rem;           /* indent lists only */
  list-style-position: outside;    /* cleaner bullets */
}

/* List items: keep tight and aligned */
.bubble-user li,
.bubble-assistant li {
  margin: 0.18rem 0;
  padding-left: 0;
}


/* List items (including nested) */
.bubble-user li,
.bubble-assistant li {
  margin: 0.18rem 0;               /* tight, even bullets */
}

/* Reduce extra spacing on nested lists */
.bubble-user ul ul,
.bubble-user ol ol,
.bubble-assistant ul ul,
.bubble-assistant ol ol {
  margin: 0.25rem 0;
  padding-left: 1.15rem;
}

/* User bubble visual */
.bubble-user {
  background: rgba(59,130,246,.18);
  color: #d6e9ff;
  margin-left: 30%;
  border: 1px solid rgba(59,130,246,.25);
  padding: 8px 12px;
  border-radius: 14px;
}

/* Assistant bubble visual */
.bubble-assistant {
  background: rgba(255,255,255,.08);
  border: 1px solid rgba(255,255,255,.10);
  margin-right: 30%;
  padding: 10px 14px;
  border-radius: 14px;
}

/* Right-aligned typing indicator INSIDE the chat column */
.typing {
  max-width: 840px;
  margin: 6px auto 2px auto;
  text-align: right;
  opacity: .70;
  font-size: .85rem;
}

/* Chat input — auto-adapt to Streamlit light/dark */
[data-testid="stChatInput"] {
  max-width: 840px !important;
  margin: 8px auto 12px auto !important;
}

/* Wrapper (the visible input container) */
[data-testid="stChatInput"] > div {
  max-width: 840px !important;
  margin: 0 auto !important;

  /* Use Streamlit theme variables with sensible fallbacks */
  background: var(--background-color, #ffffff) !important;
  border: 1px solid var(--secondary-background-color, #d0d5dd) !important;
  border-radius: 12px !important;
  box-shadow: none !important;
}

/* Actual textarea */
[data-testid="stChatInput"] textarea {
  color: var(--text-color, #111111) !important;
  background: var(--background-color, #ffffff) !important;
  box-shadow: none !important;
  outline: none !important;
}

/* Placeholder text */
[data-testid="stChatInput"] textarea::placeholder {
  /* Slightly muted versus normal text */
  color: color-mix(in srgb, var(--text-color, #111111) 55%, transparent) !important;
}

/* Focus outline uses theme primary color */
[data-testid="stChatInput"] > div:focus-within {
  border-color: var(--primary-color, #3b82f6) !important;
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--primary-color, #3b82f6) 28%, transparent) !important;
}

/* Fallback for environments where theme vars aren't injected */
@media (prefers-color-scheme: dark) {
  [data-testid="stChatInput"] > div {
    background: #0e1117 !important;
    border-color: #2b2f36 !important;
  }
  [data-testid="stChatInput"] textarea {
    color: #ffffff !important;
    background: #0e1117 !important;
  }
  [data-testid="stChatInput"] textarea::placeholder {
    color: #9aa4b2 !important;
  }
}



/* Tiny hint on top-left */
.smallhint { position:fixed; top:8px; left:12px; opacity:.6; font-size:.85rem; z-index:9999; }

/* Footer */
.footer { opacity:.6; font-size:.8rem; margin: 12px auto; text-align:center; max-width: 840px; }
</style>
""", unsafe_allow_html=True)

# ----------------------------- #
# State
# ----------------------------- #
ss = st.session_state
if "session_id" not in ss:
    ss.session_id = str(uuid.uuid4())
if "history" not in ss:
    ss.history = []  # [{role, content, ts}]
if "api_url" not in ss:
    ss.api_url = DEFAULT_API_URL
if "busy" not in ss:
    ss.busy = False
if "hide_chips" not in ss:
    ss.hide_chips = False
if "pending_prompt" not in ss:
    ss.pending_prompt = ""  # text we will send on the next run

# ----------------------------- #
# Helpers
# ----------------------------- #
def friendly_time():
    return dt.datetime.now().strftime("%I:%M %p").lstrip("0")

def clean_text(s: str) -> str:
    """Strip tags & tame spacing for natural reading."""
    if s is None:
        return ""
    s = str(s)
    s = re.sub(r"<[^>]+>", "", s)            # remove HTML tags
    s = s.replace("&nbsp;", " ").replace("\r", "\n")
    s = re.sub(r"\n{2,}", "\n\n", s)         # keep ONE blank line between blocks
    s = re.sub(r"[ \t]{2,}", " ", s)         # collapse multi-spaces
    return s.strip()

def post_to_n8n(message: str) -> requests.Response:
    payload = {"action": "sendMessage", "chatInput": message, "sessionId": ss.session_id}
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    return requests.post(ss.api_url, json=payload, headers=headers, timeout=120)

def add_msg(role, content):
    ss.history.append({"role": role, "content": content, "ts": friendly_time()})

def export_markdown() -> str:
    lines = [f"# {APP_TITLE} — chat export\n"]
    for m in ss.history:
        who = "You" if m["role"] == "user" else "Assistant"
        lines.append(f"**{who} ({m['ts']})**\n\n{m['content']}\n")
    return "\n".join(lines)

# >>> REPLACED with stronger, anchor-pinned version <<<
def scroll_to_bottom():
    """Pin viewport to #chat-bottom every time the DOM changes."""
    st.markdown(
        """
        <script>
        (function () {
          const scroll = () => {
            const el = document.getElementById('chat-bottom');
            if (el) el.scrollIntoView({behavior: 'instant', block: 'end'});
          };
          // run immediately and after a short tick
          scroll();
          setTimeout(scroll, 30);
          // re-scroll on subsequent DOM mutations
          const obs = new MutationObserver(scroll);
          obs.observe(document.body, {subtree: true, childList: true});
          // also on window load
          window.addEventListener('load', scroll);
        })();
        </script>
        """,
        unsafe_allow_html=True,
    )

def start_interaction(text: str):
    """Two-phase send:
       1) immediately show the user message (chips disappear)
       2) set pending_prompt and rerun to call n8n on the next cycle
    """
    ss.hide_chips = True
    add_msg("user", text)
    ss.pending_prompt = text

    # keep screen pinned immediately (before rerun)
    scroll_to_bottom()
    st.rerun()

def render_centered_chips(items, per_row=3):
    """Render chips neatly centered, not stretched apart."""
    st.markdown('<div id="chipbar" class="maxw">', unsafe_allow_html=True)

    n = len(items)
    idx = 0
    while idx < n:
        remain = n - idx
        take = min(per_row, remain)

        # Dynamic centering
        if take == 3:
            cols = st.columns([1,1,1,1,1], gap="small")
            positions = [1,2,3]     # middle three
        elif take == 2:
            cols = st.columns([1,1,1,1], gap="small")
            positions = [1,2]       # middle two
        else:  # 1 chip
            cols = st.columns([1,1,1], gap="small")
            positions = [1]         # center

        for j in range(take):
            ico, text = items[idx + j]
            with cols[positions[j]]:
                if st.button(f"{ico} {text}", key=f"chip_{idx+j}", disabled=ss.busy):
                    if not ss.busy:
                        start_interaction(text)
        idx += take

    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------- #
# Small top-left hint (sidebar)
# ----------------------------- #
st.markdown("<div class='smallhint'>Use the ▸ in the top‑left to open <b>Controls</b>.</div>", unsafe_allow_html=True)

# ----------------------------- #
# Sidebar (user opens via ▸)
# ----------------------------- #
with st.sidebar:
    st.header("Controls")
    st.caption("Your n8n Chat Webhook must end with `/chat` and the workflow should use **Using Response Nodes**.")
    st.text_input("API URL", value=ss.api_url, key="api_url_input")
    ss.api_url = ss.api_url_input
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🧹 Clear chat", use_container_width=True):
            ss.history = []
            ss.hide_chips = False
            ss.pending_prompt = ""
            ss.busy = False
            st.rerun()
    with c2:
        st.download_button("⬇️ Export", data=export_markdown(), file_name="chat_export.md",
                           mime="text/markdown", use_container_width=True)

# ----------------------------- #
# Hero
# ----------------------------- #
st.markdown(f"""
<div class="maxw hero">
  <div class="hero-title">{APP_TITLE}</div>
  <div class="hero-subtle">Ask legal questions, search acts, and chat naturally.</div>
</div>
""", unsafe_allow_html=True)

# ----------------------------- #
# Chips — only before first user message
# ----------------------------- #
show_chips = (not ss.hide_chips) and (len(ss.history) == 0)

if show_chips:
    chips = [
        ("📘", "Summarize Section 302 PPC in simple words."),
        ("⚖️", "What is the punishment for theft under Pakistani law?"),
        ("✉️", "Draft a polite legal notice about late rent."),
        ("🧾", "Summarize a court judgment into bullet points."),
        ("🧾", "Explain key amendments in Income Tax Ordinance 2001."),
        ("📌", "What is the procedure to file an FIR in Pakistan (CrPC 1898)."),
        ("💼", "How to register a Private Ltd company (Companies Act 2017)?"),
        ("💰", "Tell me the Latest changes in Income Tax Ordinance 2001."),
        ("📄", "Create a basic NDA for a freelance project.")
    ]
    render_centered_chips(chips, per_row=3)

# ----------------------------- #
# History
# ----------------------------- #
for m in ss.history:
    role = m["role"]
    css = "bubble-user" if role == "user" else "bubble-assistant"
    st.markdown(
        f"<div class='bubble-wrap'><div class='{css}'>{clean_text(m['content'])}</div></div>",
        unsafe_allow_html=True
    )

# Right-aligned typing indicator INSIDE the centered column
typing_placeholder = st.empty()
if ss.pending_prompt or ss.busy:
    typing_placeholder.markdown("<div class='typing'>Wakeel is typing…</div>", unsafe_allow_html=True)
    scroll_to_bottom()   # keep viewport pinned during typing

# ----------------------------- #
# If there is a pending prompt (from chat box or chip), call n8n now
# (after rendering history so the user message shows immediately)
# ----------------------------- #
if ss.pending_prompt and not ss.busy:
    ss.busy = True
    with st.spinner(""):
        try:
            resp = post_to_n8n(ss.pending_prompt)
            if not resp.ok:
                reply = f"HTTP {resp.status_code} Reply: {clean_text(resp.text)}"
            else:
                ct = (resp.headers.get("Content-Type") or "")
                if "application/json" in ct:
                    try:
                        data = resp.json()
                    except Exception:
                        reply = clean_text(resp.text)
                    else:
                        reply = clean_text(
                            data.get("reply")
                            or (data.get("data") or {}).get("reply")
                            or ((data.get("messages") or [{}])[0]).get("text")
                            or json.dumps(data, ensure_ascii=False)
                        )
                else:
                    reply = clean_text(resp.text)
        except Exception:
            reply = "Sorry, I couldn't reach the server."

    typing_placeholder.empty()
    add_msg("assistant", reply)
    ss.pending_prompt = ""
    ss.busy = False
    scroll_to_bottom()
    st.rerun()

# ----------------------------- #
# Chat input (centered & locked during request)
# ----------------------------- #
text = st.chat_input("Ask anything related to law…", disabled=ss.busy)
if text and not ss.busy and not ss.pending_prompt:
    start_interaction(text)

# --- Bottom anchor: keep this LAST so we always scroll here ---
st.markdown("<div id='chat-bottom'></div>", unsafe_allow_html=True)

# Final nudge (optional; safe with anchor+observer)
if ss.history:
    scroll_to_bottom()
