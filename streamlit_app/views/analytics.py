import streamlit as st

import api_client

st.title("Analytics")
st.caption("Track your study progress across all uploaded documents.")

try:
    analytics = api_client.get_analytics()
    info = api_client.system_info()
except api_client.APIError as exc:
    st.error(f"Could not load analytics: {exc}")
    st.stop()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Documents", analytics["total_documents"])
col2.metric("Chunks", analytics["total_chunks"])
col3.metric("Topics Learned", analytics["topics_learned"])
col4.metric("Quizzes Taken", analytics["quizzes_taken"])
col5.metric("Average Score", f"{analytics['average_score']}%")

st.divider()

st.subheader("Weakest Topics")
if analytics["weak_topics"]:
    for entry in analytics["weak_topics"]:
        st.markdown(f"- **{entry['topic']}** — {entry['accuracy']}% accuracy")
else:
    st.info("Take a quiz to see your weak topics here.")

st.divider()

st.subheader("System Configuration")
st.markdown(
    f"""
    <div class="app-card">
    <b>LLM</b>: {info['llm_model']}<br>
    <b>Embedding Model</b>: {info['embedding_model']}<br>
    <b>Vector Database</b>: {info['vector_db']} ({info['pinecone_index']})<br>
    <b>Vision OCR Model</b>: {info['vision_model']}
    </div>
    """,
    unsafe_allow_html=True,
)
