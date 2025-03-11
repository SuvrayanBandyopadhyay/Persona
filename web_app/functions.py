from ollama import Client
import streamlit as st

client = Client(host='http://localhost:11434')

def handle_prompt(prompt):
    # Add user message to history
    st.chat_message('user').markdown(prompt)
    st.session_state.messages.append({'role': 'user', 'content': prompt})

    # Generate and stream response
    with st.chat_message('assistant'):
        response_placeholder = st.empty()
        full_response = ''

        history = '\n'.join(
            f'{msg["role"].title()}: {msg["content"]}'
            for msg in st.session_state.messages
        )
        
        for chunk in client.generate(
            # suvraryan pls dont change to 3.1; i dont have enough ram to run it
            model='llama3.2',
            prompt=history + '\nassistant: ',
            stream=True,
            options={'temperature': 0.5}
        ):
            token = chunk.get('response', '')
            full_response += token
            response_placeholder.markdown(full_response + '▌') # Typing indicator

        response_placeholder.markdown(full_response)

    st.session_state.messages.append({'role': 'assistant', 'content': full_response})

    st.session_state.state = 'chat'
    st.rerun()
