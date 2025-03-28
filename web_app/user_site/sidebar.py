import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage

from mysql_wrapper import *

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

        new_index = st.selectbox(
            "Chats",
            range(len(st.session_state.conversations) + 1),
            index=st.session_state.conversation_index + 1,
            format_func=lambda select_index: "New Chat" if not select_index else st.session_state.conversations[select_index - 1]["title"],
        ) - 1
        if new_index != st.session_state.conversation_index:
            st.session_state.conversation_index = new_index
            st.session_state.messages = st.session_state.messages[:1]

            if new_index < 0:
                st.session_state.state = 'init'
                st.session_state.cID = None
            else:
                st.session_state.state = 'chat'
                st.session_state.cID = st.session_state.conversations[new_index]["cID"]

                cursor.execute(
                    """SELECT content
                    FROM conversations NATURAL JOIN conmess NATURAL JOIN messages
                    WHERE cID=%s
                    ORDER BY mID""",
                    [st.session_state.cID]
                )
                st.session_state.messages += [(AIMessage(content=content_dict["content"]) if i % 2 else HumanMessage(content=content_dict["content"])) for i, content_dict in enumerate(cursor.fetchall())]

            st.rerun()

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