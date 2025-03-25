# stack
    - profile gen (TONIGHT)
        - messages -> vecror store
        - retrieve top 5 messages for a give query
    - suicide detection (TONIGHT)
    - proper conversations (TOM MORNING)

    - polish
        - stop gen button (asyncio)

    - demo vids and all that shit

- profile rag
    - profile format
        - each atomic memory is single document (to prevent useless retrieval, which can cause the llm to go off topic)
        - each has 'category' and 'message_id' (maybe even timestamp)
    - ask gpt to create dummy profile
        - assume each section is one doc
        - profile = list of strings (each is one section / doc)
    - get basic queries working
- profile __generation__ rag
    - only include HumanMessage of unanalyzed profile
    - currently don't check for repreating memories
    - citations
- generation of multiple follow ups
- chatbot that can talk about suicide (for alert_and_comfort)
- whatsappp message on alert

# heap

- chatbot
    - features
        - baseline
            - "inquisitive and engaging"
            - "thoughtful and relevant follow-up questions"
        - additional
            - constitutional
            - automated emergency alert
            - jailbreak, halucination resistance
    - techniques
        - few-shot in-context learning
        - fine-tuning
    - tech stack
        - streamlit
        - langchain

- profile
    - profile data structure
        - ???
        - convo pointers and reasoning logs ???
    - chatbot that answers questions about the given profile (profile provided in-context)
    - emulate the user based on profile
