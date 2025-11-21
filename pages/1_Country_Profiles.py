import streamlit as st
import pandas as pd
import random
import numpy as np
import plotly.express as px
from utils.load_data import load_all, read_uploaded
from utils.doc_generator import make_docx, make_pdf
from utils.formatting import justify, style_table
from utils.auth import require_login

# BLOCK access if not logged in
require_login()

# -----------------------------------
# PAGE TITLE
# -----------------------------------
st.title("Country Profiles")

# Load data
data = load_all()
countries = data['procurement']['Country'].tolist()

# -----------------------------------
# COUNTRY SELECTION
# -----------------------------------
selected = st.selectbox("Select country to view profile", countries)

# Extract selected country rows
proc_row = data['procurement'][data['procurement']['Country'] == selected].iloc[0]
pfm_row = data['pfm'][data['pfm']['Country'] == selected].iloc[0]
qa_row = data['qa'][data['qa']['Country'] == selected].iloc[0]
text_row = data['ctexts'][data['ctexts']['Country'] == selected].iloc[0]

# -----------------------------------
# TABLE FORMAT FUNCTION
# -----------------------------------
def format_table(row):
    row = row.drop(labels=["Country"])
    df = pd.DataFrame({
        "Indicator": row.index,
        "Value": row.values
    })
    return df

# Create tables
proc_table = format_table(proc_row)
pfm_table = format_table(pfm_row)
qa_table = format_table(qa_row)

# -----------------------------------
# DISPLAY SECTIONS
# -----------------------------------
st.subheader("Policy & Regulatory Framework")
st.markdown(style_table(proc_table), unsafe_allow_html=True)
st.markdown(justify(text_row["policy_framework"]), unsafe_allow_html=True)

st.subheader("Procurement Cycle Mapping")
st.markdown(style_table(pfm_table), unsafe_allow_html=True)
st.markdown(justify(text_row["procurement_cycle"]), unsafe_allow_html=True)

st.subheader("Bottlenecks and Root Causes")
st.markdown(style_table(qa_table), unsafe_allow_html=True)
st.markdown(justify(text_row["bottlenecks"]), unsafe_allow_html=True)

st.subheader("Quality Assurance Mechanisms")
st.markdown(style_table(qa_table), unsafe_allow_html=True)
st.markdown(justify(text_row["quality_assurance"]), unsafe_allow_html=True)

st.subheader("Successful Practices & Innovations")
st.markdown(style_table(qa_table), unsafe_allow_html=True)
st.markdown(justify(text_row["innovations"]), unsafe_allow_html=True)
