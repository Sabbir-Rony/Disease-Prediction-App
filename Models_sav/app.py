# -*- coding: utf-8 -*-
"""
Created on Wed Oct 23 2025
@author: Sabbir Roni
"""

import streamlit as st
from streamlit_option_menu import option_menu
import mysql.connector
import pickle
import os

# ===============================
# 🧩 Database Connection Function
# ===============================
def connect_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",          
            database="disease1_db" 
        )
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None


# ===============================
# 🧩 Create User Table if not exist
# ===============================
def create_user_table():
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100),
            email VARCHAR(100),
            password VARCHAR(100)
        )
        """)
        conn.commit()
        conn.close()


# ===============================
# 🧩 Add user to database
# ===============================
def add_user(username, email, password):
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, email, password) VALUES (%s,%s,%s)", (username, email, password))
        conn.commit()
        conn.close()


# ===============================
# 🧩 Verify login user
# ===============================
def login_user(email, password):
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        data = cursor.fetchone()
        conn.close()
        return data


# ===============================
# 🧩 Load ML Models
# ===============================
def load_models():
    diabetes_model = pickle.load(open('diabetes_model.sav', 'rb'))
    heart_model = pickle.load(open('heart_disease_model.sav', 'rb'))
    parkinsons_model = pickle.load(open('parkinsons_model.sav', 'rb'))
    return diabetes_model, heart_model, parkinsons_model


# ===============================
# 🧩 Suggestion Function
# ===============================
def get_suggestion(disease_name):
    suggestions = {
        "diabetes": "🩸 Maintain a healthy diet, exercise regularly, and check blood sugar often.",
        "heart": "❤️ Avoid fatty foods, do light cardio, and manage stress properly.",
        "parkinsons": "🧠 Do physical therapy, take prescribed medicines, and stay active mentally."
    }
    return suggestions.get(disease_name.lower(), "Stay healthy and consult your doctor regularly.")


# ===============================
# 🧩 Main Streamlit App
# ===============================
def main():
    st.set_page_config(page_title="Multiple Disease Prediction", layout="wide")
    create_user_table()

    # Session state setup
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    # =========================
    # Login / Signup Section
    # =========================
    if not st.session_state.logged_in:
        st.title("🔐 Login or Sign Up")

        choice = st.radio("Select Option:", ["Login", "Sign Up"])

        if choice == "Sign Up":
            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")

            if st.button("Create Account"):
                add_user(username, email, password)
                st.success("✅ Account created successfully! Now you can log in.")

        elif choice == "Login":
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")

            if st.button("Login"):
                user = login_user(email, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.username = user[1]
                    st.success(f"✅ Welcome {user[1]}!")
                else:
                    st.error("❌ Invalid email or password")

    # =========================
    # After Login UI
    # =========================
    else:
        st.sidebar.title(f"Welcome, {st.session_state.username}")
        selected = option_menu(
            'Multiple Disease Prediction System',
            ['Diabetes Prediction', 'Heart Disease Prediction', 'Parkinsons Prediction', 'Logout'],
            icons=['activity', 'heart', 'person', 'box-arrow-right'],
            default_index=0
        )

        diabetes_model, heart_model, parkinsons_model = load_models()

        # ================= Diabetes Prediction =================
        if selected == 'Diabetes Prediction':
            st.title("🩸 Diabetes Prediction Using Machine Learning")

            col1, col2, col3 = st.columns(3)
            with col1:
                Pregnancies = st.text_input('Number of Pregnancies')
            with col2:
                Glucose = st.text_input('Glucose Level')
            with col3:
                BloodPressure = st.text_input('Blood Pressure value')
            with col1:
                SkinThickness = st.text_input('Skin Thickness value')
            with col2:
                Insulin = st.text_input('Insulin Level')
            with col3:
                BMI = st.text_input('BMI value')
            with col1:
                DiabetesPedigreeFunction = st.text_input('Diabetes Pedigree Function value')
            with col2:
                Age = st.text_input('Age of the Person')

            diab_diagnosis = ''
            if st.button('Diabetes Test Result'):
                user_input = [float(x) for x in [Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, Age]]
                diab_prediction = diabetes_model.predict([user_input])
                if diab_prediction[0] == 1:
                    diab_diagnosis = 'The person is diabetic'
                    st.warning(diab_diagnosis)
                    st.info(get_suggestion("diabetes"))
                else:
                    diab_diagnosis = 'The person is not diabetic'
                    st.success(diab_diagnosis)

        # ================= Heart Disease Prediction =================
        elif selected == 'Heart Disease Prediction':
            st.title("❤️ Heart Disease Prediction Using Machine Learning")

            col1, col2, col3 = st.columns(3)
            with col1:
                age = st.text_input('Age')
            with col2:
                sex = st.text_input('Sex (1 = Male, 0 = Female)')
            with col3:
                cp = st.text_input('Chest Pain Type')
            with col1:
                trestbps = st.text_input('Resting Blood Pressure')
            with col2:
                chol = st.text_input('Cholesterol Level')
            with col3:
                fbs = st.text_input('Fasting Blood Sugar > 120 mg/dl (1/0)')
            with col1:
                restecg = st.text_input('Resting ECG results')
            with col2:
                thalach = st.text_input('Max Heart Rate achieved')
            with col3:
                exang = st.text_input('Exercise Induced Angina (1/0)')
            with col1:
                oldpeak = st.text_input('ST depression')
            with col2:
                slope = st.text_input('Slope of peak ST')
            with col3:
                ca = st.text_input('Major vessels count')
            with col1:
                thal = st.text_input('Thal (0 = normal, 1 = fixed, 2 = reversible)')

            if st.button('Heart Disease Test Result'):
                user_input = [float(x) for x in [age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal]]
                heart_prediction = heart_model.predict([user_input])
                if heart_prediction[0] == 1:
                    st.warning("The person has heart disease")
                    st.info(get_suggestion("heart"))
                else:
                    st.success("The person does not have any heart disease")

        # ================= Parkinson's Prediction =================
        elif selected == 'Parkinsons Prediction':
            st.title("🧠 Parkinson's Disease Prediction")

            fo = st.text_input('MDVP:Fo(Hz)')
            fhi = st.text_input('MDVP:Fhi(Hz)')
            flo = st.text_input('MDVP:Flo(Hz)')
            Jitter_percent = st.text_input('MDVP:Jitter(%)')
            Jitter_Abs = st.text_input('MDVP:Jitter(Abs)')
            RAP = st.text_input('MDVP:RAP')
            PPQ = st.text_input('MDVP:PPQ')
            DDP = st.text_input('Jitter:DDP')
            Shimmer = st.text_input('MDVP:Shimmer')
            Shimmer_dB = st.text_input('MDVP:Shimmer(dB)')
            APQ3 = st.text_input('Shimmer:APQ3')
            APQ5 = st.text_input('Shimmer:APQ5')
            APQ = st.text_input('MDVP:APQ')
            DDA = st.text_input('Shimmer:DDA')
            NHR = st.text_input('NHR')
            HNR = st.text_input('HNR')
            RPDE = st.text_input('RPDE')
            DFA = st.text_input('DFA')
            spread1 = st.text_input('spread1')
            spread2 = st.text_input('spread2')
            D2 = st.text_input('D2')
            PPE = st.text_input('PPE')

            if st.button("Parkinson's Test Result"):
                user_input = [float(x) for x in [fo, fhi, flo, Jitter_percent, Jitter_Abs, RAP, PPQ, DDP,
                                                 Shimmer, Shimmer_dB, APQ3, APQ5, APQ, DDA, NHR, HNR,
                                                 RPDE, DFA, spread1, spread2, D2, PPE]]
                parkinson_prediction = parkinsons_model.predict([user_input])
                if parkinson_prediction[0] == 1:
                    st.warning("The person has Parkinson's disease")
                    st.info(get_suggestion("parkinsons"))
                else:
                    st.success("The person does not have Parkinson's disease")

        elif selected == 'Logout':
            st.session_state.logged_in = False
            st.experimental_rerun()


# ===============================
# Run App
# ===============================
if __name__ == '__main__':
    main()
