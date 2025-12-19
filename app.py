import streamlit as st
from groq import Groq
from gtts import gTTS
import time
import os
import requests
import base64

# --- 1. SET PAGE CONFIG ---
st.set_page_config(page_title="GLIZZYGPT 2.0", page_icon="🌭", layout="wide")

# --- 2. ICON HANDLER (BASE64 FORCE-LOAD) ---
def get_base64_image(url):
    try:
        response = requests.get(url, timeout=5)
        return base64.b64encode(response.content).decode()
    except:
        return None

LOGO_URL = "https://raw.githubusercontent.com/renzoni-kieran-prog/glizzygpt2/main/glizzy_icon.png"
logo_base64 = get_base64_image(LOGO_URL)
logo_html = f"data:image/png;base64,{logo_base64}" if logo_base64 else ""

# --- 3. SESSION STATE ---
if "booted" not in st.session_state:
    st.session_state.booted = False
if "sessions" not in st.session_state:
    st.session_state.sessions = {}
if "chat_names" not in st.session_state:
    st.session_state.chat_names = {}
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# --- 4. BOOT SEQUENCE (Restored & Refined) ---
if not st.session_state.booted:
    placeholder = st.empty()
    for i in range(12):
        hotdogs = "🌭 " * (i % 5 + 1)
        binary = "".join(["10"[j%2] for j in range(25)])
        placeholder.markdown(f"""
        <div style="text-align:center; padding-top:100px; background-color:#121212; height:100vh;">
            <h1 style="font-size:60px;">{hotdogs}</h1>
            <code style="color:#00FF00; background:black; padding:10px; font-family:monospace;">
                GLIZZY_OS_v2.0: {binary}<br>CALCULATING_MUSTARD_RATIO...
            </code>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(0.15)
    placeholder.empty()
    st.session_state.booted = True

# --- 5. THEME DEFINITIONS ---
THEMES = {
    "🌭 Gourmet Glizzies": {
        "Classic Mustard": {"bg": "#FFCC00", "sidebar": "#F0F2F6", "text": "#000000"},
        "Spicy Sriracha": {"bg": "#FF4B4B", "sidebar": "#333333", "text": "#FFFFFF"},
        "Neon Relish": {"bg": "#39FF14", "sidebar": "#002200", "text": "#000000"},
    },
    "🎄 Holiday Specials": {
        "Glizzy Xmas": {"bg": "#2F5233", "sidebar": "#1A3300", "text": "#FFFFFF"},
        "Spooky Sausage": {"bg": "#FF8C00", "sidebar": "#111111", "text": "#FFFFFF"},
    }
}

# --- 6. SIDEBAR: STYLING & SETTINGS ---
with st.sidebar:
    if logo_base64:
        st.markdown(f'<div style="text-align:center;"><img src="{logo_html}" width="150"></div>', unsafe_allow_html=True)
    else:
        st.title("🌭 GLIZZYGPT 2.0")

    dark_mode = st.toggle("🌙 Dark Mode", value=True)
    
    with st.expander("🎨 Appearance & Themes"):
        cat = st.selectbox("Category", list(THEMES.keys()))
        style_name = st.selectbox("Style", list(THEMES[cat].keys()))
        current_style = THEMES[cat][style_name]
        bg_opacity = st.slider("Pattern Visibility", 0.0, 1.0, 0.4)
    
    with st.expander("🔊 TTS Customization"):
        disable_tts = st.toggle("Silent Mode", value=False)
        voice_speed = st.slider("Talk Speed", 0.7, 1.5, 1.0)
        voice_lang = st.selectbox("Accent", ["en", "en-uk", "fr", "es"])

    st.divider()

    # --- HOT DOG COLORED NEW CHAT BUTTON ---
    st.markdown("""
        <style>
        div.stButton > button:first-child {
            background-color: #FF9933 !important; /* Hot Dog Orange/Brown */
            color: black !important; /* Black Text */
            border: 2px solid #8B4513 !important;
            font-weight: bold !important;
            height: 3em !important;
            width: 100% !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    if st.button("+ New Glizzy Chat"):
        new_id = str(time.time())
        st.session_state.sessions[new_id] = []
        st.session_state.chat_names[new_id] = "New Relish Chat"
        st.session_state.current_chat_id = new_id

    st.subheader("Memory History")
    for cid in reversed(list(st.session_state.sessions.keys())):
        if st.button(st.session_state.chat_names[cid], key=cid):
            st.session_state.current_chat_id = cid

# --- 7. DYNAMIC CSS (Text Color & Background) ---
text_col = "#FFFFFF" if dark_mode else current_style["text"]
bg_col = "#121212" if dark_mode else current_style["bg"]

st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(0,0,0,{1-bg_opacity}), rgba(0,0,0,{1-bg_opacity})), 
                    url("https://www.transparenttextures.com/patterns/food.png");
        background-color: {bg_col};
    }}
    .stApp, p, h1, h2, h3, span, label {{ color: {text_col} !important; }}
    [data-testid="stSidebar"] {{ background-color: {"#1E1E1E" if dark_mode else current_style["sidebar"]} !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 8. CHAT LOGIC ---
if st.session_state.current_chat_id:
    cid = st.session_state.current_chat_id
    messages = st.session_state.sessions[cid]
    
    for m in messages:
        avatar = logo_html if m["role"] == "assistant" else "👤"
        with st.chat_message(m["role"], avatar=avatar):
            st.markdown(m["content"])

    if prompt := st.chat_input("Relish the conversation..."):
        # Identity Check
        if any(q in prompt.lower() for q in ["who are you", "what model"]):
            response = "I am GLIZZYGPT 2.0! The world's most processed intelligence."
        else:
            try:
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                response = st.write_stream(client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": "You are GLIZZYGPT 2.0."}] + messages + [{"role": "user", "content": prompt}],
                    stream=True
                ))
            except Exception as e:
                response = f"Connection Error: {e}"

        if not messages:
            st.session_state.chat_names[cid] = " ".join(prompt.split()[:8])
            
        messages.append({"role": "user", "content": prompt})
        messages.append({"role": "assistant", "content": response})
        st.rerun() # Refresh to show response and TTS

        if not disable_tts:
            tts = gTTS(text=response, lang=voice_lang, slow=(voice_speed < 1.0))
            tts.save("speech.mp3")
            st.audio("speech.mp3", autoplay=True)
else:
    st.info("👈 Start a new chat to begin.")
