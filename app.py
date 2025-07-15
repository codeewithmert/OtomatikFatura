# NOTE: This app requires 'plotly' to be installed for interactive image display.
# pip install plotly
import streamlit as st
import pytesseract
from PIL import Image
from ocr.image_utils import enhance_image
from ocr.ocr_engine import extract_text_from_image, clean_ocr_text
from ocr.invoice_parser import get_pattern, set_pattern, remove_pattern, list_patterns
from utils.session import get_or_init_fatura_df, reset_fatura_df
import json
import pandas as pd
from typing import List, Optional

# Tesseract yolunu ayarla
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

st.set_page_config(page_title="Otomatik Fatura İşleme Sistemi", layout="centered")
st.title("🧾 Otomatik Fatura İşleme Sistemi")
st.markdown("""
    <style>
    .block-container { max-width: 700px !important; }
    @media (max-width: 600px) {
        .block-container { padding: 1rem !important; }
    }
    </style>
""", unsafe_allow_html=True)

lang_map = {"Türkçe": "tur", "İngilizce": "eng"}
language = st.selectbox("OCR Dili", options=list(lang_map.keys()), index=0)
ocr_lang = lang_map[language]
enhance = st.checkbox("Görüntüyü iyileştir (kontrast & siyah-beyaz)")
uploaded_files: Optional[List] = st.file_uploader(
    "Fatura dosyalarını yükleyin (PDF, JPG, PNG)",
    type=["pdf", "jpg", "jpeg", "png"],
    accept_multiple_files=True
)

with st.expander("RegEx Desenlerini Yönet (JSON)"):
    patterns = list_patterns()
    st.markdown("**Mevcut Desenler:**")
    st.table([{ 'Alan': k, 'Desen': v['pattern'] if isinstance(v, dict) else v, 'Örnek Veri': v.get('example', '') if isinstance(v, dict) else '', 'Tip': v.get('type', '') if isinstance(v, dict) else '' } for k, v in patterns.items()])
    st.markdown("---")
    regex_keys = list(patterns.keys())
    pattern_types = ["tarih", "tutar", "fatura no", "satıcı", "vergi", "satın alım", "satış", "diğer"]
    selected_key = st.selectbox("Düzenlenecek/Silinecek Alan", regex_keys + ["Yeni Alan Ekle"])
    if selected_key == "Yeni Alan Ekle":
        new_key = st.text_input("Yeni Alan Adı (ör: custom_field)")
        new_pattern = st.text_input("Yeni RegEx Deseni")
        new_example = st.text_input("Örnek Veri (isteğe bağlı)")
        new_type = st.selectbox("Desen Tipi", pattern_types, index=len(pattern_types)-1)
        if st.button("Desen Ekle"):
            if new_key and new_pattern:
                set_pattern(new_key, {"pattern": new_pattern, "example": new_example, "type": new_type})
                st.success(f"{new_key} alanı eklendi.")
                st.rerun()
    else:
        current = patterns[selected_key]
        if isinstance(current, dict):
            edit_pattern = st.text_input("Deseni Düzenle", value=current.get('pattern', ''))
            edit_example = st.text_input("Örnek Veri Düzenle", value=current.get('example', ''))
            edit_type = st.selectbox("Desen Tipi", pattern_types, index=pattern_types.index(current.get('type', 'diğer')) if current.get('type', 'diğer') in pattern_types else len(pattern_types)-1)
        else:
            edit_pattern = st.text_input("Deseni Düzenle", value=current)
            edit_example = st.text_input("Örnek Veri Düzenle", value='')
            edit_type = st.selectbox("Desen Tipi", pattern_types, index=len(pattern_types)-1)
        col_edit, col_del = st.columns(2)
        with col_edit:
            if st.button("Deseni Kaydet", key="edit_save"):
                set_pattern(selected_key, {"pattern": edit_pattern, "example": edit_example, "type": edit_type})
                st.success(f"{selected_key} deseni güncellendi.")
                st.rerun()
        with col_del:
            if st.button("Deseni Sil", key="edit_delete"):
                remove_pattern(selected_key)
                st.success(f"{selected_key} deseni silindi.")
                st.rerun()

fatura_df = get_or_init_fatura_df()

# --- Toplu fatura yükleme ve işleme ---
def process_files(files: List, ocr_lang: str, enhance: bool) -> pd.DataFrame:
    """Yüklenen dosyaları işler ve DataFrame'e ekler."""
    df = fatura_df.copy()
    for uploaded_file in files:
        try:
            image = None
            if uploaded_file.type == "application/pdf":
                from pdf2image import convert_from_bytes
                images = convert_from_bytes(uploaded_file.read())
                image = images[0]
            else:
                image = Image.open(uploaded_file)
            if not isinstance(image, Image.Image):
                import numpy as np
                if isinstance(image, np.ndarray):
                    image = Image.fromarray(image)
                else:
                    raise ValueError("Desteklenmeyen görüntü formatı")
            if image is not None and enhance:
                image = enhance_image(image)
            raw_text = extract_text_from_image(image, ocr_lang)
            text = clean_ocr_text(raw_text)
            # RegEx ile toplu işleme (tüm alanlar için)
            patterns = list_patterns()
            import re
            result = {"dosya_adi": uploaded_file.name}
            for key, pattern in patterns.items():
                match = re.search(pattern, text)
                result[key] = match.group(0) if match else "bulunamadı"
            df = pd.concat([df, pd.DataFrame([result])], ignore_index=True)
        except Exception as e:
            st.error(f"{uploaded_file.name} işlenirken hata oluştu: {e}")
    return df

if uploaded_files:
    fatura_df = process_files(uploaded_files, ocr_lang, enhance)
    st.session_state['fatura_df'] = fatura_df
    st.success(f"{len(uploaded_files)} fatura işlendi ve tabloya eklendi!")

# --- Tablo ve dışa aktarma ---
st.subheader("Fatura Tablosu (Geçmiş/Toplu İşlenenler)")
st.dataframe(fatura_df)
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Tabloyu Temizle"):
        reset_fatura_df()
        st.success("Tablo temizlendi!")
with col2:
    csv_data = fatura_df.to_csv(index=False) or ''
    st.download_button("CSV Olarak Dışa Aktar", data=csv_data, file_name="faturalar.csv", mime="text/csv")
with col3:
    json_data = fatura_df.to_json(orient="records", indent=2) or '[]'
    st.download_button("JSON Olarak Dışa Aktar", data=json_data, file_name="faturalar.json", mime="application/json")
    # SQL dışa aktarma
    def export_df_to_sql(df: pd.DataFrame, table_name: str = "fatura_df") -> str:
        sql = f"CREATE TABLE {table_name} (" + ", ".join([f'{col} TEXT' for col in df.columns]) + ");\n"
        for _, row in df.iterrows():
            values = [str(row[col]).replace("'", "''") for col in df.columns]
            sql += f"INSERT INTO {table_name} VALUES ('{', '.join(values)}');\n"
        return sql
    sql_export = export_df_to_sql(fatura_df)
    st.download_button("SQL Olarak Dışa Aktar", data=sql_export, file_name="faturalar.sql", mime="text/plain")

# --- Geçmişi göster ---
if not fatura_df.empty:
    st.markdown("#### Son İşlenen Faturalar")
    st.table(fatura_df.tail(5))

# --- Tekli fatura işlemleri (önizleme, koordinatla OCR ve RegEx) ---
if uploaded_files and len(uploaded_files) == 1:
    uploaded_file = uploaded_files[0]
    try:
        image = None
        if uploaded_file.type == "application/pdf":
            from pdf2image import convert_from_bytes
            images = convert_from_bytes(uploaded_file.read())
            image = images[0]
        else:
            image = Image.open(uploaded_file)
        if not isinstance(image, Image.Image):
            import numpy as np
            if isinstance(image, np.ndarray):
                image = Image.fromarray(image)
            else:
                raise ValueError("Desteklenmeyen görüntü formatı")
        if image is not None and enhance:
            image = enhance_image(image)
        st.subheader("Fatura Önizlemesi ve Koordinat Seçimi")
        zoom = st.slider("Yakınlaştırma (%)", min_value=10, max_value=400, value=100, step=10)
        display_image = image.copy()
        try:
            import numpy as np
            import plotly.express as px
            img_np = np.array(display_image)
            if zoom != 100:
                new_size = (int(display_image.width * zoom / 100), int(display_image.height * zoom / 100))
                display_image = display_image.resize(new_size)
                img_np = np.array(display_image)
            st.markdown("**Görsel üzerinde bir alan seçmek için kutu koordinatlarını girin.**")
            colx1, colx2 = st.columns(2)
            with colx1:
                x = st.number_input("X (sol)", min_value=0, max_value=img_np.shape[1]-1, value=0)
                w = st.number_input("Genişlik", min_value=1, max_value=img_np.shape[1]-x, value=img_np.shape[1])
            with colx2:
                y = st.number_input("Y (üst)", min_value=0, max_value=img_np.shape[0]-1, value=0)
                h = st.number_input("Yükseklik", min_value=1, max_value=img_np.shape[0]-y, value=img_np.shape[0])
            # Görsel üzerinde kutu çizimi (plotly ile)
            fig = px.imshow(img_np)
            fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
            fig.add_shape(type="rect", x0=x, y0=y, x1=x+w, y1=y+h, line=dict(color="red", width=3))
            st.plotly_chart(fig, use_container_width=True)
            regex_keys = list_patterns().keys()
            regex_key = st.selectbox("RegEx Alanı", list(regex_keys))
            pattern = get_pattern(regex_key)
            if st.button("Koordinattan OCR ve RegEx ile Değer Al"):
                scale = image.width / img_np.shape[1]
                crop_box = (int(x*scale), int(y*scale), int((x+w)*scale), int((y+h)*scale))
                cropped = image.crop(crop_box)
                st.image(cropped, caption="Kırpılan Alan", use_container_width=True)
                with st.spinner("OCR ve RegEx uygulanıyor..."):
                    try:
                        ocr_text = extract_text_from_image(cropped, ocr_lang)
                        st.text_area("OCR Sonucu (Kırpılan Alan)", ocr_text, height=100)
                        import re
                        if pattern is None or pattern == "":
                            st.warning("Seçilen alan için RegEx deseni tanımlı değil.")
                        else:
                            match = re.search(pattern, ocr_text)
                            if match:
                                st.success(f"RegEx ile bulunan değer: {match.group(0)}")
                            else:
                                st.warning("RegEx ile eşleşen değer bulunamadı.")
                    except Exception as e:
                        st.error(f"OCR/RegEx Hatası: {e}")
        except ModuleNotFoundError as e:
            st.error("Plotly kütüphanesi yüklü değil. Lütfen terminalde 'pip install plotly' komutunu çalıştırın.")
            st.stop()
    except Exception as e:
        st.error(f"{uploaded_file.name} işlenirken hata oluştu: {e}") 