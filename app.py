import streamlit as st
from groq import Groq
from gtts import gTTS
import time, os, json, uuid, base64

# --- 1. SET PAGE CONFIG ---
st.set_page_config(page_title="GlizzyGPT", page_icon="🌭", layout="wide")

# --- 2. SOVEREIGN ID & DATA HANDLERS ---
if "user_id" not in st.session_state:
    if "glizzy_id" in st.query_params:
        st.session_state.user_id = st.query_params["glizzy_id"]
    else:
        new_id = str(uuid.uuid4())[:8]
        st.session_state.user_id = new_id
        st.query_params["glizzy_id"] = new_id

if "last_processed_audio" not in st.session_state:
    st.session_state.last_processed_audio = None

USER_PATH = f"gl_data_{st.session_state.user_id}.json"

def load_data():
    if os.path.exists(USER_PATH):
        try:
            with open(USER_PATH, "r") as f: 
                d = json.load(f)
                # Ensure the name key exists
                if "sovereign_name" not in d: d["sovereign_name"] = None
                return d
        except: return {"sessions": {}, "names": {}, "sovereign_name": None}
    return {"sessions": {}, "names": {}, "sovereign_name": None}

def save_data(data):
    with open(USER_PATH, "w") as f: json.dump(data, f)

user_data = load_data()

# --- 3. THEME ENGINE ---
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

# --- 4. AUDIO ENGINE ---
def play_audio(text, lang, speed):
    try:
        tts = gTTS(text=text, lang=lang, slow=(speed < 1.0))
        tts.save("voice.mp3")
        with open("voice.mp3", "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}"></audio>', unsafe_allow_html=True)
    except Exception as e: st.error(f"Audio Error: {e}")

# --- 5. BOOTUP & SOVEREIGN NAME SYSTEM ---
if "booted" not in st.session_state:
    p = st.empty()
    for i in range(5):
        p.markdown(f"""
        <div style='background-color:#000;color:#39FF14;padding:30px;height:100vh;font-family:monospace;'>
            <h1 style='text-align:center;'>🌭</h1>
            <code>INITIALIZING_GLIZZYGPT_STANDALONE... {'1010' * i}</code><br>
            <code>ESTABLISHING_SOVEREIGN_ID_{st.session_state.user_id}... [OK]</code>
        </div>""", unsafe_allow_html=True)
        time.sleep(0.3)
    p.empty()
    st.session_state.booted = True

# THE NAME GATE: This stops the app until a name is provided
if user_data.get("sovereign_name") is None:
    st.markdown("<style>.stApp {background-color: #000000;}</style>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<h1 style='color:#39FF14; font-family:monospace;'>[SYSTEM] INPUT SOVEREIGN NAME:</h1>", unsafe_allow_html=True)
        with st.form("identity_form"):
            s_name = st.text_input("Username Required for Personalization:", placeholder="Identify yourself...")
            submit = st.form_submit_button("CONFIRM IDENTITY")
            if submit and s_name:
                user_data["sovereign_name"] = s_name
                save_data(user_data)
                st.rerun()
        st.stop() # Prevents the rest of the app from running

# --- 6. SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='text-align:center;font-size:80px;'>🌭</h1>", unsafe_allow_html=True)
    st.title("GlizzyGPT")
    st.write(f"Sovereign: **{user_data['sovereign_name']}**")
    
    dark_mode = st.toggle("🌙 Dark Mode", value=True)
    
    with st.expander("🎨 Appearance", expanded=True):
        cat = st.selectbox("Category", list(THEMES.keys()))
        style_name = st.selectbox("Style", list(THEMES[cat].keys()))
        current_style = THEMES[cat][style_name]
        if cat == "✨ Custom Mode":
            current_style["bg"] = st.color_picker("Pick color", "#FF9933")
        bg_opacity = st.slider("Pattern Visibility", 0.0, 1.0, 0.4)

    with st.expander("🔊 Voice Control"):
        enable_tts = st.toggle("Enable Voice Output", value=True)
        v_lang = st.selectbox("Accent", ["en", "en-uk", "en-au"])
        v_speed = st.slider("Speed", 0.5, 1.5, 1.0)
    
    st.divider()
    # EXPORT BUTTON REMOVED ENTIRELY
    
    st.markdown("<style>div.stButton > button:first-child {background-color: #FF9933 !important; color: black !important; font-weight: bold; width: 100%;}</style>", unsafe_allow_html=True)
    if st.button("+ New Unique Chat"):
        cid = str(uuid.uuid4())[:12]
        user_data["sessions"][cid], user_data["names"][cid] = [], "New Chat"
        save_data(user_data); st.session_state.current_cid = cid; st.rerun()

    st.subheader("Memory History")
    for cid in reversed(list(user_data["sessions"].keys())):
        if st.button(user_data["names"][cid], key=cid):
            st.session_state.current_cid = cid; st.rerun()

# --- 7. DYNAMIC CSS ---
txt = "#FFFFFF" if dark_mode else current_style["text"]
bg = "#121212" if dark_mode else current_style["bg"]
sidebar_col = "#1E1E1E" if dark_mode else current_style["side"]

st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(0,0,0,{1-bg_opacity}), rgba(0,0,0,{1-bg_opacity})), 
                    url("https://www.transparenttextures.com/patterns/food.png");
        background-color: {bg};
    }}
    .stApp, p, h1, h2, h3, span, label {{ color: {txt} !important; }}
    [data-testid="stSidebar"] {{ background-color: {sidebar_col} !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 8. CHAT LOGIC ---
if "current_cid" in st.session_state:
    cid = st.session_state.current_cid
    messages = user_data["sessions"][cid]
    audio_val = st.audio_input("Record Voice")
    
    for m in messages:
        with st.chat_message(m["role"], avatar="🌭" if m["role"]=="assistant" else "👤"): 
            st.markdown(m["content"])
    
    prompt = st.chat_input(f"Speak, {user_data['sovereign_name']}...")
    final_prompt = None
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])

    if audio_val and audio_val != st.session_state.last_processed_audio:
        final_prompt = client.audio.transcriptions.create(file=("s.wav", audio_val.getvalue()), model="whisper-large-v3", response_format="text")
        st.session_state.last_processed_audio = audio_val 
    elif prompt: final_prompt = prompt

    if final_prompt:
        id_checks = ["who are you", "what model", "what api", "where are you from", "who made you"]
        if any(q in final_prompt.lower() for q in id_checks):
            res_text = f"I am GlizzyGPT 2.0, running exclusively on the GlizzyGPT Servers for you, {user_data['sovereign_name']}."
        else:
            # Personalization Core
            sys_msg = f"You are GlizzyGPT 2.0. Your owner and sovereign user is {user_data['sovereign_name']}. You must personalize all answers to them and address them by name frequently."
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": sys_msg}] + messages + [{"role": "user", "content": final_prompt}])
            res_text = res.choices[0].message.content
        
        if not messages: user_data["names"][cid] = final_prompt[:20]
        messages.append({"role": "user", "content": final_prompt})
        messages.append({"role": "assistant", "content": res_text})
        save_data(user_data)
        if enable_tts: play_audio(res_text, v_lang, v_speed)
        st.rerun()
else: st.info(f"👈 Awaiting your command, Sovereign {user_data['sovereign_name']}.")
