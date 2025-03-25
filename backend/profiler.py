import streamlit as st
import mysql.connector
from langchain_ollama import ChatOllama
from langchain_huggingface import HuggingFaceEmbeddings
from chromadb import EphemeralClient, PersistentClient
from uuid import uuid4

conn = mysql.connector.connect(**st.secrets.mysql)
cur = conn.cursor(dictionary=True)

embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

llm = ChatOllama(
    model="llama3.2",
)

persistent_client = PersistentClient()
temp_client = EphemeralClient()

def get_unprofiled_messages(uID, min_words, limit):
    query = """
    select mID, content, time from
    messages natural join conmess natural join conversations natural join usercon natural join users
    where uID=%s and role='user' and not profiled
    and length(content) - length(replace(content, ' ', '')) + 1 >= %s
    order by length(content) desc limit %s
    """
    cur.execute(query, [uID, min_words, limit])
    return cur.fetchall()

def get_new_profile(old_profile, messages):
    old_profile_str = "\n".join(old_profile)
    messages_str = "\n".join(messages)
    prompt = f"""
    You are a summarizer for a therapeutic chatbot system. You will be give user messages, and you must summarize them as best as you can.
    Be succint, and don't repeat yourself.
    Give each point on a separate line.
    Output only the summary, nothing else.
    User info:
    {old_profile_str}
    
    User messages:
    {messages_str}
    """
    
    return [line for line in llm.invoke(prompt).content.split("\n") if line.strip()]

def update_profile(uID):
    message_dicts = get_unprofiled_messages(uID, 5, 10)
    if not message_dicts:
        print("Skipping")
        return

    messages = [message_dict["content"] for message_dict in message_dicts]
    


    old_profile = []

    combined_collection = temp_client.create_collection(
        name='temp',
        metadata={"hnsw:space": "cosine"},
    )
    
    try:
        # May not exist
        old_data = persistent_client.get_collection(f"user_{uID}").get(include=["embeddings", "metadatas", "documents"])

        old_profile = old_data["documents"]
        
        combined_collection.add(
            ids=old_data["ids"],
            embeddings=old_data["embeddings"],
            metadatas=old_data["metadatas"],
        )
    except:
        pass
        
    print(f"old_profile: {len(old_profile)}")
    print(f"messages:    {len(messages)}")

    new_profile = get_new_profile(old_profile, messages)
    print(f"new_profile: {len(messages)}")
    
    combined_collection.add(
        ids=[str(uuid4()) for _ in messages],
        embeddings=embedder.embed_documents(messages),
        metadatas=[{'mID': message_dict['mID'], 'time': str(message_dict['time'])} for message_dict in message_dicts],
    )
    
    new_embeddings = embedder.embed_documents(new_profile)
    citations = combined_collection.query(
        query_embeddings=new_embeddings,
        n_results=1,
        include=["metadatas"],
    )
        
    metadatas=[]
    for metadata in citations["metadatas"]:
        metadatas.append(metadata[0])
        
    try:
        persistent_client.delete_collection(f"user_{uID}")
    except:
        pass
    
    persistent_client.create_collection(
        name=f"user_{uID}",
        metadata={"hnsw:space": "cosine"}
    ).add(
        ids = [str(uuid4()) for _ in new_profile],
        documents=new_profile,
        embeddings=new_embeddings,
        metadatas=metadatas,
    )
    
    temp_client.delete_collection("temp")



    # Mark profiled
    for message_dict in message_dicts:
        cur.execute("update messages set profiled=1 where mID=%s", [message_dict["mID"]])
    conn.commit()
 


if __name__ == "__main__":
    cur.execute("select uID from users")
    results = cur.fetchall()
    for i, uID_dict in enumerate(results):
        print(f"[{i + 1} / {len(results)}]")
        update_profile(uID_dict["uID"])
        print()