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

# --- 3. THEME DEFINITIONS ---
THEMES = {
    "🌭 Gourmet Glizzies": {
        "Classic Mustard": {"bg": "#FFCC00", "side_light": "#F0F2F6", "text": "#000000"},
        "Spicy Sriracha": {"bg": "#FF4B4B", "side_light": "#F5E6E6", "text": "#FFFFFF"},
        "Neon Relish": {"bg": "#39FF14", "side_light": "#E6F5E6", "text": "#000000"},
    },
    "🎄 Holiday Specials": {
        "Glizzy Xmas": {"bg": "#2F5233", "side_light": "#E6F0E6", "text": "#FFFFFF"},
        "Spooky Sausage": {"bg": "#FF8C00", "side_light": "#F5EBE6", "text": "#000000"},
    },
    "🎨 Solid Colors": {
        "Midnight Blue": {"bg": "#191970", "side_light": "#E6E6F5", "text": "#FFFFFF"},
        "Forest Green": {"bg": "#228B22", "side_light": "#E6F5E6", "text": "#FFFFFF"},
    }
}

# --- 4. BOOT SEQUENCE (RESTORED) ---
if "booted" not in st.session_state:
    placeholder = st.empty()
    for i in range(10):
        binary = "".join(["10"[j%2] for j in range(20)])
        placeholder.markdown(f"""
        <div style="text-align:center; padding-top:100px; background-color:#121212; height:100vh;">
            <h1 style="font-size:80px;">🌭 🌭 🌭</h1>
            <code style="color:#00FF00; background:black; padding:10px;">GLIZZY_OS_{st.session_state.user_id}: {binary}</code>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(0.1)
    placeholder.empty()
    st.session_state.booted = True

# --- 5. SIDEBAR: THEMES, TOOLS & MEMORY ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; font-size: 80px;'>🌭</h1>", unsafe_allow_html=True)
    st.title("GLIZZYGPT 2.0")
    st.caption(f"ID: {st.session_state.user_id}")

    dark_mode = st.toggle("🌙 Dark Mode", value=True)
    
    with st.expander("🎨 Appearance & Themes", expanded=True):
        cat = st.selectbox("Category", list(THEMES.keys()))
        style_name = st.selectbox("Style", list(THEMES[cat].keys()))
        current_style = THEMES[cat][style_name]
        bg_opacity = st.slider("Pattern Visibility", 0.0, 1.0, 0.4)
    
    with st.expander("🔊 TTS & Voice (RESTORED)"):
        disable_tts = st.toggle("Silent Mode", value=False)
        voice_speed = st.slider("Talk Speed", 0.7, 1.5, 1.0)
    
    with st.expander("📬 Productivity Tools"):
        st.button("📧 Connect Email")
        st.button("🗓️ Connect Calendar")

    st.divider()

    # HOT DOG BUTTON STYLING
    st.markdown("""<style>div.stButton > button:first-child {background-color: #FF9933 !important; color: black !important; font-weight: bold !important; width: 100% !important;}</style>""", unsafe_allow_html=True)
    
    if st.button("+ New Unique Chat"):
        cid = str(time.time())
        user_data["sessions"][cid] = []
        user_data["names"][cid] = "New Relish Chat"
        save_data(user_data)
        st.session_state.current_cid = cid
        st.rerun()

    st.subheader("Chat Memory")
    for cid in reversed(list(user_data["sessions"].keys())):
        if st.button(user_data["names"][cid], key=cid):
            st.session_state.current_cid = cid
            st.rerun()

# --- 6. DYNAMIC CSS ---
text_col = "#FFFFFF" if dark_mode else current_style["text"]
bg_col = "#121212" if dark_mode else current_style["bg"]
side_col = "#1E1E1E" if dark_mode else current_style["side_light"]

st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(0,0,0,{1-bg_opacity}), rgba(0,0,0,{1-bg_opacity})), 
                    url("https://www.transparenttextures.com/patterns/food.png");
        background-color: {bg_col};
    }}
    .stApp, p, h1, h2, h3, span, label {{ color: {text_col} !important; }}
    [data-testid="stSidebar"] {{ background-color: {side_col} !important; }}
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {{ color: {text_col} !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 7. CHAT LOGIC ---
if "current_cid" in st.session_state:
    cid = st.session_state.current_cid
    messages = user_data["sessions"][cid]
    
    for m in messages:
        with st.chat_message(m["role"], avatar="🌭" if m["role"]=="assistant" else "👤"):
            st.markdown(m["content"])

    if prompt := st.chat_input("Ask GLIZZYGPT 2.0..."):
        if any(q in prompt.lower() for q in ["who are you", "what model"]):
            res_text = "I am GLIZZYGPT 2.0! Your private, uniquely-processed intelligence."
        else:
            try:
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                stream = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": "You are GLIZZYGPT 2.0."}] + messages + [{"role": "user", "content": prompt}],
                    stream=True
                )
                res_text = ""
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        res_text += chunk.choices[0].delta.content
            except Exception as e:
                res_text = f"Error: {e}"

        if not messages:
            user_data["names"][cid] = " ".join(prompt.split()[:5])
            
        messages.append({"role": "user", "content": prompt})
        messages.append({"role": "assistant", "content": res_text})
        user_data["sessions"][cid] = messages
        save_data(user_data)
        st.rerun()

        if not disable_tts:
            tts = gTTS(text=res_text, lang='en', slow=(voice_speed < 1.0))
            tts.save("speech.mp3")
            st.audio("speech.mp3", autoplay=True)
else:
    st.info("👈 Create a '+ New Unique Chat' to begin.")
