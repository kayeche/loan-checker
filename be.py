import sqlite3
import pandas as pd
import streamlit as st

# Load the dataset into a database
def load_loan_dataset():
    conn = sqlite3.connect("data/indian_banks_education_loans.csv")
    cursor = conn.cursor()

    # Create the Loans Table (if not exists)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bank_name TEXT,
            loan_name TEXT,
            interest_rate REAL,
            max_loan_amount INTEGER,
            eligibility_criteria TEXT,
            repayment_period INTEGER,
            processing_fee REAL,
            required_documents TEXT
        )
    ''')

    # Check if data already exists
    cursor.execute("SELECT COUNT(*) FROM loans")
    if cursor.fetchone()[0] == 0:
        df = pd.read_csv("indian_banks_loans.csv")  # Load CSV
        df.to_sql("loans", conn, if_exists="append", index=False)  # Insert into DB

    conn.commit()
    conn.close()

# Register function
def register():
    st.subheader("Register")
    username = st.text_input("Enter Username")
    password = st.text_input("Enter Password", type="password")

    if st.button("Register"):
        conn = sqlite3.connect("loan_checker.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        st.success("Registration Successful. Please login.")

# Login function
def login():
    st.subheader("Login")
    username = st.text_input("Enter Username")
    password = st.text_input("Enter Password", type="password")

    if st.button("Login"):
        conn = sqlite3.connect("loan_checker.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()

        if user:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.success("Login Successful!")
        else:
            st.error("Invalid credentials")

    conn.close()

# Fetch loan recommendations
def recommend_loans():
    st.subheader("Loan Recommendations")
    
    # Get student details
    student_score = st.number_input("Enter your 12th or UG Percentage")
    max_loan_needed = st.number_input("Enter Maximum Loan Required (₹)")

    if st.button("Find Best Loans"):
        conn = sqlite3.connect("loan_checker.db")
        query = "SELECT * FROM loans WHERE max_loan_amount >= ?"
        df = pd.read_sql_query(query, conn, params=(max_loan_needed,))

        st.write("Recommended Loans:")
        st.dataframe(df)

        conn.close()
