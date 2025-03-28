from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage, HumanMessage
import streamlit as st
import edge_tts
import asyncio
from mysql_wrapper import *

#llm = ChatOllama(model="hf.co/victunes/TherapyBeagle-11B-v2-GGUF:Q2_K",temperature=0.1)
llm = ChatOllama(model="llama3.2", temperature=0.1, streaming=True)

def create_conversation(prompt):
    title_prompt = f"""
    Provide a title for a conversation beginning with:
    {prompt}
    
    The title should be no longer than 16 characters.
    Output only the title, nothing else.
    """
    title = llm.invoke(title_prompt).content.strip()
    if len(title) > 32:
        title = f"{title[:29]}..."
        
    cursor.execute("INSERT INTO conversations (title) VALUES (%s)", [title])
    st.session_state.cID = cursor.lastrowid
    st.session_state.conversation_index = 0
    st.session_state.conversations.insert(0, {"cID": st.session_state.cID, "title": title})

    cursor.execute("INSERT INTO usercon VALUES (%s, %s)", [st.session_state.user["uID"], st.session_state.cID])
    
    conn.commit()

async def generate_speech(text):
    output_file = f"user-tts/{st.session_state.user['uID']}-{st.session_state.cID}.mp3"
    tts = edge_tts.Communicate(text, st.session_state.voice)
    await tts.save(output_file)

def save_chat(role: str, content: str):
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
 
def handle_prompt(prompt):
    if st.session_state.cID is None:
        create_conversation(prompt)
        st.session_state.callbacks.append(lambda: handle_prompt(prompt))
        st.rerun()

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
    save_chat("assistant", full_response)
    asyncio.run(generate_speech(full_response))
    st.rerun()
