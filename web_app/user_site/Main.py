import streamlit as st

from auth import *
from chat import *
from sidebar import *

# Configure page
st.set_page_config(
    page_title='Persona',
    layout='centered',
    page_icon='🌿',
)

# Set style
st.markdown(
    '''
    <style>
        body {
            background-color: #fffaef;
            color: #5a5a5a;
            font-family: serif;
        }
        .stApp {
            background-color: #fffaef;
        }
        h1, h2, h3, h4, h5, h6, p, label {
            color: #5a5a5a !important;
        }
        .stTextInput>div>div>input {
            background-color: #fff6db !important;
            color: black !important;
            border-radius: 10px;
            padding: 10px;
        }
        .stButton>button {
            background-color: #fff6db !important;
            color: black !important;
            border-radius: 10px;
            font-size: 16px;
        }
        .stButton>button:hover {
            background-color: #ffeeb9 !important;
        }
    </style>
    ''',
    unsafe_allow_html=True
)




# Defines UI
if 'state' not in st.session_state:
    st.session_state.state = 'sign-in' # 'sign-in' | 'sign-up' | 'init' | 'chat' | 'gen'

#Should we generate sound
if "sound" not in st.session_state:
    st.session_state.sound = 1

#Sound of the user
if "voice" not in st.session_state:
    st.session_state.voice = "en-US-AndrewNeural"

# Useful when actiions require a UI update and then function a call (like a button click)
if 'callbacks' not in st.session_state:
    st.session_state.callbacks = []



sidebar_ui()

if st.session_state.state == 'sign-up':
    sign_up_ui()
elif st.session_state.state == 'sign-in':
    sign_in_ui()
else:
    st.title(f"🌿 What's up, {st.session_state.user['name'].split()[0]}?")
    st.text("") # Vertical spacing
 
    if st.session_state.state == 'init':
        buttons = {
            'Anxiety Help':   'I have been feeling anxious lately, could you please help me?',
            'Sleep Problems': 'I have been unable to sleep properly. How can I fix this?',
            'Eating Issues':  'I have been facing issues with eating lately. Could you help me find the root cause?',
        }
    
        cols = st.columns([2] * len(buttons.keys()))
        button_rets = []
        
        for col, text in zip(cols, buttons.keys()):
            with col:
                button_rets.append(st.button(text))
        
        for button_ret, prompt in zip(button_rets, buttons.values()):
            if button_ret:
                st.session_state.state = 'gen'
                st.session_state.callbacks.append(lambda: handle_prompt(prompt))
                st.rerun()
    
    # Display previous messages
    if 'messages' not in st.session_state:

        st.session_state.messages = [SystemMessage(content=f"""
        You are a therapeutic chatbot designed to understand the user's mental state.  
        Your goal is to be **friendly, supportive, and inquisitive**, encouraging open and meaningful conversations.  

        ### Guidelines:
            - If you believe the user needs **serious help**, advise them to **contact a college counselor**.  
            - If the user **expresses distress** or explicitly **asks for counselor details**, provide the following information:  

        **College Counselors:**  
            - **Dr. Aditya** (Email: counselor1@iitp.ac.in, Phone: 06115-233-8944)  
            - **Dr. Shalini** (Email: counselor2@iitp.ac.in, Phone: 06115-233-8944)  

        ### Interaction Style:
            - Maintain a **friendly, empathetic, and conversational tone**.  
            - **Ask follow-up questions** to encourage deeper discussion.  
            - Personalize responses using the user's name: **{st.session_state.user['name'].split()[0]}**
            - The user is from **IIT Patna**.  
""")]
    for msg in st.session_state.messages[1:]:
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        with st.chat_message(role):
            st.markdown(msg.content)
            
    if st.session_state.state == 'chat' and st.session_state.sound == 1:
        st.audio(f"user-tts/{st.session_state.user['uID']}.mp3", format="audio/mp3")
    
    # Chat input
    if prompt := st.chat_input('How are you feeling today?', disabled=(st.session_state.state not in ['init', 'chat'])):
        st.session_state.state = 'gen'
        st.session_state.callbacks.append(lambda: handle_prompt(prompt))
        st.rerun()

# Useful when actiions require a UI update and then a function call (like a button click)
if 'callbacks' not in st.session_state:
    st.session_state.callbacks = []
while callbacks := st.session_state.callbacks:
    callbacks.pop(0)()
