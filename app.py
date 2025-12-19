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

# --- 3. FUN & REALISTIC BOOTUP SYSTEM ---
if "booted" not in st.session_state:
    placeholder = st.empty()
    boot_phases = [
        {"msg": "LOADING GLIZZY_KERNEL v2.0.5...", "sleep": 0.4},
        {"msg": "MOUNTING /dev/buns/seeded...", "sleep": 0.3},
        {"msg": "INITIALIZING MUSTARD_V_ENGINE...", "sleep": 0.4},
        {"msg": "DECRYPTING MEAT_VALUES...", "sleep": 0.3},
        {"msg": "ERROR: KETCHUP_OVERFLOW_DETECTED (Ignoring...)", "sleep": 0.5},
        {"msg": "CALIBRATING RELISH_NEURAL_NET...", "sleep": 0.4},
        {"msg": "GLIZZY_ID: " + st.session_state.user_id + " VERIFIED.", "sleep": 0.2},
        {"msg": "SYSTEM ONLINE. ENJOY THE BITE.", "sleep": 0.6}
    ]
    
    full_log = ""
    for phase in boot_phases:
        # Generate flying binary and hot dogs for the visual header
        binary_rain = " ".join(["10"[i%2] for i in range(15)])
        flying_glizzies = "🌭 " * (int(time.time()) % 5 + 2)
        
        full_log += f"[SYSTEM]: {phase['msg']}\n"
        
        placeholder.markdown(f"""
        <div style="background-color: #000; color: #39FF14; font-family: 'Courier New', Courier, monospace; padding: 30px; height: 100vh; border: 4px solid #444;">
            <div style="text-align:center; margin-bottom: 20px;">
                <h2 style="color: #FF9933;">{flying_glizzies}</h2>
                <code style="color: #00FF00;">{binary_rain} {binary_rain}</code>
            </div>
            <hr style="border-color: #333;">
            <pre style="white-space: pre-wrap; font-size: 14px;">{full_log}</pre>
            <div style="position: absolute; bottom: 50px; left: 50%; transform: translateX(-50%);">
                <div style="width: 300px; height: 10px; background: #333; border-radius: 5px;">
                    <div style="width: {min((len(full_log)/200)*100, 100)}%; height: 100%; background: #FF9933; border-radius: 5px;"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(phase['sleep'])
    
    placeholder.empty()
    st.session_state.booted = True

# --- 4. THEMES & CUSTOM PALETTE ---
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
    "🎨 Custom Glizzy": {"Custom Mode": {"bg": "#FFFFFF", "side": "#F0F2F6", "text": "#000000"}}
}

# --- 5. SIDEBAR: THEMES, TOOLS & MEMORY ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; font-size: 80px;'>🌭</h1>", unsafe_allow_html=True)
    st.title("GLIZZYGPT 2.0")
    
    dark_mode = st.toggle("🌙 Dark Mode", value=True)
    
    with st.expander("🎨 Appearance & Themes", expanded=True):
        cat = st.selectbox("Category", list(THEMES.keys()))
        style_name = st.selectbox("Style", list(THEMES[cat].keys()))
        current_style = THEMES[cat][style_name]
        
        if cat == "🎨 Custom Glizzy":
            custom_color = st.color_picker("Choose Your Bun Color", "#FF9933")
            current_style["bg"] = custom_color
            
        bg_opacity = st.slider("Pattern Visibility", 0.0, 1.0, 0.4)
    
    with st.expander("📬 Productivity Tools"):
        st.button("📧 Connect Email")
        st.button("🗓️ Connect Calendar")

    st.divider()
    st.markdown("""<style>div.stButton > button:first-child {background-color: #FF9933 !important; color: black !important; font-weight: bold !important; width: 100% !important;}</style>""", unsafe_allow_html=True)
    
    if st.button("+ New Unique Chat"):
        cid = str(uuid.uuid4())[:12]
        user_data["sessions"][cid] = []
        user_data["names"][cid] = "New Relish Chat"
        save_data(user_data)
        st.session_state.current_cid = cid
        st.rerun()

    st.subheader("Memory History")
    for cid in reversed(list(user_data["sessions"].keys())):
        if st.button(user_data["names"][cid], key=cid):
            st.session_state.current_cid = cid
            st.rerun()

# --- 6. DYNAMIC CSS ---
main_txt_col = "#FFFFFF" if dark_mode else current_style["text"]
main_bg_col = "#121212" if dark_mode else current_style["bg"]
sidebar_col = "#1E1E1E" if dark_mode else current_style["side"]

st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(0,0,0,{1-bg_opacity}), rgba(0,0,0,{1-bg_opacity})), 
                    url("https://www.transparenttextures.com/patterns/food.png");
        background-color: {main_bg_col};
    }}
    .stApp, p, h1, h2, h3, span, label, .stMarkdown {{ color: {main_txt_col} !important; }}
    [data-testid="stSidebar"] {{ background-color: {sidebar_col} !important; }}
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {{ color: {main_txt_col} !important; }}
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
else:
    st.info("👈 Create a '+ New Unique Chat' to begin.")
