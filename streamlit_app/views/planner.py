import streamlit as st

import api_client

st.title("Study Planner")
st.caption(
    "Get a personalized day-by-day study plan across your topics, "
    "prioritizing weak areas identified from your quiz history."
)

try:
    topics = api_client.list_topics()
except api_client.APIError as exc:
    st.error(f"Could not load topics: {exc}")
    st.stop()

if not topics:
    st.info("No topics yet. Upload documents first — topics are assigned automatically.")
    st.stop()

topic_names = [entry["topic"] for entry in topics]
selected_topics = st.multiselect("Topics to include (leave empty for all)", topic_names)
hours_per_day = st.number_input(
    "Hours available per day", min_value=0.5, max_value=12.0, value=2.0, step=0.5
)

if st.button("Generate Plan", type="primary"):
    with st.spinner("Building your study plan..."):
        try:
            plan = api_client.generate_study_plan({
                "topics": selected_topics or None,
                "hours_per_day": hours_per_day,
            })
        except api_client.APIError as exc:
            st.error(f"Could not generate plan: {exc}")
        else:
            st.divider()
            if plan["weak_topics"]:
                st.warning("Weak topics prioritized: " + ", ".join(plan["weak_topics"]))
            st.markdown(plan["plan"])
