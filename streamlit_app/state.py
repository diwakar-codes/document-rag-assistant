import streamlit as st

DEFAULT_SETTINGS = {
    "retrieval_mode": "dense",
    "top_k": 5,
    "similarity_threshold": 0.10,
    "temperature": 0.2,
    "max_tokens": 1024,
}


def init_session_state():
    if "settings" not in st.session_state:
        st.session_state.settings = dict(DEFAULT_SETTINGS)

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    if "selected_topic" not in st.session_state:
        st.session_state.selected_topic = None

    if "current_quiz" not in st.session_state:
        st.session_state.current_quiz = None

    if "quiz_answers" not in st.session_state:
        st.session_state.quiz_answers = {}

    if "quiz_result" not in st.session_state:
        st.session_state.quiz_result = None

    if "flashcards" not in st.session_state:
        st.session_state.flashcards = None

    if "flashcard_index" not in st.session_state:
        st.session_state.flashcard_index = 0

    if "flashcard_flipped" not in st.session_state:
        st.session_state.flashcard_flipped = False

    if "preview_data" not in st.session_state:
        st.session_state.preview_data = None
