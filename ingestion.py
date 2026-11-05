from pypdf import PdfReader


def load_linkedin():
    reader = PdfReader("twin/linkedin.pdf")

    linkedin_text = ""

    for page in reader.pages:
        text = page.extract_text()

        if text:
            linkedin_text += text + "\n"

    return linkedin_text


def load_summary():
    with open("twin/summary.txt", "r", encoding="utf-8") as file:
        return file.read()


linkedin = load_linkedin()
summary = load_summary()
