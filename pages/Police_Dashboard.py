import streamlit as st
from database import run_query

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
background:#2563eb;
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
color:white;
border:none;
border-radius:8px;
font-weight:600;
}

div[data-testid="stButton"]:last-child button:hover{
background: linear-gradient(90deg,#b91c1c,#dc2626);
}

/* Dashboard title */
.dashboard-title{
font-size:56px;
font-weight:800;
letter-spacing:1px;
background: linear-gradient(90deg,#3b82f6,#06b6d4);
-webkit-background-clip:text;
-webkit-text-fill-color:transparent;
margin-bottom:10px;
}

/* Tables */
[data-testid="stDataFrame"]{
border-radius:10px;
overflow:hidden;
border:1px solid #1e293b;
}

</style>
""", unsafe_allow_html=True)


if st.session_state.get('role') not in ['Police', 'Admin']:
    st.error("Access Denied: Police clearance required.")
    st.stop()


# DASHBOARD TITLE
st.write('<div class="dashboard-title">Police Dashboard</div>', unsafe_allow_html=True)

st.markdown(
"""
<div class="header-bar">
<b>Field Operations Panel</b><br>
Manage assigned cases and submit evidence.
</div>
""",
unsafe_allow_html=True
)

st.caption("Courage is not the absence of fear, but the decision to stand between danger and the innocent.")

st.divider()


tab1, tab2, tab3 = st.tabs([
    "Cases Under My Charge",
    "Update Case Status",
    "Evidence Submission Desk"
])


cases = run_query("SELECT Case_ID FROM CIDER_CRIME.CASE_FILE;")
officers = run_query("SELECT Officer_ID FROM CIDER_HR.OFFICER;")


# My Cases
with tab1:

    officer_id = st.session_state.get("user_id")

    query = f"""
    SELECT cf.Case_ID, cf.Status
    FROM CIDER_CRIME.CASE_FILE cf
    JOIN CIDER_CRIME.CASE_OFFICER co
    ON cf.Case_ID = co.Case_ID
    WHERE co.Officer_ID = {officer_id};
    """

    my_cases = run_query(query)

    st.dataframe(my_cases, use_container_width=True)



# Update Case Status
with tab2:

    st.subheader("Update Case Status")

    if not my_cases.empty:

        case_id = st.selectbox("Select Case", my_cases["Case_ID"])

        new_status = st.selectbox(
            "Update Status",
            ["Active", "Pending", "Solved"]
        )

        if st.button("Update Status"):

            query = f"""
            UPDATE CIDER_CRIME.CASE_FILE
            SET Status = '{new_status}'
            WHERE Case_ID = {case_id};
            """

            run_query(query)

            st.toast("Updated!")

    else:
        st.info("No cases assigned.")



# Evidence Submission
with tab3:

    st.subheader("Add Evidence")

    case_id = st.selectbox("Select Case for Evidence", my_cases["Case_ID"])

    evidence_desc = st.text_input("Enter Evidence Description")

    if st.button("Submit Evidence"):

        if evidence_desc:

            query = f"""
            INSERT INTO CIDER_EVIDENCE.EVIDENCE (Case_ID, Description)
            VALUES ({case_id}, '{evidence_desc}');
            """

            run_query(query)

            st.success("Evidence submitted successfully.")

        else:
            st.warning("Please enter evidence details.")


st.divider()


# LOGOUT BUTTON (BOTTOM)
st.markdown('<div class="logout-red">', unsafe_allow_html=True)

if st.button("Logout", key="logout_btn"):
    st.session_state.clear()
    st.switch_page("Login_Page.py")

st.markdown('</div>', unsafe_allow_html=True)