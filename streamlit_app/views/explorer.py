import streamlit as st

import api_client

st.title("Document Explorer")

try:
    documents = api_client.list_documents()
except api_client.APIError as exc:
    st.error(f"Could not load documents: {exc}")
    st.stop()

if not documents:
    st.info("No documents uploaded yet.")
    st.stop()

filenames = [doc["filename"] for doc in documents]
selected_filename = st.selectbox("Select a document", filenames)
selected_doc = next(doc for doc in documents if doc["filename"] == selected_filename)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Pages", selected_doc["total_pages"])
col2.metric("Chunks", selected_doc["total_chunks"])
col3.metric("Extraction", selected_doc["extraction_method"])
col4.metric("Uploaded", selected_doc["uploaded_at"][:10])

if selected_doc["topics"]:
    st.caption("Topics: " + ", ".join(selected_doc["topics"]))

try:
    detail = api_client.get_document(selected_doc["document_id"])
except api_client.APIError as exc:
    st.error(f"Could not load document detail: {exc}")
    st.stop()

chunks = detail["chunks"]
pages = sorted({chunk["page"] for chunk in chunks})
selected_page = st.selectbox("Page", pages)

page_chunks = [chunk for chunk in chunks if chunk["page"] == selected_page]

for chunk in page_chunks:
    with st.container(border=True):
        caption = f"Chunk {chunk['chunk_id']}"
        if chunk.get("topic"):
            caption += f" — {chunk['topic']}"
        st.caption(caption)
        st.write(chunk["text"])

st.divider()

if st.button("Delete this document"):
    try:
        api_client.delete_document(selected_doc["document_id"])
    except api_client.APIError as exc:
        st.error(f"Delete failed: {exc}")
    else:
        st.success("Document deleted.")
        st.rerun()
