import streamlit as st

import api_client

st.title("Quiz")
st.caption("Generate a quiz from a topic and test your knowledge.")

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

QUESTION_TYPE_LABELS = {
    "mcq": "MCQ",
    "true_false": "True/False",
    "fill_blank": "Fill in the Blanks",
    "mixed": "Mixed",
}

with st.form("quiz_config"):
    cols = st.columns(3)
    topic = cols[0].selectbox("Topic", topic_names, index=default_index)
    difficulty = cols[1].radio("Difficulty", ["easy", "medium", "hard"], horizontal=True)
    num_questions = cols[2].radio("Questions", [5, 10, 20], horizontal=True)
    question_type = st.radio(
        "Question type",
        list(QUESTION_TYPE_LABELS.keys()),
        horizontal=True,
        format_func=lambda v: QUESTION_TYPE_LABELS[v],
    )
    submitted = st.form_submit_button("Generate Quiz", type="primary")

if submitted:
    with st.spinner("Generating quiz..."):
        try:
            quiz = api_client.generate_quiz({
                "topic": topic,
                "difficulty": difficulty,
                "num_questions": num_questions,
                "question_type": question_type,
            })
        except api_client.APIError as exc:
            st.error(f"Could not generate quiz: {exc}")
        else:
            st.session_state.current_quiz = quiz
            st.session_state.quiz_answers = {}
            st.session_state.quiz_result = None

quiz = st.session_state.current_quiz

if quiz:
    st.divider()
    st.subheader(f"{quiz['topic']} — {quiz['difficulty'].title()}")

    for question in quiz["questions"]:
        qid = question["id"]
        widget_key = f"quiz_q_{quiz['quiz_id']}_{qid}"

        st.markdown(f"**Question {qid}. {question['question']}**")

        if question["type"] == "mcq" and question.get("options"):
            answer = st.radio(
                "Choose one", question["options"],
                key=widget_key, label_visibility="collapsed",
            )
        elif question["type"] == "true_false":
            answer = st.radio(
                "Choose one", question.get("options") or ["True", "False"],
                key=widget_key, label_visibility="collapsed", horizontal=True,
            )
        else:
            answer = st.text_input(
                "Your answer", key=widget_key, label_visibility="collapsed",
            )

        st.session_state.quiz_answers[qid] = answer
        st.divider()

    if st.button("Submit Quiz", type="primary"):
        answers = [
            {"question_id": qid, "answer": answer or ""}
            for qid, answer in st.session_state.quiz_answers.items()
        ]
        with st.spinner("Evaluating..."):
            try:
                result = api_client.evaluate_quiz({
                    "topic": quiz["topic"],
                    "questions": quiz["questions"],
                    "answers": answers,
                })
            except api_client.APIError as exc:
                st.error(f"Could not evaluate quiz: {exc}")
            else:
                st.session_state.quiz_result = result

result = st.session_state.quiz_result

if result:
    st.subheader("Results")
    col1, col2 = st.columns(2)
    col1.metric("Score", f"{result['score']}/{result['total']}")
    col2.metric("Accuracy", f"{result['accuracy']}%")

    for item in result["results"]:
        with st.container(border=True):
            status = "Correct" if item["is_correct"] else "Incorrect"
            st.markdown(f"**Question {item['question_id']}: {status}**")
            st.write(item["question"])
            st.caption(f"Your answer: {item['given_answer'] or '(no answer)'}")

            if not item["is_correct"]:
                st.markdown(f"**Correct answer:** {item['correct_answer']}")
                st.markdown(f"**Explanation:** {item['explanation']}")
                if item.get("reference"):
                    st.caption(f"Reference: {item['reference']}")

    if st.button("Study weak topics again"):
        st.switch_page("views/planner.py")
