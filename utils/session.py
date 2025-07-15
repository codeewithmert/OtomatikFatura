import pandas as pd
import streamlit as st

def get_or_init_fatura_df() -> pd.DataFrame:
    if 'fatura_df' not in st.session_state:
        st.session_state['fatura_df'] = pd.DataFrame({col: pd.Series(dtype='str') for col in ["fatura_tarihi", "toplam_tutar", "fatura_no", "satıcı_adı", "vergi_no"]})
    return st.session_state['fatura_df']

def reset_fatura_df():
    st.session_state['fatura_df'] = pd.DataFrame({col: pd.Series(dtype='str') for col in ["fatura_tarihi", "toplam_tutar", "fatura_no", "satıcı_adı", "vergi_no"]}) 