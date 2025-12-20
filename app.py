import streamlit as st
from groq import Groq
from gtts import gTTS
import time
import os
import json
import uuid
import base64
import requests  # Handle location lookup

# --- 1. SET PAGE CONFIG ---
st.set_page_config(page_title="GLIZZYGPT 2.0", page_icon="🌭", layout="wide")

# --- 2. LOCALIZATION ENGINE (COUNTRY DETECTION) ---
def get_user_country():
    try:
        # IP-based lookup to find the user's country without GPS
        response = requests.get('https://ipapi.co/json/', timeout=5)
        data = response.json()
        return data.get("country_name", "Unknown")
    except:
        return "Unknown"

if "user_country" not in st.session_state:
    st.session_state.user_country = get_user_country()

# --- 3. SOVEREIGN ID SYSTEM ---
if "user_id" not in st.session_state:
    if "glizzy_id" in st.query_params:
        st.session_state.user_id = st.query_params["glizzy_id"]
    else:
        new_id = str(uuid.uuid4())[:8]
        st.session_state.user_id = new_id
        st.query_params["glizzy_id"] = new_id

if "last_processed_audio" not in st.session_state:
    st.session_state.last_processed_audio = None

USER_PATH = f"glizzy_data_{st.session_state.user_id}.json"

def load_data():
    if os.path.exists(USER_PATH):
        try:
            with open(USER_PATH, "r") as f: return json.load(f)
        except: return {"sessions": {}, "names": {}}
    return {"sessions": {}, "names": {}}

def save_data(data):
    with open(USER_PATH, "w") as f: json.dump(data, f)

user_data = load_data()

# --- 4. THEME ENGINE ---
THEMES = {
    "🌭 Gourmet Glizzies": {
        "Classic Mustard": {"bg": "#FFCC00", "side": "#F0F2F6", "text": "#000000"},
        "Spicy Sriracha": {"bg": "#FF4B4B", "side": "#F5E6E6", "text": "#FFFFFF"},
        "Neon Relish": {"bg": "#39FF14", "side": "#E6F5E6", "text": "#000000"},
    },
    "🎄 Holiday Specials": {
        "Glizzy Xmas": {"bg": "#2F5233", "side": "#E6F0E6", "text": "#FFFFFF"},
        "Spooky Sausage": {"bg": "#FF8C00", "side": "#F5EBE6", "text": "#000000"},
    },
    "🎨 Solid Colors": {
        "Midnight Blue": {"bg": "#191970", "side": "#E6E6F5", "text": "#FFFFFF"},
        "Cyberpunk Pink": {"bg": "#FF00FF", "side": "#F5E6F5", "text": "#FFFFFF"},
    },
    "✨ Custom Mode": {"User Defined": {"bg": "#FFFFFF", "side": "#F0F2F6", "text": "#000000"}}
}

# --- 5. AUDIO ENGINE ---
def play_audio(text, lang, speed):
    try:
        tts = gTTS(text=text, lang=lang, slow=(speed < 1.0))
        tts.save("temp_voice.mp3")
        with open("temp_voice.mp3", "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            md = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
            st.markdown(md, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Audio Error: {e}")

# --- 6. REALISTIC BOOTUP ---
if "booted" not in st.session_state:
    placeholder = st.empty()
    for i in range(5):
        placeholder.markdown(f"<div style='background-color:#000;color:#39FF14;padding:30px;height:100vh;'><h1>🌭</h1><code>BOOTING_GLIZZY_OS_{st.session_state.user_id}... {'1010' * i}</code></div>", unsafe_allow_html=True)
        time.sleep(0.3)
    placeholder.empty()
    st.session_state.booted = True

# --- 7. SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='text-align:center;font-size:80px;'>🌭</h1>", unsafe_allow_html=True)
    st.title("GLIZZYGPT 2.0")
    
    # Visual confirmation of the detected country
    st.success(f"📍 Region: {st.session_state.user_country}")
    
    dark_mode = st.toggle("🌙 Dark Mode", value=True)
    
    with st.expander("🎨 Appearance"):
        cat = st.selectbox("Category", list(THEMES.keys()))
        style = st.selectbox("Style", list(THEMES[cat].keys()))
        current_style = THEMES[cat][style]
        if cat == "✨ Custom Mode":
            current_style["bg"] = st.color_picker("Pick Color", "#FF9933")
        bg_opacity = st.slider("Opacity", 0.0, 1.0, 0.4)
    
    with st.expander("🔊 Voice"):
        enable_tts = st.toggle("TTS On", value=True)
        v_lang = st.selectbox("Accent", ["en", "en-uk", "en-au"])
        v_speed = st.slider("Speed", 0.5, 1.5, 1.0)

    st.divider()
    st.markdown("<style>div.stButton > button:first-child {background-color: #FF9933 !important; color: black !important; font-weight: bold; width: 100%;}</style>", unsafe_allow_html=True)
    if st.button("+ New Unique Chat"):
        cid = str(uuid.uuid4())[:12]
        user_data["sessions"][cid] = []
        user_data["names"][cid] = "New Chat"
        save_data(user_data)
        st.session_state.current_cid = cid
        st.rerun()

    for cid in reversed(list(user_data["sessions"].keys())):
        if st.button(user_data["names"][cid], key=cid):
            st.session_state.current_cid = cid
            st.rerun()

# --- 8. DYNAMIC STYLING ---
txt = "#FFFFFF" if dark_mode else current_style["text"]
bg = "#121212" if dark_mode else current_style["bg"]
st.markdown(f"<style>.stApp {{background-color: {bg}; color: {txt} !important;}} p, h1, span {{color: {txt} !important;}}</style>", unsafe_allow_html=True)

# --- 9. CHAT LOGIC ---
if "current_cid" in st.session_state:
    cid = st.session_state.current_cid
    messages = user_data["sessions"][cid]
    
    audio_val = st.audio_input("Record Voice")

    for m in messages:
        with st.chat_message(m["role"], avatar="🌭" if m["role"]=="assistant" else "👤"):
            st.markdown(m["content"])

    prompt = st.chat_input("Ask GLIZZYGPT...")
    final_prompt = None
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])

    if audio_val and audio_val != st.session_state.last_processed_audio:
        transcription = client.audio.transcriptions.create(file=("s.wav", audio_val.getvalue()), model="whisper-large-v3", response_format="text")
        final_prompt = transcription
        st.session_state.last_processed_audio = audio_val 
    elif prompt:
        final_prompt = prompt

    if final_prompt:
        # THE ADAPTATION BRAIN:
        # This system prompt forces the AI to check the detected country before answering
        system_instruction = (
            f"You are GLIZZYGPT 2.0. The user is in {st.session_state.user_country}. "
            "IMPORTANT: Do not use American defaults. You must provide information relevant to the user's country. "
            "This includes: local emergency numbers (e.g., 999 for UK, 000 for AU), local institutions (e.g., NHS, HMRC), "
            "local spellings (e.g., 'colour', 'realise'), and local measurements (metric vs imperial)."
        )
        
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=[{"role": "system", "content": system_instruction}] + messages + [{"role": "user", "content": final_prompt}]
        )
        res_text = res.choices[0].message.content
        
        if not messages: user_data["names"][cid] = final_prompt[:15]
        messages.append({"role": "user", "content": final_prompt})
        messages.append({"role": "assistant", "content": res_text})
        save_data(user_data)
        
        if enable_tts: play_audio(res_text, v_lang, v_speed)
        st.rerun()
else:
    st.info("👈 Start a chat!")
