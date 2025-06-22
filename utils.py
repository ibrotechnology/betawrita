# utils.py
import os
import re
from collections import Counter

# ---------- Word Count ----------
def get_word_count(text):
    words = text.split()
    return len(words)

# ---------- Grammar Tips ----------
def get_grammar_tips(text):
    tips = []
    if "very" in text.lower():
        tips.append("Consider reducing use of the word 'very'.")
    if re.search(r"\bis\b|\bare\b.*\bby\b", text):
        tips.append("Watch out for passive voice (e.g., 'is done by').")
    return tips

# ---------- Outline Generator ----------
def generate_outline(essay_type):
    outlines = {
        "formal_letter": [
            "[Your Address]",
            "[Date]",
            "[Recipient's Address]",
            "[Salutation]",
            "[Opening Paragraph]",
            "[Main Issue Paragraph]",
            "[Suggested Solutions Paragraph]",
            "[Conclusion]",
            "[Yours faithfully, Your Name]"
        ],
        "article": [
            "[Title in Capital Letters]",
            "[Introduction]",
            "[1st Argument/Paragraph]",
            "[2nd Argument/Paragraph]",
            "[Conclusion with Suggestions]"
        ],
        "narrative": [
            "[Set the Scene]",
            "[Describe Key Characters]",
            "[Build the Conflict]",
            "[Climax]",
            "[Resolution and Moral]"
        ]
    }
    return "\n\n".join(outlines.get(essay_type, ["No outline available."]))

# ---------- Dictionary Loader ----------
def load_dictionary(file_path):
    dictionary = {}
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if ":" in line:
                    word, definition = line.strip().split(":", 1)
                    dictionary[word.strip()] = definition.strip()
    return dictionary

# ---------- Draft Manager ----------
def save_draft(username, title, text):
    folder = os.path.join("saved_drafts", username)
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, f"{title}.txt"), "w", encoding='utf-8') as f:
        f.write(text)

def load_draft(username, title):
    path = os.path.join("saved_drafts", username, f"{title}.txt")
    if os.path.exists(path):
        with open(path, "r", encoding='utf-8') as f:
            return f.read()
    return ""

def list_drafts(username):
    folder = os.path.join("saved_drafts", username)
    if os.path.exists(folder):
        return [f[:-4] for f in os.listdir(folder) if f.endswith(".txt")]
    return []
