import hashlib
import hmac
import mysql.connector
from mysql.connector import Error
import re
import streamlit as st
import time

def is_email_invalid(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is None

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

            if is_email_invalid(email):
                st.error("Email invalid")
                return

            if len(password) < 8:
                st.error("Password must contain atleast 8 characters")
                return
            
            if re_password != password:
                st.error("Passwords don't match")
                return
                
            passHash = hashlib.sha256(password.encode()).hexdigest()
            
            try:
                conn = mysql.connector.connect(**st.secrets.mysql)
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    INSERT INTO users (email, passHash, name)
                    VALUES (%s, %s, %s)
                """, (email, passHash, name))
                cursor.execute(f"SELECT * FROM users WHERE uID={cursor.lastrowid}")
                result = cursor.fetchone()
                conn.commit()

                st.session_state.state = 'init'
                st.session_state.user = result
                st.success("Sign-up successful!")
                time.sleep(2)
                st.rerun()
                
            except Error as e:
                st.error(f"Sign-up failed: {e}")
            finally:
                cursor.close()
                conn.close()

    if st.button("Sign-In Instead", type="primary"):
        st.session_state.state = 'sign-in'
        st.rerun()
                
def sign_in_ui():
    st.title('🌿 Sign-In to Persona')

    with st.form("Sign-In"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        
        if st.form_submit_button("Sign-In"):
            try:
                conn = mysql.connector.connect(**st.secrets.mysql)
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT * FROM users 
                    WHERE email=%s
                """, (email,))
                
                result = cursor.fetchone()
                if result and hmac.compare_digest(
                    result['passHash'],
                    hashlib.sha256(password.encode()).hexdigest()
                ):
                    st.session_state.state = 'init'
                    st.session_state.user = result
                    
                    query = "SELECT MAX(cID) from conversations"
                    cursor.execute(query)
                    num = 1

                    result = cursor.fetchone()
        
                    if(result is None):
                        num = 1 
                    else:
                        num =result["MAX(cID)"]+1

                    st.session_state.conversationID = num

                    query = "INSERT INTO conversations values (%s,CURRENT_TIMESTAMP())"
                    values = [num]
                    cursor.execute(query,values)
                    conn.commit()

                    query  = "INSERT INTO usercon values (%s,%s)"
                    values = [st.session_state.user["uID"],st.session_state.conversationID]
                    cursor.execute(query,values)
                    conn.commit()

                    st.success("Sign-in successful!")
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("Invalid credentials")
                    
            except Error as e:
                st.error(f"Sign-in error: {e}")
            finally:
                cursor.close()
                conn.close()

    if st.button("Sign-Up First", type="primary"):
        st.session_state.state = 'sign-up'
        st.rerun()