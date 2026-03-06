import streamlit as st
import mysql.connector
from database import get_connection, run_query

st.title("👮 HR & Roster")

st.subheader("Officer Directory")
df_officers = run_query("SELECT * FROM CIDER_HR.OFFICER;")
st.dataframe(df_officers, use_container_width=True)

st.divider()

# Form to Insert Data
st.subheader("Add New Officer")
with st.form("add_officer_form"):
    new_id = st.number_input("Officer ID", min_value=1, step=1)
    new_name = st.text_input("Full Name")
    new_rank = st.selectbox("Rank", ["Constable", "Inspector", "ACP"])
    new_branch = st.number_input("Branch ID", min_value=1, step=1)
    
    submitted = st.form_submit_button("Submit to Database")
    
    if submitted:
        conn = get_connection()
        cursor = conn.cursor()
        # Ensure your table uses 'Officer_Rank' or backticks around 'Rank' based on our earlier fix!
        insert_query = "INSERT INTO CIDER_HR.OFFICER (Officer_ID, Name, Officer_Rank, Branch_ID) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_query, (new_id, new_name, new_rank, new_branch))
        conn.commit()
        conn.close()
        st.success(f"Officer {new_name} added successfully! Refresh to see them in the directory.")