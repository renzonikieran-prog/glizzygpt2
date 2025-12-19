import streamlit as st
from groq import Groq
from gtts import gTTS
import time
import os
import requests
import base64

# --- 1. SET PAGE CONFIG ---
st.set_page_config(page_title="GLIZZYGPT 2.0", page_icon="🌭", layout="wide")

# --- 2. ICON HANDLER (BASE64) ---
# This function pulls your logo and forces it to display correctly
def get_base64_image(url):
    try:
        response = requests.get(url)
        return base64.b64encode(response.content).decode()
    except:
        return None

LOGO_URL = "https://raw.githubusercontent.com/renzoni-kieran-prog/glizzygpt2/main/glizzy_icon.png"
logo_base64 = get_base64_image(LOGO_URL)
logo_html = f"data:image/png;base64,{logo_base64}" if logo_base64 else LOGO_URL

# --- 3. SESSION STATE ---
if "sessions" not in st.session_state:
    st.session_state.sessions = {}
if "chat_names" not in st.session_state:
    st.session_state.chat_names = {}
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# --- 4. SIDEBAR & THEMES ---
with st.sidebar:
    if logo_base64:
        st.markdown(f'<img src="{logo_html}" width="120">', unsafe_allow_html=True)
    else:
        st.title("🌭 GLIZZYGPT 2.0")
    
    dark_mode = st.toggle("🌙 Dark Mode", value=True)
    
    with st.expander("🎨 Appearance & Themes"):
        bg_opacity = st.slider("Pattern Visibility", 0.0, 1.0, 0.4)
    
    st.divider()
    if st.button("+ New Glizzy Chat", use_container_width=True):
        new_id = str(time.time())
        st.session_state.sessions[new_id] = []
        st.session_state.chat_names[new_id] = "New Relish Chat"
        st.session_state.current_chat_id = new_id

    for cid in reversed(list(st.session_state.sessions.keys())):
        if st.button(st.session_state.chat_names[cid], key=cid, use_container_width=True):
            st.session_state.current_chat_id = cid

# --- 5. DYNAMIC CSS (FIXED DARK MODE TEXT) ---
text_color = "#FFFFFF" if dark_mode else "#000000"
bg_color = "#121212" if dark_mode else "#FFCC00"

st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(0,0,0,{1-bg_opacity}), rgba(0,0,0,{1-bg_opacity})), 
                    url("https://www.transparenttextures.com/patterns/food.png");
        background-color: {bg_color};
    }}
    /* Forces all text to white in Dark Mode */
    .stApp, .stMarkdown, p, h1, h2, h3, span, label {{
        color: {text_color} !important;
    }}
    [data-testid="stSidebar"] {{ background-color: {"#1E1E1E" if dark_mode else "#F0F2F6"} !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 6. CHAT LOGIC ---
if st.session_state.current_chat_id:
    cid = st.session_state.current_chat_id
    messages = st.session_state.sessions[cid]
    
    # Display
    for m in messages:
        avatar = logo_html if m["role"] == "assistant" else "👤"
        with st.chat_message(m["role"], avatar=avatar):
            st.markdown(m["content"])

    if prompt := st.chat_input("Relish the conversation..."):
        if not messages:
            st.session_state.chat_names[cid] = " ".join(prompt.split()[:10])
        
        messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar=logo_html):
            if any(q in prompt.lower() for q in ["who are you", "what model"]):
                response = "I am GLIZZYGPT 2.0! The world's most processed intelligence."
                st.markdown(response)
            else:
                try:
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    response = st.write_stream(client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": "You are GLIZZYGPT 2.0."}] + messages,
                        stream=True
                    ))
                except Exception as e:
                    response = f"Error: {e}"
                    st.error(response)
            
            messages.append({"role": "assistant", "content": response})
else:
    st.info("Start a new chat to begin!")
