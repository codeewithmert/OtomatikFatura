import pytesseract
from PIL import Image

def extract_text_from_image(image: Image.Image, lang: str) -> str:
    try:
        return pytesseract.image_to_string(image, lang=lang)
    except Exception as e:
        return f"OCR Hatası: {e}"

def clean_ocr_text(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines) 