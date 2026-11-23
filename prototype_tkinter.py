"""Small classroom version based on Saumya's original Tkinter project.

The punctuation issue is fixed by joining sentences with a space.
Run this file directly to open the learning interface.
"""
import re
import tkinter as tk


def summarize_text(text):
    """Return the first two sentences, preserving short input."""
    text = text.strip()
    if not text:
        return ""
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    return text if len(sentences) <= 2 else " ".join(sentences[:2])


def main():
    root = tk.Tk()
    root.title("AI Text Summarizer · Tkinter learning version")
    root.geometry("560x620")
    root.minsize(500, 550)
    root.configure(bg="lightblue")

    tk.Label(root, text="AI TEXT SUMMARIZER", font=("Arial", 18, "bold"), bg="lightblue").pack(pady=14)
    tk.Label(root, text="Saumya · Roll No. 078", font=("Arial", 10), bg="lightblue").pack()
    tk.Label(root, text="Enter your paragraph:", font=("Arial", 11), bg="lightblue").pack(pady=(14, 0))
    input_box = tk.Text(root, height=10, width=58, wrap="word", undo=True)
    input_box.pack(padx=20, pady=10, fill="both", expand=True)

    def run_summary():
        result = summarize_text(input_box.get("1.0", tk.END))
        result_box.delete("1.0", tk.END)
        result_box.insert(tk.END, result or "Please enter some text.")

    def clear():
        input_box.delete("1.0", tk.END)
        result_box.delete("1.0", tk.END)
        input_box.focus_set()

    tk.Button(root, text="Summarize", command=run_summary, bg="green", fg="white", padx=18).pack(pady=5)
    tk.Label(root, text="Your Summary:", font=("Arial", 11), bg="lightblue").pack(pady=(8, 0))
    result_box = tk.Text(root, height=7, width=58, wrap="word")
    result_box.pack(padx=20, pady=10, fill="both", expand=True)
    tk.Button(root, text="Clear", command=clear, bg="red", fg="white", padx=18).pack(pady=(0, 15))
    input_box.focus_set()
    root.mainloop()


if __name__ == "__main__":
    main()
