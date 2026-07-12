import streamlit as st

import api_client

st.title("About")

try:
    info = api_client.system_info()
except api_client.APIError:
    info = None

st.markdown(
    """
    <div class="app-card">
    <b>AI Study Companion</b> is a retrieval-augmented learning assistant.
    Upload PDFs or images (including scanned or handwritten notes), and it
    extracts, chunks, embeds, and indexes the content to support question
    answering, topic summaries, quizzes, flashcards, and a personalized
    study planner.
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("Tech Stack")
llm_label = info["llm_model"] if info else "Groq"
embedding_label = info["embedding_model"] if info else "Sentence Transformers"
vision_label = info["vision_model"] if info else "Groq Vision"
st.markdown(
    f"""
    - **Backend**: FastAPI
    - **Frontend**: Streamlit
    - **Workflow orchestration**: LangGraph
    - **LLM**: {llm_label}
    - **Vision OCR**: {vision_label}
    - **Vector database**: Pinecone
    - **Embeddings**: {embedding_label}
    - **Retrieval**: Hybrid (dense + BM25)
    """
)

st.subheader("Notes")
st.markdown(
    """
    - This is a portfolio project: there is no user authentication and no
      SQL/NoSQL database. Document and chunk metadata are kept in a local
      JSON file; embeddings live in Pinecone.
    - Everything runs against your own Pinecone index and Groq API key.
    """
)
