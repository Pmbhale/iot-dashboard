import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import random, time, base64, os
from datetime import datetime, timedelta
from io import BytesIO
import platform
import socket

# ✅ MUST BE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="Critical Space Monitoring",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

if platform.system() == "Windows":
    import winsound


# Try to import email_alert module
try:
    import email_alert
except ImportError:
    class DummyEmailAlert:
        @staticmethod
        def send_email(subject, message):
            print(f"Would send email:\nSubject: {subject}\nMessage: {message}")
            return True

    email_alert = DummyEmailAlert()


def is_cloud():
    host = socket.gethostname().lower()
    return "streamlit" in host or "heroku" in host or "render" in host


# ✅ SESSION INIT FIX (for AttributeError prevention)
if "sound_allowed" not in st.session_state: st.session_state.sound_allowed = True
if "current_page" not in st.session_state: st.session_state.current_page = "dashboard"
if "email_sent" not in st.session_state:
    st.session_state.email_sent = {"temperature": False,"humidity": False,"pressure": False,"co2": False,"pm25": False}
if "beep_on" not in st.session_state: st.session_state.beep_on = False
if "alarm" not in st.session_state: st.session_state.alarm = False
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "hist" not in st.session_state:
    st.session_state.hist = pd.DataFrame(columns=["t","Temp","Hum","Press","CO2","PM25"])


# Analytics Data
if "historical_data" not in st.session_state:
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    st.session_state.historical_data = pd.DataFrame({
        'Date': dates,
        'Temperature': np.random.uniform(22, 36, 30),
        'Humidity': np.random.uniform(40, 75, 30),
        'Pressure': np.random.uniform(980, 1025, 30),
        'PM2.5': np.random.uniform(10, 80, 30),
        'CO2': np.random.uniform(400, 1500, 30),
        'Noise': np.random.uniform(25, 85, 30),
        'Energy_Consumption': np.random.uniform(50, 200, 30)
    })


# ---------------------- ANALYTICS PAGE ----------------------
def analytics_page():
    if not st.session_state.logged_in: st.stop()
    st.markdown("<div class='hero'>📊 Advanced Analytics & Trends</div>", unsafe_allow_html=True)
    st.write("Analytics working ✅")


# ---------------------- REPORTS PAGE ----------------------
def reports_page():
    if not st.session_state.logged_in: st.stop()
    st.markdown("<div class='hero'>📋 Reports Section</div>", unsafe_allow_html=True)
    st.write("Reports working ✅")


# ---------------------- DASHBOARD PAGE ----------------------
def dashboard_page():
    if not st.session_state.logged_in: st.stop()

    st.markdown("""
    <style>
    header, footer {visibility:hidden;}
    [data-testid="stToolbar"] {visibility:hidden;}
    </style>
    """, unsafe_allow_html=True)

    # Background
    def b64(file):
        try:
            with open(file,"rb") as f: return base64.b64encode(f.read()).decode()
        except: return ""

    bg = b64("bg1.png")

    st.markdown(f"""
    <style>
    .stApp {{
        background: url("data:image/png;base64,{bg}") center/cover no-repeat;
        color: #d8f6ff;
    }}
    .veil {{
        position:fixed; inset:0;
        background: linear-gradient(180deg, rgba(7,16,28,.55), rgba(5,12,22,.85));
        z-index:-1;
    }}
    </style>
    <div class="veil"></div>
    """, unsafe_allow_html=True)

    # Header bar
    now = datetime.now().strftime("%H:%M:%S")
    st.markdown(f"""
    <div class="top">
      <div class="brand">CRITICAL SPACE MONITORING</div>
      <div class="menu">
        <span>Dashboard</span>
        <span>Analytics</span>
        <span>Reports</span>
        <span class="live">● LIVE {now}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Routing
    if st.session_state.current_page == "analytics":
        analytics_page(); return
    if st.session_state.current_page == "reports":
        reports_page(); return

    # Data
    def read():
        return {
           "Temperature": round(random.uniform(22,36),1),
           "Humidity": round(random.uniform(40,75),1),
           "Pressure": round(random.uniform(980,1025),1),
           "PM2.5": round(random.uniform(10,80),1),
           "CO2": round(random.uniform(400,1500),1),
           "Noise": round(random.uniform(25,85),1)
        }

    s = read()

    # Alarm conditions
    critical = [
        s["Temperature"]>34,
        s["Humidity"]>70,
        s["Pressure"]<990,
        s["CO2"]>1200,
        s["PM2.5"]>55
    ]

    def load_beep():
        try:
            with open("beep-02.mp3","rb") as f:
                return base64.b64encode(f.read()).decode()
        except:
            return ""

    beep = load_beep()

    # ALARM
    if any(critical) and st.session_state.sound_allowed:
        if beep:
            st.markdown(f"""
            <audio autoplay>
            <source src="data:audio/mp3;base64,{beep}" type="audio/mp3">
            </audio>
            """, unsafe_allow_html=True)

    st.write("Dashboard Live ✅", s)

    # ✅ SAFE CLOUD REFRESH
    st.experimental_set_query_params(refresh=str(time.time()))


# ---------------------- MAIN ----------------------
def main():

    if not st.session_state.logged_in:
        st.markdown("## 🔐 Login")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login"):
            if u=="admin" and p=="admin":
                st.session_state.logged_in=True
                st.rerun()
            else:
                st.error("Invalid credentials")

    else:
        dashboard_page()


if __name__ == "__main__":
    main()
