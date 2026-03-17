import streamlit as st
from database import run_query
import pandas as pd

if st.session_state.get('role') not in ['ACP', 'Admin']:
    st.error("Access Denied: ACP clearance required.")
    st.stop()

with st.sidebar:
    st.write(f"Logged in as: **{st.session_state.get('role')}**")
    st.caption(f"ID: {st.session_state.get('user_id')}")
    st.divider()

    role = st.session_state.get('role')
    st.subheader("Navigation")
    
    if role == 'Admin':
        st.page_link("pages/Admin_Panel.py", label="Admin Panel", icon="🛡️")
    elif role == 'ACP':
        st.page_link("pages/ACP_Dashboard.py", label="ACP Dashboard", icon="🏢")
    elif role == 'Police':
        st.page_link("pages/Police_Dashboard.py", label="Police Dashboard", icon="🚓")
    elif role == 'Forensic':
        st.page_link("pages/Evidence_Room.py", label="Evidence Room", icon="🧬")
        
    st.divider()
    if st.button("Logout", type="primary", use_container_width=True):
        st.session_state['logged_in'] = False
        st.session_state['role'] = None
        st.session_state['user_id'] = None
        st.switch_page("Login_Page.py")


user_id = st.session_state.get('user_id')
try:
    user_info = run_query(f"SELECT Branch_ID FROM CIDER_HR.OFFICER WHERE Officer_ID = {user_id};")
    acp_branch_id = user_info['Branch_ID'].iloc[0] if not user_info.empty else 1
except:
    acp_branch_id = 1 

st.title("ACP Operations Dashboard")
st.caption(f"Monitor Branch {acp_branch_id}. Manage the force. Close the cases.")

st.divider()

tab1, tab2, tab3, tab4 = st.tabs(["Crime Hotspots", "Officer Workload", "Assign Case", "Search Cases"])

#Crime Hotspots
with tab1:
    st.subheader(f"Branch {acp_branch_id} Case Load by Crime Type")

    query = f"""SELECT Crime_Type, COUNT(*) AS Active_Cases
    FROM CIDER_CRIME.CASE_FILE
    WHERE Status != 'Solved' AND Branch_ID = {acp_branch_id}
    GROUP BY Crime_Type
    ORDER BY Active_Cases DESC;
    """
    data = run_query(query)

    if data is not None and not data.empty:
        col1, col2 = st.columns(2)

        total_cases = data["Active_Cases"].sum()
        total_types = len(data)

        col1.metric("Total Active Cases", total_cases)
        col2.metric("Different Crime Types", total_types)

        hotspot_cases = data["Active_Cases"].max()
        hotspot_type = data[data["Active_Cases"] == hotspot_cases]["Crime_Type"].values[0]

        st.info(f"The primary crime hotspot in your branch is {hotspot_type} with {hotspot_cases} active cases.")

        st.divider()
        st.subheader("Active Cases by Type")
        st.bar_chart(data.set_index("Crime_Type"))
    else:
        st.info("No active cases found for your branch.")

# Officer Workload
with tab2:
    st.subheader("Branch Officer Workload Dashboard")

    officers_df = run_query(f"SELECT Officer_ID FROM CIDER_HR.OFFICER WHERE Branch_ID = {acp_branch_id};")

    query = f"""SELECT co.Officer_ID, COUNT(co.Case_ID) AS Total_Cases
    FROM CIDER_CRIME.CASE_OFFICER co
    JOIN CIDER_HR.OFFICER o ON co.Officer_ID = o.Officer_ID
    WHERE o.Branch_ID = {acp_branch_id}
    GROUP BY co.Officer_ID;
    """
    data = run_query(query)

    col1, col2 = st.columns(2)
    col1.metric("Total Branch Officers", len(officers_df) if officers_df is not None else 0)
    
    if data is not None and not data.empty:
        col2.metric("Officers With Assigned Cases", len(data))

        st.divider()
        st.subheader("Cases per Officer")
        st.line_chart(data.set_index("Officer_ID"))

        st.divider()
        st.subheader("Officer Case Distribution")

        data_sorted = data.sort_values(by="Total_Cases", ascending=False)
        st.table(data_sorted)

        max_cases = data_sorted["Total_Cases"].max()
        busy = data_sorted[data_sorted["Total_Cases"] == max_cases]
        officer_ids = busy["Officer_ID"].to_list()

        st.info(f"Officer(s) {', '.join(map(str, officer_ids))} currently have the highest workload with {max_cases} cases.")
    else:
        col2.metric("Officers With Assigned Cases", 0)
        st.info("No cases currently assigned to your branch officers.")

# Assign Case
with tab3:
    st.subheader("Case Assignment Portal")

    cases_query = f"SELECT Case_ID FROM CIDER_CRIME.CASE_FILE WHERE Branch_ID = {acp_branch_id} AND Status != 'Solved';"
    cases = run_query(cases_query)
    
    officers_query = f"SELECT Officer_ID FROM CIDER_HR.OFFICER WHERE Branch_ID = {acp_branch_id};"
    officers = run_query(officers_query)

    if (cases is not None and not cases.empty) and (officers is not None and not officers.empty):
        st.markdown("### Case Information")
        case_id = st.selectbox("Select Active Case", cases["Case_ID"])

        case_info = run_query(f"SELECT Case_ID, Crime_Type, Status FROM CIDER_CRIME.CASE_FILE WHERE Case_ID = {case_id};")
        st.dataframe(case_info, use_container_width=True)

        st.divider()

        st.markdown("### Officer Information")
        officer_id = st.selectbox("Select Branch Officer", officers["Officer_ID"])

        officer_info = run_query(f"SELECT Officer_ID, Name, Officer_Rank, Branch_ID FROM CIDER_HR.OFFICER WHERE Officer_ID = {officer_id};")
        st.dataframe(officer_info, use_container_width=True)

        st.divider()

        if st.button("Assign Case to Officer"):
            check_query = f"SELECT * FROM CIDER_CRIME.CASE_OFFICER WHERE Case_ID = {case_id} AND Officer_ID = {officer_id};"
            check = run_query(check_query)

            if check is None or check.empty:
                run_query(f"INSERT INTO CIDER_CRIME.CASE_OFFICER (Case_ID, Officer_ID, Assigned_Date) VALUES ({case_id}, {officer_id}, CURDATE());")
                st.success(f"Case {case_id} successfully assigned to Officer {officer_id}.")
            else:
                st.warning("This case is already assigned to the selected officer.")
    else:
        st.info("You either have no unresolved cases or no available officers in your branch right now.")

# Case Search
with tab4:
    st.subheader("Global Case Search Portal")
    
    search_type = st.radio("Search By:", ["Case ID", "Crime Type", "Status"], horizontal=True)
    
    if search_type == "Case ID":
        search_val = st.number_input("Enter Case ID", min_value=1, step=1)
        query = f"SELECT * FROM CIDER_CRIME.CASE_FILE WHERE Case_ID = {search_val};"
        
    elif search_type == "Crime Type":
        search_val = st.text_input("Enter Crime Type (e.g., Robbery, Fraud)")
        query = f"SELECT * FROM CIDER_CRIME.CASE_FILE WHERE Crime_Type LIKE '%{search_val}%';"
        
    else: # Status
        search_val = st.selectbox("Select Status", ["Active", "Pending", "Solved"])
        query = f"SELECT * FROM CIDER_CRIME.CASE_FILE WHERE Status = '{search_val}';"

    if st.button("Search Cases", type="primary"):
        try:
            results = run_query(query)
            if results is not None and not results.empty:
                st.success(f"Found {len(results)} matching records.")
                st.dataframe(results, use_container_width=True)
            else:
                st.warning("No cases found matching your criteria.")
        except Exception as e:
            st.error(f"Database Error: {e}")