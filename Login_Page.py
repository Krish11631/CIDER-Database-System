import streamlit as st
from database import run_query

st.set_page_config(page_title="CIDER Login", layout="centered")

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'role' not in st.session_state:
    st.session_state['role'] = None
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None

if not st.session_state['logged_in']:
    st.title("CIDER System")
    st.write("Please log in with your credentials.")
    
    with st.form("login_form"):
        role = st.selectbox("Select Role", ["Admin", "ACP", "Police", "Forensic"])
        entered_id = st.text_input("Officer / Employee ID", type="password")
        entered_passkey = st.text_input("Passkey", type="password")
        
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if entered_id and entered_passkey:
                passkey = f"{role.lower()}{entered_id}"
                
                if entered_passkey.lower() == passkey:
                    try:
                        query = f"SELECT * FROM CIDER_HR.OFFICER WHERE Officer_ID = {entered_id};"
                        runner = run_query(query)

                        if not runner.empty:
                            st.session_state['logged_in'] = True
                            st.session_state['role'] = role
                            st.session_state['user_id'] = entered_id
                            
                            st.success("Login Successful")
                            st.rerun()
                        else:
                            st.error("Invalid ID")
                    except Exception as e:
                        st.error(f"Database error : {e}")
                else:
                    st.error("Invalid Passkey")
            else:
                st.error("Please enter both ID and Passkey")

else:
    role = st.session_state['role']
    
    if role == "Admin":
        st.switch_page("pages/Admin_Panel.py")
    elif role == "ACP":
        st.switch_page("pages/ACP_Dashboard.py")
    elif role == "Police":
        st.switch_page("pages/Police_Dashboard.py")
    elif role == "Forensic":
        st.switch_page("pages/Evidence_Room.py")