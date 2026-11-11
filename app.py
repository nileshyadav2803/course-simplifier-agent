"""
Course Content Simplification Agent
Streamlit app — IBM watsonx.ai (granite-4-h-small)
Production-grade dark UI: glassmorphism, animations, sidebar panel,
typing indicator, token card glows, shimmer accent line.
"""

import os

import streamlit as st
from dotenv import load_dotenv
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────
MODEL_ID    = "ibm/granite-4-h-small"
MAX_TOKENS  = 1000
TEMPERATURE = 0.1

SYSTEM_MESSAGE = (
    "You are a Course Content Simplification Agent. "
    "The user will send course text and a level: Beginner, Intermediate, or Expert. "
    "Rewrite the text in simple language for that level. "
    "Beginner: very simple words, short sentences, define every technical term, "
    "add one small everyday example. "
    "Intermediate: clear language, keep key technical terms with a short explanation. "
    "Expert: concise and precise, keep technical terms, remove extra explanation. "
    "Do not add information that is not in the text. "
    "If the level is missing, ask the user to choose one."
)

LEVELS = ["Beginner", "Intermediate", "Expert"]

LEVEL_STYLE = {
    "Beginner":     {"bg": "#052e16", "border": "#16a34a", "text": "#4ade80", "glow": "#16a34a40"},
    "Intermediate": {"bg": "#2d1d00", "border": "#d97706", "text": "#fbbf24", "glow": "#d9770640"},
    "Expert":       {"bg": "#2d0a0a", "border": "#dc2626", "text": "#f87171", "glow": "#dc262640"},
}

# ─────────────────────────────────────────────────────────────────────────────
# Page config  — must be FIRST Streamlit call
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Course Simplifier · IBM watsonx.ai",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');

/* ── Keyframes ── */
@keyframes shimmer {
  0%   { background-position: -400px 0; }
  100% { background-position:  400px 0; }
}
@keyframes pulse-dot {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40%            { transform: scale(1.0); opacity: 1.0; }
}
@keyframes fadeSlideUp {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0);    }
}
@keyframes glow-pulse {
  0%, 100% { box-shadow: 0 0 8px #2563eb30; }
  50%       { box-shadow: 0 0 20px #2563eb60; }
}

/* ── Global reset ── */
*, *::before, *::after { box-sizing: border-box; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"] {
    background: #07070a !important;
    color: #e4e4e7 !important;
    font-family: 'IBM Plex Sans', 'Segoe UI', system-ui, sans-serif !important;
}

/* Strip every default padding Streamlit injects */
[data-testid="block-container"],
[data-testid="stVerticalBlock"],
[data-testid="stVerticalBlockBorderWrapper"],
section[data-testid="stSidebar"] > div:first-child {
    padding-top: 0 !important;
    padding-bottom: 0 !important;
}
[data-testid="block-container"] { padding-left: 0 !important; padding-right: 0 !important; max-width: 100% !important; }

/* Hide chrome */
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="collapsedControl"],
#MainMenu, footer { display: none !important; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #0d0d10 !important;
    border-right: 1px solid #1e1e24 !important;
    min-width: 240px !important;
    max-width: 240px !important;
}
section[data-testid="stSidebar"] * { color: #a1a1aa !important; }
.sb-logo {
    display: flex; align-items: center; gap: 0.6rem;
    padding: 1.4rem 1.2rem 0.8rem;
    border-bottom: 1px solid #1e1e24;
    margin-bottom: 0.8rem;
}
.sb-logo-icon {
    width: 32px; height: 32px; border-radius: 8px;
    background: linear-gradient(135deg,#1d4ed8,#2563eb);
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem; flex-shrink: 0;
}
.sb-logo-text { font-size: 0.82rem; font-weight: 600; color: #e4e4e7 !important; line-height: 1.3; }
.sb-logo-sub  { font-size: 0.65rem; color: #52525b !important; }

.sb-section { padding: 0 1.2rem; margin-bottom: 1.2rem; }
.sb-section-title {
    font-size: 0.6rem; font-weight: 700; letter-spacing: 1px;
    text-transform: uppercase; color: #3f3f46 !important;
    margin-bottom: 0.6rem;
}
.sb-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 0.35rem 0; border-bottom: 1px solid #18181b;
}
.sb-key   { font-size: 0.72rem; color: #71717a !important; }
.sb-val   { font-size: 0.72rem; font-weight: 600; color: #a1a1aa !important; }
.sb-val.blue   { color: #60a5fa !important; }
.sb-val.green  { color: #4ade80 !important; }
.sb-val.purple { color: #c084fc !important; }

.sb-stat-card {
    background: #111114; border: 1px solid #1e1e24;
    border-radius: 10px; padding: 0.7rem 0.9rem;
    margin-bottom: 0.5rem;
}
.sb-stat-num  { font-size: 1.4rem; font-weight: 700; color: #e4e4e7 !important; line-height: 1; }
.sb-stat-lbl  { font-size: 0.65rem; color: #52525b !important; margin-top: 2px; }

.sb-divider { border: none; border-top: 1px solid #18181b; margin: 0.8rem 0; }

/* ── Hero ── */
.hero {
    width: 100%;
    background: linear-gradient(110deg, #05050f 0%, #080d25 45%, #060e30 100%);
    padding: 1.4rem 2.5rem 1.2rem;
    display: flex; align-items: center; justify-content: space-between; gap: 1rem;
    position: relative; overflow: hidden;
}
.hero::after {
    content: '';
    position: absolute; bottom: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, #2563eb, #7c3aed, #0ea5e9, transparent);
    background-size: 400px 1px;
    animation: shimmer 3s linear infinite;
}
.hero-left  { display: flex; flex-direction: column; gap: 0.3rem; }
.hero-title {
    font-size: 1.55rem; font-weight: 700;
    color: #f4f4f5; letter-spacing: -0.5px; line-height: 1.25;
}
.hero-title .accent { color: #3b82f6; }
.hero-title .accent2{ color: #8b5cf6; }
.hero-sub {
    font-size: 0.76rem; color: #52525b;
    display: flex; align-items: center; gap: 0.5rem;
}
.hero-dot { width: 5px; height: 5px; border-radius: 50%; background: #22c55e; display: inline-block; }
.hero-right { display: flex; flex-direction: column; align-items: flex-end; gap: 0.4rem; }
.hero-pill {
    background: rgba(37,99,235,0.12); border: 1px solid rgba(59,130,246,0.3);
    color: #60a5fa; padding: 3px 12px; border-radius: 999px;
    font-size: 0.7rem; font-weight: 600; letter-spacing: 0.4px;
}
.hero-meta { font-size: 0.68rem; color: #3f3f46; text-align: right; }

/* ── Main layout ── */
.chat-wrap {
    max-width: 820px; margin: 0 auto;
    padding: 0 2rem 0;
}
.chat-area { display: flex; flex-direction: column; gap: 1.2rem; }

/* ── Empty state ── */
.empty-state {
    display: flex; flex-direction: column; align-items: center;
    padding: 0.8rem 1rem 0.5rem; gap: 0.5rem; opacity: 0.4;
}
.empty-icon { font-size: 1.6rem; }
.empty-text { font-size: 0.78rem; color: #52525b; text-align: center; }

/* ── Bubble rows ── */
.brow {
    display: flex; gap: 0.7rem; align-items: flex-start;
    animation: fadeSlideUp 0.25s ease both;
}
.brow.user { flex-direction: row-reverse; }

.av {
    width: 34px; height: 34px; border-radius: 50%; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.9rem; margin-top: 2px;
}
.av.user { background: linear-gradient(135deg,#1d4ed8,#3b82f6); box-shadow: 0 2px 10px #3b82f640; }
.av.bot  {
    background: #111114; border: 1px solid #27272a;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 40'%3E%3Ccircle cx='20' cy='20' r='18' fill='%231d4ed820'/%3E%3C/svg%3E");
}

.bgroup { display: flex; flex-direction: column; max-width: 78%; }
.brow.user .bgroup { align-items: flex-end; }

.badge {
    display: inline-flex; align-items: center;
    font-size: 0.6rem; font-weight: 700;
    padding: 2px 9px; border-radius: 999px;
    letter-spacing: 0.9px; text-transform: uppercase;
    margin-bottom: 5px; align-self: flex-start;
    transition: transform 0.15s;
}
.badge:hover { transform: scale(1.05); }
.brow.user .badge { align-self: flex-end; }

.bubble {
    padding: 0.75rem 1.05rem;
    border-radius: 18px;
    line-height: 1.75; font-size: 0.875rem; font-weight: 400;
    word-break: break-word; letter-spacing: 0.01em;
    animation: fadeSlideUp 0.2s ease both;
}
.bubble.user {
    background: linear-gradient(145deg,#1e40af,#2563eb);
    color: #eff6ff; font-weight: 500;
    border-bottom-right-radius: 5px;
    box-shadow: 0 4px 20px rgba(37,99,235,0.35);
}
.bubble.bot {
    background: #111114;
    border: 1px solid #1e1e24;
    color: #d4d4d8;
    border-bottom-left-radius: 5px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.5);
}

/* ── Typing indicator ── */
.typing { display: flex; gap: 5px; align-items: center; padding: 0.75rem 1rem; }
.typing span {
    width: 7px; height: 7px; border-radius: 50%; background: #52525b;
    display: inline-block; animation: pulse-dot 1.2s ease-in-out infinite;
}
.typing span:nth-child(2) { animation-delay: 0.2s; }
.typing span:nth-child(3) { animation-delay: 0.4s; }

/* ── Token cards ── */
.tok-row { display: flex; gap: 0.55rem; margin-top: 0.7rem; }
.tok-card {
    flex: 1; border-radius: 10px; padding: 0.5rem 0.65rem; text-align: center;
    background: #0d0d10; border: 1px solid #1e1e24;
    transition: transform 0.15s, box-shadow 0.15s;
    cursor: default;
}
.tok-card:hover { transform: translateY(-2px); }
.tok-card.blue   { border-top: 2px solid #3b82f6; }
.tok-card.blue:hover   { box-shadow: 0 4px 16px #3b82f630; }
.tok-card.purple { border-top: 2px solid #a855f7; }
.tok-card.purple:hover { box-shadow: 0 4px 16px #a855f730; }
.tok-card.cyan   { border-top: 2px solid #06b6d4; }
.tok-card.cyan:hover   { box-shadow: 0 4px 16px #06b6d430; }
.tok-lbl { font-size: 0.58rem; color: #3f3f46; text-transform: uppercase; letter-spacing: 0.6px; }
.tok-val { font-size: 1.05rem; font-weight: 700; color: #71717a; margin-top: 2px; }

/* ── Divider ── */
.sep {
    border: none; height: 1px; margin: 1.5rem 0;
    background: linear-gradient(90deg, transparent, #27272a 20%, #27272a 80%, transparent);
}

/* ── Input panel (glassmorphism) ── */
.input-wrap {
    max-width: 820px; margin: 0 auto;
    padding: 0.5rem 2rem 1.5rem;
}
.glass-card {
    background: rgba(17,17,20,0.85);
    backdrop-filter: blur(20px) saturate(140%);
    -webkit-backdrop-filter: blur(20px) saturate(140%);
    border: 1px solid rgba(39,39,42,0.8);
    border-radius: 20px;
    padding: 1.3rem 1.5rem 1.1rem;
    box-shadow: 0 8px 40px rgba(0,0,0,0.6), 0 1px 0 rgba(255,255,255,0.04) inset;
    transition: border-color 0.2s;
}
.glass-card:focus-within {
    border-color: rgba(59,130,246,0.4);
    box-shadow: 0 8px 40px rgba(0,0,0,0.6), 0 0 0 1px rgba(59,130,246,0.2);
}
.pill-row { display: flex; gap: 0.4rem; margin-bottom: 0.8rem; }
.level-pill {
    font-size: 0.72rem; font-weight: 600; padding: 4px 14px;
    border-radius: 999px; cursor: pointer; letter-spacing: 0.3px;
    border: 1px solid #27272a; background: #18181b; color: #71717a;
    transition: all 0.15s;
}
.level-pill:hover { border-color: #3f3f46; color: #a1a1aa; }

/* ── Radio pills override ── */
div[data-testid="stRadio"] > label { display: none !important; }
div[data-testid="stRadio"] > div {
    display: flex !important; flex-direction: row !important;
    gap: 0.4rem !important; flex-wrap: nowrap !important;
}
div[data-testid="stRadio"] div[data-testid="stMarkdownContainer"] p {
    font-size: 0.72rem !important; font-weight: 600 !important; margin: 0 !important;
}
div[data-testid="stRadio"] label[data-baseweb="radio"] {
    background: #18181b !important; border: 1px solid #27272a !important;
    border-radius: 999px !important; padding: 4px 15px !important;
    color: #71717a !important; cursor: pointer !important;
    transition: all 0.15s ease !important;
}
div[data-testid="stRadio"] label[data-baseweb="radio"]:hover {
    border-color: #3f3f46 !important; color: #a1a1aa !important;
}
div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) {
    background: linear-gradient(135deg,#1d4ed8,#2563eb) !important;
    border-color: #3b82f6 !important; color: #fff !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.2), 0 2px 8px rgba(37,99,235,0.4) !important;
    transform: scale(1.04);
    animation: glow-pulse 2s ease-in-out infinite !important;
}
[data-baseweb="radio"] > div:first-child { display: none !important; }

/* ── Textarea ── */
textarea {
    background: #09090c !important; color: #e4e4e7 !important;
    border: 1px solid #27272a !important; border-radius: 12px !important;
    font-size: 0.875rem !important; font-family: inherit !important;
    line-height: 1.6 !important; resize: vertical !important;
    transition: border 0.15s, box-shadow 0.15s !important;
    padding: 0.7rem 0.9rem !important;
}
textarea::placeholder { color: #3f3f46 !important; }
textarea:focus {
    border-color: rgba(59,130,246,0.5) !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.12) !important; outline: none !important;
}

/* ── Buttons ── */
button[kind="primaryFormSubmit"] {
    background: linear-gradient(135deg,#1d4ed8,#2563eb) !important;
    border: none !important; border-radius: 12px !important;
    font-weight: 600 !important; font-size: 0.875rem !important;
    color: #fff !important; letter-spacing: 0.2px !important;
    box-shadow: 0 2px 16px rgba(37,99,235,0.45) !important;
    transition: all 0.15s ease !important; height: 2.75rem !important;
}
button[kind="primaryFormSubmit"]:hover {
    background: linear-gradient(135deg,#1e40af,#1d4ed8) !important;
    box-shadow: 0 4px 24px rgba(37,99,235,0.55) !important;
    transform: translateY(-1px) !important;
}
button[kind="secondaryFormSubmit"] {
    background: #18181b !important; border: 1px solid #27272a !important;
    color: #52525b !important; border-radius: 12px !important;
    font-size: 0.85rem !important; height: 2.75rem !important;
    transition: all 0.15s !important;
}
button[kind="secondaryFormSubmit"]:hover {
    background: #27272a !important; color: #71717a !important;
    border-color: #3f3f46 !important;
}

/* ── Alerts ── */
[data-testid="stAlert"] {
    background: #1c1917 !important; border: 1px solid #292524 !important;
    border-radius: 10px !important; font-size: 0.82rem !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 3px; height: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #27272a; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #3f3f46; }

/* ── Native chat_message container — strip default styling ── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}
[data-testid="stChatMessage"] [data-testid="stChatMessageAvatarAssistant"],
[data-testid="stChatMessage"] [data-testid="stChatMessageAvatarUser"] {
    display: none !important;
}
[data-testid="stChatMessageContent"] {
    background: #111114 !important;
    border: 1px solid #1e1e24 !important;
    border-radius: 18px !important;
    border-bottom-left-radius: 5px !important;
    padding: 0.75rem 1.05rem !important;
    color: #d4d4d8 !important;
    font-size: 0.875rem !important;
    line-height: 1.75 !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.5) !important;
    max-width: 78% !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def load_env() -> tuple[str, str, str]:
    load_dotenv()
    api_key    = os.getenv("WATSONX_API_KEY",    "").strip()
    project_id = os.getenv("WATSONX_PROJECT_ID", "").strip()
    url        = os.getenv("WATSONX_URL",        "").strip()
    missing = [n for n, v in [
        ("WATSONX_API_KEY", api_key),
        ("WATSONX_PROJECT_ID", project_id),
        ("WATSONX_URL", url),
    ] if not v]
    if missing:
        raise EnvironmentError(
            f"Missing required environment variable(s): {', '.join(missing)}. "
            "Copy .env.example to .env and fill in your values."
        )
    return api_key, project_id, url


def build_prompt(level: str, user_text: str) -> str:
    return f"{level}: {user_text}"


def _make_model(api_key: str, project_id: str, url: str) -> ModelInference:
    return ModelInference(
        model_id=MODEL_ID,
        credentials=Credentials(url=url, api_key=api_key),
        project_id=project_id,
        params={GenParams.MAX_NEW_TOKENS: MAX_TOKENS, GenParams.TEMPERATURE: TEMPERATURE},
    )


def stream_watsonx(prompt: str, api_key: str, project_id: str, url: str):
    model = _make_model(api_key, project_id, url)
    for chunk in model.generate_text_stream(
        prompt=f"{SYSTEM_MESSAGE}\n\n{prompt}", raw_response=True
    ):
        token = (chunk.get("results") or [{}])[0].get("generated_text", "")
        if token:
            yield token


def get_token_counts(api_key: str, project_id: str, url: str, prompt: str) -> dict:
    model  = _make_model(api_key, project_id, url)
    result = model.generate(prompt=f"{SYSTEM_MESSAGE}\n\n{prompt}")["results"][0]
    return {
        "input":  result.get("input_token_count",    "n/a"),
        "output": result.get("generated_token_count", "n/a"),
    }


def user_bubble_html(content: str, level: str) -> str:
    ls = LEVEL_STYLE.get(level, {})
    badge = (
        f'<div class="badge" style="background:{ls["bg"]};'
        f'border:1px solid {ls["border"]};color:{ls["text"]}">{level}</div>'
    ) if ls else ""
    safe = content.replace("<", "&lt;").replace(">", "&gt;")
    return (
        f'<div class="brow user">'
        f'<div class="av user">🧑</div>'
        f'<div class="bgroup">{badge}'
        f'<div class="bubble user">{safe}</div>'
        f'</div></div>'
    )


def bot_bubble_html(content: str, tok: dict | None) -> str:
    safe = content.replace("<", "&lt;").replace(">", "&gt;")
    tok_html = ""
    if tok:
        inp = tok.get("input", "n/a")
        out = tok.get("output", "n/a")
        tot = inp + out if isinstance(inp, int) and isinstance(out, int) else "n/a"
        tok_html = (
            f'<div class="tok-row">'
            f'<div class="tok-card blue">'
            f'  <div class="tok-lbl">Input tokens</div><div class="tok-val">{inp}</div>'
            f'</div>'
            f'<div class="tok-card purple">'
            f'  <div class="tok-lbl">Output tokens</div><div class="tok-val">{out}</div>'
            f'</div>'
            f'<div class="tok-card cyan">'
            f'  <div class="tok-lbl">Total tokens</div><div class="tok-val">{tot}</div>'
            f'</div>'
            f'</div>'
        )
    return (
        f'<div class="brow bot">'
        f'<div class="av bot">🤖</div>'
        f'<div class="bgroup">'
        f'<div class="bubble bot">{safe}</div>'
        f'{tok_html}</div></div>'
    )


# ─────────────────────────────────────────────────────────────────────────────
# Session state
# ─────────────────────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "total_in"  not in st.session_state:
    st.session_state.total_in  = 0
if "total_out" not in st.session_state:
    st.session_state.total_out = 0

n_turns  = sum(1 for m in st.session_state.messages if m["role"] == "user")
total_in  = st.session_state.total_in
total_out = st.session_state.total_out

# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sb-logo">
      <div class="sb-logo-icon">📚</div>
      <div>
        <div class="sb-logo-text">Course Simplifier</div>
        <div class="sb-logo-sub">IBM watsonx.ai</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sb-section">
      <div class="sb-section-title">Model</div>
      <div class="sb-row"><span class="sb-key">Name</span>
        <span class="sb-val blue">granite-4-h-small</span></div>
      <div class="sb-row"><span class="sb-key">Provider</span>
        <span class="sb-val">IBM watsonx.ai</span></div>
      <div class="sb-row"><span class="sb-key">Temperature</span>
        <span class="sb-val purple">0.1</span></div>
      <div class="sb-row"><span class="sb-key">Max tokens</span>
        <span class="sb-val">1 000</span></div>
    </div>
    <hr class="sb-divider">
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="sb-section">
      <div class="sb-section-title">Session</div>
      <div class="sb-stat-card">
        <div class="sb-stat-num">{n_turns}</div>
        <div class="sb-stat-lbl">Turns this session</div>
      </div>
      <div class="sb-stat-card">
        <div class="sb-stat-num">{total_in + total_out}</div>
        <div class="sb-stat-lbl">Total tokens used</div>
      </div>
    </div>
    <hr class="sb-divider">
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sb-section">
      <div class="sb-section-title">Levels</div>
      <div class="sb-row">
        <span class="sb-key" style="color:#4ade80!important">● Beginner</span>
        <span class="sb-val" style="font-size:0.65rem">Simple, examples</span>
      </div>
      <div class="sb-row">
        <span class="sb-key" style="color:#fbbf24!important">● Intermediate</span>
        <span class="sb-val" style="font-size:0.65rem">Clear + terms</span>
      </div>
      <div class="sb-row">
        <span class="sb-key" style="color:#f87171!important">● Expert</span>
        <span class="sb-val" style="font-size:0.65rem">Concise, precise</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Hero
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-left">
    <div class="hero-title">
      Course Content <span class="accent">Simplification</span>
      <span class="accent2"> Agent</span>
    </div>
    <div class="hero-sub">
      <span class="hero-dot"></span>
      IBM watsonx.ai &nbsp;·&nbsp; ibm/granite-4-h-small &nbsp;·&nbsp; IBM Granite Foundation Model
    </div>
  </div>
  <div class="hero-right">
    <div class="hero-pill">✦ Powered by IBM Granite</div>
    <div class="hero-meta">temp 0.1 &nbsp;·&nbsp; max 1 000 tokens &nbsp;·&nbsp; streaming</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Input panel  (rendered FIRST so form values are captured before chat logic)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="input-wrap"><div class="glass-card">', unsafe_allow_html=True)

with st.form("simplify_form", clear_on_submit=True, border=False):
    level = st.radio(
        "Simplification level", options=LEVELS, index=0,
        horizontal=True, label_visibility="visible",
    )
    user_input = st.text_area(
        "content", height=120,
        placeholder="Paste your course content here… (e.g. 'A neural network is a system that…')",
        label_visibility="collapsed",
    )
    c1, c2 = st.columns([5, 1])
    submitted = c1.form_submit_button("✦  Simplify", type="primary", use_container_width=True)
    cleared   = c2.form_submit_button("🗑  Clear", use_container_width=True)

st.markdown('</div></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Actions — run immediately after form so state updates before chat renders
# ─────────────────────────────────────────────────────────────────────────────
if cleared:
    st.session_state.messages  = []
    st.session_state.total_in  = 0
    st.session_state.total_out = 0
    st.rerun()

if submitted:
    if not user_input.strip():
        st.warning("Please paste some course content before clicking Simplify.")
        st.stop()

    try:
        api_key, project_id, url = load_env()
    except EnvironmentError as exc:
        st.error(str(exc))
        st.stop()

    prompt = build_prompt(level, user_input.strip())

    # Save user message immediately
    st.session_state.messages.append(
        {"role": "user", "content": user_input.strip(), "level": level, "tokens": None}
    )

    # Stream and save assistant message
    with st.chat_message("assistant"):
        try:
            response_text = st.write_stream(stream_watsonx(prompt, api_key, project_id, url))
        except Exception as exc:  # noqa: BLE001
            st.error(f"watsonx.ai API error: {exc}")
            st.stop()

        try:
            tok = get_token_counts(api_key, project_id, url, prompt)
        except Exception:  # noqa: BLE001
            tok = {"input": "n/a", "output": "n/a"}

        inp = tok.get("input", "n/a")
        out = tok.get("output", "n/a")
        tot = inp + out if isinstance(inp, int) and isinstance(out, int) else "n/a"
        st.markdown(
            f'<div class="tok-row">'
            f'<div class="tok-card blue"><div class="tok-lbl">Input tokens</div><div class="tok-val">{inp}</div></div>'
            f'<div class="tok-card purple"><div class="tok-lbl">Output tokens</div><div class="tok-val">{out}</div></div>'
            f'<div class="tok-card cyan"><div class="tok-lbl">Total tokens</div><div class="tok-val">{tot}</div></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    if isinstance(inp, int):
        st.session_state.total_in  += inp
    if isinstance(out, int):
        st.session_state.total_out += out

    st.session_state.messages.append(
        {"role": "assistant", "content": response_text, "level": "", "tokens": tok}
    )
    st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# Chat history  (rendered AFTER actions so it always shows the latest state)
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.messages:
    for msg in st.session_state.messages:
        ls = LEVEL_STYLE.get(msg.get("level", ""), {})
        if msg["role"] == "user":
            badge = (
                f'<span class="badge" style="background:{ls["bg"]};border:1px solid {ls["border"]};color:{ls["text"]}">'
                f'{msg["level"]}</span>' if ls else ""
            )
            safe = msg["content"].replace("<", "&lt;").replace(">", "&gt;")
            st.markdown(
                f'<div class="brow user">'
                f'<div class="av user">🧑</div>'
                f'<div class="bgroup">{badge}'
                f'<div class="bubble user">{safe}</div>'
                f'</div></div>',
                unsafe_allow_html=True,
            )
        else:
            tok = msg.get("tokens") or {}
            inp = tok.get("input", "n/a")
            out = tok.get("output", "n/a")
            tot = inp + out if isinstance(inp, int) and isinstance(out, int) else "n/a"
            safe = msg["content"].replace("<", "&lt;").replace(">", "&gt;")
            tok_html = (
                f'<div class="tok-row">'
                f'<div class="tok-card blue"><div class="tok-lbl">Input tokens</div><div class="tok-val">{inp}</div></div>'
                f'<div class="tok-card purple"><div class="tok-lbl">Output tokens</div><div class="tok-val">{out}</div></div>'
                f'<div class="tok-card cyan"><div class="tok-lbl">Total tokens</div><div class="tok-val">{tot}</div></div>'
                f'</div>'
            ) if tok else ""
            st.markdown(
                f'<div class="brow bot">'
                f'<div class="av bot">🤖</div>'
                f'<div class="bgroup">'
                f'<div class="bubble bot">{safe}</div>'
                f'{tok_html}</div></div>',
                unsafe_allow_html=True,
            )
