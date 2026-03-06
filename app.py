import streamlit as st
from database import run_query

st.set_page_config(page_title="CIDER Command Center", layout="wide")

st.title("🚨 CIDER: Command Center")
st.write("Welcome to the Crime Investigation & Evidence Management System.")

# Example: A simple metric and a recent case table
st.subheader("Department Overview")
col1, col2, col3 = st.columns(3)

try:
    # A basic query to count active cases
    df_active = run_query("SELECT COUNT(*) as count FROM CIDER_CRIME.CASE_FILE WHERE Status = 'Active';")
    active_cases = df_active['count'][0]
    
    col1.metric("Active Cases", active_cases)
    col2.metric("Officers on Duty", "Loading...") # You will fill this in later
    col3.metric("Solved Cases", "Loading...")     # You will fill this in later

    st.divider()
    
    st.subheader("Recent Case Activity")
    df_recent = run_query("SELECT Case_ID, Crime_Type, Description, Status FROM CIDER_CRIME.CASE_FILE LIMIT 5;")
    st.dataframe(df_recent, use_container_width=True)

except Exception as e:
    st.error(f"Database Connection Error: Make sure MySQL is running and your .env is correct. Details: {e}")