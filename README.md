# summarizer
# Text Summarization system

A Python-based desktop application that summarizes long text or PDF documents using Hugging Face Transformers and NLTK. Built with Tkinter, this app runs entirely offline—no browser required!

# Features

-  Accepts raw text input or PDF file upload
-  Uses Hugging Face's transformer-based summarization pipeline
-  Automatically splits long text into manageable chunks
-  Extracts top 3 key sentences from the summary
-  Displays results in a clean popup window
-  Built with NLTK for sentence tokenization
-  GUI built using Python's Tkinter (no browser needed)


# Installation
    Install dependencies
       python 3.11+
        pip install transformers PyPDF2 nltk

# Running the app
    python summarizer_gui.py
This will launch a desktop window where you can paste text or upload a PDF.
# How it works
    text-summarization-app/
│
├── summarizer_gui.py        
├── README.md               
└── screenshots

# Limitations
- Does not support scanned PDFs (no OCR).
- Summarization may be slow for very large documents.
- Requires internet access to download the model the first time

# Mainwindow
![Mainwindow](https://github.com/Forhin78/summarizer/blob/2b576d01d1758341730bb85f0a29d6ac2fbc498d/main.png)
# Summary output
![summary output]()
       

