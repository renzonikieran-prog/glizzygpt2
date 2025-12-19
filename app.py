import streamlit as st
from groq import Groq
from gtts import gTTS
import time
import os
import base64

# --- 1. SET PAGE CONFIG ---
st.set_page_config(page_title="Glizzy GPT", page_icon="🌭", layout="wide")

# --- 2. BOOT SEQUENCE (Binary + Flying Hotdogs) ---
if "booted" not in st.session_state:
    placeholder = st.empty()
    # Animation loop
    for i in range(15):
        # Falling hotdogs + binary mess
        hotdogs = "🌭 " * (i % 5 + 1)
        binary = "".join(["10"[j%2] for j in range(30)])
        placeholder.markdown(f"""
        <div style="text-align:center; padding:100px;">
            <h1 style="color:white; font-size:50px;">{hotdogs}</h1>
            <code style="color:#00FF00;">SYSTEM_INITIALIZING: {binary}</code><br>
            <code style="color:#00FF00;">E=mc^2 + Mustard = GLIZZY_OS_v3.0</code>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(0.15)
    placeholder.empty()
    st.session_state.booted = True

# --- 3. SESSION & MEMORY ---
if "sessions" not in st.session_state:
    st.session_state.sessions = {} 
if "chat_names" not in st.session_state:
    st.session_state.chat_names = {}
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# --- 4. SIDEBAR: THEMES & SETTINGS ---
with st.sidebar:
    st.title("🌭 Glizzy GPT Pro")
    
    # Appearance Section
    with st.expander("🎨 Appearance & Themes", expanded=True):
        theme_choice = st.selectbox("Color Palette", ["Classic Mustard", "Spicy Sriracha", "Neon Relish"])
        bg_opacity = st.slider("Background Opacity", 0.0, 1.0, 0.4)
    
    # TTS & Audio Section
    with st.expander("🔊 Audio Settings", expanded=True):
        disable_tts = st.toggle("Disable All TTS (Silent Mode)", value=False)
        voice_speed = st.select_slider("Voice Speed", options=[0.8, 1.0, 1.2, 1.5], value=1.0)
    
    st.divider()
    
    # ChatGPT-style Chat List
    if st.button("+ New Glizzy Chat", use_container_width=True):
        cid = str(time.time())
        st.session_state.sessions[cid] = []
        st.session_state.chat_names[cid] = "New Relish Chat"
        st.session_state.current_chat_id = cid

    st.subheader("Memory History")
    for cid in reversed(list(st.session_state.sessions.keys())):
        if st.button(st.session_state.chat_names[cid], key=cid, use_container_width=True):
            st.session_state.current_chat_id = cid

# --- 5. THEME CSS ---
bg_colors = {"Classic Mustard": "#FFCC00", "Spicy Sriracha": "#FF4B4B", "Neon Relish": "#39FF14"}
main_color = bg_colors[theme_choice]

st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(255,255,255,{1-bg_opacity}), rgba(255,255,255,{1-bg_opacity})), 
                    url("https://www.transparenttextures.com/patterns/food.png");
        background-color: {main_color};
        background-attachment: fixed;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 6. MAIN CHAT INTERFACE ---
if st.session_state.current_chat_id:
    cid = st.session_state.current_chat_id
    messages = st.session_state.sessions[cid]
    
    # Voice Input
    audio_data = st.audio_input("Speak to the Glizzy")

    # Message Display
    for m in messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # Input Logic
    if prompt := st.chat_input("Relish the conversation..."):
        # Dynamic Naming
        if not messages:
            st.session_state.chat_names[cid] = " ".join(prompt.split()[:10]) + "..."
        
        messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # AI Response
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        with st.chat_message("assistant", avatar="🌭"):
            full_res = st.write_stream(client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "You are Glizzy GPT. Use puns."}] + messages,
                stream=True
            ))
            messages.append({"role": "assistant", "content": full_res})

        # Final TTS Call
        if not disable_tts:
            tts = gTTS(text=full_res, lang='en', slow=(voice_speed < 1.0))
            tts.save("speech.mp3")
            st.audio("speech.mp3", autoplay=True)
else:
    st.info("Start a new chat in the sidebar to begin.")
