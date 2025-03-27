import streamlit as st
import mysql.connector
from langchain_core.messages import AIMessage, HumanMessage

def sidebar_ui():
    with st.sidebar:
        st.title('🌿 Persona')
        st.markdown("""
        ## About
        A friendly, interactive AI powered platform curated to assist students' mental well-being
        
        ## Features
        - 😊 Specially curated to address student issues
        - 🔒 Secured chats, shared only with the college mental health counsellors
        - 🤝 Connect with professionals for serious assistance
    
        _Made by Team Draco 🐉_
        """)
        
        if st.session_state.state in ['sign-in', 'sign-up']:
            return
        
        st.divider()

        # UNFINISHED
        st.session_state.cID = st.selectbox(
            "Chats",
            range(len(st.session_state.conversations)),
            index=None,
            format_func=lambda index: st.session_state.conversations[index]["title"],
            placeholder="New Chat",
        )
        
        st.session_state.messages = st.session_state.messages[:1]

        if st.session_state.cID is None:
            st.session_state.state = 'init'
        else:
            st.session_state.state = 'chat'
            conn = mysql.connector.connect(**st.secrets.mysql)
            cursor = conn.cursor()
            
            cursor.execute(
                """SELECT content
                FROM conversations NATURAL JOIN conmess NATURAL JOIN messages
                WHERE cID=%s
                ORDER BY mID""",
                [st.session_state.cID]
            )
            st.session_state.messages += [(AIMessage(content=content) if i % 2 else HumanMessage(content=content)) for i, (content,) in enumerate(cursor.fetchall())]

            cursor.close()
            conn.close()

        st.divider()
      
        if st.checkbox("🔊 Audio", disabled=(st.session_state.state == "gen"),value=True):
            st.session_state.sound = 1
        else:
            st.session_state.sound = 0
    
        if st.session_state.sound == 1:
            option = st.selectbox(
                "Narrator Voice",
                [
                    "en-US-AndrewNeural",
                    "en-US-JennyNeural",	
                    "en-US-AriaNeural",	
                    "en-US-GuyNeural",	
                    "en-GB-RyanNeural",
                    "en-IN-NeerjaNeural",
                    "en-IN-PrabhatNeural",
                ],
                format_func=lambda string: string[6:-6],
                disabled=st.session_state.state == "gen",
            )
            st.session_state.voice = option
            st.markdown("Changes will take effect from the next conversation")

        # Mailto
        st.markdown(
            """<a href="mailto:counselor1@iitp.ac.in" style="text-decoration: none; color: black;">
            <i><u>Contact Counsellor</u></i>
            </a>""",
            unsafe_allow_html=True
        )