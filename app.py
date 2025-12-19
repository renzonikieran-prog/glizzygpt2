import streamlit as st
from groq import Groq
from gtts import gTTS
import time
import os
import json
import uuid

# --- 1. SET PAGE CONFIG ---
st.set_page_config(page_title="GLIZZYGPT 2.0", page_icon="🌭", layout="wide")

# --- 2. UNIQUE USER IDENTIFICATION (Prevents Chaos) ---
# This creates a permanent ID for the browser so every person has a unique app
if "user_id" not in st.session_state:
    if "glizzy_user_id" in st.query_params:
        st.session_state.user_id = st.query_params["glizzy_user_id"]
    else:
        new_id = str(uuid.uuid4())[:8]
        st.session_state.user_id = new_id
        st.query_params["glizzy_user_id"] = new_id

USER_PATH = f"data_{st.session_state.user_id}.json"

def load_data():
    if os.path.exists(USER_PATH):
        with open(USER_PATH, "r") as f: return json.load(f)
    return {"sessions": {}, "names": {}}

def save_data(data):
    with open(USER_PATH, "w") as f: json.dump(data, f)

user_data = load_data()

# --- 3. BOOT SEQUENCE ---
if "booted" not in st.session_state:
    placeholder = st.empty()
    for i in range(8):
        binary = "".join(["10"[j%2] for j in range(20)])
        placeholder.markdown(f"<div style='text-align:center;padding-top:100px;'><h1>🌭</h1><code>GLIZZY_OS_{st.session_state.user_id}: {binary}</code></div>", unsafe_allow_html=True)
        time.sleep(0.1)
    placeholder.empty()
    st.session_state.booted = True

# --- 4. SIDEBAR: THEMES & PERSISTENT MEMORY ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; font-size: 80px;'>🌭</h1>", unsafe_allow_html=True)
    st.caption(f"Sovereign ID: {st.session_state.user_id}")
    
    dark_mode = st.toggle("🌙 Dark Mode", value=True)
    
    # Tool Integrations (Placeholders for uniqueness)
    with st.expander("📬 Glizzy Productivity"):
        st.button("🔗 Link Google Calendar")
        st.button("📧 Link Glizzy Email")

    st.divider()
    
    # HOT DOG BUTTON
    st.markdown("<style>div.stButton > button {background-color: #FF9933 !important; color: black !important; font-weight: bold; width: 100%;}</style>", unsafe_allow_html=True)
    
    if st.button("+ New Unique Chat"):
        cid = str(time.time())
        user_data["sessions"][cid] = []
        user_data["names"][cid] = "New Relish Chat"
        save_data(user_data)
        st.session_state.current_cid = cid

    st.subheader("Memory History")
    for cid in reversed(list(user_data["sessions"].keys())):
        if st.button(user_data["names"][cid], key=cid):
            st.session_state.current_cid = cid

# --- 5. DYNAMIC CSS ---
bg = "#121212" if dark_mode else "#FFCC00"
txt = "#FFFFFF" if dark_mode else "#000000"
side = "#1E1E1E" if dark_mode else "#F0F2F6"

st.markdown(f"<style>.stApp {{background-color: {bg}; color: {txt} !important;}} [data-testid='stSidebar'] {{background-color: {side} !important;}} p, h1, span {{color: {txt} !important;}}</style>", unsafe_allow_html=True)

# --- 6. CHAT LOGIC ---
if "current_cid" in st.session_state:
    cid = st.session_state.current_cid
    messages = user_data["sessions"][cid]
    
    st.title(f"🌭 {user_data['names'][cid]}")

    for m in messages:
        with st.chat_message(m["role"], avatar="🌭" if m["role"]=="assistant" else "👤"):
            st.markdown(m["content"])

    if prompt := st.chat_input("Relish the conversation..."):
        # Identity Check
        if any(q in prompt.lower() for q in ["who are you", "what model"]):
            res_text = "I am GLIZZYGPT 2.0! Your unique, sovereign hotdog intelligence."
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
                res_text = f"Connection Error: {e}"

        if not messages:
            user_data["names"][cid] = " ".join(prompt.split()[:5])
            
        messages.append({"role": "user", "content": prompt})
        messages.append({"role": "assistant", "content": res_text})
        user_data["sessions"][cid] = messages
        save_data(user_data)
        st.rerun()
else:
    st.info("👈 Create a '+ New Unique Chat' to begin your private Glizzy session.")
