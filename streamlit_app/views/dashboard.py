import streamlit as st

import api_client

st.title("AI Study Companion")
st.caption("Upload notes, ask questions, generate quizzes, and track your progress.")

if not api_client.health_check():
    st.error("Backend is unreachable. Make sure the FastAPI server is running.")
    st.stop()

try:
    analytics = api_client.get_analytics()
    info = api_client.system_info()
    documents = api_client.list_documents()
except api_client.APIError as exc:
    st.error(f"Could not load dashboard data: {exc}")
    st.stop()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Documents", analytics["total_documents"])
col2.metric("Chunks", analytics["total_chunks"])
col3.metric("Topics Learned", analytics["topics_learned"])
col4.metric("Quizzes Taken", analytics["quizzes_taken"])
col5.metric("Average Score", f"{analytics['average_score']}%")

st.divider()

left, right = st.columns([2, 1])

with left:
    st.subheader("Uploaded Documents")

    if not documents:
        st.info("No documents uploaded yet. Go to the Upload page to add your notes.")
    else:
        for doc in documents:
            with st.container(border=True):
                cols = st.columns([3, 1, 1, 1])
                cols[0].markdown(f"**{doc['filename']}**")
                cols[1].caption(f"{doc['total_pages']} pages")
                cols[2].caption(f"{doc['total_chunks']} chunks")
                cols[3].caption(doc["extraction_method"])
                if doc["topics"]:
                    st.caption("Topics: " + ", ".join(doc["topics"]))

with right:
    st.subheader("System Information")
    st.markdown(
        f"""
        <div class="app-card">
        <b>LLM</b><br>{info['llm_model']}<br><br>
        <b>Embedding Model</b><br>{info['embedding_model']}<br><br>
        <b>Vector Database</b><br>{info['vector_db']}<br><br>
        <b>Vision OCR Model</b><br>{info['vision_model']}
        </div>
        """,
        unsafe_allow_html=True,
    )
