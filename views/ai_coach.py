
import streamlit as st

from coach.planner import ask_coach


def render_ai_coach(df):

    st.title("AI Running Coach")

    st.caption(
        "Your personal endurance training assistant"
    )

    if "coach_history" not in st.session_state:
        st.session_state.coach_history = []

    for message in st.session_state.coach_history:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input(
        "Ask your coach about your training..."
    )

    if question:

        st.session_state.coach_history.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):

            with st.spinner("Analyzing your training..."):

                try:
                    answer = ask_coach(df, question)

                    st.markdown(answer)

                    st.session_state.coach_history.append({
                        "role": "assistant",
                        "content": answer
                    })

                except Exception as e:
                    st.error(f"Coach error: {e}")
