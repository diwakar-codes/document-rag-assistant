import streamlit as st

import api_client

st.title("Flashcards")
st.caption("Generate flashcards from a topic and review them.")

try:
    topics = api_client.list_topics()
except api_client.APIError as exc:
    st.error(f"Could not load topics: {exc}")
    st.stop()

if not topics:
    st.info("No topics yet. Upload documents first — topics are assigned automatically.")
    st.stop()

topic_names = [entry["topic"] for entry in topics]
default_index = (
    topic_names.index(st.session_state.selected_topic)
    if st.session_state.selected_topic in topic_names
    else 0
)

col1, col2 = st.columns([3, 1])
topic = col1.selectbox("Topic", topic_names, index=default_index)
num_cards = col2.slider("Number of cards", 5, 20, 10)

if st.button("Generate Flashcards", type="primary"):
    with st.spinner("Generating flashcards..."):
        try:
            deck = api_client.generate_flashcards(
                {"topic": topic, "num_cards": num_cards}
            )
        except api_client.APIError as exc:
            st.error(f"Could not generate flashcards: {exc}")
        else:
            st.session_state.flashcards = deck["flashcards"]
            st.session_state.flashcard_index = 0
            st.session_state.flashcard_flipped = False

deck = st.session_state.flashcards

if deck:
    st.divider()
    index = st.session_state.flashcard_index
    card = deck[index]

    st.caption(f"Card {index + 1} of {len(deck)}")

    with st.container(border=True):
        if st.session_state.flashcard_flipped:
            st.markdown(f"### {card['back']}")
        else:
            st.markdown(f"### {card['front']}")

    nav_cols = st.columns(3)

    if nav_cols[0].button("Previous", disabled=index == 0):
        st.session_state.flashcard_index -= 1
        st.session_state.flashcard_flipped = False
        st.rerun()

    if nav_cols[1].button("Flip"):
        st.session_state.flashcard_flipped = not st.session_state.flashcard_flipped
        st.rerun()

    if nav_cols[2].button("Next", disabled=index == len(deck) - 1):
        st.session_state.flashcard_index += 1
        st.session_state.flashcard_flipped = False
        st.rerun()
