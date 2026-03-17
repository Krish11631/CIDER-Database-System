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
                            # 1. Force all column names to lowercase so we never miss one
                            runner.columns = [col.lower() for col in runner.columns]
                            
                            # 2. Extract rank safely
                            if 'officer_rank' in runner.columns:
                                db_rank = runner['officer_rank'].iloc[0]
                            elif 'rank' in runner.columns:
                                db_rank = runner['rank'].iloc[0]
                            else:
                                db_rank = "Unknown"
                                
                            # 3. Extract branch safely
                            if 'branch_id' in runner.columns:
                                db_branch = runner['branch_id'].iloc[0]
                            else:
                                db_branch = 1
                            
                            valid_login = False
                            final_rank = str(db_rank).strip().lower()
                            
                            # Validate dropdown role against actual database rank/branch
                            # ADDED "dgp" TO THE ADMIN CHECK HERE!
                            if role == "Admin" and ("admin" in final_rank or "dgp" in final_rank):
                                valid_login = True
                            elif role == "ACP" and "acp" in final_rank:
                                valid_login = True
                            elif role == "Police" and final_rank in ["constable", "sub-inspector", "inspector", "police"]:
                                valid_login = True
                            elif role == "Forensic" and db_branch == 3:
                                valid_login = True
                                
                            if valid_login:
                                st.session_state['logged_in'] = True
                                st.session_state['role'] = role
                                st.session_state['user_id'] = entered_id
                                
                                st.success("Login Successful")
                                st.rerun()
                            else:
                                st.error(f"Access Denied: ID {entered_id} does not have {role} privileges. (Database rank found: '{final_rank}')")
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
    
    # Automatically route the user to their specific dashboard
    if role == "Admin":
        st.switch_page("pages/Admin_Panel.py")
    elif role == "ACP":
        st.switch_page("pages/ACP_Dashboard.py")
    elif role == "Police":
        st.switch_page("pages/Police_Dashboard.py")
    elif role == "Forensic":
        st.switch_page("pages/Evidence_Room.py")