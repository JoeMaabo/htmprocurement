import streamlit as st
import pandas as pd
import plotly.express as px
from utils.load_data import load_all
from utils.auth import require_login

# BLOCK access if not logged in
require_login()

st.title("Quality Assurance")

data = load_all()
qa = data['qa']


st.subheader("QA Table")
selected_cols3 = st.multiselect("",qa.columns.tolist(), default=['Country', 'QA Policy Exists', 'Pre-shipment Testing', 'Post-market Surveillance'])
if selected_cols3:
    st.dataframe(qa[selected_cols3].set_index('Country'))

st.subheader("QA Readiness Score (simple composite)")
# compute a naive QA score
def qa_score(row):
    s = 1
    s += 1 if str(row.get('QA Policy Exists','')).lower() == 'yes' else 0
    s += 1 if str(row.get('Pre-shipment Testing','')).lower() in ['yes','partial'] else 0
    s += 2 if str(row.get('Post-market Surveillance','')).lower() in ['moderate','strong'] else 0
    return s

qa['QA Score'] = qa.apply(qa_score, axis=1)
fig = px.bar(qa.sort_values('QA Score', ascending=False), x='Country', y='QA Score', title='QA Readiness Score (0-5)')
st.plotly_chart(fig, use_container_width=True)

st.markdown("""
**Notes:** This QA score is illustrative.
""")
