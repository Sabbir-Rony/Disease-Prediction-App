# -*- coding: utf-8 -*-
"""
Created on Nov 2025
@author: Sabbir
JSON Database Version (MySQL removed)
"""

import streamlit as st
import json
import pickle
import os

# -------------------------
# JSON DATABASE FUNCTIONS
# -------------------------

USER_FILE = "users.json"

def load_users():
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, "w") as f:
            json.dump([], f)
    with open(USER_FILE, "r") as f:
        return json.load(f)


def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)


def add_user(username, email, password):
    users = load_users()
    users.append({
        "username": username,
        "email": email,
        "password": password
    })
    save_users(users)


def login_user(email, password):
    users = load_users()
    for u in users:
        if u["email"] == email and u["password"] == password:
            return u
    return None


# -------------------------
# Load ML Models
# -------------------------
def load_models():
    base = "models"

    dp = os.path.join(base, "diabetes_model.sav")
    hp = os.path.join(base, "heart_disease_model.sav")
    pp = os.path.join(base, "parkinsons_model.sav")

    diabetes = pickle.load(open(dp, 'rb')) if os.path.exists(dp) else None
    heart = pickle.load(open(hp, 'rb')) if os.path.exists(hp) else None
    park = pickle.load(open(pp, 'rb')) if os.path.exists(pp) else None

    return diabetes, heart, park


# -------------------------
# Suggestions
# -------------------------
def suggestion(disease, result):
    s = {
        "diabetes": {
            "pos": "Follow a controlled diet with low sugar and refined carbs.Take your medicines regularly and check blood glucose as advised.Exercise daily and avoid stress to keep your sugar stable.",
            "neg": "Maintain a healthy weight and eat balanced meals with less sugar.Exercise regularly to keep insulin levels normal.Go for routine checkups if you have a family history of diabetes."
        },
        "heart": {
            "pos": "Follow a low-salt and low-fat diet strictly.Take heart medications exactly as prescribed.Avoid smoking, alcohol, and heavy stress.Do light exercise only after your doctor approves.",
            "neg": "Eat heart-healthy foods like vegetables, fruits, and lean proteins.Exercise regularly to keep your heart strong.Avoid smoking and control cholesterol levels.Go for routine heart checkups if you have risk factors."
        },
        "parkinsons": {
            "pos": "Take your Parkinson’s medications consistently and on time.Do regular physiotherapy to keep movement flexible.Avoid falls by keeping your home safe and walking carefully.Follow up with a neurologist regularly.",
            "neg": "Exercise daily to keep your brain and nerves healthy.Eat antioxidant-rich foods like fruits and vegetables.Avoid exposure to toxins, chemicals, and pesticides.Protect your head from injuries and maintain overall brain health."
        }
    }
    return s[disease]["pos" if result == 1 else "neg"]


# -------------------------
# Auth UI
# -------------------------
def ui_signup():
    st.subheader("Create Account")
    with st.form("signup"):
        u = st.text_input("Username")
        e = st.text_input("Email")
        p = st.text_input("Password", type="password")
        btn = st.form_submit_button("Sign Up")

        if btn:
            if u and e and p:
                add_user(u, e, p)
                st.success("Account created! Please login.")
                st.session_state.auth = "Login"
                st.experimental_rerun()
            else:
                st.error("All fields required!")


def ui_login():
    st.subheader("Login")
    with st.form("login"):
        e = st.text_input("Email")
        p = st.text_input("Password", type="password")
        btn = st.form_submit_button("Login")

        if btn:
            user = login_user(e, p)
            if user:
                st.session_state.logged = True
                st.session_state.username = user["username"]
                st.experimental_rerun()
            else:
                st.error("Wrong email or password")


# -------------------------
# Main App
# -------------------------
def main():
    st.set_page_config(page_title="Disease Prediction", layout="wide")

    if "logged" not in st.session_state:
        st.session_state.logged = False

    if not st.session_state.logged:
        st.title("🩺 Multiple Disease Prediction System")
        st.write("Please Sign Up or Login to continue.")

        tab = st.radio("", ["Sign Up", "Login"], horizontal=True)
        st.session_state.auth = tab

        ui_signup() if tab == "Sign Up" else ui_login()
        return

    # Logged In Menu
    st.sidebar.markdown("Menu")
    page = st.sidebar.radio(
        "",
        ["Home", "Diabetes", "Heart", "Parkinsons", "Logout"]
    )

    diabetes_model, heart_model, park_model = load_models()

    # HOME PAGE
    if page == "Home":
        st.header(f"Welcome, {st.session_state.username} 👋")
        st.header("DISEASE PREDICTION MODEL")
        st.info("Disease prediction uses medical data and machine learning models to estimate the likelihood of a person developing a certain illness.")

    # DIABETES PAGE
    if page == "Diabetes":
        st.title("🩸 Diabetes Prediction")
        if diabetes_model is None:
            st.error("Model file missing.")
        else:
            cols = st.columns(3)
            fields = ["Pregnancies", "Glucose", "BloodPressure", "SkinThickness",
                      "Insulin", "BMI", "DPF", "Age"]
            inputs = [cols[i % 3].text_input(f) for i, f in enumerate(fields)]

            if st.button("Predict"):
                try:
                    nums = [float(x) for x in inputs]
                    r = diabetes_model.predict([nums])[0]
                    st.write(suggestion("diabetes", r))
                    st.warning("Positive") if r == 1 else st.success("Negative")
                except:
                    st.error("Invalid inputs!")

    # HEART PAGE
    if page == "Heart":
        st.title("❤ Heart Disease Prediction")
        if heart_model is None:
            st.error("Model file missing.")
        else:
            cols = st.columns(3)
            fields = ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
                      "thalach", "exang", "oldpeak", "slope", "ca", "thal"]
            inputs = [cols[i % 3].text_input(f) for i, f in enumerate(fields)]

            if st.button("Predict"):
                try:
                    nums = [float(x) for x in inputs]
                    r = heart_model.predict([nums])[0]
                    st.write(suggestion("heart", r))
                    st.warning("Positive") if r == 1 else st.success("Negative")
                except:
                    st.error("Invalid Input")

    # PARKINSON PAGE
    if page == "Parkinsons":
        st.title("🧠 Parkinson's Disease Prediction")

        if park_model is None:
            st.error("Model file missing.")
        else:
            fields = [
                'MDVP:Fo(Hz)', 'MDVP:Fhi(Hz)', 'MDVP:Flo(Hz)', 'MDVP:Jitter(%)',
                'MDVP:Jitter(Abs)', 'MDVP:RAP', 'MDVP:PPQ', 'Jitter:DDP',
                'MDVP:Shimmer', 'MDVP:Shimmer(dB)', 'Shimmer:APQ3', 'Shimmer:APQ5',
                'MDVP:APQ', 'Shimmer:DDA', 'NHR', 'HNR', 'RPDE', 'DFA',
                'spread1', 'spread2', 'D2', 'PPE'
            ]

            cols = st.columns(3)
            inputs = [cols[i % 3].text_input(f) for i, f in enumerate(fields)]

            if st.button("Predict Parkinson’s"):
                try:
                    nums = [float(x) for x in inputs]
                    r = park_model.predict([nums])[0]
                    st.write(suggestion("parkinsons", r))
                    st.warning("Positive") if r == 1 else st.success("Negative")
                except:
                    st.error("Invalid Input")

    # LOGOUT
    if page == "Logout":
        st.session_state.logged = False
        st.experimental_rerun()


if __name__ == "__main__":
    main()
