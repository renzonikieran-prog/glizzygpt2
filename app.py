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

# --- 3. THE FULL COLOR PALETTE (RE-ADDED) ---
THEMES = {
    "🌭 Gourmet Glizzies": {
        "Classic Mustard": {"bg": "#FFCC00", "side_light": "#F0F2F6", "text": "#000000", "is_dark": False},
        "Spicy Sriracha": {"bg": "#FF4B4B", "side_light": "#F5E6E6", "text": "#FFFFFF", "is_dark": True},
        "Neon Relish": {"bg": "#39FF14", "side_light": "#E6F5E6", "text": "#000000", "is_dark": False},
        "BBQ Smoke": {"bg": "#4E2728", "side_light": "#F5EBEB", "text": "#FFFFFF", "is_dark": True},
    },
    "🎄 Holiday Specials": {
        "Glizzy Xmas": {"bg": "#2F5233", "side_light": "#E6F0E6", "text": "#FFFFFF", "is_dark": True},
        "Spooky Sausage": {"bg": "#FF8C00", "side_light": "#F5EBE6", "text": "#000000", "is_dark": False},
        "Valentine Frank": {"bg": "#FF69B4", "side_light": "#F5E6F0", "text": "#FFFFFF", "is_dark": True},
    },
    "🎨 Solid Colors": {
        "Midnight Blue": {"bg": "#191970", "side_light": "#E6E6F5", "text": "#FFFFFF", "is_dark": True},
        "Forest Green": {"bg": "#228B22", "side_light": "#E6F5E6", "text": "#FFFFFF", "is_dark": True},
        "Cyberpunk Pink": {"bg": "#FF00FF", "side_light": "#F5E6F5", "text": "#FFFFFF", "is_dark": True},
    }
}

# --- 4. SIDEBAR: THEMES & MEMORY ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; font-size: 80px;'>🌭</h1>", unsafe_allow_html=True)
    st.title("GLIZZYGPT 2.0")
    
    dark_mode = st.toggle("🌙 Dark Mode", value=True)
    
    with st.expander("🎨 Appearance & Themes", expanded=True):
        cat = st.selectbox("Category", list(THEMES.keys()))
        style_name = st.selectbox("Style", list(THEMES[cat].keys()))
        current_style = THEMES[cat][style_name]
        bg_opacity = st.slider("Pattern Visibility", 0.0, 1.0, 0.4)
    
    st.divider()

    # HOT DOG BUTTON STYLING (Forced Contrast)
    st.markdown("""<style>div.stButton > button:first-child {background-color: #FF9933 !important; color: black !important; font-weight: bold !important; width: 100% !important;}</style>""", unsafe_allow_html=True)
    
    if st.button("+ New Unique Chat"):
        cid = str(time.uuid4())[:12]
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

# --- 5. DYNAMIC LEGIBILITY ENGINE ---
# This ensures text is ALWAYS readable regardless of background color
if dark_mode:
    main_txt_col = "#FFFFFF"
    main_bg_col = "#121212"
    sidebar_col = "#1E1E1E"
else:
    main_txt_col = current_style["text"]
    main_bg_col = current_style["bg"]
    sidebar_col = current_style["side_light"]

st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(0,0,0,{1-bg_opacity}), rgba(0,0,0,{1-bg_opacity})), 
                    url("https://www.transparenttextures.com/patterns/food.png");
        background-color: {main_bg_col};
    }}
    /* Legibility Overrides */
    .stApp, p, h1, h2, h3, span, label, .stMarkdown {{ 
        color: {main_txt_col} !important; 
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5) if not {dark_mode} else none;
    }}
    [data-testid="stSidebar"] {{ background-color: {sidebar_col} !important; }}
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {{ color: {main_txt_col} !important; }}
    
    /* Input Box Legibility */
    .stChatInput textarea {{
        background-color: rgba(255,255,255,0.1) !important;
        color: {main_txt_col} !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 6. CHAT LOGIC ---
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
