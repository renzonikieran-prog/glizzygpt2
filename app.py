import streamlit as st
import ollama

# --- THEME DEFINITIONS ---
THEMES = {
    "Classic Glizzy 🌭": {
        "primary": "#FF4B4B", "bg": "#FFFFFF", "text": "#31333F", 
        "sidebar": "#F0F2F6", "icon": "🌭", "system": "You are Glizzy GPT, a hotdog-themed AI."
    },
    "Spicy Mustard 🍯": {
        "primary": "#FFCC00", "bg": "#FFF9E6", "text": "#5C4033", 
        "sidebar": "#FFE066", "icon": "🍯", "system": "You are a spicy, witty hotdog assistant."
    },
    "Halloween Horror 🎃": {
        "primary": "#FF7518", "bg": "#1A1A1A", "text": "#FFFFFF", 
        "sidebar": "#333333", "icon": "👻", "system": "You are a spooky 'Ghost Glizzy' for Halloween."
    },
    "Christmas Cheer 🎄": {
        "primary": "#D42426", "bg": "#F8F9F8", "text": "#165B33", 
        "sidebar": "#E5F2E5", "icon": "🎁", "system": "You are a festive holiday Glizzy."
    }
}

# --- SIDEBAR THEME SELECTOR ---
with st.sidebar:
    st.title("Settings")
    selected_theme_name = st.selectbox("Choose Theme", list(THEMES.keys()))
    theme = THEMES[selected_theme_name]
    st.markdown(f"**Current Icon:** {theme['icon']}")

# --- APPLY CUSTOM CSS ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {theme['bg']}; color: {theme['text']}; }}
    [data-testid="stSidebar"] {{ background-color: {theme['sidebar']}; }}
    .stButton>button {{ background-color: {theme['primary']}; color: white; border-radius: 20px; }}
    </style>
    """, unsafe_allow_html=True)

st.title(f"{theme['icon']} Glizzy GPT")
st.caption(f"The world's most processed intelligence. Running on {selected_theme_name}")

# --- AI LOGIC ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask Glizzy GPT..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar=theme['icon']):
        # We inject the identity into the call here
        full_system_prompt = f"{theme['system']} Always answer with a pun or hotdog reference."
        
        response = ollama.chat(
            model='qwen3:0.6b', 
            messages=[{"role": "system", "content": full_system_prompt}] + st.session_state.messages,
            stream=True
        )
        
        full_response = ""
        placeholder = st.empty()
        for chunk in response:
            full_response += chunk['message']['content']
            placeholder.markdown(full_response + "▌")
        placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})