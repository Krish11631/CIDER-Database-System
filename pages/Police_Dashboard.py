import streamlit as st
from database import run_query


if st.session_state.get('role') not in ['Police', 'Admin']:
    st.error("Access Denied: Police clearance required.")
    st.stop()


st.title("Police Dashboard")
st.caption("Courage is not the absence of fear, but the decision to stand between danger and the innocent.")

#Written the login details in side and automatically opens up acc to login details
with st.sidebar:
    st.write(f"Logged in as: {st.session_state.get('role')} (ID: {st.session_state.get('user_id')})")
    if st.button("Logout", type="primary"):
        st.session_state['logged_in'] = False
        st.session_state['role'] = None
        st.session_state['user_id'] = None
        st.switch_page("Login_Page.py")

st.divider()

tab1, tab2, tab3 = st.tabs(["Cases Under My Charge", "Update Case Status", "Evidence Submission Desk"])
cases = run_query("SELECT Case_ID FROM CIDER_CRIME.CASE_FILE;")
officers = run_query("SELECT Officer_ID FROM CIDER_HR.OFFICER;")

# My Cases (Particular)
with tab1:
    officer_id = st.session_state.get("user_id")

    query = f"""SELECT cf.Case_ID, cf.Status
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

    if (not my_cases.empty):
        case_id = st.selectbox("Select Case", my_cases["Case_ID"])

        new_status = st.selectbox("Update Status", ["Active", "Pending", "Solved"])

        if (st.button("Update Status")):
            query = f"""UPDATE CIDER_CRIME.CASE_FILE
            SET Status = '{new_status}'
            WHERE Case_ID = {case_id};
            """

            run_query(query)

            st.toast("Updated!")
    else:
        st.info("No cases assigned.")

# Provide Evidence
with tab3:
    st.subheader("Add Evidence")

    case_id = st.selectbox("Select Case for Evidence", my_cases["Case_ID"])

    evidence_desc = st.text_input("Enter Evidence Description")

    if (st.button("Submit Evidence")):

        if (evidence_desc):
            query = f"""INSERT INTO CIDER_EVIDENCE.EVIDENCE (Case_ID, Description)
            VALUES ({case_id}, '{evidence_desc}');
            """

            run_query(query)

            st.success("Evidence submitted successfully.")
        else:
            st.warning("Please enter evidence details.")