import streamlit as st
from database import run_query
import time
from streamlit_autorefresh import st_autorefresh

count = st_autorefresh(3000)

st.markdown("""
<style>

/* Hide sidebar completely */
[data-testid="stSidebar"] {display:none;}
[data-testid="stSidebarNav"] {display:none;}
div[data-testid="collapsedControl"] {display:none;}

/* Dark control-room background */
.stApp{
background: linear-gradient(180deg,#0b1120,#020617);
color:white;
}

/* Header bar */
.header-bar{
background:#020617;
padding:12px 20px;
border-radius:10px;
border:1px solid #1e293b;
margin-bottom:20px;
}

/* Title */
.dashboard-title{
font-size:56px;
font-weight:800;
letter-spacing:1px;
background: linear-gradient(90deg,#3b82f6,#06b6d4);
-webkit-background-clip:text;
-webkit-text-fill-color:transparent;
margin-bottom:10px;
}

/* Tabs styling */
.stTabs [role="tab"]{
background:#020617;
border:1px solid #1e293b;
padding:10px 18px;
border-radius:8px;
margin-right:6px;
font-weight:600;
}

.stTabs [aria-selected="true"]{
background:#303641;
color:white;
}

/* Metric cards */
[data-testid="stMetric"]{
background:#020617;
border:1px solid #1e293b;
padding:20px;
border-radius:12px;
}

/* Buttons */
.stButton>button{
background: linear-gradient(90deg,#2563eb,#0ea5e9);
color:white;
border:none;
border-radius:8px;
font-weight:600;
padding:8px 16px;
}

.stButton>button:hover{
background: linear-gradient(90deg,#1d4ed8,#0284c7);
}

/* Logout button */
div[data-testid="stButton"]:last-child button{
background: linear-gradient(90deg,#dc2626,#ef4444);
}

div[data-testid="stButton"]:last-child button:hover{
background: linear-gradient(90deg,#b91c1c,#dc2626);
}

/* Tables */
[data-testid="stDataFrame"]{
border-radius:10px;
overflow:hidden;
border:1px solid #1e293b;
}

/* Forms */
form{
background:#020617;
padding:20px;
border-radius:10px;
border:1px solid #1e293b;
}

</style>
""", unsafe_allow_html=True)


if st.session_state.get('role') != 'Admin':
    st.error("Access Denied: Administrator clearance required.")
    st.stop()

officers = run_query("SELECT Officer_ID FROM CIDER_HR.OFFICER;")

# Header
st.write('<div class="dashboard-title">DGP Admin Panel</div>', unsafe_allow_html=True)

st.markdown("""
<div class="header-bar">
<b>Police Headquarters Control Panel</b><br>
Administrative command interface for officer management
</div>
""", unsafe_allow_html=True)


tab1, tab2, tab3, tab4 = st.tabs(["Directory", "Recruit", "Transfer", "Terminate"])


# List of all Officers
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


# Recruit new Officer
with tab2:

    st.subheader("Recruit New Officer")

    try:
        df_branches = run_query("SELECT Branch_ID FROM CIDER_HR.BRANCH;")
        valid_branches = df_branches['Branch_ID'].tolist()
    except Exception:
        valid_branches = []

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



# Transfer officer
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



# Terminate officer
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

# Logout
st.divider()

if st.button("Logout"):
    st.session_state['logged_in'] = False
    st.session_state['role'] = None
    st.session_state['user_id'] = None
    st.switch_page("Login_Page.py")