
import streamlit as st
from PIL import Image

# 1. SET TAB TITLE AND ICON (FAVICON)
st.set_page_config(
    page_title="Glizzy GPT",
    page_icon="glizzy_icon.png", # This uses your uploaded icon
    layout="wide"
)

# 2. ADD LOGO TO SIDEBAR
st.logo("glizzy_icon.png", icon_image="glizzy_icon.png")

# ... rest of your code ...
import streamlit as st
from groq import Groq
import time
import base64
from streamlit_tts import text_to_speech

# --- 1. BOOT SEQUENCE (Binary & Equations) ---
if "booted" not in st.session_state:
    placeholder = st.empty()
    for i in range(10):
        binary_mess = " ".join([format(i, 'b') for i in range(50)])
        placeholder.markdown(f"**LOADING GLIZZY OS...**\n\n`{binary_mess}`\n\n`E=mc^2 + Mustard = 🌭`")
        time.sleep(0.2)
    placeholder.empty()
    st.session_state.booted = True

# --- 2. THEME & BACKGROUND ENGINE ---
# Link to a Glizzy Pattern image or upload your own to GitHub
GLIZZY_BG_URL = "https://www.transparenttextures.com/patterns/food.png" 

st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("{GLIZZY_BG_URL}");
        background-color: #FF4B4B; /* Glizzy Red */
        background-attachment: fixed;
    }}
    [data-testid="stSidebar"] {{ background-color: #FFCC00; }} /* Mustard Yellow */
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION MEMORY (Individual Chat Memory) ---
if "sessions" not in st.session_state:
    st.session_state.sessions = {"Chat 1": []}
if "current_session" not in st.session_state:
    st.session_state.current_session = "Chat 1"

with st.sidebar:
    st.title("🌭 Glizzy Settings")
    
    # Session Manager
    new_chat = st.button("+ New Glizzy Chat")
    if new_chat:
        new_name = f"Chat {len(st.session_state.sessions) + 1}"
        st.session_state.sessions[new_name] = []
        st.session_state.current_session = new_name
    
    st.session_state.current_session = st.selectbox(
        "Select Memory Device", 
        options=list(st.session_state.sessions.keys()),
        index=list(st.session_state.sessions.keys()).index(st.session_state.current_session)
    )

    st.divider()
    use_tts = st.toggle("Enable Voice Output (TTS)")
    use_voice = st.toggle("Enable Voice Input (Mic)")

# --- 4. AI LOGIC ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
messages = st.session_state.sessions[st.session_state.current_session]

st.title(f"🌭 Glizzy GPT: {st.session_state.current_session}")

# Display Chat
for m in messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Voice Input Handling
user_input = None
if use_voice:
    audio_val = st.audio_input("Speak to the Glizzy") # New Streamlit Feature
    if audio_val:
        st.info("Audio recorded! (Note: Speech-to-Text requires an extra API call like Whisper)")

# Standard Text Input
if prompt := st.chat_input("Relish the conversation..."):
    user_input = prompt

if user_input:
    messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="🌭"):
        placeholder = st.empty()
        full_res = ""
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "You are Glizzy GPT. You love hotdogs."}] + messages,
            stream=True
        )
        
        for chunk in completion:
            if chunk.choices[0].delta.content:
                full_res += chunk.choices[0].delta.content
                placeholder.markdown(full_res + "▌")
        
        placeholder.markdown(full_res)
        messages.append({"role": "assistant", "content": full_res})
        
        # Optional TTS
        if use_tts:
            text_to_speech(full_res)

