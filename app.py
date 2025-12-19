import streamlit as st
from groq import Groq
from gtts import gTTS
import time
import os
import json
import uuid

# --- 1. SET PAGE CONFIG ---
st.set_page_config(page_title="GLIZZYGPT 2.0", page_icon="🌭", layout="wide")

# --- 2. UNIQUE USER IDENTIFICATION ---
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

# --- 3. BOOTUP SYSTEM ---
if "booted" not in st.session_state:
    placeholder = st.empty()
    boot_logs = [
        "Initializing GLIZZY_OS v2.0.8...",
        "Patching Audio Drivers... [OK]",
        f"USER_ID: {st.session_state.user_id} DETECTED.",
        "SYSTEM ONLINE. VOLUME 100%."
    ]
    full_log = ""
    for log in boot_logs:
        full_log += f"> {log}\n"
        placeholder.markdown(f"""
        <div style="background-color: #000; color: #39FF14; font-family: monospace; padding: 30px; height: 100vh;">
            <h1 style="text-align:center;">🌭</h1>
            <pre>{full_log}</pre>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(0.2)
    placeholder.empty()
    st.session_state.booted = True

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; font-size: 80px;'>🌭</h1>", unsafe_allow_html=True)
    st.title("GLIZZYGPT 2.0")
    
    dark_mode = st.toggle("🌙 Dark Mode", value=True)
    
    with st.expander("🎨 Appearance & Themes", expanded=True):
        custom_color = st.color_picker("Choose Your Theme Color", "#FF9933")
        bg_opacity = st.slider("Pattern Visibility", 0.0, 1.0, 0.4)
    
    with st.expander("🔊 TTS & Voice Control", expanded=True):
        enable_tts = st.toggle("Enable Voice Output", value=True)
        voice_lang = st.selectbox("Voice Accent", ["en", "en-uk", "en-au", "en-in"])
        voice_speed = st.slider("Speech Speed", 0.5, 1.5, 1.0)
        
        # DEBUG BUTTON
        if st.button("🔊 Test Audio Output"):
            test_tts = gTTS(text="Mustard check, one two, one two.", lang=voice_lang)
            test_tts.save("test.mp3")
            st.audio("test.mp3", autoplay=True)

    st.divider()
    st.markdown("""<style>div.stButton > button:first-child {background-color: #FF9933 !important; color: black !important; font-weight: bold !important; width: 100% !important;}</style>""", unsafe_allow_html=True)
    
    if st.button("+ New Unique Chat"):
        cid = str(uuid.uuid4())[:12]
        user_data["sessions"][cid] = []
        user_data["names"][cid] = "New Relish Chat"
        save_data(user_data)
        st.session_state.current_cid = cid
        st.rerun()

    for cid in reversed(list(user_data["sessions"].keys())):
        if st.button(user_data["names"][cid], key=cid):
            st.session_state.current_cid = cid
            st.rerun()

# --- 5. DYNAMIC CSS ---
main_txt_col = "#FFFFFF" if dark_mode else "#000000"
main_bg_col = "#121212" if dark_mode else custom_color
sidebar_col = "#1E1E1E" if dark_mode else "#F0F2F6"

st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(0,0,0,{1-bg_opacity}), rgba(0,0,0,{1-bg_opacity})), 
                    url("https://www.transparenttextures.com/patterns/food.png");
        background-color: {main_bg_col};
    }}
    .stApp, p, h1, h2, h3, span, label, .stMarkdown {{ color: {main_txt_col} !important; }}
    [data-testid="stSidebar"] {{ background-color: {sidebar_col} !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 6. CHAT LOGIC ---
if "current_cid" in st.session_state:
    cid = st.session_state.current_cid
    messages = user_data["sessions"][cid]
    
    audio_val = st.audio_input("Record your Glizzy command") 

    for m in messages:
        with st.chat_message(m["role"], avatar="🌭" if m["role"]=="assistant" else "👤"):
            st.markdown(m["content"])

    prompt = st.chat_input("Ask GLIZZYGPT 2.0...")
    
    final_prompt = None
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])

    if audio_val and audio_val != st.session_state.last_processed_audio:
        with st.status("Transcribing..."):
            transcription = client.audio.transcriptions.create(
                file=("sample.wav", audio_val.getvalue()),
                model="whisper-large-v3",
                response_format="text"
            )
            final_prompt = transcription
            st.session_state.last_processed_audio = audio_val 
    elif prompt:
        final_prompt = prompt

    if final_prompt:
        if any(q in final_prompt.lower() for q in ["who are you", "what model"]):
            res_text = "I am GLIZZYGPT 2.0! Your sonic, sovereign hotdog intelligence."
        else:
            try:
                stream = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": "You are GLIZZYGPT 2.0."}] + messages + [{"role": "user", "content": final_prompt}],
                    stream=True
                )
                res_text = ""
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        res_text += chunk.choices[0].delta.content
            except Exception as e:
                res_text = f"Error: {e}"

        if not messages:
            user_data["names"][cid] = " ".join(final_prompt.split()[:5])
            
        messages.append({"role": "user", "content": final_prompt})
        messages.append({"role": "assistant", "content": res_text})
        user_data["sessions"][cid] = messages
        save_data(user_data)
        
        # --- IMPROVED TTS TRIGGER ---
        if enable_tts:
            try:
                tts = gTTS(text=res_text, lang=voice_lang, slow=(voice_speed < 1.0))
                # Use a unique filename for each turn to force browser refresh
                audio_file = f"speech_{int(time.time())}.mp3"
                tts.save(audio_file)
                st.audio(audio_file, autoplay=True)
            except Exception as e:
                st.error(f"TTS Error: {e}")
            
        st.rerun()
else:
    st.info("👈 Create a '+ New Unique Chat' to begin.")
