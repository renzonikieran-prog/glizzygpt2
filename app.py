import streamlit as st
from groq import Groq
from gtts import gTTS
import time

# --- 1. SET PAGE CONFIG ---
LOGO_URL = "https://raw.githubusercontent.com/renzoni-kieran-prog/glizzygpt2/main/glizzy_icon.png"
st.set_page_config(page_title="GLIZZYGPT 2.0", page_icon=LOGO_URL, layout="wide")

# --- 2. THEMES & UI ---
st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
                    url("https://www.transparenttextures.com/patterns/food.png");
        background-color: #121212;
        color: #FFFFFF;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR & STATUS ---
with st.sidebar:
    st.image(LOGO_URL, width=100)
    st.title("GLIZZYGPT 2.0")
    
    # API CHECKER
    if "GROQ_API_KEY" in st.secrets:
        st.success("✅ Groq Linked")
    else:
        st.error("❌ GROQ_API_KEY Missing in Secrets")
    
    st.divider()
    disable_tts = st.toggle("Silent Mode", value=False)

# --- 4. CHAT LOGIC ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history
for m in st.session_state.messages:
    avatar = LOGO_URL if m["role"] == "assistant" else "👤"
    with st.chat_message(m["role"], avatar=avatar):
        st.markdown(m["content"])

# Input
if prompt := st.chat_input("Relish the convo..."):
    # Identity Check Logic
    id_questions = ["who are you", "what model do you run", "what model are you"]
    if any(q in prompt.lower() for q in id_questions):
        response_text = "I am GLIZZYGPT 2.0! The fastest frankfurter in the cloud."
    else:
        # Standard Groq Call
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "You are GLIZZYGPT 2.0. Use hotdog puns."}] + st.session_state.messages + [{"role": "user", "content": prompt}]
            )
            response_text = completion.choices[0].message.content
        except Exception as e:
            response_text = f"Glizzy Error: {str(e)}"

    # Display & Save
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    st.session_state.messages.append({"role": "assistant", "content": response_text})
    with st.chat_message("assistant", avatar=LOGO_URL):
        st.markdown(response_text)

    # TTS
    if not disable_tts:
        tts = gTTS(text=response_text, lang='en')
        tts.save("voice.mp3")
        st.audio("voice.mp3", autoplay=True)
