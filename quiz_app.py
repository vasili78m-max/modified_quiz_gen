import streamlit as st
import fitz  # PyMuPDF
import nltk
from questgen import main
import os

# Ensure NLTK tokenizer
nltk.download("punkt")

# Streamlit UI config
st.set_page_config(page_title="AI Quiz Generator", layout="wide")
st.title("AI Quiz Generator (Powered by QuestgenAI)")
st.write("Upload a PDF to generate high-quality MCQs using NLP models.")

# Upload PDF
uploaded_file = st.file_uploader("Upload your PDF file", type=["pdf"])

# Extract text from PDF
def extract_text_from_pdf(file):
    text = ""
    with fitz.open(stream=file.read(), filetype="pdf") as pdf:
        for page in pdf:
            text += page.get_text("text") + "\n"
    return text.strip()

# Use Questgen to generate MCQs
def generate_mcqs_questgen(text):
    qg = main.QGen()

    payload = {"input_text": text}
    output = qg.predict_mcq(payload)

    return output

# Main logic
if uploaded_file is not None:
    text = extract_text_from_pdf(uploaded_file)

    if not text:
        st.error("The PDF had no extractable text.")
    else:
        st.success("PDF extracted successfully!")

        if st.button("Generate MCQs with QuestgenAI"):
            with st.spinner("Generating questions... This may take 10–20 seconds..."):
                try:
                    mcq_output = generate_mcqs_questgen(text)

                    questions = mcq_output.get("questions", [])
                    if not questions:
                        st.warning("Questgen couldn't generate questions. Try another PDF.")
                    else:
                        st.session_state["quiz"] = questions
                        st.session_state["answers"] = {}

                except Exception as e:
                    st.error(f"Questgen Error: {e}")

# Display Quiz
if "quiz" in st.session_state:
    st.subheader("Generated Quiz")

    for i, q in enumerate(st.session_state["quiz"], 1):
        question = q.get("question")
        options = q.get("options")
        answer = q.get("answer")

        selected = st.radio(f"Q{i}. {question}", options, key=f"q{i}")
        st.session_state["answers"][i] = {"selected": selected, "correct": answer}

    if st.button("Submit"):
        score = 0
        for i, data in st.session_state["answers"].items():
            if data["selected"] == data["correct"]:
                score += 1

        st.success(f"Score: {score}/{len(st.session_state['answers'])}")
        st.info("Created by Gaurav Yadav, Mayank Kaushik, Aadarsh Tripathi, Satyam Srivastava [1CSE17]")

        del st.session_state["quiz"]
