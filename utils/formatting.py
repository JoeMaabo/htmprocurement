# utils/formatting.py
import pandas as pd

def justify(text: str) -> str:
    """
    Wrap text in a div for justified alignment.
    """
    return f"""
    <div style="text-align: justify; text-justify: inter-word;">
        {text}
    </div>
    """

def style_table(df: pd.DataFrame) -> str:
    """
    Convert DataFrame to HTML table with custom styling for Streamlit.
    """
    # Reset index to hide it
    df = df.reset_index(drop=True)

    html = """
    <style>
    table {
        border-collapse: collapse;
        width: 100%;
    }
    th, td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
    }
    th {
        background-color: #DAE9F8;
        color: black;
    }
    tr:nth-child(even) {background-color: #f2f2f2;}
    tr:hover {background-color: #ddd;}
    </style>
    <table>
        <thead>
            <tr>
                <th>Indicator</th>
                <th>Value</th>
            </tr>
        </thead>
        <tbody>
    """

    for _, row in df.iterrows():
        html += f"<tr><td>{row['Indicator']}</td><td>{row['Value']}</td></tr>"

    html += "</tbody></table>"
    return html
