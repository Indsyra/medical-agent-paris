import streamlit as st
import requests

API_URL = "https://medical-agent-paris-756908488363.europe-west1.run.app"

CHAT_ENDPOINT = f"{API_URL}/summarize"

EXAMPLE_TEXT = (
    "John Smith, 52 years old. Sudden onset shortness of breath and dizziness "
    "since this morning. History of hypertension, no known allergies. Blood "
    "pressure 150/95, heart rate 110 bpm, oxygen saturation 94%. Urgent chest "
    "X-ray ordered. Aspirin 300mg administered."
)

st.set_page_config(
    page_title="Medical Agent",
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="auto"
)


col_title, col_reset = st.columns([5, 1])
with col_title:
    st.title("Medical Agent")
with col_reset:
    st.write("")
    if st.button("Reset"):
        st.session_state.messages = []
        st.rerun()

st.markdown(
    "Conversational AI agent based on **LangGraph**, "
    "based on consultations to provide SOAP notes."
)

with st.expander("Example Consultation"):
    st.code(EXAMPLE_TEXT, language=None)
    st.caption(
        "Write consultation notes in free text: patient info, symptoms, medical history, vitals, exams ordered, medications given."
    )
    use_example = st.button("Use Example")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

def process_consultation(text: str) -> None:
    st.session_state.messages.append({"role": "user", "content": text})
    with st.chat_message("user"):
        st.write(text)

    with st.chat_message("assistant"):
        assistant_message = "Sorry, something went wrong while contacting the agent."
        with st.spinner("Generating response..."):
            try:
                response = requests.post(
                    CHAT_ENDPOINT,
                    json={"text": text},
                    timeout=30,
                )
            except requests.RequestException as e:
                assistant_message = f"Network error: {e}"
                st.error(f"Error during API request: {e}")
            else:
                if response.status_code == 200:
                    data = response.json()
                    soap_summary = data.get("soap_summary", "No response from the assistant.")
                    verification_ok = data.get("verification_ok", False)
                    badge = "Verified" if verification_ok else "Verification incomplete"
                    assistant_message = f"{soap_summary}\n\nStatus: *{badge}*"
                else:
                    try:
                        detail = response.json().get("detail", "")
                    except ValueError:
                        detail = response.text
                    assistant_message = f"API error {response.status_code}: {detail}."
                    st.error(f"API error {response.status_code}: {detail}.")
        st.session_state.messages.append({"role": "assistant", "content": assistant_message})
        st.write(assistant_message)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("Enter the consultation details...")
if use_example:
    process_consultation(EXAMPLE_TEXT)
elif user_input:
    process_consultation(user_input)
