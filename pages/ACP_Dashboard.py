import streamlit as st
from database import run_query

st.title("ACP Operations Dashboard")
st.caption("Monitor the city. Manage the force. Close the cases.")

st.divider()

tab1, tab2, tab3 = st.tabs(["Crime Hotspots", "Officer Workload", "Assign Case"])
cases = run_query("SELECT Case_ID FROM CIDER_CRIME.CASE_FILE;")
officers = run_query("SELECT Officer_ID FROM CIDER_HR.OFFICER;")

# Branch with Most Active Cases 
with tab1:
    st.subheader("Branch Case Load (Crime Hotspots)")

    query = """SELECT Branch_ID, COUNT(*) AS Active_Cases
    FROM CIDER_CRIME.CASE_FILE
    WHERE Status='Active'
    GROUP BY Branch_ID
    ORDER BY Active_Cases DESC;
    """

    data = run_query(query)

    if (not data.empty):
        col1, col2 = st.columns(2)

        total_cases = data["Active_Cases"].sum()
        total_branches = len(data)

        col1.metric("Total Active Cases", total_cases)
        col2.metric("Branches Handling Cases", total_branches)

        hotspot_cases = data["Active_Cases"].max()
        hotspot_branch = data[data["Active_Cases"] == hotspot_cases]
        hotspot = hotspot_branch["Branch_ID"].values[0]

        st.info(f"Branch {hotspot} is currently the main crime hotspot with {hotspot_cases} active cases.")

        st.divider()

        st.subheader("Active Cases by Branch")

        st.bar_chart(data.set_index("Branch_ID"))

    else:
        st.info("No active cases found.")
# Number of Cases Handled by Each Officer
with tab2:
    st.subheader("Officer Workload Dashboard")

    query = """SELECT Officer_ID, COUNT(Case_ID) AS Total_Cases
    FROM CIDER_CRIME.CASE_OFFICER
    GROUP BY Officer_ID;
    """
    
    data = run_query(query)

    col1, col2 = st.columns(2)

    col1.metric("Total Officers", len(officers))
    col2.metric("Officers With Assigned Cases", len(data))

    st.divider()

    st.subheader("Cases per Officer")

    st.line_chart(data)

    st.divider()

    st.subheader("Officer Case Distribution")

    data_sorted = data.sort_values(by="Total_Cases", ascending=False)
    st.table(data_sorted)

    if (not data_sorted.empty):
        max_cases = data_sorted["Total_Cases"].max()

        busy = data_sorted[data_sorted["Total_Cases"] == max_cases]
        officer_ids = busy["Officer_ID"].to_list()

        st.info(
            f"Officer(s) {', '.join(map(str, officer_ids))} currently have the highest workload with {max_cases} cases."
        )

# Assign Case
with tab3:
    st.subheader("Case Assignment Portal")

    st.markdown("### Case Information")

    case_id = st.selectbox("Select Case", cases["Case_ID"])

    case_query = f"""SELECT Case_ID, Crime_Type, Status
    FROM CIDER_CRIME.CASE_FILE
    WHERE Case_ID = {case_id};
    """

    case_info = run_query(case_query)

    st.dataframe(case_info, use_container_width=True)

    st.divider()

    st.markdown("### Officer Information")

    officer_id = st.selectbox("Select Officer", officers["Officer_ID"])

    officer_query = f"""SELECT Officer_ID, Name, Officer_Rank, Branch_ID
    FROM CIDER_HR.OFFICER
    WHERE Officer_ID = {officer_id};
    """

    officer_info = run_query(officer_query)

    st.dataframe(officer_info, use_container_width=True)

    st.divider()

    if st.button("Assign Case to Officer"):
        check_query = f"""SELECT * FROM CIDER_CRIME.CASE_OFFICER
        WHERE Case_ID = {case_id} AND Officer_ID = {officer_id};
        """
        check = run_query(check_query)

        if(check.empty):
            query = f"""INSERT INTO CIDER_CRIME.CASE_OFFICER (Case_ID, Officer_ID, Assigned_Date)
            VALUES ({case_id}, {officer_id}, CURDATE());
            """

            run_query(query)

            st.success(f"Case {case_id} successfully assigned to Officer {officer_id}.")
        else:
            st.warning("This case is already assigned to the selected officer.")