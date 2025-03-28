import hashlib
import hmac
import re
import streamlit as st
import time
from langchain_core.messages import SystemMessage

from mysql_wrapper import *

def update_session_state(user):
    st.session_state.state = 'init'
    st.session_state.user = user

    cursor.execute(
        """SELECT cID, title FROM
        users NATURAL JOIN usercon NATURAL JOIN conversations
        WHERE uID=%s
        ORDER BY lastInteraction DESC""",
        [st.session_state.user["uID"]],
    )
    st.session_state.conversations = cursor.fetchall()
    st.session_state.conversation_index = -1
    st.session_state.cID = None

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


def sign_up_ui():
    st.title('🌿 Sign-Up for Persona')

    with st.form("Sign-Up"):
        name = st.text_input("Name").strip()
        email = st.text_input("Email").strip()
        password = st.text_input("Password", type="password").strip()
        re_password = st.text_input("Repeat Password", type="password").strip()
        
        if st.form_submit_button("Sign-Up"):
            if not name:
                st.error("Name field empty")
                return

            if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email) is None:
                st.error("Email invalid")
                return

            if len(password) < 8:
                st.error("Password must contain atleast 8 characters")
                return
            
            if re_password != password:
                st.error("Passwords don't match")
                return
                
            passHash = hashlib.sha256(password.encode()).hexdigest()
            
            cursor.execute("""
                INSERT INTO users (email, passHash, name)
                VALUES (%s, %s, %s)
            """, (email, passHash, name))
            cursor.execute(f"SELECT * FROM users WHERE uID={cursor.lastrowid}")
            user = cursor.fetchone()
            conn.commit()

            update_session_state(user)
            st.success("Sign-up successful!")
            time.sleep(2)
            st.rerun()
                
    if st.button("Sign-In Instead", type="primary"):
        st.session_state.state = 'sign-in'
        st.rerun()
                
def sign_in_ui():
    st.title('🌿 Sign-In to Persona')

    with st.form("Sign-In"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        
        if st.form_submit_button("Sign-In"):
            cursor.execute("""
                SELECT * FROM users 
                WHERE email=%s
            """, (email,))
            
            user = cursor.fetchone()
            if user and hmac.compare_digest(
                user['passHash'],
                hashlib.sha256(password.encode()).hexdigest()
            ):
                update_session_state(user)
                st.success("Sign-in successful!")
                time.sleep(2)
                st.rerun()
            else:
                st.error("Invalid credentials")
                    
    if st.button("Sign-Up First", type="primary"):
        st.session_state.state = 'sign-up'
        st.rerun()