import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ocr.invoice_parser import list_patterns, set_pattern, get_pattern, parse_invoice_data

def test_pattern_crud():
    patterns = list_patterns()
    assert isinstance(patterns, dict)
    set_pattern('test_field', {'pattern': r'Test(\d+)', 'example': 'Test123', 'type': 'test'})
    assert get_pattern('test_field') == r'Test(\d+)'
    patterns = list_patterns()
    assert 'test_field' in patterns

def test_parse_invoice_data():
    text = 'Fatura No: FTR20230001\nToplam: 1.234,56 TL\nTarih: 01.01.2023\nSatıcı: Axxion Yazılım\nVergi No: 1234567890'
    result = parse_invoice_data(text)
    assert result['fatura_tarihi'] == '01.01.2023'
    assert result['toplam_tutar'] == '1.234,56'
    assert result['fatura_no'] == 'FTR20230001'
    assert result['satıcı_adı'] == 'Axxion Yazılım'
    assert result['vergi_no'] == '1234567890'

if __name__ == '__main__':
    test_pattern_crud()
    test_parse_invoice_data()
    print('All tests passed.') 