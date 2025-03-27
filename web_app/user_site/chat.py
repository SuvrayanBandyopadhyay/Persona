from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage, HumanMessage
import streamlit as st
import edge_tts
import asyncio
import mysql.connector

#llm = ChatOllama(model="hf.co/victunes/TherapyBeagle-11B-v2-GGUF:Q2_K",temperature=0.1)
llm = ChatOllama(model="llama3.2", temperature=0.1, streaming=True)

async def generate_speech(text):
    output_file = f"user-tts/{st.session_state.user['uID']}.mp3"
    tts = edge_tts.Communicate(text, st.session_state.voice)
    await tts.save(output_file)

def save_chat(role: str, content: str):
    conn = mysql.connector.connect(**st.secrets.mysql)
    cursor = conn.cursor() 
    
    if st.session_state.cID is None:
        title = "testing"
        cursor.execute("INSERT INTO conversations (title) VALUES (%s)", [title])
        cursor.execute("INSERT INTO usercon VALUES (%s, %s)", [st.session_state.user["uID"], cursor.lastrowid])

    query = "INSERT INTO messages (role, content) VALUES (%s, %s)"
    values = [role, content]
    cursor.execute(query, values)
    
    query = "INSERT INTO conmess VALUES (%s, %s)"
    values = [st.session_state.cID, cursor.lastrowid]
    cursor.execute(query, values)

    query = "UPDATE conversations SET lastInteraction=CURRENT_TIMESTAMP() WHERE cID=%s"
    values = [st.session_state.cID]
    cursor.execute(query, values)
    conn.commit()
    
    cursor.close()
    conn.close()
 
def handle_prompt(prompt):
    st.chat_message('user').markdown(prompt)
    st.session_state.messages.append(HumanMessage(content=prompt))
    save_chat("user", prompt)
    
    with st.chat_message('assistant'):
        response_placeholder = st.empty()
        full_response = ''
        
        for chunk in llm.stream(st.session_state.messages):
            token = chunk.content
            full_response += token
            response_placeholder.markdown(full_response + '▌')
        
        response_placeholder.markdown(full_response)

    st.session_state.state = 'chat'
    st.session_state.messages.append(AIMessage(content=full_response))
    asyncio.run(generate_speech(full_response))
    save_chat("assistant", full_response)
    st.rerun()