import streamlit as st

import api_client

st.title("Topics")
st.caption("Browse notes by topic and generate a study summary.")

try:
    topics = api_client.list_topics()
except api_client.APIError as exc:
    st.error(f"Could not load topics: {exc}")
    st.stop()

if not topics:
    st.info("No topics yet. Upload documents first — topics are assigned automatically.")
    st.stop()

for entry in topics:
    with st.container(border=True):
        cols = st.columns([3, 1, 2])
        cols[0].markdown(f"**{entry['topic']}**")
        cols[1].caption(f"{entry['chunks']} chunks")
        cols[2].caption(", ".join(entry["documents"]))

st.divider()

topic_names = [entry["topic"] for entry in topics]
selected_topic = st.selectbox("Select a topic", topic_names)

col1, col2 = st.columns(2)

with col1:
    if st.button("Generate Summary", type="primary"):
        with st.spinner("Summarizing..."):
            try:
                summary = api_client.topic_summary(selected_topic)
            except api_client.APIError as exc:
                st.error(f"Could not summarize topic: {exc}")
            else:
                st.markdown(summary["summary"])

with col2:
    if st.button("Study This Topic (go to Chat)"):
        st.session_state.selected_topic = selected_topic
        st.switch_page("views/chat.py")
