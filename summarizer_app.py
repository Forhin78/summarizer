import tkinter as tk
from tkinter import filedialog, messagebox
import threading
from transformers import pipeline
import PyPDF2
import nltk
from nltk.tokenize import sent_tokenize
import os

NLTK_DATA_DIR = os.path.join(os.path.expanduser("~"), "nltk_data")
nltk.data.path.append(NLTK_DATA_DIR)

def ensure_nltk_data():
    """Ensure required NLTK tokenizers are available."""
    try:
        nltk.data.find("tokenizers/punkt")
    except LookupError:
        print("Downloading punkt...")
        nltk.download("punkt", quiet=True, download_dir=NLTK_DATA_DIR)

    try:
        nltk.data.find("tokenizers/punkt_tab")
    except LookupError:
        print("Downloading punkt_tab...")
        nltk.download("punkt_tab", quiet=True, download_dir=NLTK_DATA_DIR)

ensure_nltk_data()
print("✅ NLTK tokenizer ready.")

def load_summarizer():
    model_name = "sshleifer/distilbart-cnn-12-6"
    try:
        return pipeline("summarization", model=model_name)
    except Exception as e:
        print("Model load error:", e)
        try:
            return pipeline("summarization", model=model_name, local_files_only=True)
        except Exception as e_local:
            print("Local model load error:", e_local)
            return None

summarizer = load_summarizer()

def split_text(text, max_words=500):
    sentences = sent_tokenize(text)
    chunks, current, count = [], [], 0
    for sent in sentences:
        words = sent.split()
        if count + len(words) > max_words and current:
            chunks.append(" ".join(current))
            current, count = [sent], len(words)
        else:
            current.append(sent)
            count += len(words)
    if current:
        chunks.append(" ".join(current))
    return chunks

def extract_key_sentences(text, top_n=3):
    return sent_tokenize(text)[:top_n]

def load_pdf_text(path):
    text = ""
    with open(path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            ptext = page.extract_text()
            if ptext:
                text += ptext + "\n"
    return text

def run_summarization(input_text, result_callback, error_callback, max_chunk_words=400):
    if summarizer is None:
        error_callback("Summarization model not available. Check model download/internet.")
        return

    try:
        chunks = split_text(input_text, max_words=max_chunk_words)
        partial_summaries = []
        for chunk in chunks:
            try:
                out = summarizer(chunk, max_length=150, min_length=50, do_sample=False)
                if isinstance(out, list) and len(out) > 0:
                    if isinstance(out[0], dict) and "summary_text" in out[0]:
                        partial_summaries.append(out[0]["summary_text"])
                    else:
                        partial_summaries.append(str(out[0]))
                else:
                    partial_summaries.append(str(out))
            except Exception as e:
                print("Chunk summarization error:", e)

        final_summary = " ".join(partial_summaries).strip()
        if not final_summary:
            error_callback("Empty summary returned.")
            return

        keys = extract_key_sentences(final_summary, top_n=3)
        result_callback(final_summary, keys)
    except Exception as e:
        error_callback(str(e))


root = tk.Tk()
root.title("🧠 Text Summarization App")

tk.Label(root, text="Enter text or upload a PDF:", font=("Arial", 12)).pack(anchor="w", padx=8, pady=(8,0))
text_input = tk.Text(root, height=15, width=80, wrap="word")
text_input.pack(padx=8, pady=6)

frame = tk.Frame(root)
frame.pack(pady=5)
status_var = tk.StringVar(value="")
status_label = tk.Label(root, textvariable=status_var, anchor="w")
status_label.pack(fill="x", padx=8, pady=(0,8))

def on_upload_pdf():
    path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if not path:
        return
    try:
        txt = load_pdf_text(path)
        text_input.delete("1.0", tk.END)
        text_input.insert(tk.END, txt)
    except Exception as e:
        messagebox.showerror("PDF Error", str(e))

def on_result(summary, key_sents):
    def show_result():
        status_var.set("Done.")
        summarize_btn.config(state="normal")
        upload_btn.config(state="normal")

        win = tk.Toplevel(root)
        win.title("Summary Results")

        tk.Label(win, text="Summary:", font=("Arial", 12, "bold")).pack(anchor="w", padx=8)
        text_box = tk.Text(win, height=10, width=80, wrap="word")
        text_box.pack(padx=8, pady=(0,8))
        text_box.insert("1.0", summary)
        text_box.config(state="disabled")

        tk.Label(win, text="Key Sentences:", font=("Arial", 12, "bold")).pack(anchor="w", padx=8)
        for i, s in enumerate(key_sents, start=1):
            tk.Label(win, text=f"{i}. {s}", wraplength=700, justify="left").pack(anchor="w", padx=12)
    root.after(0, show_result)

def on_error(msg):
    def show_err():
        status_var.set("")
        summarize_btn.config(state="normal")
        upload_btn.config(state="normal")
        messagebox.showerror("Summarization Error", msg)
    root.after(0, show_err)

def on_summarize():
    txt = text_input.get("1.0", tk.END).strip()
    if not txt:
        messagebox.showwarning("No Input", "Please enter text or upload a PDF.")
        return

    summarize_btn.config(state="disabled")
    upload_btn.config(state="disabled")
    status_var.set("Summarizing... please wait ⏳")

    threading.Thread(target=run_summarization, args=(txt, on_result, on_error), daemon=True).start()

upload_btn = tk.Button(frame, text="Upload PDF", width=14, command=on_upload_pdf)
upload_btn.grid(row=0, column=0, padx=6)

summarize_btn = tk.Button(frame, text="Summarize", width=14, command=on_summarize)
summarize_btn.grid(row=0, column=1, padx=6)

root.mainloop()


