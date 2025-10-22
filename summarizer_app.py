import streamlit as st
from transformers import pipeline
import PyPDF2
import nltk
from nltk.tokenize import sent_tokenize

# Download NLTK tokenizer
@st.cache_resource
def setup_nltk():
    nltk.download('punkt', quiet=True)

setup_nltk()

# Load summarization pipeline
@st.cache_resource
def load_model():
    return pipeline("summarization")

summarizer = load_model()

# Streamlit UI
st.title("📄 Advanced Text Summarization App")
st.write("Paste text or upload a PDF to summarize and highlight key sentences.")

# Option 1: Text input
input_text = st.text_area("Enter your text here:")

# Option 2: PDF upload
uploaded_file = st.file_uploader("Or upload a PDF file:", type=["pdf"])
if uploaded_file:
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
    input_text = text

# Function to split text into chunks for long documents
def split_text(text, max_words=500):
    sentences = sent_tokenize(text)
    chunks = []
    chunk = ""
    word_count = 0
    for sentence in sentences:
        words = sentence.split()
        if word_count + len(words) > max_words:
            chunks.append(chunk.strip())
            chunk = sentence + " "
            word_count = len(words)
        else:
            chunk += sentence + " "
            word_count += len(words)
    if chunk:
        chunks.append(chunk.strip())
    return chunks

# Function to extract key sentences
def extract_key_sentences(summary_text):
    sentences = sent_tokenize(summary_text)
    return sentences[:3]  # top 3 sentences as key points

# Summarize button
if st.button("Summarize") and input_text:
    try:
        # Split text into chunks if too long
        text_chunks = split_text(input_text, max_words=1000)
        summary_text = ""
        for chunk in text_chunks:
            summary = summarizer(chunk, max_length=150, min_length=50, do_sample=False)
            summary_text += summary[0]['summary_text'] + " "

        st.subheader("Summary:")
        st.write(summary_text)

        st.subheader("Key Sentences / Highlights:")
        key_sentences = extract_key_sentences(summary_text)
        for i, sentence in enumerate(key_sentences, 1):
            st.write(f"{i}. {sentence}")

    except Exception as e:
        st.error(f"Error: {e}")

st.write("---")
st.write("Developed with ❤️ using Python, Hugging Face Transformers & NLTK")