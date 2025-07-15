import re
import json
import os
from typing import Dict, Optional, Any

PATTERN_FILE = os.path.join(os.path.dirname(__file__), 'regex_patterns.json')

DEFAULT_PATTERNS = {
    'date': {"pattern": r"(\d{2}[./-]\d{2}[./-]\d{4})|((\d{4}[./-]\d{2}[./-]\d{2}))", "example": "01.01.2023", "type": "tarih"},
    'total': {"pattern": r"(Toplam|Genel Toplam|Tutar)[^\d]*(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})|(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})\s*(TL|TRY|₺)", "example": "1.234,56 TL", "type": "tutar"},
    'invoice_no': {"pattern": r"(Fatura No|Fatura Numarası|No|Numara)[^\w]*(\w{5,})|No[:\s]+(\w{5,})", "example": "FTR20230001", "type": "fatura no"},
    'seller': {"pattern": r"(Satıcı|Firma|Şirket)[^\n:]*[:\s]+([\w\s\-\.]+)", "example": "Axxion Yazılım", "type": "satıcı"},
    'tax': {"pattern": r"(Vergi No|VKN|Vergi Numarası)[^\d]*(\d{10})", "example": "1234567890", "type": "vergi"},
    'purchase': {"pattern": r"(Satın Alım|Alım|Satınalma)[^\n:]*[:\s]+([\w\s\-\.]+)", "example": "Satın Alım: Bilgisayar", "type": "satın alım"},
    'sale': {"pattern": r"(Satış|Satılan|Satış İşlemi)[^\n:]*[:\s]+([\w\s\-\.]+)", "example": "Satış: Yazıcı", "type": "satış"}
}

def load_patterns() -> Dict[str, Any]:
    if not os.path.exists(PATTERN_FILE):
        save_patterns(DEFAULT_PATTERNS)
        return DEFAULT_PATTERNS.copy()
    with open(PATTERN_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_patterns(patterns: Dict[str, Any]) -> None:
    with open(PATTERN_FILE, 'w', encoding='utf-8') as f:
        json.dump(patterns, f, ensure_ascii=False, indent=2)

def get_pattern(key: str) -> Optional[str]:
    patterns = load_patterns()
    val = patterns.get(key)
    if isinstance(val, dict):
        return val.get('pattern', '')
    return val

def get_pattern_full(key: str) -> Optional[dict]:
    patterns = load_patterns()
    val = patterns.get(key)
    if isinstance(val, dict):
        return val
    return {"pattern": val, "example": "", "type": ""} if val else None

def set_pattern(key: str, pattern: dict) -> None:
    patterns = load_patterns()
    patterns[key] = pattern
    save_patterns(patterns)

def remove_pattern(key: str) -> None:
    patterns = load_patterns()
    if key in patterns:
        del patterns[key]
        save_patterns(patterns)

def list_patterns() -> Dict[str, Any]:
    return load_patterns()

def parse_invoice_data(
    text: str,
    date_pattern: Optional[str] = None,
    total_pattern: Optional[str] = None,
    invoice_no_pattern: Optional[str] = None,
    seller_pattern: Optional[str] = None,
    tax_pattern: Optional[str] = None
) -> Dict[str, str]:
    patterns = load_patterns()
    def extract_pattern(val):
        if isinstance(val, dict):
            return val.get('pattern', '')
        return val or ''
    def search_pattern(pattern, text, flags=0, group=1):
        try:
            match = re.search(pattern, text, flags)
            if match:
                for g in range(1, len(match.groups())+1):
                    if match.group(g):
                        return match.group(g)
            return None
        except Exception:
            return None
    date = search_pattern(extract_pattern(date_pattern or patterns.get('date')), text, group=1)
    total = search_pattern(extract_pattern(total_pattern or patterns.get('total')), text, re.IGNORECASE, group=2)
    invoice_no = search_pattern(extract_pattern(invoice_no_pattern or patterns.get('invoice_no')), text, re.IGNORECASE, group=2)
    seller = search_pattern(extract_pattern(seller_pattern or patterns.get('seller')), text, re.IGNORECASE, group=2)
    tax_no = search_pattern(extract_pattern(tax_pattern or patterns.get('tax')), text, re.IGNORECASE, group=2)
    return {
        "fatura_tarihi": date if date else "bulunamadı",
        "toplam_tutar": total if total else "bulunamadı",
        "fatura_no": invoice_no if invoice_no else "bulunamadı",
        "satıcı_adı": seller if seller else "bulunamadı",
        "vergi_no": tax_no if tax_no else "bulunamadı",
    } 