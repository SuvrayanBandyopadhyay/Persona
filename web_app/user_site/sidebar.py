import streamlit as st

def sidebar_ui():
    with st.sidebar:
        st.title('🌿 Persona')
        st.markdown('''
        ## About
        A friendly, interactive AI powered platform curated to assist students' mental well-being
        
        ## Features
        - 😊 Specially curated to address student issues
        - 🔒 Secured chats, which stay private unless you want to share them
        - 🤝 Connect with professionals for a more \'human\' touch
    
        _Made by Team Draco 🐉_
        ''')
        
        if st.session_state.state in ['sign-in', 'sign-up']:
            return
      
        if st.checkbox("🔊 Audio", disabled=(st.session_state.state == "gen"),value=True):
            st.session_state.sound = 1
        else:
            st.session_state.sound = 0
    
        if st.session_state.sound == 1:
            option = st.selectbox(
        "Choose an option:",
        ["en-US-AndrewNeural",
        "en-US-JennyNeural",	
        "en-US-AriaNeural",	
        "en-US-GuyNeural",	
        "en-GB-RyanNeural",
        "en-IN-NeerjaNeural",
        "en-IN-PrabhatNeural"],disabled=st.session_state.state == "gen"    
        )
            st.session_state.voice = option
            st.markdown("Changes will take effect from the next conversation")

        #Mailto
        st.markdown(
        '<a href="mailto:counselor1@iitp.ac.in" style="text-decoration: none; color: black;">'
        '<i><u>Contact Counsellor</u></i>'
        '</a>',
        unsafe_allow_html=True
        )