import streamlit as st
from database import run_query
import pandas as pd
import time

# Access control
if st.session_state.get('role') != 'Forensic':
    st.error("Access Denied: Forensic Department Only")
    st.stop()

with st.sidebar:
    st.write(f"Logged in as: {st.session_state.get('role')} (ID: {st.session_state.get('user_id')})")
    if st.button("Logout", type="primary"):
        st.session_state['logged_in'] = False
        st.session_state['role'] = None
        st.session_state['user_id'] = None
        st.switch_page("loginpage.py")

st.title("🧬 Forensic Evidence Management System")

try:
    total_ev = run_query("SELECT COUNT(*) as total FROM CIDER_EVIDENCE.EVIDENCE")
    case_ev = run_query("SELECT COUNT(DISTINCT Case_ID) as cases FROM CIDER_EVIDENCE.EVIDENCE")
except:
    total_ev = pd.DataFrame({"total":[0]})
    case_ev = pd.DataFrame({"cases":[0]})

col1, col2 = st.columns(2)

col1.metric("Total Evidence Records", total_ev["total"][0])
col2.metric("Cases with Evidence", case_ev["cases"][0])

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Evidence Records",
    "Add Evidence",
    "Update Analysis",
    "Search by Case",
    "Evidence Summary"
])

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
with tab2:
    st.subheader("Register New Evidence")
    with st.form("add_evidence_form"):
        ev_id = st.number_input("Evidence ID", min_value=1, step=1)
        ev_type = st.selectbox(
            "Evidence Type",
            ["Physical","Digital","Fingerprint","DNA","Weapon","Other"]
        )
        analysis = st.text_area("Analysis Log")
        storage = st.text_input("Storage Location")
        case_id = st.number_input("Case ID", min_value=1, step=1)
        submit = st.form_submit_button("Add Evidence")
        if submit:
            try:
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
with tab4:
    st.subheader("Search Evidence by Case ID")
    case_search = st.number_input("Enter Case ID", min_value=1, step=1)
    if st.button("Search"):
        try:
            query = f"""
            SELECT *
            FROM CIDER_EVIDENCE.EVIDENCE
            WHERE Case_ID = {case_search}
            """
            df = run_query(query)
            if df.empty:
                st.warning("No evidence found for this case")
            else:
                st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Database Error: {e}")

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