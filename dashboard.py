import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import random, time, base64, os
from datetime import datetime
from io import BytesIO
import platform

if platform.system() == "Windows":
    import winsound

import email_alert
import socket

def is_cloud():
    host = socket.gethostname().lower()
    return "streamlit" in host or "heroku" in host or "render" in host

def dashboard_page():
    # ----- LOGIN GUARD -----
    # ---- BEEP STATE ----
    if "beep_on" not in st.session_state:
        st.session_state.beep_on = False

    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.stop()

    # ----- HIDE STREAMLIT CHROME -----
    st.markdown("""
    <style>
    header, footer {visibility:hidden;}
    [data-testid="stToolbar"] {visibility:hidden;}
    </style>
    """, unsafe_allow_html=True)

    # ----- BACKGROUND IMAGE -----
    def b64(file):
        with open(file,"rb") as f: return base64.b64encode(f.read()).decode()
    bg = b64("bg1.png")

    # ----- GLOBAL CSS (MATCH IMAGE FEEL) -----
    st.markdown(f"""
    <style>
    .stApp {{
        background: url("data:image/png;base64,{bg}") center/cover no-repeat;
        color: #d8f6ff;
    }}
    .veil {{
        position: fixed; inset:0;
        background: linear-gradient(180deg, rgba(7,16,28,.55), rgba(5,12,22,.85));
        z-index:-1;
    }}

    /* Top bar */
    .top {{
        display:grid; grid-template-columns: 1fr 2fr;
        align-items:center;
        padding: 14px 28px;
        border-bottom:1px solid rgba(140,220,255,.25);
        background: rgba(8,18,33,.65);
        backdrop-filter: blur(8px);
    }}
    .brand {{
        letter-spacing:.18em; font-weight:700; color:#7ceaff;
    }}
    .menu {{
        text-align:right; font-weight:600;
    }}
    .menu span {{ margin-left:26px; color:#a8edff; }}
    .live {{ color:#67ffb5; }}

    /* Title */
    .hero {{
        margin: 18px 28px;
        font-size: 28px; font-weight:700; color:#bff5ff;
    }}

    /* Glass cards */
    .card {{
        background: rgba(11,24,44,.75);
        border:1px solid rgba(140,220,255,.25);
        box-shadow: inset 0 0 0 1px rgba(255,255,255,.02), 0 0 24px rgba(0,0,0,.45);
        border-radius: 14px;
        padding: 16px 18px;
    }}
    .hdr {{ font-size:20px; margin-bottom:10px; }}

    /* Table style (left block) */
    table {{ width:100%; border-collapse:collapse; }}
    th,td {{ padding:10px; }}
    tr:not(:last-child) td {{ border-bottom:1px solid rgba(255,255,255,.06); }}
    .ok {{ color:#67ffb5; }}
    .mid {{ color:#ffd966; }}
    .bad {{ color:#ff7676; }}

    /* Alerts + Notifications */
    .alert {{ background: rgba(110,20,20,.6); border-left:4px solid #ff6b6b; padding:10px; border-radius:8px; margin-bottom:8px; }}
    .note  {{ background: rgba(15,80,65,.55); border-left:4px solid #4deac2; padding:10px; border-radius:8px; margin-bottom:8px; }}

    /* Export */
    .btnlike {{
        display:inline-block; padding:10px 16px;
        border:1px solid rgba(140,220,255,.35);
        border-radius:8px; cursor:pointer; color:#dffaff;
        background: rgba(8,20,38,.8);
    }}
    </style>
    <div class="veil"></div>
    """, unsafe_allow_html=True)

    # ----- HEADER / NAVBAR -----
    now = datetime.now().strftime("%H:%M:%S")
    st.markdown(f"""
    <div class="top">
      <div class="brand">CRITICAL SPACE MONITORING</div>
      <div class="menu">
        <span>Dashboard</span><span>Reports</span><span>Analytics</span>
        <span class="live">● LIVE&nbsp;{now}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ----- TITLE -----
    st.markdown("<div class='hero'>Critical Space Environment Monitoring – Real-Time Dashboard</div>",
                unsafe_allow_html=True)

    # ----- DATA (demo) -----
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

    # ----- STATUS -----
    def status(name,val):
        if name=="Temperature":
            if val>34: return "High","bad"
            if val>26: return "Warm","mid"
            return "Normal","ok"
        if name=="Humidity":
            return ("High","mid") if val>60 else ("Normal","ok")
        if name=="CO2":
            if val>1200: return "High","bad"
            if val>800:  return "Moderate","mid"
            return "Normal","ok"
        if name=="PM2.5":
            return ("Moderate","mid") if val>35 else ("Clean","ok")
        return "Safe","ok"

    # ----- BEEP -----
    def load_beep():
        try:
            with open("beep-02.mp3","rb") as f:
                return base64.b64encode(f.read()).decode()
        except: return None


    # ----- MAIN GRID (TOP ROW: LEFT + RIGHT) -----
    top_left, top_right = st.columns([1.15, 2.0], gap="large")

    # LEFT: LIVE SENSOR DATA (table card)
    with top_left:
        st.markdown("<div class='card'><div class='hdr'>Live Sensor Data</div>", unsafe_allow_html=True)
        rows = [
            ("Temperature", f"{s['Temperature']} °C"),
            ("Humidity", f"{s['Humidity']} %"),
            ("Pressure", f"{s['Pressure']} hPa"),
            ("Air Quality (PM2.5)", f"{s['PM2.5']} µg/m³"),
            ("CO₂ Level", f"{s['CO2']} ppm"),
            ("Noise Level", f"{s['Noise']} dB"),
        ]
        html = "<table><tr><th>Parameter</th><th>Current Value</th><th>Status</th></tr>"
        key_map = {
            "Temperature": "Temperature",
            "Humidity": "Humidity",
            "Pressure": "Pressure",
            "Air Quality (PM2.5)": "PM2.5",
            "CO₂ Level": "CO2",
            "Noise Level": "Noise"
        }

        for name, val in rows:
            key = key_map[name]
            lab, cls = status(key, s[key])
            html += f"<tr><td>{name}</td><td>{val}</td><td class='{cls}'>{lab}</td></tr>"

        html += "</table></div>"
        st.markdown(html, unsafe_allow_html=True)

    # RIGHT: LINE GRAPH (big card)
    with top_right:
        st.markdown("<div class='card'><div class='hdr'>Line Graph</div>", unsafe_allow_html=True)
        if "hist" not in st.session_state:
            st.session_state.hist = pd.DataFrame(columns=["t","Temp","Hum"])
        st.session_state.hist.loc[len(st.session_state.hist)] = [
            datetime.now().strftime("%H:%M:%S"), s["Temperature"], s["Humidity"]
        ]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=st.session_state.hist["t"], y=st.session_state.hist["Temp"],
                                 name="Temperature", line=dict(color="#6fe3ff")))
        fig.add_trace(go.Scatter(x=st.session_state.hist["t"], y=st.session_state.hist["Hum"],
                                 name="Humidity", line=dict(color="#ff7d7d")))
        fig.update_layout(template="plotly_dark", height=310, margin=dict(l=10,r=10,t=24,b=10))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ----- BOTTOM GRID (ALERTS | NOTIFICATIONS) -----
    bottom_left, bottom_right = st.columns([1,1], gap="large")

    # ALERTS
    with bottom_left:
        st.markdown("<div class='card'><div class='hdr'>Alerts</div>", unsafe_allow_html=True)
        unsafe=False
        if "email_sent" not in st.session_state:
            st.session_state.email_sent = False
        # EMAIL ALERT FOR TEMPERATURE
        if s["Temperature"] > 34:
            unsafe = True
            st.markdown("<div class='alert'>🔥 Temperature exceeded 34°C (Email sent)</div>", unsafe_allow_html=True)

            if not st.session_state.email_sent:
                email_alert.send_email(
                    "CRITICAL TEMPERATURE ALERT",
                    f"Temperature crossed safe limit!\n\n"
                    f"Current Value: {s['Temperature']}°C\n"
                    f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                    f"Please take immediate action."
                )
                st.session_state.email_sent = True

        if s["Humidity"]>60:
            unsafe=True
            st.markdown("<div class='alert'>ALERT (10:45) – Humidity crossed 60% (Email + SMS to Admin)</div>",
                        unsafe_allow_html=True)
        if s["Pressure"]<990:
            unsafe=True
            st.markdown("<div class='alert'>ALERT (11:05) – Pressure below safe limit in Lab 2</div>",
                        unsafe_allow_html=True)
        if not unsafe:
            st.write("No critical alerts – all parameters within safe range.")
            # RESET EMAIL WHEN SAFE AGAIN
            if s["Temperature"] <= 34:
                st.session_state.email_sent = False

        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div class='card'><div class='hdr'>Export / Report</div>", unsafe_allow_html=True)

    def make_pdf(d):
        from reportlab.platypus import SimpleDocTemplate, Table, Paragraph
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4)
        styles = getSampleStyleSheet()
        content = [Paragraph("Critical Space Monitoring Report", styles["Title"])]
        content.append(Table([[k, str(v)] for k, v in d.items()]))
        doc.build(content)
        data = buf.getvalue();
        buf.close();
        return data

    if st.button("Generate PDF Report"):
        pdf = make_pdf(s)
        st.download_button("Download PDF", pdf, file_name="Report.pdf", mime="application/pdf")
    st.markdown("</div>", unsafe_allow_html=True)
    # NOTIFICATIONS + EXPORT
    with bottom_right:
        st.markdown("<div class='card'><div class='hdr'>Notifications</div>", unsafe_allow_html=True)
        st.markdown("<div class='note'>Email – Critical alert queued</div>", unsafe_allow_html=True)
        st.markdown("<div class='note'>SMS – Sent to Admin</div>", unsafe_allow_html=True)
        st.markdown("<div class='note'>Cloud – Stored to ThingSpeak / Firebase</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ---------- EVENT BASED BEEP (FINAL) ----------
    # ===== SYSTEM LEVEL BEEP (NO BROWSER ISSUE) =====

    beep = load_beep()

    if "alarm" not in st.session_state:
        st.session_state.alarm = False

    # ----------- TRIGGER ----------------

    if s["Temperature"] > 34 and not st.session_state.alarm:

        st.warning("🚨 TEMPERATURE ALARM ACTIVE")

        # ===== LOCALHOST =====
        if not is_cloud():
            try:
                import winsound
                winsound.Beep(2500, 1200)
            except:
                pass

        # ===== CLOUD =====
        if is_cloud() and beep:
            stamp = str(time.time())
            st.markdown(f"""
                <audio autoplay loop>
                    <source src="data:audio/mp3;base64,{beep}#{stamp}" type="audio/mp3">
                </audio>
            """, unsafe_allow_html=True)

        st.session_state.alarm = True

    # -------- RESET when SAFE ----------
    if s["Temperature"] <= 34:
        st.session_state.alarm = False

    # ----- SIDEBAR (logout) -----
    if st.sidebar.button("Logout"):
        st.session_state.logged_in=False
        st.rerun()

    # ----- REFRESH -----
    time.sleep(3)
    st.rerun()
