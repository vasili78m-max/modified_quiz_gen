import streamlit as st
import fitz   # PyMuPDF
import nltk
import os

# Download NLTK tokenizer
nltk.download("punkt")
from nltk.tokenize import sent_tokenize

# Questgen Imports
from Questgen import main
qg = main.QGen()

# ------------------ PAGE CONFIG ------------------ #
st.set_page_config(page_title="AI Concept-Based Quiz Generator", layout="wide")

st.markdown("""
    <h1 style='text-align:center; color:#6a5acd;'>AI Concept-Based Quiz Generator</h1>
    <p style='text-align:center; color:#ccccff;'>Upload any PDF and the AI will generate meaningful conceptual MCQs.</p>
""", unsafe_allow_html=True)


# ------------------ PDF TEXT EXTRACTOR ------------------ #
def extract_text_from_pdf(file):
    text = ""
    try:
        with fitz.open(stream=file.read(), filetype="pdf") as pdf:
            for page in pdf:
                text += page.get_text("text") + "\n"
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
    return text


# ------------------ QUESTGEN MCQ GENERATOR ------------------ #
def generate_concept_mcqs(text, num_questions=5):
    try:
        payload = {"input_text": text}
        response = qg.mcq(payload)

        if "questions" not in response:
            return []

        all_q = response["questions"]
        all_q = all_q[:num_questions]  # limit the number

        formatted_mcqs = []
        for item in all_q:
            question = item.get("question")
            options = item.get("options")
            answer = item.get("answer")

            if question and options and answer:
                formatted_mcqs.append((question, options, answer))

        return formatted_mcqs

    except Exception as e:
        st.error(f"Questgen generation error: {e}")
        return []


# ------------------ FILE UPLOAD SECTION ------------------ #
uploaded_file = st.file_uploader("Upload your study PDF", type=["pdf"])

if uploaded_file is not None:
    text = extract_text_from_pdf(uploaded_file)

    if not text.strip():
        st.error("No readable text found in this PDF.")
    else:
        st.success("PDF processed successfully!")

        num_questions = st.number_input(
            "How many MCQs do you want?",
            min_value=1,
            max_value=20,
            value=5
        )

        if st.button("Generate Quiz"):
            with st.spinner("Generating conceptual questions..."):
                mcqs = generate_concept_mcqs(text, num_questions)

            if not mcqs:
                st.warning("Could not generate MCQs. Try using a more descriptive PDF.")
            else:
                st.session_state["quiz"] = mcqs
                st.session_state["answers"] = {}


# ------------------ QUIZ DISPLAY SECTION ------------------ #
if "quiz" in st.session_state:

    st.markdown("<h2 style='color:#b9b9ff;'>Your Concept-Based Quiz</h2>", unsafe_allow_html=True)

    for i, (question, options, correct) in enumerate(st.session_state["quiz"], start=1):
        selected = st.radio(
            f"**Q{i}. {question}**",
            options,
            key=f"q{i}",
            index=None
        )
        st.session_state["answers"][i] = {
            "selected": selected,
            "correct": correct
        }

    if st.button("Submit Answers"):
        score = 0
        total = len(st.session_state["answers"])

        for i, data in st.session_state["answers"].items():
            if data["selected"] == data["correct"]:
                score += 1

        st.success(f"Your final score: **{score}/{total}**")

        st.info("Concept-Based Quiz Generated Using Questgen-AI + NLTK + Streamlit")

        del st.session_state["quiz"]  # Clear quiz after submission
