import streamlit as st

from state import init_session_state
from style import inject_style

st.set_page_config(
    page_title="AI Study Companion",
    layout="wide",
)

init_session_state()
inject_style()

pages = [
    st.Page("views/dashboard.py", title="Dashboard", default=True),
    st.Page("views/upload.py", title="Upload"),
    st.Page("views/chat.py", title="Chat"),
    st.Page("views/explorer.py", title="Document Explorer"),
    st.Page("views/topics.py", title="Topics"),
    st.Page("views/quiz.py", title="Quiz"),
    st.Page("views/flashcards.py", title="Flashcards"),
    st.Page("views/planner.py", title="Study Planner"),
    st.Page("views/analytics.py", title="Analytics"),
    st.Page("views/settings.py", title="Settings"),
    st.Page("views/about.py", title="About"),
]

navigation = st.navigation(pages)
navigation.run()
