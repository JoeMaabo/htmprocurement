import streamlit as st
import pandas as pd
import plotly.express as px
from utils.load_data import load_all
from utils.auth import require_login
from utils.formatting import justify, style_table

# BLOCK access if not logged in
require_login()

st.title("Cross-Country Comparison")

data = load_all()
proc = data['procurement']
pfm = data['pfm']
qa = data['qa']
cof = data['cofinancing']
cpfm = data['cpfm']


st.header("Procurement Table")
selected_cols2 = st.multiselect("",proc.columns.tolist(), default=['Country', 'Dedicated Procurement Agency', 'Autonomy Level', 'HTM Procurement Guidelines'])
if selected_cols2:
    st.dataframe(proc[selected_cols2].set_index('Country'))

st.markdown("Download cross-country table:")
csv = proc.to_csv(index=False).encode()
st.download_button("Download procurement CSV", data=csv, file_name="procurement_table.csv", mime="text/csv")

st.header("PFM Execution Rate (Co-financing)")
if 'Execution Rate (%)' in cof.columns:
    cof['Execution Rate (%)'] = pd.to_numeric(cof['Execution Rate (%)'], errors='coerce')
    fig = px.bar(cof.sort_values("Execution Rate (%)", ascending=False), x='Country', y='Execution Rate (%)',
                 title="Co-financing Execution (%) by Country")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No 'Execution Rate (%)' column in cofinancing dataset.")

st.header("Autonomy Level Distribution")
if 'Autonomy Level' in proc.columns:
    counts = proc['Autonomy Level'].value_counts().reset_index()
    counts.columns = ['Autonomy Level', 'Count']
    fig2 = px.pie(counts, values='Count', names='Autonomy Level', title='Procurement Agency Autonomy Levels')
    st.plotly_chart(fig2, use_container_width=True)

# Filter + heatmap-like summary
st.header("Summary Matrix (select columns to pivot)")
selected_cols = st.multiselect("Columns (procurement)", proc.columns.tolist(), default=['Country', 'Autonomy Level', 'Dedicated Procurement Agency'])
if selected_cols:
    st.dataframe(proc[selected_cols].set_index('Country'))

st.header("Comparative Analysis")

# 1. Prepare the column configuration dictionary
column_settings = {}
# Get all column names from your DataFrame
column_names = cpfm.columns

# 2. Loop through all column names and configure them for wrapping
for col in column_names:
    column_settings[col] = st.column_config.TextColumn(
        col,  # Use the column name as the label
        width="medium",  # Use a consistent width for balance
        # The key setting to allow wrapping and prevent truncation:
        help=f"Details for the column: {col}" 
    )

# 3. Display the DataFrame using the generated configuration
st.dataframe(
    cpfm,
    column_config=column_settings, # Apply the settings to all columns
    hide_index=True,
    use_container_width=True # Ensure the table expands horizontally
)