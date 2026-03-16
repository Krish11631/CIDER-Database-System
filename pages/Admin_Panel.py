import streamlit as st
from database import run_query
import time

if st.session_state.get('role') != 'Admin':
    st.error("Access Denied: Administrator clearance required.")
    st.stop()

officers = run_query("SELECT Officer_ID FROM CIDER_HR.OFFICER;")

#Written the login details in side and automatically opens up acc to login details
with st.sidebar:
    st.write(f"Logged in as: {st.session_state.get('role')} (ID: {st.session_state.get('user_id')})")
    if st.button("Logout", type="primary"):
        st.session_state['logged_in'] = False
        st.session_state['role'] = None
        st.session_state['user_id'] = None
        st.switch_page("Login_Page.py")


st.title("DGP Admin Panel")

tab1, tab2, tab3, tab4 = st.tabs(["Directory", "Recruit", "Transfer", "Terminate"])

#List of all Officers
with tab1:
    st.subheader("Officer Directory")
    try:
        query3 = """
        SELECT O.Officer_ID, O.Name, O.officer_rank, B.Location 
        FROM CIDER_HR.OFFICER O 
        JOIN CIDER_HR.BRANCH B ON O.Branch_ID = B.Branch_ID;
        """
        df_officers = run_query(query3)
        st.dataframe(df_officers, use_container_width=True)
    except Exception as e:
        st.error(f"Failed to load directory: {e}")

#Recruiting new Officer(Only Admin can)
with tab2:
    st.subheader("Recruit New Officer")
    #We want to select from the exisiting ones
    try:
        df_branches = run_query("SELECT Branch_ID FROM CIDER_HR.BRANCH;")
        valid_branches = df_branches['Branch_ID'].tolist()
    except Exception:
        valid_branches = []
# here
    with st.form("recruit_form"):
        new_id = st.number_input("Officer ID")
        new_name = st.text_input("Full Name")
        new_rank = st.selectbox("Rank", ["Constable", "Sub-Inspector", "Inspector", "ACP", "System Admin"])
        new_branch = st.selectbox("Branch ID", valid_branches)
        
        submit_recruit = st.form_submit_button("Recruit")
        
        if submit_recruit:
            if new_name:
                try:
                    insert_query = f"INSERT INTO CIDER_HR.OFFICER (Officer_ID, Name, officer_rank, Branch_ID) VALUES ({new_id}, '{new_name}', '{new_rank}', {new_branch});"
                    run_query(insert_query)
                    st.toast("Officer recruited successfully!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Database Error: {e}")
            else:
                st.error("Please provide a name.")


#Transfer one to another
with tab3:
    st.subheader("Update Officer Profile")
    with st.form("update_form"):
        update_id = st.selectbox("Select Officer to update", officers["Officer_ID"])
        update_rank = st.selectbox("New Rank", ["Constable", "Sub-Inspector", "Inspector", "ACP", "System Admin"])
        update_branch = st.selectbox("New Branch ID", valid_branches)
        
        submit_update = st.form_submit_button("Update Profile")
        
        if submit_update:
            try:
                update_query = f"UPDATE CIDER_HR.OFFICER SET officer_rank = '{update_rank}', Branch_ID = {update_branch} WHERE Officer_ID = {update_id};"
                run_query(update_query)
                st.toast("Profile updated successfully!")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Database Error: {e}")


#Remove somebody by ID
with tab4:
    st.subheader("Terminate Officer")
    with st.form("terminate_form"):
        term_id = st.selectbox("Select Officer to terminate", officers["Officer_ID"])
        submit_term = st.form_submit_button("Terminate", type="primary")
        
        if submit_term:
            try:
                del_query = f"DELETE FROM CIDER_HR.OFFICER WHERE Officer_ID = {term_id};"
                run_query(del_query)
                st.toast("Officer terminated successfully!")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error("Cannot delete officer. Please reassign their active cases first.")