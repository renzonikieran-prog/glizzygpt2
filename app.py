import streamlit as st
from groq import Groq
import time

# --- 1. SET PAGE CONFIG (MUST BE FIRST) ---
st.set_page_config(
    page_title="Glizzy GPT",
    page_icon="glizzy_icon.png", 
    layout="wide"
)

# --- 2. BRANDING & LOGO (SAFE LOAD) ---
try:
    # This is the modern way to add a sidebar logo
    st.logo("glizzy_icon.png", icon_image="glizzy_icon.png")
except Exception:
    # Fallback if st.logo fails or file is missing
    st.sidebar.image("glizzy_icon.png", width=100) if "glizzy_icon.png" else st.sidebar.title("🌭 Glizzy GPT")

# --- 3. BOOT SEQUENCE (Binary & Equations) ---
if "booted" not in st.session_state:
    placeholder = st.empty()
    for i in range(8):
        binary = " ".join([format(i, 'b') for i in range(40)])
        placeholder.markdown(f"**LOADING GLIZZY OS...**\n\n`{binary}`\n\n`E=mc^2 + Mustard = 🌭`")
        time.sleep(0.2)
    placeholder.empty()
    st.session_state.booted = True

# --- 4. CUSTOM STYLING ---
st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("https://www.transparenttextures.com/patterns/food.png");
        background-color: #FF4B4B; /* Glizzy Red */
        background-attachment: fixed;
    }}
    [data-testid="stSidebar"] {{ background-color: #FFCC00; }} /* Mustard Yellow */
    .stChatMessage {{ background-color: rgba(255, 255, 255, 0.9); border-radius: 15px; margin: 5px; }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. SESSION MEMORY MANAGER ---
if "sessions" not in st.session_state:
    st.session_state.sessions = {"Initial Glizzy": []}
if "current_session" not in st.session_state:
    st.session_state.current_session = "Initial Glizzy"

with st.sidebar:
    st.title("🌭 Settings")
    
    # Session Management
    if st.button("+ New Glizzy Memory"):
        new_name = f"Glizzy Chat {len(st.session_state.sessions) + 1}"
        st.session_state.sessions[new_name] = []
        st.session_state.current_session = new_name
    
    st.session_state.current_session = st.selectbox(
        "Chat Memory Devices", 
        options=list(st.session_state.sessions.keys()),
        index=list(st.session_state.sessions.keys()).index(st.session_state.current_session)
    )
    
    st.divider()
    st.info("Glizzy GPT v2.0 - Running on Llama 3")

# --- 6. AI LOGIC ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
current_messages = st.session_state.sessions[st.session_state.current_session]

st.title(f"🌭 {st.session_state.current_session}")

# Display Chat History
for m in current_messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# User Interaction
if prompt := st.chat_input("Relish the conversation..."):
    current_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🌭"):
        placeholder = st.empty()
        full_res = ""
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "You are Glizzy GPT. You are a genius AI that loves hotdogs. You speak in puns."}] + current_messages,
            stream=True
        )
        
        for chunk in completion:
            if chunk.choices[0].delta.content:
                full_res += chunk.choices[0].delta.content
                placeholder.markdown(full_res + "▌")
        
        placeholder.markdown(full_res)
        current_messages.append({"role": "assistant", "content": full_res})
