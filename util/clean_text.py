import unicodedata

def clean_text(text: str) -> str:
    return unicodedata.normalize("NFKC", text).encode("utf-8", "ignore").decode("utf-8")
