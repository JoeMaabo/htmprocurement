import pandas as pd
import io
import streamlit as st

DATA_FILES = {
    "procurement": "data/procurement.csv",
    "pfm": "data/pfm.csv",
    "qa": "data/qa.csv",
    "cofinancing": "data/cofinancing.csv",
    "ctexts": "data/ctexts.csv",
    "cpfm": "data/cpfm.csv",
    "wca_summary": "data/wca_summary.csv"
}

@st.cache_data
def load_csv(path):
    # Try 'utf-8' first, then fall back to 'latin-1' if needed
    try:
        return pd.read_csv(path, encoding='utf-8')
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding='latin-1')
    
def load_all():
    data = {}
    for k, p in DATA_FILES.items():
        try:
            data[k] = load_csv(p)
        except Exception:
            data[k] = pd.DataFrame()
    return data

def read_uploaded(file) -> pd.DataFrame:
    # Accepts in-memory uploaded file
    if file is None:
        return None
    content = file.read()
    try:
        return pd.read_csv(io.BytesIO(content))
    except Exception:
        # try Excel
        try:
            return pd.read_excel(io.BytesIO(content))
        except Exception:
            return None
