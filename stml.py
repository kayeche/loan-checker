import streamlit as st
import sqlite3
import bcrypt
import pandas as pd
import os

# Database setup
conn = sqlite3.connect("loan_checker.db", check_same_thread=False)
cursor = conn.cursor()

# Create users table (for authentication)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
''')

# Create students table (for storing student details)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        user_id INTEGER PRIMARY KEY,
        name TEXT,
        age INTEGER,
        dob TEXT,
        contact TEXT,
        address TEXT,
        caste TEXT,
        gpa REAL,
        transactions TEXT,
        certifications TEXT,
        exam_scores TEXT,
        tenth_marks TEXT,
        twelfth_marks TEXT,
        documents TEXT
    )
''')

conn.commit()

# Password hashing functions
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

# Function to register a new user
def register():
    st.subheader("Register")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Register"):
        if password != confirm_password:
            st.error("Passwords do not match!")
        else:
            try:
                hashed_password = hash_password(password)
                cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
                conn.commit()
                st.success("Registration successful! Please log in.")
            except sqlite3.IntegrityError:
                st.error("Username already exists. Choose a different one.")

# Function to login
def login():
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if user and check_password(password, user[0]):
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.success("Login successful!")
        else:
            st.error("Invalid credentials. Try again.")

# Function to enter student details
def student_details():
    st.subheader("Enter Student Details")
    
    name = st.text_input("Full Name")
    age = st.number_input("Age", min_value=16, max_value=100, step=1)
    dob = st.date_input("Date of Birth")
    contact = st.text_input("Contact Number")
    address = st.text_area("Address")
    caste = st.selectbox("Caste Category", ["General", "OBC", "SC", "ST", "Other"])
    gpa = st.number_input("GPA (Out of 10)", min_value=0.0, max_value=10.0, step=0.1)
    transactions = st.text_input("Transaction History (e.g., 'No Defaults, Regular Payer')")
    certifications = st.text_area("Certifications & Achievements")
    exam_scores = st.text_input("Scores from Competitive Exams (e.g., JEE: 90, CAT: 80)")
    
    tenth_marks = st.file_uploader("Upload 10th Marksheet", type=["pdf", "jpg", "png"])
    twelfth_marks = st.file_uploader("Upload 12th Marksheet", type=["pdf", "jpg", "png"])
    documents = st.file_uploader("Upload Additional Certifications", type=["pdf", "jpg", "png"], accept_multiple_files=True)
    
    if st.button("Save Details"):
        cursor.execute('''
            INSERT OR REPLACE INTO students 
            (user_id, name, age, dob, contact, address, caste, gpa, transactions, certifications, exam_scores, tenth_marks, twelfth_marks, documents)
            VALUES ((SELECT id FROM users WHERE username=?), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (st.session_state["username"], name, age, dob, contact, address, caste, gpa, transactions, certifications, exam_scores, str(tenth_marks), str(twelfth_marks), str([doc.name for doc in documents])))
        conn.commit()
        st.success("Details saved successfully!")

# Function to recommend loans based on student details
def recommend_loans():
    st.subheader("Loan Recommendations")

    cursor.execute("SELECT * FROM students WHERE user_id = (SELECT id FROM users WHERE username=?)", 
                   (st.session_state["username"],))
    student = cursor.fetchone()

    if student:
        name, age, dob, contact, address, caste, gpa, transactions, certifications, exam_scores, tenth_marks, twelfth_marks, documents = student[1:]
        
        recommended_loans = []
        
        if gpa > 8.0:
            recommended_loans.append("High GPA Loan (0% Interest for Top Students)")
        
        if "No Defaults" in transactions:
            recommended_loans.append("Premium Bank Loan (Low Interest for Good Transactions)")
        
        if caste in ["SC", "ST"]:
            recommended_loans.append("Government Subsidized Loan")
        
        if certifications or documents:
            recommended_loans.append("Skill-Based Education Loan")
        
        if not recommended_loans:
            recommended_loans.append("General Student Loan (Standard Rate)")
        
        st.write(f"**Hello, {name}! Based on your profile, these are the best loan options for you:**")
        for loan in recommended_loans:
            st.success(loan)
    else:
        st.warning("Please enter your details first!")

# Main app
def main():
    st.title("🎓 Educational Loan Checker")
    
    menu = ["Login", "Register"]
    choice = st.sidebar.selectbox("Menu", menu)

    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        if choice == "Login":
            login()
        else:
            register()
    else:
        st.sidebar.success("Logged in as " + st.session_state["username"])
        app_section = st.sidebar.radio("Go to", ["Student Details", "Loan Recommendations"])

        if app_section == "Student Details":
            student_details()
        elif app_section == "Loan Recommendations":
            recommend_loans()

        if st.sidebar.button("Logout"):
            st.session_state["logged_in"] = False
            st.experimental_rerun()

if __name__ == "__main__":
    main()