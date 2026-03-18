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
/* Logout button (last button on page) */
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

if st.session_state.get('role') not in ['ACP', 'Admin']:
    st.error("Access Denied: ACP clearance required.")
    st.stop()

user_id = st.session_state.get('user_id')
try:
    user_info = run_query(f"SELECT Name, Branch_ID FROM CIDER_HR.OFFICER WHERE Officer_ID = {user_id};")
    if user_info is not None and not user_info.empty:
        acp_name = user_info['Name'].iloc[0]
        acp_branch_id = user_info['Branch_ID'].iloc[0]
    else:
        acp_name = "Unknown"
        acp_branch_id = 1 
except:
    acp_name = "Error"
    acp_branch_id = 1 

st.write('<div class="dashboard-title">ACP Dashboard</div>', unsafe_allow_html=True)

st.markdown(
    f"""
    <div class="header-bar">
    <b>ACP Command Center</b><br>
    Officer: {acp_name.upper()} | Branch {acp_branch_id}
    </div>
    """,
    unsafe_allow_html=True
)

st.caption(f"Monitor Branch {acp_branch_id}. Manage the force. Close the cases.")

st.divider()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Crime Hotspots",
    "Officer Workload",
    "Assign Case",
    "Search Cases",
    "Add Suspect"
])

with tab1:
    st.markdown("""
    ### Branch Crime Activity
    Identify the most active crime categories in the branch.
    """)

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

        col1.metric("Total Active Cases", int(total_cases))
        col2.metric("Different Crime Types", total_types)

        hotspot_cases = data["Active_Cases"].max()
        hotspot_type = data[data["Active_Cases"] == hotspot_cases]["Crime_Type"].values[0]

        st.markdown(f"""
        <div style="
        background:#020617;
        border:1px solid #1e293b;
        padding:18px;
        border-radius:10px;
        margin-top:10px;
        font-size:16px;
        ">
        🔥 <b>Crime Hotspot Detected</b><br>
        {hotspot_type} currently has <b>{hotspot_cases}</b> active cases in this branch.
        </div>
        """, unsafe_allow_html=True)

        st.divider()
        st.subheader("Active Cases by Type")
        st.bar_chart(data.set_index("Crime_Type"))
    else:
        st.info("No active cases found for your branch.")

with tab2:
    st.markdown("""
    ### Officer Workload Analysis
    Track officer assignment load and identify overburdened personnel.
    """)

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
        st.dataframe(data_sorted, use_container_width=True, height=300)

        max_cases = data_sorted["Total_Cases"].max()
        busy = data_sorted[data_sorted["Total_Cases"] == max_cases]
        officer_ids = busy["Officer_ID"].to_list()

        st.info(f"Officer(s) {', '.join(map(str, officer_ids))} currently have the highest workload with {max_cases} cases.")
    else:
        col2.metric("Officers With Assigned Cases", 0)
        st.info("No cases currently assigned to your branch officers.")

with tab3:
    st.markdown("""
    ### Case Assignment Portal
    Assign unresolved cases to available branch officers.
    """)

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

with tab5:
    st.markdown("""
    ### Suspect Intake Desk
    Add a suspect to a branch case using Case ID and map role in the investigation.
    """)

    case_options = run_query(
        f"""
        SELECT Case_ID
        FROM CIDER_CRIME.CASE_FILE
        WHERE Branch_ID = {acp_branch_id}
        ORDER BY Case_ID;
        """
    )

    existing_criminals = run_query(
        """
        SELECT Criminal_ID, Name, Age
        FROM CIDER_CRIME.CRIMINAL
        ORDER BY Criminal_ID;
        """
    )

    next_criminal_df = run_query(
        "SELECT COALESCE(MAX(Criminal_ID), 900) + 1 AS Next_Criminal_ID FROM CIDER_CRIME.CRIMINAL;"
    )
    default_criminal_id = 901
    if next_criminal_df is not None and not next_criminal_df.empty:
        default_criminal_id = int(next_criminal_df["Next_Criminal_ID"].iloc[0])

    if case_options is None or case_options.empty:
        st.info("No cases found in your branch to map suspects.")
    else:
        with st.form("acp_add_suspect_form"):

            selected_case_id = st.selectbox("Select Case ID", case_options["Case_ID"])
            suspect_mode = st.radio(
                "Suspect Source",
                ["Use Existing Suspect", "Create New Suspect"],
                horizontal=True
            )

            role_in_case = st.selectbox(
                "Role In Case",
                ["Suspect", "Accused", "Convicted", "Associate", "Unknown"]
            )

            if suspect_mode == "Use Existing Suspect":
                if existing_criminals is not None and not existing_criminals.empty:
                    selected_criminal_id = st.selectbox(
                        "Select Criminal ID",
                        existing_criminals["Criminal_ID"]
                    )

                    selected_row = existing_criminals[
                        existing_criminals["Criminal_ID"] == selected_criminal_id
                    ]
                    if not selected_row.empty:
                        st.caption(
                            f"Name: {selected_row['Name'].iloc[0]} | Age: {selected_row['Age'].iloc[0]}"
                        )
                else:
                    selected_criminal_id = None
                    st.warning("No existing suspects found. Choose 'Create New Suspect'.")
            else:
                st.text_input(
                    "Criminal ID (Auto Generated)",
                    value=str(default_criminal_id),
                    disabled=True
                )
                new_name = st.text_input("Suspect Name")
                new_age = st.number_input("Age", min_value=1, max_value=120, step=1)
                new_history = st.text_area("Previous Crime History")

            submit_suspect = st.form_submit_button("Add Suspect To Case")

            if submit_suspect:
                try:
                    if selected_case_id is None:
                        st.warning("Please select a valid case.")
                    else:
                        if suspect_mode == "Use Existing Suspect":
                            if selected_criminal_id is None:
                                st.warning("No suspect selected.")
                            else:
                                link_exists = run_query(
                                    f"""
                                    SELECT 1
                                    FROM CIDER_CRIME.CASE_CRIMINAL
                                    WHERE Case_ID = {selected_case_id}
                                      AND Criminal_ID = {selected_criminal_id};
                                    """
                                )

                                if link_exists is not None and not link_exists.empty:
                                    st.warning("This suspect is already linked with the selected case.")
                                else:
                                    run_query(
                                        f"""
                                        INSERT INTO CIDER_CRIME.CASE_CRIMINAL
                                        (Case_ID, Criminal_ID, Role_In_Case)
                                        VALUES
                                        ({selected_case_id}, {selected_criminal_id}, '{role_in_case}');
                                        """
                                    )
                                    st.success("Suspect linked to case successfully.")
                        else:
                            name_clean = new_name.strip().replace("'", "''")
                            history_clean = new_history.strip().replace("'", "''")

                            if not name_clean:
                                st.warning("Suspect name is required.")
                            else:
                                next_criminal_df_submit = run_query(
                                    "SELECT COALESCE(MAX(Criminal_ID), 900) + 1 AS Next_Criminal_ID FROM CIDER_CRIME.CRIMINAL;"
                                )
                                selected_criminal_id = default_criminal_id
                                if next_criminal_df_submit is not None and not next_criminal_df_submit.empty:
                                    selected_criminal_id = int(next_criminal_df_submit["Next_Criminal_ID"].iloc[0])

                                run_query(
                                    f"""
                                    INSERT INTO CIDER_CRIME.CRIMINAL
                                    (Criminal_ID, Name, Age, Previous_Crime_History)
                                    VALUES
                                    ({selected_criminal_id}, '{name_clean}', {new_age}, '{history_clean}');
                                    """
                                )

                                run_query(
                                    f"""
                                    INSERT INTO CIDER_CRIME.CASE_CRIMINAL
                                    (Case_ID, Criminal_ID, Role_In_Case)
                                    VALUES
                                    ({selected_case_id}, {selected_criminal_id}, '{role_in_case}');
                                    """
                                )

                                st.success(
                                    f"New suspect created and linked to case successfully. Criminal ID: {selected_criminal_id}"
                                )
                                time.sleep(1)
                                st.rerun()

                except Exception as e:
                    st.error(f"Database Error: {e}")

st.divider()

st.markdown('<div class="logout-red">', unsafe_allow_html=True)

if st.button("Logout", key="logout_btn"):
    st.session_state.clear()
    st.switch_page("Login_Page.py")

st.markdown('</div>', unsafe_allow_html=True)