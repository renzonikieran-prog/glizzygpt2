import streamlit as st
from groq import Groq
from gtts import gTTS
import time
import os

# --- 1. SET PAGE CONFIG ---
st.set_page_config(page_title="Glizzy GPT Pro", page_icon="🌭", layout="wide")

# --- 2. THEME DEFINITIONS ---
THEMES = {
    "🌭 Gourmet Glizzies": {
        "Classic Mustard": {"bg": "#FFCC00", "text": "#000000", "accent": "#8B4513"},
        "Spicy Sriracha": {"bg": "#FF4B4B", "text": "#FFFFFF", "accent": "#FFFF00"},
        "Neon Relish": {"bg": "#39FF14", "text": "#000000", "accent": "#008000"},
        "Burnt End BBQ": {"bg": "#4E2728", "text": "#FFFFFF", "accent": "#FF6347"}
    },
    "🎄 Holiday Specials": {
        "Glizzy Xmas": {"bg": "#2F5233", "text": "#FFFFFF", "accent": "#D4AF37"},
        "Spooky Sausage": {"bg": "#FF8C00", "text": "#000000", "accent": "#4B0082"},
        "Valentine Frank": {"bg": "#FF69B4", "text": "#FFFFFF", "accent": "#800000"},
        "New Year Sparkle": {"bg": "#000080", "text": "#FFFFFF", "accent": "#C0C0C0"}
    },
    "🎨 Solid Colors": {
        "Midnight Blue": {"bg": "#191970", "text": "#FFFFFF", "accent": "#ADD8E6"},
        "Forest Green": {"bg": "#228B22", "text": "#FFFFFF", "accent": "#98FB98"},
        "Soft Lavender": {"bg": "#E6E6FA", "text": "#000000", "accent": "#9370DB"},
        "Cyberpunk Pink": {"bg": "#FF00FF", "text": "#FFFFFF", "accent": "#00FFFF"}
    }
}

# --- 3. BOOT SEQUENCE ---
if "booted" not in st.session_state:
    placeholder = st.empty()
    for i in range(12):
        hotdogs = "🌭" * (i % 4 + 1)
        binary = "".join(["10"[j%2] for j in range(25)])
        placeholder.markdown(f"""
        <div style="text-align:center; padding-top:100px;">
            <h1 style="font-size:60px;">{hotdogs}</h1>
            <code style="color:#00FF00; background:black; padding:10px;">{binary} LOADING_THEMES...</code>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(0.12)
    placeholder.empty()
    st.session_state.booted = True

# --- 4. SIDEBAR SETTINGS ---
with st.sidebar:
    st.title("🌭 Glizzy Settings")
    
    # Theme Category Selection
    cat = st.selectbox("Theme Category", list(THEMES.keys()))
    theme_name = st.selectbox("Select Style", list(THEMES[cat].keys()))
    current_style = THEMES[cat][theme_name]
    
    st.divider()
    
    # Customization Controls
    with st.expander("🛠️ Fine-Tune Look", expanded=False):
        custom_bg = st.color_picker("Override Background", current_style["bg"])
        bg_opacity = st.slider("Pattern Visibility", 0.0, 1.0, 0.3)
    
    # Audio Settings
    with st.expander("🔊 Audio Settings", expanded=True):
        disable_tts = st.toggle("Silent Mode (No TTS)", value=False)
        voice_speed = st.select_slider("Voice Speed", options=[0.8, 1.0, 1.2], value=1.0)

# --- 5. DYNAMIC CSS ---
st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(255,255,255,{1-bg_opacity}), rgba(255,255,255,{1-bg_opacity})), 
                    url("https://www.transparenttextures.com/patterns/food.png");
        background-color: {custom_bg};
        color: {current_style['text']};
    }}
    .stChatMessage {{ background-color: rgba(255,255,255,0.1); border-radius: 15px; }}
    </style>
    """, unsafe_allow_html=True)

# --- 6. CHAT LOGIC ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Messages
for m in st.session_state.messages:
    with st.chat_message(m["role"], avatar="🌭" if m["role"] == "assistant" else None):
        st.markdown(f"<span style='color:{current_style['text']}'>{m['content']}</span>", unsafe_allow_html=True)

# Audio Input
audio_value = st.audio_input("Speak to the Glizzy")

if prompt := st.chat_input("Relish the moment..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Groq AI Call
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    with st.chat_message("assistant", avatar="🌭"):
        response = st.write_stream(client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "You are Glizzy GPT. Be funny and punny."}] + st.session_state.messages,
            stream=True
        ))
        st.session_state.messages.append({"role": "assistant", "content": response})

    # TTS Logic
    if not disable_tts:
        tts = gTTS(text=response, lang='en', slow=(voice_speed < 1.0))
        tts.save("response.mp3")
        st.audio("response.mp3", autoplay=True)
