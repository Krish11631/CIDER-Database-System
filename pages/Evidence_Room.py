import streamlit as st
from database import run_query
import pandas as pd
import time

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


# Access control
if st.session_state.get('role') not in ['Forensic', 'Admin']:
    st.error("Access Denied: Forensic Department Only")
    st.stop()

if st.session_state.get('role') != 'Forensic':
    st.error("Access Denied: Forensic Department Only")
    st.stop()


# TITLE
st.write('<div class="dashboard-title">Forensic Dashboard</div>', unsafe_allow_html=True)

st.markdown("""
<div class="header-bar">
<b>Forensic Evidence Control Center</b><br>
Analyze, track and manage forensic evidence across cases.
</div>
""", unsafe_allow_html=True)

st.caption("Science speaks where witnesses fail.")

st.divider()


# METRICS
try:
    total_ev = run_query("SELECT COUNT(*) as total FROM CIDER_EVIDENCE.EVIDENCE")
    case_ev = run_query("SELECT COUNT(DISTINCT Case_ID) as cases FROM CIDER_EVIDENCE.EVIDENCE")
except:
    total_ev = pd.DataFrame({"total":[0]})
    case_ev = pd.DataFrame({"cases":[0]})

col1, col2 = st.columns(2)

col1.metric("Total Evidence Records", total_ev["total"][0])
col2.metric("Cases with Evidence", case_ev["cases"][0])


# TABS
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Evidence Records",
    "Add Evidence",
    "Update Analysis",
    "Search by Case",
    "Evidence Summary"
])


# VIEW EVIDENCE
with tab1:

    st.subheader("All Evidence Records")

    try:
        query = """
        SELECT Evidence_ID, Evidence_Type, Analysis_Log,
        Storage_Location, Case_ID
        FROM CIDER_EVIDENCE.EVIDENCE
        """

        df = run_query(query)

        st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"Error loading records: {e}")


# ADD EVIDENCE
with tab2:

    st.subheader("Register New Evidence")

    case_ids_df = run_query("SELECT Case_ID FROM CIDER_CRIME.CASE_FILE ORDER BY Case_ID;")

    with st.form("add_evidence_form"):

        ev_id = st.number_input("Evidence ID", min_value=1, step=1)

        ev_type = st.selectbox(
            "Evidence Type",
            ["Physical","Digital","Fingerprint","DNA","Weapon","Other"]
        )

        analysis = st.text_area("Analysis Log")
        storage = st.text_input("Storage Location")

        if case_ids_df is not None and not case_ids_df.empty:
            case_id = st.selectbox("Case ID", case_ids_df["Case_ID"])
        else:
            case_id = None
            st.info("No case IDs available in database.")

        submit = st.form_submit_button("Add Evidence")

        if submit:

            try:

                if case_id is None:
                    st.warning("Cannot add evidence without a valid Case ID.")
                else:

                    insert_query = f"""
                    INSERT INTO CIDER_EVIDENCE.EVIDENCE
                    (Evidence_ID, Evidence_Type, Analysis_Log, Storage_Location, Case_ID)
                    VALUES
                    ({ev_id}, '{ev_type}', '{analysis}', '{storage}', {case_id})
                    """

                    run_query(insert_query)

                    st.success("Evidence registered successfully")

                    time.sleep(1)
                    st.rerun()

            except Exception as e:
                st.error(f"Database Error: {e}")


# UPDATE ANALYSIS
with tab3:

    st.subheader("Update Evidence Analysis Log")

    with st.form("update_analysis_form"):

        ev_id_update = st.number_input("Evidence ID", min_value=1, step=1)

        new_analysis = st.text_area("Updated Analysis Log")

        submit_update = st.form_submit_button("Update")

        if submit_update:

            try:

                update_query = f"""
                UPDATE CIDER_EVIDENCE.EVIDENCE
                SET Analysis_Log = '{new_analysis}'
                WHERE Evidence_ID = {ev_id_update}
                """

                run_query(update_query)

                st.success("Analysis updated successfully")

                time.sleep(1)
                st.rerun()

            except Exception as e:
                st.error(f"Database Error: {e}")


# SEARCH CASE
with tab4:

    st.markdown("""
    ### Case Intelligence Search
    Search the entire crime database by case ID, crime type, or status.
    """)
    
    case_ids_df = run_query("SELECT Case_ID FROM CIDER_CRIME.CASE_FILE ORDER BY Case_ID;")
    crime_types_df = run_query("SELECT DISTINCT Crime_Type FROM CIDER_CRIME.CASE_FILE WHERE Crime_Type IS NOT NULL ORDER BY Crime_Type;")

    search_type = st.radio("Search By:", ["Case ID", "Crime Type", "Status"], horizontal=True)
    
    if search_type == "Case ID":
        if case_ids_df is not None and not case_ids_df.empty:
            search_val = st.selectbox("Select Case ID", case_ids_df["Case_ID"])
            query = f"SELECT * FROM CIDER_CRIME.CASE_FILE WHERE Case_ID = {search_val};"
        else:
            query = None
            st.info("No case IDs available in database.")
        
    elif search_type == "Crime Type":
        if crime_types_df is not None and not crime_types_df.empty:
            search_val = st.selectbox("Select Crime Type", crime_types_df["Crime_Type"])
            query = f"SELECT * FROM CIDER_CRIME.CASE_FILE WHERE Crime_Type = '{search_val}';"
        else:
            query = None
            st.info("No crime types available in database.")
        
    else: 
        search_val = st.selectbox("Select Status", ["Active", "Pending", "Solved"])
        query = f"SELECT * FROM CIDER_CRIME.CASE_FILE WHERE Status = '{search_val}';"

    if st.button("Search Cases", type="primary"):
        try:
            if query is None:
                st.warning("No search query could be created.")
            else:
                results = run_query(query)
                if results is not None and not results.empty:
                    st.success(f"Found {len(results)} matching records.")
                    st.dataframe(results, use_container_width=True)
                else:
                    st.warning("No cases found matching your criteria.")
        except Exception as e:
            st.error(f"Database Error: {e}")

# SUMMARY
with tab5:

    st.subheader("Evidence Count per Case")

    try:

        query = """
        SELECT Case_ID, COUNT(*) as Evidence_Count
        FROM CIDER_EVIDENCE.EVIDENCE
        GROUP BY Case_ID
        """

        df = run_query(query)

        if not df.empty:
            st.dataframe(df)
            st.bar_chart(df.set_index("Case_ID"))
        else:
            st.info("No evidence data available")

    except Exception as e:
        st.error(f"Error generating report: {e}")


st.divider()


# LOGOUT BUTTON (BOTTOM)
st.markdown('<div class="logout-red">', unsafe_allow_html=True)

if st.button("Logout", key="logout_btn"):
    st.session_state.clear()
    st.switch_page("Login_Page.py")

st.markdown('</div>', unsafe_allow_html=True)