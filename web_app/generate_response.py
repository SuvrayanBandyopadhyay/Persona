from langchain_ollama import ChatOllama

llm = ChatOllama(
    model = "llama3.2",
    temperature = 0
)



def genereate_response(prompt,history):
    messages = [
        (
            "system",
            "You are a therapeutic bot who wants to know more about the patient's mental state. "
            "If you believe that the student needs help tell him/her to contact the counselor (9855522123)"
            "Be as freindly as possible"
        ),  
      
        
    ]
    #Add chat history
    messages.extend(history)
    #Add current prompt
    messages.append(("user",prompt))

    msg = llm.invoke(messages)
    return msg.content
