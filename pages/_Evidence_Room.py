import streamlit as st
from database import run_query

st.title("🔬 Forensics & Evidence Room")

filter_type = st.radio("Filter Evidence By:", ["All", "Physical", "Digital", "Fingerprint"])

try:
    if filter_type == "All":
        query = "SELECT * FROM CIDER_EVIDENCE.EVIDENCE;"
    else:
        query = f"SELECT * FROM CIDER_EVIDENCE.EVIDENCE WHERE Evidence_Type = '{filter_type}';"
        
    df_evidence = run_query(query)
    st.dataframe(df_evidence, use_container_width=True)

except Exception as e:
    st.error("Error loading evidence.")