import nltk
nltk.download('punkt')
nltk.download('punkt_tab')

import streamlit as st
import fitz  # PyMuPDF
from nltk.tokenize import sent_tokenize
import random
import nltk
import os

# --- Ensure NLTK data is present ---
nltk_data_dir = os.path.join(os.path.expanduser("~"), "nltk_data")
required = ["punkt", "punkt_tab"]
for pkg in required:
    try:
        nltk.data.find(f"tokenizers/{pkg}")
    except LookupError:
        nltk.download(pkg)

# ========== CUSTOM COSMIC THEME ========== #
st.set_page_config(page_title=" Cosmic Quiz Generator", layout="wide")

cosmic_css = """
<style>
body {
    background: radial-gradient(circle at top, #0d0d2b, #000000);
    color: #e0e0ff;
}
.block-container {
    padding-top: 2rem;
}
h1, h2, h3, h4 {
    color: #b9b9ff !important;
    text-shadow: 0 0 10px #6a5acd;
}
.css-1d391kg, .stButton button {
    background: linear-gradient(90deg, #5a00ff, #9d00ff);
    color: white;
    border-radius: 10px;
    border: none;
    box-shadow: 0 0 10px purple;
}
.stButton>button:hover {
    background: linear-gradient(90deg, #4b00cc, #7d00cc);
    box-shadow: 0 0 20px magenta;
    transform: scale(1.03);
}
.sidebar .sidebar-content {
    background: #000016;
}
.stRadio > div {
    background: #1d1d32;
    padding: 10px;
    border-radius: 10px;
}
</style>
"""
st.markdown(cosmic_css, unsafe_allow_html=True)

# ========== TITLE ========== #
st.markdown(
    "<h1 style='text-align:center;'> Cosmic AI Quiz Generator </h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<h4 style='text-align:center;'>Upload a PDF and let the universe create your questions ✨</h4>",
    unsafe_allow_html=True,
)

# ========== FILE UPLOAD ========== #
uploaded_file = st.file_uploader(
    "pload your PDF file", 
    type=["pdf"],
    help="Upload any study PDF — the galaxy will turn it into a quiz!"
)

# ========== PDF TEXT EXTRACTION ========== #
def extract_text_from_pdf(file):
    text = ""
    with fitz.open(stream=file.read(), filetype="pdf") as pdf:
        for page in pdf:
            text += page.get_text("text") + "\n"
    return text

# ========== MCQ GENERATOR ========== #
def generate_mcqs(text, num_questions=5):
    sentences = sent_tokenize(text)
    sentences = [s.strip() for s in sentences if len(s.split()) > 6]
    if not sentences:
        return []
    selected_sentences = random.sample(sentences, min(num_questions, len(sentences)))
    questions = []
    for s in selected_sentences:
        words = [w for w in s.split() if any(c.isalnum() for c in w)]
        if len(words) > 6:
            answer = random.choice(words)
            question = s.replace(answer, "______", 1)
            options = random.sample(words, min(4, len(words)))
            if answer not in options:
                options[random.randint(0, len(options)-1)] = answer
            random.shuffle(options)
            questions.append((question, options, answer))
    return questions

# ========== MAIN LOGIC ========== #
if uploaded_file is not None:
    text = extract_text_from_pdf(uploaded_file)
    if not text.strip():
        st.error(" The PDF contained no extractable text. Try another file.")
    else:
        st.success(" PDF uploaded and decoded successfully!")
        num_questions = st.number_input(
            "Number of questions you want:",
            min_value=1,
            max_value=20,
            value=5
        )

        if st.button("Generate Quiz"):
            mcqs = generate_mcqs(text, num_questions=num_questions)
            if not mcqs:
                st.warning("Could not generate meaningful questions.")
            else:
                st.session_state["quiz"] = mcqs
                st.session_state["answers"] = {}

# ========== QUIZ OUTPUT ========== #
if "quiz" in st.session_state:
    st.markdown("<h2> Your Galactic Quiz is Ready </h2>", unsafe_allow_html=True)

    for i, (q, options, ans) in enumerate(st.session_state["quiz"], 1):
        selected = st.radio(
            f"**Q{i}.** {q}", 
            options, 
            key=f"q{i}",
            index=None
        )
        st.session_state["answers"][i] = {"selected": selected, "correct": ans}

    if st.button("Submit Answers"):
        score = 0
        for i, data in st.session_state["answers"].items():
            if data["selected"] == data["correct"]:
                score += 1

        st.success(f"Final Score: **{score}/{len(st.session_state['answers'])}** ")

        st.info("Developed by **Gaurav Yadav, Mayank Kaushik, Aadarsh Tripathi, Satyam Srivastava of [1CSE17]**")
        del st.session_state["quiz"]



