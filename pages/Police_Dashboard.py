import streamlit as st
from database import run_query
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


tab1, tab2, tab3, tab4 = st.tabs([
    "Cases Under My Charge",
    "Update Case Status",
    "Evidence Submission Desk",
    "File New Case"
])


cases = run_query("SELECT Case_ID FROM CIDER_CRIME.CASE_FILE;")
officers = run_query("SELECT Officer_ID FROM CIDER_HR.OFFICER;")
branch_df = run_query(
    f"SELECT Branch_ID FROM CIDER_HR.OFFICER WHERE Officer_ID = {st.session_state.get('user_id')};"
)
all_branches = run_query("SELECT Branch_ID FROM CIDER_HR.BRANCH ORDER BY Branch_ID;")


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

        final_criminal_ids = []

        if new_status == "Solved":
            suspects_df = run_query(
                f"""
                SELECT cc.Criminal_ID, c.Name, cc.Role_In_Case
                FROM CIDER_CRIME.CASE_CRIMINAL cc
                JOIN CIDER_CRIME.CRIMINAL c
                  ON cc.Criminal_ID = c.Criminal_ID
                WHERE cc.Case_ID = {case_id}
                ORDER BY cc.Criminal_ID;
                """
            )

            if suspects_df is not None and not suspects_df.empty:
                suspect_options = [
                    f"{int(row['Criminal_ID'])} - {row['Name']} ({row['Role_In_Case']})"
                    for _, row in suspects_df.iterrows()
                ]

                selected_suspects = st.multiselect(
                    "Select Final Criminal(s)",
                    options=suspect_options,
                    help="Selected suspects will be marked as Convicted for this case."
                )

                final_criminal_ids = [int(item.split(" - ")[0]) for item in selected_suspects]
            else:
                st.info("No suspects linked to this case yet. You can still mark case as solved.")

        if st.button("Update Status"):

            try:
                query = f"""
                UPDATE CIDER_CRIME.CASE_FILE
                SET Status = '{new_status}'
                WHERE Case_ID = {case_id};
                """

                run_query(query)

                if new_status == "Solved" and final_criminal_ids:
                    for criminal_id in final_criminal_ids:
                        update_role_query = f"""
                        UPDATE CIDER_CRIME.CASE_CRIMINAL
                        SET Role_In_Case = 'Convicted'
                        WHERE Case_ID = {case_id}
                          AND Criminal_ID = {criminal_id};
                        """
                        run_query(update_role_query)

                    st.success("Case marked as solved and final criminals updated.")
                else:
                    st.toast("Updated!")

            except Exception as e:
                st.error(f"Database Error: {e}")

    else:
        st.info("No cases assigned.")



# Evidence Submission
with tab3:

    st.subheader("Register New Evidence")

    if my_cases.empty:
        st.info("No cases assigned.")
    else:

        eligible_cases = my_cases[
            my_cases["Status"].astype(str).str.lower() != "solved"
        ]

        if eligible_cases.empty:
            st.warning("All assigned cases are solved. Evidence cannot be added.")
        else:

            with st.form("police_add_evidence_form"):

                ev_id = st.number_input("Evidence ID", min_value=1, step=1)

                ev_type = st.selectbox(
                    "Evidence Type",
                    ["Physical", "Digital", "Fingerprint", "DNA", "Weapon", "Other"]
                )

                analysis = st.text_area("Analysis Log")
                storage = st.text_input("Storage Location")

                selected_case_id = st.selectbox(
                    "Select Case ID",
                    options=eligible_cases["Case_ID"].tolist()
                )

                submit = st.form_submit_button("Add Evidence")

                if submit:

                    selected_case_status = my_cases.loc[
                        my_cases["Case_ID"] == selected_case_id, "Status"
                    ].iloc[0]

                    if str(selected_case_status).strip().lower() == "solved":
                        st.error("Cannot add evidence to a solved case.")
                    else:
                        try:

                            insert_query = f"""
                            INSERT INTO CIDER_EVIDENCE.EVIDENCE
                            (Evidence_ID, Evidence_Type, Analysis_Log, Storage_Location, Case_ID)
                            VALUES
                            ({ev_id}, '{ev_type}', '{analysis}', '{storage}', {selected_case_id})
                            """

                            run_query(insert_query)

                            st.success("Evidence registered successfully")

                            time.sleep(1)
                            st.rerun()

                        except Exception as e:
                            st.error(f"Database Error: {e}")


# File New Case
with tab4:

    st.subheader("File FIR / New Case")

    user_role = st.session_state.get("role")
    officer_id = st.session_state.get("user_id")

    officer_branch_id = None
    if branch_df is not None and not branch_df.empty:
        officer_branch_id = int(branch_df["Branch_ID"].iloc[0])

    next_case_df = run_query(
        "SELECT COALESCE(MAX(Case_ID), 1000) + 1 AS Next_Case_ID FROM CIDER_CRIME.CASE_FILE;"
    )
    default_case_id = 1001
    if next_case_df is not None and not next_case_df.empty:
        default_case_id = int(next_case_df["Next_Case_ID"].iloc[0])

    with st.form("file_new_case_form"):

        st.text_input("Case ID (Auto Generated)", value=str(default_case_id), disabled=True)
        paper_number = st.text_input("FIR / Paper Number")

        crime_type = st.selectbox("Crime Type", ["Normal", "Terrorism"])

        incident_date = st.date_input("Incident Date")
        incident_time = st.time_input("Incident Time")

        location = st.text_input("Incident Location")
        description = st.text_area("Case Description")

        if user_role == "Admin":
            if all_branches is not None and not all_branches.empty:
                selected_branch_id = st.selectbox("Branch ID", all_branches["Branch_ID"])
            else:
                selected_branch_id = None
                st.warning("No branches found in database.")
        else:
            selected_branch_id = officer_branch_id
            st.caption(f"Branch ID: {selected_branch_id}")

        submit_case = st.form_submit_button("File Case")

        if submit_case:

            paper_number_clean = paper_number.strip()
            location_clean = location.strip()
            description_clean = description.strip().replace("'", "''")

            if not paper_number_clean:
                st.warning("FIR / Paper Number is required.")
            elif not location_clean:
                st.warning("Incident Location is required.")
            elif selected_branch_id is None:
                st.warning("Branch is required to file a case.")
            else:
                try:
                    next_case_df_submit = run_query(
                        "SELECT COALESCE(MAX(Case_ID), 1000) + 1 AS Next_Case_ID FROM CIDER_CRIME.CASE_FILE;"
                    )
                    new_case_id = default_case_id
                    if next_case_df_submit is not None and not next_case_df_submit.empty:
                        new_case_id = int(next_case_df_submit["Next_Case_ID"].iloc[0])

                    duplicate_paper = run_query(
                        f"SELECT Case_ID FROM CIDER_CRIME.CASE_FILE WHERE Paper_Number = '{paper_number_clean.replace("'", "''")}';"
                    )

                    if duplicate_paper is not None and not duplicate_paper.empty:
                        st.error("FIR / Paper Number already exists. Use a unique value.")
                    else:
                        insert_case_query = f"""
                        INSERT INTO CIDER_CRIME.CASE_FILE
                        (Case_ID, Crime_Type, Description, Paper_Number, Incident_Date, Incident_Time, Location, Status, Branch_ID)
                        VALUES
                        ({new_case_id}, '{crime_type}', '{description_clean}', '{paper_number_clean.replace("'", "''")}', '{incident_date}', '{incident_time}', '{location_clean.replace("'", "''")}', 'Active', {selected_branch_id});
                        """

                        run_query(insert_case_query)

                        officer_exists = run_query(
                            f"SELECT Officer_ID FROM CIDER_HR.OFFICER WHERE Officer_ID = {officer_id};"
                        )

                        if officer_exists is not None and not officer_exists.empty:
                            assign_query = f"""
                            INSERT INTO CIDER_CRIME.CASE_OFFICER (Case_ID, Officer_ID, Assigned_Date)
                            VALUES ({new_case_id}, {officer_id}, CURDATE());
                            """
                            run_query(assign_query)

                        st.success(f"Case {new_case_id} filed successfully.")
                        time.sleep(1)
                        st.rerun()

                except Exception as e:
                    st.error(f"Database Error: {e}")


st.divider()


# LOGOUT BUTTON (BOTTOM)
st.markdown('<div class="logout-red">', unsafe_allow_html=True)

if st.button("Logout", key="logout_btn"):
    st.session_state.clear()
    st.switch_page("Login_Page.py")

st.markdown('</div>', unsafe_allow_html=True)