import streamlit as st
from groq import Groq
from gtts import gTTS
import time
import os

# --- 1. SET PAGE CONFIG ---
st.set_page_config(page_title="GLIZZYGPT 2.0", page_icon="🌭", layout="wide")

# --- 2. SESSION STATE ---
if "booted" not in st.session_state:
    st.session_state.booted = False
if "sessions" not in st.session_state:
    st.session_state.sessions = {}
if "chat_names" not in st.session_state:
    st.session_state.chat_names = {}
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# --- 3. BOOT SEQUENCE ---
if not st.session_state.booted:
    placeholder = st.empty()
    for i in range(10):
        binary = "".join(["10"[j%2] for j in range(20)])
        placeholder.markdown(f"""
        <div style="text-align:center; padding-top:100px; background-color:#121212; height:100vh;">
            <h1 style="font-size:80px;">🌭 🌭 🌭</h1>
            <code style="color:#00FF00; background:black; padding:10px; font-family:monospace;">
                GLIZZY_OS_v2.0: {binary}<br>WAKING_THE_GLIZZY...
            </code>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(0.1)
    placeholder.empty()
    st.session_state.booted = True

# --- 4. SIDEBAR: EMOJI LOGO & BUTTON STYLING ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; font-size: 100px;'>🌭</h1>", unsafe_allow_html=True)
    st.title("GLIZZYGPT 2.0")

    dark_mode = st.toggle("🌙 Dark Mode", value=True)
    
    with st.expander("🎨 Appearance & Themes"):
        bg_opacity = st.slider("Pattern Visibility", 0.0, 1.0, 0.4)
    
    with st.expander("🔊 TTS Customization"):
        disable_tts = st.toggle("Silent Mode", value=False)
        voice_speed = st.slider("Talk Speed", 0.7, 1.5, 1.0)

    st.divider()

    # --- HOT DOG COLORED BUTTON ---
    st.markdown("""
        <style>
        div.stButton > button:first-child {
            background-color: #FF9933 !important; 
            color: black !important;
            border: 2px solid #8B4513 !important;
            font-weight: bold !important;
            width: 100% !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    if st.button("+ New Glizzy Chat"):
        new_id = str(time.time())
        st.session_state.sessions[new_id] = []
        st.session_state.chat_names[new_id] = "New Relish Chat"
        st.session_state.current_chat_id = new_id

    st.subheader("Memory History")
    for cid in reversed(list(st.session_state.sessions.keys())):
        if st.button(st.session_state.chat_names[cid], key=cid):
            st.session_state.current_chat_id = cid

# --- 5. DYNAMIC CSS (FIXED SIDEBAR COLORS) ---
text_col = "#FFFFFF" if dark_mode else "#000000"
bg_col = "#121212" if dark_mode else "#FFCC00"
# Sidebar: Dark Grey (#1E1E1E) vs Light Grey (#F0F2F6)
side_col = "#1E1E1E" if dark_mode else "#F0F2F6"

st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(0,0,0,{1-bg_opacity}), rgba(0,0,0,{1-bg_opacity})), 
                    url("https://www.transparenttextures.com/patterns/food.png");
        background-color: {bg_col};
    }}
    .stApp, p, h1, h2, h3, span, label {{ color: {text_col} !important; }}
    
    /* Target the Sidebar specifically */
    [data-testid="stSidebar"] {{
        background-color: {side_col} !important;
    }}
    
    /* Ensure sidebar text stays readable */
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] span {{
        color: {text_col} !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 6. CHAT LOGIC ---
if st.session_state.current_chat_id:
    cid = st.session_state.current_chat_id
    messages = st.session_state.sessions[cid]
    
    for m in messages:
        with st.chat_message(m["role"], avatar="🌭" if m["role"]=="assistant" else "👤"):
            st.markdown(m["content"])

    if prompt := st.chat_input("Relish the conversation..."):
        # Identity Check
        if any(q in prompt.lower() for q in ["who are you", "what model"]):
            response_text = "I am GLIZZYGPT 2.0! The world's most processed intelligence."
        else:
            try:
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                stream = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": "You are GLIZZYGPT 2.0."}] + messages + [{"role": "user", "content": prompt}],
                    stream=True
                )
                
                response_text = ""
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        response_text += chunk.choices[0].delta.content
                
            except Exception as e:
                response_text = f"Connection Error: {e}"

        if not messages:
            st.session_state.chat_names[cid] = " ".join(prompt.split()[:8])
            
        messages.append({"role": "user", "content": prompt})
        messages.append({"role": "assistant", "content": response_text})
        
        st.rerun()

        if not disable_tts:
            tts = gTTS(text=response_text, lang='en', slow=(voice_speed < 1.0))
            tts.save("speech.mp3")
            st.audio("speech.mp3", autoplay=True)
else:
    st.info("👈 Start a new chat to begin.")
