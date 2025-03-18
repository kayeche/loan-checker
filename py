import streamlit as st
import pandas as pd
from backend import load_loan_dataset, register, login, recommend_loans

st.title("🎓 Educational Loan Checker")

# Load the dataset when the app starts
load_loan_dataset()

menu = ["Login", "Register"]
choice = st.sidebar.selectbox("Menu", menu)

# Session state for login status
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    if choice == "Login":
        login()
    else:
        register()
else:
    st.sidebar.success(f"Logged in as {st.session_state['username']}")
    app_section = st.sidebar.radio("Go to", ["Loan Recommendations"])

    if app_section == "Loan Recommendations":
        recommend_loans()

    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False
        st.experimental_rerun()
