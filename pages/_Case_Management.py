import streamlit as st
from database import run_query

st.title("📂 Case Management")

# Search Bar
search_id = st.text_input("Enter Case ID to search:")

if search_id:
    try:
        query = f"SELECT * FROM CIDER_CRIME.CASE_FILE WHERE Case_ID = {search_id};"
        df_case = run_query(query)
        
        if not df_case.empty:
            st.success(f"Record found for Case: {search_id}")
            st.dataframe(df_case, use_container_width=True)
            
            # Here you can later add the UPDATE code to change the status
        else:
            st.warning("No case found with that ID.")
    except Exception as e:
        st.error("Error fetching data.")