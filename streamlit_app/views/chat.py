import streamlit as st

import api_client

st.title("Chat with Your Notes")
st.caption(
    "Ask questions about your uploaded notes, or scope the conversation to a "
    "document or topic and try tutor-style prompts (e.g. 'explain like I'm a "
    "beginner', 'give me a real-world example')."
)

try:
    documents = api_client.list_documents()
    topics = api_client.list_topics()
except api_client.APIError as exc:
    st.error(f"Could not load documents/topics: {exc}")
    documents, topics = [], []

settings = st.session_state.settings

top_row = st.columns([1.2, 1.2, 1.6])

with top_row[0]:
    modes = ["dense", "bm25", "hybrid"]
    mode = st.radio(
        "Retrieval mode",
        modes,
        index=modes.index(settings["retrieval_mode"]),
        horizontal=True,
    )

with top_row[1]:
    doc_options = ["All documents"] + [doc["filename"] for doc in documents]
    doc_choice = st.selectbox("Document filter", doc_options)

with top_row[2]:
    topic_names = [entry["topic"] for entry in topics]
    topic_options = ["All topics"] + topic_names
    default_index = 0
    if st.session_state.selected_topic in topic_names:
        default_index = topic_options.index(st.session_state.selected_topic)
    topic_choice = st.selectbox("Topic filter", topic_options, index=default_index)

document_id = None
if doc_choice != "All documents":
    match = next((d for d in documents if d["filename"] == doc_choice), None)
    document_id = match["document_id"] if match else None

topic = None if topic_choice == "All topics" else topic_choice
st.session_state.selected_topic = topic

if st.button("Clear Conversation"):
    try:
        api_client.clear_chat()
    except api_client.APIError:
        pass
    st.session_state.chat_messages = []
    st.rerun()

st.divider()


def render_sources(sources):
    if not sources:
        return
    with st.expander("Sources"):
        for source in sources:
            st.markdown(
                f"**{source['label']}: {source['reference']}** "
                f"(similarity {source['score']})"
            )
            st.caption(source["text"][:300])


AVATARS = {"user": "You", "assistant": "AI"}

for message in st.session_state.chat_messages:
    with st.chat_message(message["role"], avatar=AVATARS[message["role"]]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            render_sources(message.get("sources"))

question = st.chat_input("Ask a question about your documents...")

if question:
    st.session_state.chat_messages.append({"role": "user", "content": question})
    with st.chat_message("user", avatar=AVATARS["user"]):
        st.markdown(question)

    payload = {
        "question": question,
        "mode": mode,
        "top_k": settings["top_k"],
        "document_id": document_id,
        "topic": topic,
        "similarity_threshold": settings["similarity_threshold"],
        "temperature": settings["temperature"],
        "max_tokens": settings["max_tokens"],
    }

    with st.chat_message("assistant", avatar=AVATARS["assistant"]):
        with st.spinner("Thinking..."):
            try:
                result = api_client.chat(payload)
            except api_client.APIError as exc:
                st.error(f"Chat failed: {exc}")
                result = None

        if result:
            st.markdown(result["answer"])
            render_sources(result.get("sources"))

            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": result["answer"],
                "sources": result.get("sources", []),
            })
