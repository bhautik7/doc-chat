import re

def clean_text(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)      # collapse excessive newlines
    text = re.sub(r"[ \t]{2,}", " ", text)        # collapse repeated spaces/tabs
    text = re.sub(r"\x00", "", text)              # strip null bytes (common in bad PDF extraction)
    return text.strip()