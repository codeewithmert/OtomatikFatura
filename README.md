# Otomatik Fatura OCR Sistemi / Automatic Invoice OCR System

## Açıklama / Description

Bu proje, Python, Streamlit ve Tesseract kullanarak profesyonel, modüler ve gelişmiş bir fatura OCR sistemidir. Kullanıcılar birden fazla fatura yükleyebilir, RegEx desenlerini ve alan tiplerini yönetebilir, koordinatla alan seçebilir, sonuçları dışa aktarabilir ve arayüzden her şeyi özelleştirebilir.

This project is a professional, modular, and advanced invoice OCR system using Python, Streamlit, and Tesseract. Users can upload multiple invoices, manage RegEx patterns and field types, select areas by coordinates, export results, and customize everything from the UI.

## Özellikler / Features
- Çoklu dosya yükleme (PDF, JPG, PNG)
- RegEx desenlerini, tiplerini ve örnek verileri yönetme
- Koordinatla alan seçimi ve görsel üzerinde kutu çizimi
- Sonuçları CSV, JSON, SQL olarak dışa aktarma
- SQL CREATE TABLE + INSERT INTO çıktısı
- Hata yönetimi ve kullanıcıya açıklayıcı geri bildirim
- Modern, kullanıcı dostu ve responsive arayüz
- Koyu/açık tema desteği
- Demo fatura ve örnek RegEx JSON
- Tüm kod PEP8 uyumlu, tip anotasyonlu ve dokümantasyonlu

## Klasör Yapısı / Folder Structure
```
.
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── ocr/
│   ├── image_utils.py
│   ├── ocr_engine.py
│   ├── invoice_parser.py
│   └── regex_patterns.json
├── db/
│   └── sql_utils.py
├── utils/
│   └── session.py
├── assets/
│   ├── demo_invoice.jpg
│   ├── screenshot_main.png
│   ├── screenshot_regex.png
│   └── screenshot_coord.png
├── tests/
│   └── test_ocr.py
```

## Kurulum / Installation
```bash
# Gerekli paketleri yükleyin / Install required packages
pip install -r requirements.txt

# Tesseract yükleyin (Windows için)
# Download and install Tesseract (for Windows)
https://github.com/tesseract-ocr/tesseract
```

## Kullanım / Usage
```bash
streamlit run app.py
```

## Özelleştirme / Customization
- RegEx desenlerini, tiplerini ve örnek verileri arayüzden ekleyin, düzenleyin, silin.
- Koordinatla alan seçin, kutu çizin, yakınlaştırın.
- Demo fatura ve örnek JSON ile test edin.

## Lisans / License
MIT 
