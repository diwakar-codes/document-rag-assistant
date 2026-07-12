import streamlit as st

from state import DEFAULT_SETTINGS

st.title("Settings")
st.caption("Tune retrieval and generation parameters used by the Chat page.")

settings = st.session_state.settings

modes = ["dense", "bm25", "hybrid"]
settings["retrieval_mode"] = st.selectbox(
    "Default retrieval mode", modes, index=modes.index(settings["retrieval_mode"]),
)

settings["top_k"] = st.slider("Top K (chunks retrieved)", 1, 20, settings["top_k"])
settings["similarity_threshold"] = st.slider(
    "Similarity threshold (dense/hybrid only)",
    0.0, 1.0, settings["similarity_threshold"], step=0.01,
)
settings["temperature"] = st.slider(
    "Temperature", 0.0, 1.0, settings["temperature"], step=0.05
)
settings["max_tokens"] = st.slider(
    "Max tokens", 128, 4096, settings["max_tokens"], step=64
)

st.session_state.settings = settings

if st.button("Reset to Defaults"):
    st.session_state.settings = dict(DEFAULT_SETTINGS)
    st.rerun()
