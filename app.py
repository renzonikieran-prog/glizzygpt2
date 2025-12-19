import streamlit as st
from groq import Groq
from gtts import gTTS
import time
import os

# --- 1. SET PAGE CONFIG (MUST BE FIRST) ---
LOGO_URL = "https://raw.githubusercontent.com/renzoni-kieran-prog/glizzygpt2/main/glizzy_icon.png"
st.set_page_config(page_title="GLIZZYGPT 2.0", page_icon=LOGO_URL, layout="wide")

# --- 2. THEME & PALETTE DEFINITIONS ---
THEMES = {
    "🌭 Gourmet Glizzies": {
        "Classic Mustard": {"bg": "#FFCC00", "sidebar": "#F0F2F6", "text": "#000000"},
        "Spicy Sriracha": {"bg": "#FF4B4B", "sidebar": "#333333", "text": "#FFFFFF"},
        "Neon Relish": {"bg": "#39FF14", "sidebar": "#002200", "text": "#000000"},
    },
    "🎄 Holiday Specials": {
        "Glizzy Xmas": {"bg": "#2F5233", "sidebar": "#1A3300", "text": "#FFFFFF"},
        "Spooky Sausage": {"bg": "#FF8C00", "sidebar": "#111111", "text": "#FFFFFF"},
        "Valentine Frank": {"bg": "#FF69B4", "sidebar": "#4B0000", "text": "#FFFFFF"},
    },
    "🎨 Solid Colors": {
        "Midnight Blue": {"bg": "#191970", "sidebar": "#000033", "text": "#FFFFFF"},
        "Cyberpunk Pink": {"bg": "#FF00FF", "sidebar": "#330033", "text": "#FFFFFF"},
        "Forest Green": {"bg": "#228B22", "sidebar": "#0B2B0B", "text": "#FFFFFF"},
    }
}

# --- 3. SESSION STATE INITIALIZATION ---
if "booted" not in st.session_state:
    st.session_state.booted = False
if "sessions" not in st.session_state:
    st.session_state.sessions = {} # {id: [messages]}
if "chat_names" not in st.session_state:
    st.session_state.chat_names = {} # {id: name}
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# --- 4. BOOT SEQUENCE (Binary + Glizzy Rain) ---
if not st.session_state.booted:
    placeholder = st.empty()
    for i in range(12):
        hotdogs = "🌭 " * (i % 5 + 1)
        binary = "".join(["10"[j%2] for j in range(25)])
        placeholder.markdown(f"""
        <div style="text-align:center; padding-top:100px;">
            <h1 style="font-size:60px;">{hotdogs}</h1>
            <code style="color:#00FF00; background:black; padding:10px;">GLIZZY_OS_v2.0: {binary}</code>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(0.12)
    placeholder.empty()
    st.session_state.booted = True

# --- 5. SIDEBAR: CHATGPT MEMORY & THEMES ---
with st.sidebar:
    st.image(LOGO_URL, width=100)
    st.title("GLIZZYGPT 2.0")

    # --- APPEARANCE SECTION ---
    with st.expander("🎨 Appearance & Themes", expanded=False):
        dark_mode = st.toggle("🌙 Dark Mode", value=True)
        cat = st.selectbox("Theme Category", list(THEMES.keys()))
        style_name = st.selectbox("Style", list(THEMES[cat].keys()))
        current_style = THEMES[cat][style_name]
        bg_opacity = st.slider("Pattern Visibility", 0.0, 1.0, 0.4)

    # --- AUDIO SECTION ---
    with st.expander("🔊 Audio Settings", expanded=False):
        disable_tts = st.toggle("Silent Mode", value=False)
        voice_speed = st.slider("Voice Speed", 0.8, 1.5, 1.0)

    st.divider()

    # --- CHATGPT STYLE SIDEBAR ---
    if st.button("+ New Glizzy Chat", use_container_width=True):
        new_id = str(time.time())
        st.session_state.sessions[new_id] = []
        st.session_state.chat_names[new_id] = "New Relish Chat"
        st.session_state.current_chat_id = new_id

    st.subheader("Chat History")
    for cid in reversed(list(st.session_state.sessions.keys())):
        if st.button(st.session_state.chat_names[cid], key=cid, use_container_width=True):
            st.session_state.current_chat_id = cid

# --- 6. DYNAMIC CSS ---
bg_color = "#121212" if dark_mode else current_style["bg"]
text_color = "#E0E0E0" if dark_mode else current_style["text"]
sidebar_color = "#1E1E1E" if dark_mode else current_style["sidebar"]

st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(0,0,0,{1-bg_opacity}), rgba(0,0,0,{1-bg_opacity})), 
                    url("https://www.transparenttextures.com/patterns/food.png");
        background-color: {bg_color};
        color: {text_color};
    }}
    [data-testid="stSidebar"] {{ background-color: {sidebar_color} !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 7. MAIN CHAT LOGIC ---
if st.session_state.current_chat_id:
    cid = st.session_state.current_chat_id
    messages = st.session_state.sessions[cid]
    
    st.title(f"🌭 {st.session_state.chat_names[cid]}")

    # Voice Input widget
    audio_input = st.audio_input("Speak to the Glizzy")

    # Display Messages
    for m in messages:
        avatar = LOGO_URL if m["role"] == "assistant" else "👤"
        with st.chat_message(m["role"], avatar=avatar):
            st.markdown(m["content"])

    # Input Logic
    if prompt := st.chat_input("Relish the conversation..."):
        # Identity Logic (Hardcoded response)
        id_checks = ["who are you", "what model do you run", "what model are you"]
        
        # Auto-name chat based on first input
        if not messages:
            st.session_state.chat_names[cid] = " ".join(prompt.split()[:10]) + "..."

        messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar=LOGO_URL):
            if any(q in prompt.lower() for q in id_checks):
                response_text = "I am GLIZZYGPT 2.0! The world's most processed intelligence."
                st.markdown(response_text)
            else:
                try:
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    response_text = st.write_stream(client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": "You are GLIZZYGPT 2.0. Use puns."}] + messages,
                        stream=True
                    ))
                except Exception as e:
                    response_text = f"Glizzy Error: {str(e)}"
                    st.error(response_text)
            
            messages.append({"role": "assistant", "content": response_text})

        # TTS Output
        if not disable_tts:
            tts = gTTS(text=response_text, lang='en', slow=(voice_speed < 1.0))
            tts.save("speech.mp3")
            st.audio("speech.mp3", autoplay=True)
else:
    st.info("👈 Click '+ New Glizzy Chat' in the sidebar to start!")
