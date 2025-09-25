# app.py
import uuid, json, requests, datetime as dt, re
import time
import streamlit as st

# ----------------------------- #
# Config
# ----------------------------- #
DEFAULT_API_URL = "https://anthonygonservice.app.n8n.cloud/webhook/23ee85b0-c920-490b-8f47-6a6d3f24db90/chat"
APP_TITLE = "IBT Smart Wakeel"

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🧑‍⚖️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 🔒 Remove header icons (Share/Star/Edit/GitHub), hamburger, and "Manage app"
st.markdown("""
<style>
/* Nuke the whole header (removes hamburger + all right-side icons) */
header[data-testid="stHeader"] { 
  display: none !important;
}

/* Reduce the top gap since header is gone */
.block-container { 
  padding-top: 0.6rem !important;
}

/* Hide Streamlit Cloud badges / Manage app widget (bottom-right) */
[class*="viewerBadge"],
[data-testid="stStatusWidget"],
#stDecoration {
  display: none !important;
}
</style>

<script>
// Safety sweep in case Cloud renders slightly differently
const sweep = () => {
  // Header leftovers
  document.querySelectorAll('header, [data-testid="stHeader"]').forEach(el => el.style.display = "none");
  // Manage app / viewer badges
  document.querySelectorAll('[class*="viewerBadge"], [data-testid="stStatusWidget"], #stDecoration')
    .forEach(el => el.style.display = "none");
};
new MutationObserver(sweep).observe(document.body, {subtree:true, childList:true});
window.addEventListener('load', sweep);
</script>
""", unsafe_allow_html=True)





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
.bubble-user, 
.bubble-user * ,
.bubble-assistant, 
.bubble-assistant * {
  line-height: 1.38;
}
.bubble-user p,
.bubble-assistant p,
.bubble-user ul,
.bubble-assistant ul,
.bubble-user ol,
.bubble-assistant ol {
  margin: 0.40rem 0;
  padding-left: 1.15rem;
}
.bubble-user li,
.bubble-assistant li {
  margin: 0.18rem 0;
}
.bubble-user ul ul,
.bubble-user ol ol,
.bubble-assistant ul ul,
.bubble-assistant ol ol {
  margin: 0.25rem 0;
  padding-left: 1.15rem;
}
/* User bubble */
.bubble-user {
  background: rgba(59,130,246,.18);
  color: #d6e9ff;
  margin-left: 30%;
  border: 1px solid rgba(59,130,246,.25);
  padding: 8px 12px;
  border-radius: 14px;
}
/* Assistant bubble */
.bubble-assistant {
  background: rgba(255,255,255,.08);
  border: 1px solid rgba(255,255,255,.10);
  margin-right: 30%;
  padding: 10px 14px;
  border-radius: 14px;
}
/* Typing indicator */
.typing {
  max-width: 840px;
  margin: 6px auto 2px auto;
  text-align: right;
  opacity: .70;
  font-size: .85rem;
}
/* Chat input */
[data-testid="stChatInput"] {
  max-width: 840px !important;
  margin: 8px auto 12px auto !important;
}
[data-testid="stChatInput"] > div {
  max-width: 840px !important;
  margin: 0 auto !important;
  background: var(--background-color, #ffffff) !important;
  border: 1px solid var(--secondary-background-color, #d0d5dd) !important;
  border-radius: 12px !important;
  box-shadow: none !important;
}
[data-testid="stChatInput"] textarea {
  color: var(--text-color, #111111) !important;
  background: var(--background-color, #ffffff) !important;
  box-shadow: none !important;
  outline: none !important;
}
[data-testid="stChatInput"] textarea::placeholder {
  color: color-mix(in srgb, var(--text-color, #111111) 55%, transparent) !important;
}
[data-testid="stChatInput"] > div:focus-within {
  border-color: var(--primary-color, #3b82f6) !important;
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--primary-color, #3b82f6) 28%, transparent) !important;
}
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
/* Always show a visible caret (cursor) */
[data-testid="stChatInput"] textarea {
  caret-color: #3b82f6 !important;   /* bright blue cursor */
}

/* Optional: different cursor color in dark mode */
@media (prefers-color-scheme: dark) {
  [data-testid="stChatInput"] textarea {
    caret-color: #ffffff !important; /* white cursor in dark mode */
  }
}

/* ------- Mobile / touch: hide tiles ------- */
@media (max-width: 1024px), (hover: none) and (pointer: coarse){
  #chipbar{ 
    display: none !important; 
    height: 0 !important; 
    overflow: hidden !important; 
  }
  .maxw{ max-width: 96vw; }
  .hero-title{ font-size: 1.55rem; }
  .hero-subtle{ font-size: .90rem; }
  .smallhint{ display: none; }
  .bubble-user, .bubble-assistant{
    margin: 6px 0 !important;
    border-radius: 12px !important;
    padding: 9px 12px !important;
    font-size: .95rem !important;
  }
  .bubble-user{ margin-left: 0 !important; }
  .bubble-assistant{ margin-right: 0 !important; }
}

/* ===== Legal-style formatting for assistant replies ===== */
.bubble-assistant{
  text-align: justify;          /* formal doc look */
  font-size: 0.95rem;
  line-height: 1.55;            /* easier reading */
}

.bubble-assistant ul,
.bubble-assistant ol{
  padding-left: 1.8rem;         /* deeper indent */
  margin: 0.6rem 0;             /* spacing above/below list */
}

.bubble-assistant li{
  margin: 0.35rem 0;            /* space between bullets */
}

/* sub-clauses like a), b), c) */
.bubble-assistant ul ul,
.bubble-assistant ol ol{
  padding-left: 1.5rem;
  margin: 0.3rem 0;
  list-style-type: lower-alpha;
}

/* headings inside replies (when you use **bold**) */
.bubble-assistant strong{
  display: block;
  margin: 0.5rem 0 0.2rem 0;
  font-weight: 600;
  text-decoration: underline;
}
/* ===== End legal-style formatting ===== */

/* Headings inside legal text */
.bubble-assistant strong {
  display: block;
  margin: 0.5rem 0 0.2rem 0;
  font-weight: 600;
  text-decoration: underline;
}

/* Adjust spacing for assistant legal lists */
.bubble-assistant ul,
.bubble-assistant ol {
  padding-left: 1.5rem;     /* indentation only */
  margin: 0.3rem 0;         /* less top/bottom space */
}

.bubble-assistant li {
  margin: 0.15rem 0;        /* tighter vertical spacing */
  line-height: 1.45;        /* clean readable lines */
}
/* Tighter paragraphs for assistant replies */
.bubble-assistant p {
  margin: 0.2rem 0;        /* less top/bottom space */
  line-height: 1.4;        /* more compact but readable */
}

/* Keep lists compact too */
.bubble-assistant li {
  margin: 0.15rem 0;
  line-height: 1.4;
}


.smallhint { position:fixed; top:8px; left:12px; opacity:.6; font-size:.85rem; z-index:9999; }
.footer { opacity:.6; font-size:.8rem; margin: 12px auto; text-align:center; max-width: 840px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* 🔒 Hide bottom-right profile picture and Streamlit Cloud badge */
[data-testid="stStatusWidget"],
[class*="viewerBadge_container"],
[class*="stStatusWidget"],
#stDecoration {
    display: none !important;
    visibility: hidden !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* Hide Streamlit Cloud badges/profile (more variants, incl. mobile) */
[data-testid="stStatusWidget"],
[class*="viewerBadge"], 
[class*="stStatusWidget"], 
#stDecoration,
a[href*="streamlit.io"],
a[href*="share.streamlit"],
a[href*="cloud.streamlit"] {
  display: none !important;
  visibility: hidden !important;
}

/* Mobile-specific catch-all for tiny fixed widgets near bottom-right */
@media (max-width: 768px) {
  /* any small fixed element sitting in the bottom-right corner */
  .stApp div, .stApp a, .stApp button {
    /* we won't actually apply display:none here; JS below will do it precisely */
  }
}
</style>

<script>
// Extra mobile sweep: hide small fixed widgets at bottom-right (avatar/crown)
(function(){
  function hideBRBadges(){
    const vw = Math.max(document.documentElement.clientWidth, window.innerWidth || 0);
    const vh = Math.max(document.documentElement.clientHeight, window.innerHeight || 0);
    const margin = 140; // distance from bottom-right corner considered "badge zone"

    document.querySelectorAll('div, a, button, span, img').forEach(el => {
      // skip chat input area entirely
      if (el.closest('[data-testid="stChatInput"]')) return;

      const cs = window.getComputedStyle(el);
      if (cs.position !== 'fixed') return;

      const rect = el.getBoundingClientRect();
      const nearBottomRight = (vw - rect.right <= margin) && (vh - rect.bottom <= margin);
      const verySmall = rect.width <= 140 && rect.height <= 140;

      // Heuristics to catch avatar/crown without touching your UI
      if (nearBottomRight && verySmall) {
        // avoid hiding mobile browser UI overlays accidentally
        el.style.display = 'none';
      }

      // Text/links fallbacks
      const t = (el.textContent || '').trim();
      const href = el.getAttribute && el.getAttribute('href');
      if (/manage app/i.test(t)) el.style.display = 'none';
      if (href && /streamlit\\.io|share\\.streamlit|cloud\\.streamlit/i.test(href)) el.style.display = 'none';
    });
  }

  const obs = new MutationObserver(hideBRBadges);
  obs.observe(document.body, {subtree:true, childList:true});
  window.addEventListener('load', hideBRBadges);
  window.addEventListener('resize', hideBRBadges);
})();
</script>
""", unsafe_allow_html=True)

# ======================= OVERRIDE BLOCK (added) =======================
st.markdown("""
<style>
/* ---------- FIX: Quick Ask selectbox (light mode visibility) ---------- */
[data-testid="stSelectbox"] div[role="combobox"]{
  background: #e0f2fe !important;          /* soft light blue tile */
  border: 1px solid #38bdf8 !important;    /* cyan border */
  color: #0f172a !important;               /* dark text */
  box-shadow: none !important;
}
[data-testid="stSelectbox"] input{
  color: #0f172a !important;
  -webkit-text-fill-color: #0f172a !important;
  background: transparent !important;
  font-size: 16px !important;              /* stop mobile auto-zoom */
}
[data-testid="stSelectbox"] input::placeholder{
  color: #475569 !important;               /* slate-600 */
  opacity: 1 !important;
}
[data-testid="stSelectbox"] svg{
  color: #0f172a !important;
  fill: #0f172a !important;
}

/* User/Assistant bubbles – light mode contrast */
.bubble-user{ background:#e0f2fe !important; color:#0f172a !important; border:1px solid #38bdf8 !important; }
.bubble-assistant{ background:#f8fafc !important; color:#111827 !important; border:1px solid #e2e8f0 !important; }

/* Preserve dark-mode look */
@media (prefers-color-scheme: dark){
  [data-testid="stSelectbox"] div[role="combobox"]{
    background: rgba(255,255,255,.06) !important;
    border: 1px solid rgba(255,255,255,.12) !important;
    color: #e5e7eb !important;
  }
  [data-testid="stSelectbox"] input{
    color: #e5e7eb !important;
    -webkit-text-fill-color: #e5e7eb !important;
  }
  [data-testid="stSelectbox"] input::placeholder{
    color: #9aa4b2 !important;
  }
  [data-testid="stSelectbox"] svg{
    color: #e5e7eb !important; fill: #e5e7eb !important;
  }
  .bubble-user{ background:rgba(59,130,246,.18) !important; color:#d6e9ff !important; border:1px solid rgba(59,130,246,.25) !important; }
  .bubble-assistant{ background:rgba(255,255,255,.08) !important; color:#ffffff !important; border:1px solid rgba(255,255,255,.10) !important; }
}
</style>
""", unsafe_allow_html=True)
# ===================== END OVERRIDE BLOCK (added) =====================


st.markdown("""
<script>
function setMobileFlag(){
  const isTouch = matchMedia('(hover: none) and (pointer: coarse)').matches;
  const isNarrow = window.innerWidth <= 1024;
  if (isTouch || isNarrow) document.body.setAttribute('data-mobile','1');
  else document.body.removeAttribute('data-mobile');
}
setMobileFlag();
window.addEventListener('resize', setMobileFlag);
</script>
<style>
body[data-mobile="1"] #chipbar{ display:none !important; height:0 !important; overflow:hidden !important; }
</style>
""", unsafe_allow_html=True)

# ----------------------------- #
# State
# ----------------------------- #
ss = st.session_state
if "session_id" not in ss:
    ss.session_id = str(uuid.uuid4())
if "history" not in ss:
    ss.history = []
if "api_url" not in ss:
    ss.api_url = DEFAULT_API_URL
if "busy" not in ss:
    ss.busy = False
if "hide_chips" not in ss:
    ss.hide_chips = False
if "pending_prompt" not in ss:
    ss.pending_prompt = ""

# ----------------------------- #
# Helpers
# ----------------------------- #
def friendly_time():
    return dt.datetime.now().strftime("%I:%M %p").lstrip("0")

def clean_text(s: str) -> str:
    if s is None: return ""
    s = str(s)
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("&nbsp;", " ").replace("\r", "\n")
    s = re.sub(r"\n{2,}", "\n\n", s)
    s = re.sub(r"[ \t]{2,}", " ", s)
    s = re.sub(r"https?://\S+", "", s)            # 🔹 remove any http/https links
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

# --- Stable scroll script ---
def scroll_to_bottom():
    st.markdown(
        """
        <script>
        (function () {
          const NEAR = 240;
          let userScrolling = false;
          let rafID = null;

          const isNearBottom = () => {
            const doc = document.scrollingElement || document.documentElement;
            return (doc.scrollHeight - (doc.scrollTop + window.innerHeight)) <= NEAR;
          };

          const autoScroll = () => {
            if (userScrolling) return;
            if (!isNearBottom()) return;
            const doc = document.scrollingElement || document.documentElement;
            doc.scrollTop = doc.scrollHeight;
          };

          const schedule = () => {
            if (rafID) return;
            rafID = requestAnimationFrame(() => { rafID = null; autoScroll(); });
          };

          let scrollEndTimer = null;
          const onUserScroll = () => {
            userScrolling = true;
            if (scrollEndTimer) clearTimeout(scrollEndTimer);
            scrollEndTimer = setTimeout(() => { userScrolling = false; }, 180);
          };
          window.addEventListener('wheel', onUserScroll, {passive:true});
          window.addEventListener('touchmove', onUserScroll, {passive:true});
          window.addEventListener('keydown', (e) => {
            if (['ArrowUp','ArrowDown','PageUp','PageDown','Home','End',' '].includes(e.key)) {
              onUserScroll();
            }
          });

          schedule();
          setTimeout(schedule, 30);

          const obs = new MutationObserver(schedule);
          obs.observe(document.body, {subtree: true, childList: true});
          window.addEventListener('load',  schedule);
          window.addEventListener('resize', schedule);
        })();
        </script>
        """,
        unsafe_allow_html=True,
    )

def _hard_scroll_now():
    st.markdown(
        """
        <script>
        (function(){
          const el = document.getElementById('chat-bottom');
          if (el) el.scrollIntoView({behavior:'smooth', block:'end'});
        })();
        </script>
        """,
        unsafe_allow_html=True,
    )


# ----------------------------- #
# Interaction + UI
# ----------------------------- #
def start_interaction(text: str):
    ss.hide_chips = True
    add_msg("user", text)
    ss.pending_prompt = text
    scroll_to_bottom()
    st.rerun()

def render_centered_chips(items, per_row=3):
    st.markdown('<div id="chipbar" class="maxw">', unsafe_allow_html=True)
    n = len(items)
    idx = 0
    while idx < n:
        remain = n - idx
        take = min(per_row, remain)
        if take == 3:
            cols = st.columns([1,1,1,1,1], gap="small"); positions = [1,2,3]
        elif take == 2:
            cols = st.columns([1,1,1,1], gap="small"); positions = [1,2]
        else:
            cols = st.columns([1,1,1], gap="small"); positions = [1]
        for j in range(take):
            ico, text = items[idx + j]
            with cols[positions[j]]:
                if st.button(f"{ico} {text}", key=f"chip_{idx+j}", disabled=ss.busy):
                    if not ss.busy: start_interaction(text)
        idx += take
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------- #
# Sidebar + Hero
# ----------------------------- #
st.markdown("<div class='smallhint'>Use the ▸ in the top-left to open <b>Controls</b>.</div>", unsafe_allow_html=True)
with st.sidebar:
    st.header("Controls")
    #st.caption("Your n8n Chat Webhook must end with `/chat` and the workflow should use **Using Response Nodes**.")
    #st.text_input("API URL", value=ss.api_url, key="api_url_input"); ss.api_url = ss.api_url_input
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🧹 Clear chat", use_container_width=True):
            ss.history = []; ss.hide_chips = False; ss.pending_prompt = ""; ss.busy = False; st.rerun()
    with c2:
        st.download_button("⬇️ Export", data=export_markdown(), file_name="chat_export.md",
                           mime="text/markdown", use_container_width=True)

st.markdown(f"""
<div class="maxw hero">
  <div class="hero-title">{APP_TITLE}</div>
  <div class="hero-subtle">Ask legal questions, search acts, and chat naturally.</div>
</div>
""", unsafe_allow_html=True)



# ----------------------------- #
# Quick examples (mobile gets dropdown; desktop keeps tiles)
# ----------------------------- #
if (not ss.hide_chips) and (len(ss.history) == 0):
    examples = [
        "Summarize Section 302 PPC in simple words.",
        "What is the punishment for theft under Pakistani law?",
        "Draft a polite legal notice about late rent.",
        "Summarize a court judgment into bullet points.",
        "Explain key amendments in Income Tax Ordinance 2001.",
        "What is the procedure to file an FIR in Pakistan (CrPC 1898).",
        "How to register a Private Ltd company (Companies Act 2017)?",
        "Tell me the Latest changes in Income Tax Ordinance 2001.",
        "Create a basic NDA for a freelance project."
    ]

    # Mobile-first: small, single control
    sel = st.selectbox(
        "Quick Ask",
        ["Quick Legal Help…"] + examples,
        index=0,
        label_visibility="collapsed",
    )
    if sel != "Quick Legal Help…":
        start_interaction(sel)

    # Optional: keep tiles for desktop (they're auto-hidden on mobile by CSS)
    #chips = [("📘", examples[0]), ("⚖️", examples[1]), ("✉️", examples[2]),
    #         ("🧾", examples[3]), ("🧾", examples[4]), ("📌", examples[5]),
    #         ("💼", examples[6]), ("💰", examples[7]), ("📄", examples[8])]
    #render_centered_chips(chips, per_row=3)





# ----------------------------- #
# History
# ----------------------------- #
for m in ss.history:
    css = "bubble-user" if m["role"] == "user" else "bubble-assistant"
    st.markdown(f"<div class='bubble-wrap'><div class='{css}'>{clean_text(m['content'])}</div></div>", unsafe_allow_html=True)

typing_placeholder = st.empty()
if ss.pending_prompt or ss.busy:
    typing_placeholder.markdown("<div class='typing'>Wakeel is thinking for you…</div>", unsafe_allow_html=True)
    scroll_to_bottom()

# ----------------------------- #
# Pending prompt → n8n
# ----------------------------- #
if ss.pending_prompt and not ss.busy:
    ss.busy = True
    with st.spinner(""):
        try:
            resp = post_to_n8n(ss.pending_prompt)
            if not resp.ok: reply = f"HTTP {resp.status_code} Reply: {clean_text(resp.text)}"
            else:
                ct = (resp.headers.get("Content-Type") or "")
                if "application/json" in ct:
                    try: data = resp.json()
                    except Exception: reply = clean_text(resp.text)
                    else:
                        reply = clean_text(
                            data.get("reply")
                            or (data.get("data") or {}).get("reply")
                            or ((data.get("messages") or [{}])[0]).get("text")
                            or json.dumps(data, ensure_ascii=False)
                        )
                else: reply = clean_text(resp.text)
        except Exception: reply = "Sorry, I couldn't reach the server."

    # --- Word-by-word effect (mobile friendly) ---
    typing_placeholder.empty()
    animated_placeholder = st.empty()
    bottom_anchor = st.empty()
    partial = ""

    for i, chunk in enumerate(re.split(r'(\s+)', reply)):
        partial += chunk
        animated_placeholder.markdown(
            f"<div class='bubble-wrap'><div class='bubble-assistant'>{clean_text(partial)}</div></div>",
            unsafe_allow_html=True
        )
        # Always refresh anchor and scroll smoothly (better sync on mobile)
        bottom_anchor.markdown("<div id='chat-bottom'></div>", unsafe_allow_html=True)
        _hard_scroll_now()
        time.sleep(0.03)  # slightly slower for DOM paint on mobile

    # Final nudge to bottom after loop
    bottom_anchor.markdown("<div id='chat-bottom'></div>", unsafe_allow_html=True)
    _hard_scroll_now()

    # --- End typing ---

    add_msg("assistant", reply)
    ss.pending_prompt = ""; ss.busy = False
    scroll_to_bottom(); st.rerun()

# ----------------------------- #
# Chat input
# ----------------------------- #
text = st.chat_input("Ask anything related to law…", disabled=ss.busy)
if text and not ss.busy and not ss.pending_prompt: start_interaction(text)

st.markdown("<div id='chat-bottom'></div>", unsafe_allow_html=True)
if ss.history: scroll_to_bottom()

































