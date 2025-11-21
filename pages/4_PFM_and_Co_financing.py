import streamlit as st
import pandas as pd
import plotly.express as px
from utils.load_data import load_all
from utils.auth import require_login

# BLOCK access if not logged in
require_login()

st.title("PFM & Co-financing")

data = load_all()
pfm = data['pfm']
cof = data['cofinancing']

st.subheader("PFM Indicators")
selected_cols = st.multiselect("",pfm.columns.tolist(), default=['Country', 'Budget Allocation Timeliness', 'Payment Delays', 'Alignment with Procurement Cycle'])
if selected_cols:
    st.dataframe(pfm[selected_cols].set_index('Country'))


st.subheader("Co-financing Execution")
selected_cols2 = st.multiselect("",cof.columns.tolist(), default=['Country', 'Execution Rate (%)', 'Risk of Non-Materialization'])
if selected_cols2:
    st.dataframe(cof[selected_cols2].set_index('Country'))


# Plot payment delays categories across countries (if exists)
if 'Payment Delays' in pfm.columns:
    counts = pfm.groupby(['Payment Delays']).size().reset_index(name='count')
    fig = px.bar(counts, x='Payment Delays', y='count', title='Payment Delays Frequency (by category)')
    st.plotly_chart(fig, use_container_width=True)