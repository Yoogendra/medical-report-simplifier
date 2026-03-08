import streamlit as st
import requests
import os
import logging

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="Medical Report Simplifier",
    page_icon="🩺",
    layout="wide"
)

st.title("🩺 Medical Report Simplifier")
st.write("Convert complex medical reports into simple, patient-friendly explanations.")

# -------------------- SIDEBAR --------------------
st.sidebar.header("⚙️ Options")

level = "patient"   # Always patient-friendly

conciseness = st.sidebar.radio(
    "Conciseness",
    ["Short", "Medium", "Detailed"],
    index=1
)

output_format = st.sidebar.radio(
    "Output Format",
    ["Summary Only", "Summary + Key Findings", "Full Explanation"],
    index=2
)

st.sidebar.markdown("---")
st.sidebar.subheader("ℹ️ About")
st.sidebar.caption("Medical Report Simplifier")
st.sidebar.caption("Built for patient-friendly explanations.")
st.sidebar.caption("Powered by Gemini 2.5 Flash")

backend_url = os.getenv("BACKEND_URL", "http://127.0.0.1:5000")
simplify_url = f"{backend_url}/simplify"
chat_url = f"{backend_url}/chat_followup"

# -------------------- FILE UPLOAD --------------------
st.write("Upload a new PDF to automatically clear your previous session.")
uploaded_file = st.file_uploader("Upload a medical report (PDF)", type=["pdf"])

# Clear state if file changes
if "last_uploaded_file" not in st.session_state:
    st.session_state["last_uploaded_file"] = None

if uploaded_file is not None and uploaded_file.name != st.session_state["last_uploaded_file"]:
    # New file detected: Clear old report and chat history
    st.session_state["simplified_report"] = None
    st.session_state["chat_history"] = []
    st.session_state["last_uploaded_file"] = uploaded_file.name
    logging.info(f"New session initialized for file: {uploaded_file.name}")

# -------------------- MAIN LOGIC --------------------
if uploaded_file is not None:
    st.success("PDF uploaded successfully!")

    if st.button("Simplify Report"):
        with st.spinner("Processing your medical report..."):

            try:
                # Send request to backend
                files = {"file": uploaded_file}
                payload = {
                    "level": level,
                    "conciseness": conciseness,
                    "format": output_format
                }

                response = requests.post(simplify_url, data=payload, files=files)

                try:
                    data = response.json()
                except ValueError as json_err:
                    logging.error(f"Failed to parse JSON: {json_err}")
                    st.error("Backend sent invalid JSON!")
                    st.code(response.text)
                    st.stop()

                if "error" in data:
                    st.error("Backend Error: " + data["error"])
                    if "trace" in data:
                        st.code(data["trace"])
                    st.stop()

                if "simplified_text" not in data:
                    st.error("Unexpected backend response.")
                    st.write(data)
                    st.stop()

                # Store simplified text in session state
                st.session_state["simplified_report"] = data["simplified_text"]

                # Display simplified text
                st.subheader("📝 Simplified Explanation")
                st.write(data["simplified_text"])

                # Download buttons
                st.download_button(
                    "📄 Download Text Version",
                    data["simplified_text"],
                    file_name="simplified_report.txt"
                )

            except Exception as e:
                st.error("Frontend Error: " + str(e))

# -------------------- CHATBOT SECTION --------------------
if "simplified_report" in st.session_state:

    st.markdown("## 🤖 Chat with Your Medical Assistant")

    # Initialize chat session memory
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # Display past conversation
    for msg in st.session_state["chat_history"]:
        if msg["role"] == "user":
            st.markdown(f"**🧑 You:** {msg['content']}")
        else:
            st.markdown(f"**🤖 AI:** {msg['content']}")

    # Input for new question
    user_input = st.text_input("Ask a follow-up question:")

    if st.button("Send"):
        if user_input.strip():

            # Log user question
            st.session_state["chat_history"].append(
                {"role": "user", "content": user_input}
            )

            # Prepare backend payload
            payload = {
                "question": user_input,
                "simplified_report": st.session_state["simplified_report"],
                "chat_history": "\n".join(
                    [f"{m['role']}: {m['content']}" for m in st.session_state["chat_history"]]
                )
            }

            try:
                chat_response = requests.post(chat_url, data=payload)
                chat_response.raise_for_status()
                answer = chat_response.json().get("answer", "Error retrieving context-aware answer.")
            except Exception as e:
                logging.error(f"Chat Followup Exception: {e}")
                answer = f"Error: Unable to reach the medical assistant backend."

            # Add AI answer
            st.session_state["chat_history"].append(
                {"role": "ai", "content": answer}
            )

            st.rerun()

# -------------------- DEBUG SECTION --------------------
st.markdown("---")
with st.expander("🔍 Debug Information"):
    st.write(st.session_state)
