import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import docx2txt
import PyPDF2
import spacy

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")

# Define role-based skills
ROLE_SKILLS = {
    "Data Analyst": {"python", "excel", "sql", "tableau", "statistics", "data", "analysis", "visualization"},
    "Power BI Analyst": {"power", "bi", "dax", "m", "visualization", "dashboard", "reporting", "sql"},
    "Machine Learning Engineer": {"python", "machine", "learning", "tensorflow", "pytorch", "model", "training", "nlp"},
}

REQUIRED_EDUCATION = {"bachelor", "master", "phd", "b.tech", "m.tech", "bsc", "msc"}


# Text extractors
def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + " "
    return text


def extract_text_from_docx(docx_path):
    return docx2txt.process(docx_path)


# Screening and highlighting
def screen_resume(resume_text, selected_role):
    resume_text_lower = resume_text.lower()
    doc = nlp(resume_text_lower)
    tokens = {token.text for token in doc if not token.is_stop and not token.is_punct}

    role_skills = ROLE_SKILLS.get(selected_role, set())
    matched_skills = role_skills.intersection(tokens)
    matched_education = REQUIRED_EDUCATION.intersection(tokens)

    score = len(matched_skills) + len(matched_education)
    return matched_skills, matched_education, score, resume_text


def highlight_keywords(text_widget, content, skills, education):
    text_widget.delete("1.0", tk.END)
    text_widget.insert(tk.END, content)

    def highlight_terms(term_list, tag_name, tag_color):
        for term in term_list:
            start = "1.0"
            while True:
                start = text_widget.search(term, start, stopindex=tk.END, nocase=True)
                if not start:
                    break
                end = f"{start}+{len(term)}c"
                text_widget.tag_add(tag_name, start, end)
                start = end

        text_widget.tag_config(tag_name, foreground=tag_color, font=('Helvetica', 10, 'bold'))

    highlight_terms(skills, "skill", "blue")
    highlight_terms(education, "edu", "green")


# GUI callbacks
def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", ".pdf"), ("Word Documents", ".docx")])
    file_entry.delete(0, tk.END)
    file_entry.insert(0, file_path)


def analyze_resume():
    path = file_entry.get()
    role = role_combo.get()

    if not path or not role:
        messagebox.showerror("Error", "Please select a resume and a job role.")
        return

    if path.endswith(".pdf"):
        text = extract_text_from_pdf(path)
    elif path.endswith(".docx"):
        text = extract_text_from_docx(path)
    else:
        messagebox.showerror("Error", "Unsupported file format.")
        return

    matched_skills, matched_education, score, full_text = screen_resume(text, role)

    result_box.config(state=tk.NORMAL)
    result_box.delete("1.0", tk.END)
    result_box.insert(tk.END, f"\nRole Selected: {role}")
    result_box.insert(tk.END, f"\nMatched Skills ({len(matched_skills)}): {', '.join(matched_skills)}")
    result_box.insert(tk.END, f"\nMatched Education ({len(matched_education)}): {', '.join(matched_education)}")
    result_box.insert(tk.END, f"\nScore: {score}/20\n\n")
    result_box.config(state=tk.DISABLED)

    highlight_keywords(highlight_box, full_text, matched_skills, matched_education)


# GUI Layout
root = tk.Tk()
root.title("AI Resume Screener")
root.geometry("800x600")
root.configure(padx=20, pady=20)

# Resume file input
tk.Label(root, text="Select Resume File:").pack(anchor="w")
file_frame = tk.Frame(root)
file_frame.pack(fill="x", pady=5)
file_entry = tk.Entry(file_frame, width=50)
file_entry.pack(side="left", padx=(0, 10), fill="x", expand=True)
tk.Button(file_frame, text="Browse", command=browse_file).pack(side="left")

# Job role dropdown
tk.Label(root, text="Select Job Role:").pack(anchor="w", pady=(10, 0))
role_combo = ttk.Combobox(root, values=list(ROLE_SKILLS.keys()), state="readonly")
role_combo.pack(fill="x", pady=5)

# Analyze button
tk.Button(root, text="Analyze Resume", command=analyze_resume, bg="#4CAF50", fg="white").pack(pady=10)

# Result text area
tk.Label(root, text="Results Summary:").pack(anchor="w")
result_box = tk.Text(root, height=6, state=tk.DISABLED, bg="#f0f0f0", wrap="word")
result_box.pack(fill="x", padx=5)

# Resume preview with highlights
tk.Label(root, text="Resume Preview with Highlights:").pack(anchor="w", pady=(10, 0))
highlight_box = tk.Text(root, height=20, wrap="word")
highlight_box.pack(fill="both", expand=True, padx=5, pady=(0, 10))

root.mainloop()

