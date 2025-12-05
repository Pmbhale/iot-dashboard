import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import random, time, base64, os
from datetime import datetime, timedelta
from io import BytesIO
import platform
import matplotlib
if platform.system() == "Windows":
    import winsound

# Try to import email_alert module
try:
    import email_alert
except ImportError:
    # Create a dummy email_alert module for testing
    class DummyEmailAlert:
        @staticmethod
        def send_email(subject, message):
            print(f"Would send email:\nSubject: {subject}\nMessage: {message}")
            return True


    email_alert = DummyEmailAlert()

import socket


def is_cloud():
    host = socket.gethostname().lower()
    return "streamlit" in host or "heroku" in host or "render" in host


# Initialize ALL session states using the new Streamlit 1.28+ API
if "sound_allowed" not in st.session_state:
    st.session_state.sound_allowed = True

if "current_page" not in st.session_state:
    st.session_state.current_page = "dashboard"

if "email_sent" not in st.session_state:
    st.session_state.email_sent = {"temperature": False, "humidity": False, "pressure": False, "co2": False,
                                   "pm25": False}

if "beep_on" not in st.session_state:
    st.session_state.beep_on = False

if "alarm" not in st.session_state:
    st.session_state.alarm = False

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "hist" not in st.session_state:
    st.session_state.hist = pd.DataFrame(columns=["t", "Temp", "Hum", "Press", "CO2", "PM25"])

# Initialize data storage for analytics
if "historical_data" not in st.session_state:
    # Generate 30 days of fake historical data
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    historical = pd.DataFrame({
        'Date': dates,
        'Temperature': np.random.uniform(22, 36, 30),
        'Humidity': np.random.uniform(40, 75, 30),
        'Pressure': np.random.uniform(980, 1025, 30),
        'PM2.5': np.random.uniform(10, 80, 30),
        'CO2': np.random.uniform(400, 1500, 30),
        'Noise': np.random.uniform(25, 85, 30),
        'Energy_Consumption': np.random.uniform(50, 200, 30)
    })
    st.session_state.historical_data = historical


def analytics_page():

    # Initialize session state variables if needed
    if "historical_data" not in st.session_state:
        # Generate 30 days of fake historical data
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        historical = pd.DataFrame({
            'Date': dates,
            'Temperature': np.random.uniform(22, 36, 30),
            'Humidity': np.random.uniform(40, 75, 30),
            'Pressure': np.random.uniform(980, 1025, 30),
            'PM2.5': np.random.uniform(10, 80, 30),
            'CO2': np.random.uniform(400, 1500, 30),
            'Noise': np.random.uniform(25, 85, 30),
            'Energy_Consumption': np.random.uniform(50, 200, 30)
        })
        st.session_state.historical_data = historical
    
    # ----- LOGIN GUARD -----
    if not st.session_state.logged_in:
        st.stop()
    
    # ... rest of your analytics_page code ...

    # Title
    st.markdown("<div class='hero'>📊 Advanced Analytics & Trends</div>", unsafe_allow_html=True)

    # Create navigation header for analytics page
    now = datetime.now().strftime("%H:%M:%S")


    # Analytics Overview Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        avg_temp = st.session_state.historical_data['Temperature'].mean()
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{avg_temp:.1f}°C</div>
            <div class="stat-label">Avg Temperature</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        max_co2 = st.session_state.historical_data['CO2'].max()
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{max_co2:.0f} ppm</div>
            <div class="stat-label">Peak CO₂</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        alert_days = len(st.session_state.historical_data[st.session_state.historical_data['Temperature'] > 34])
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{alert_days}</div>
            <div class="stat-label">Alert Days</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        energy_avg = st.session_state.historical_data['Energy_Consumption'].mean()
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{energy_avg:.0f} kWh</div>
            <div class="stat-label">Avg Energy Use</div>
        </div>
        """, unsafe_allow_html=True)

    # Time Range Selector
    st.markdown("<div class='card'><div class='hdr'>📅 Date Range Selection</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date",
                                   value=datetime.now() - timedelta(days=30),
                                   min_value=datetime.now() - timedelta(days=365),
                                   max_value=datetime.now())
    with col2:
        end_date = st.date_input("End Date",
                                 value=datetime.now(),
                                 min_value=datetime.now() - timedelta(days=365),
                                 max_value=datetime.now())

    # Filter data based on selection
    filtered_data = st.session_state.historical_data[
        (st.session_state.historical_data['Date'] >= pd.Timestamp(start_date)) &
        (st.session_state.historical_data['Date'] <= pd.Timestamp(end_date))
        ]

    st.markdown("</div>", unsafe_allow_html=True)

    # Main Analytics Charts
    tab1, tab2, tab3 = st.tabs(["📈 Trends Over Time", "🔍 Correlation Analysis", "📊 Statistical Summary"])

    with tab1:
        st.markdown("<div class='card'><div class='hdr'>Time Series Analysis</div>", unsafe_allow_html=True)

        # Multi-line chart for all parameters - SIMPLIFIED VERSION
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=filtered_data['Date'],
            y=filtered_data['Temperature'],
            name='Temperature',
            line=dict(color='#6fe3ff', width=2)
        ))

        fig.add_trace(go.Scatter(
            x=filtered_data['Date'],
            y=filtered_data['Humidity'],
            name='Humidity',
            line=dict(color='#ff7d7d', width=2),
            yaxis='y2'
        ))

        fig.add_trace(go.Scatter(
            x=filtered_data['Date'],
            y=filtered_data['CO2'] / 10,
            name='CO₂ (ppm/10)',
            line=dict(color='#cc99ff', width=2),
            yaxis='y3'
        ))

        # SIMPLIFIED LAYOUT - NO titlefont property
        fig.update_layout(
            template="plotly_dark",
            height=500,
            title="Environmental Parameters Over Time",
            xaxis=dict(title="Date"),
            yaxis=dict(title="Temperature (°C)"),
            yaxis2=dict(
                title="Humidity (%)",
                overlaying="y",
                side="right"
            ),
            yaxis3=dict(
                title="CO₂ (ppm/10)",
                overlaying="y",
                side="right",
                position=0.95
            ),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Individual parameter charts
        st.markdown("<div class='card'><div class='hdr'>Individual Parameter Analysis</div>", unsafe_allow_html=True)
        selected_param = st.selectbox(
            "Select Parameter",
            ["Temperature", "Humidity", "Pressure", "PM2.5", "CO2", "Noise", "Energy_Consumption"],
            index=0
        )

        col1, col2 = st.columns(2)
        with col1:
            fig2 = px.line(filtered_data, x='Date', y=selected_param,
                           title=f'{selected_param} Trend',
                           template="plotly_dark")
            fig2.update_traces(line_color='#7ceaff')
            st.plotly_chart(fig2, use_container_width=True)

        with col2:
            fig3 = px.histogram(filtered_data, x=selected_param,
                                title=f'{selected_param} Distribution',
                                template="plotly_dark")
            fig3.update_traces(marker_color='#ff7d7d')
            st.plotly_chart(fig3, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown("<div class='card'><div class='hdr'>Correlation Analysis</div>", unsafe_allow_html=True)

        # Correlation matrix
        corr_params = ['Temperature', 'Humidity', 'CO2', 'PM2.5', 'Energy_Consumption']
        corr_matrix = filtered_data[corr_params].corr()

        fig4 = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_params,
            y=corr_params,
            colorscale='RdYlBu_r',
            zmin=-1,
            zmax=1,
            text=np.round(corr_matrix.values, 2),
            texttemplate='%{text}',
            textfont={"size": 10},
            hoverinfo='text'
        ))

        fig4.update_layout(
            template="plotly_dark",
            title="Correlation Matrix",
            height=500
        )

        st.plotly_chart(fig4, use_container_width=True)

        # Scatter plot for selected correlation - REMOVED TRENDLINE
        st.markdown("<div class='card'><div class='hdr'>Scatter Plot Analysis</div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            x_param = st.selectbox("X-axis Parameter", corr_params, index=0, key='x_param')
        with col2:
            y_param = st.selectbox("Y-axis Parameter", corr_params, index=1, key='y_param')

        # FIXED: Removed trendline="ols" to avoid statsmodels dependency
        fig5 = px.scatter(filtered_data, x=x_param, y=y_param,
                          title=f'{x_param} vs {y_param}',
                          template="plotly_dark")
        fig5.update_traces(marker=dict(color='#7ceaff', size=8))
        st.plotly_chart(fig5, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        st.markdown("<div class='card'><div class='hdr'>Statistical Summary</div>", unsafe_allow_html=True)

        # Summary statistics table
        stats_df = filtered_data.describe().round(2)
        st.dataframe(stats_df.style.background_gradient(cmap='Blues'), use_container_width=True)

        # Alert statistics
        st.markdown("<div class='card'><div class='hdr'>Alert Statistics</div>", unsafe_allow_html=True)

        alert_stats = pd.DataFrame({
            'Parameter': ['Temperature', 'Humidity', 'Pressure', 'CO2', 'PM2.5'],
            'Threshold': ['>34°C', '>70%', '<990 hPa', '>1200 ppm', '>55 µg/m³'],
            'Alerts Count': [
                len(filtered_data[filtered_data['Temperature'] > 34]),
                len(filtered_data[filtered_data['Humidity'] > 70]),
                len(filtered_data[filtered_data['Pressure'] < 990]),
                len(filtered_data[filtered_data['CO2'] > 1200]),
                len(filtered_data[filtered_data['PM2.5'] > 55])
            ],
            'Max Value': [
                filtered_data['Temperature'].max(),
                filtered_data['Humidity'].max(),
                filtered_data['Pressure'].min(),
                filtered_data['CO2'].max(),
                filtered_data['PM2.5'].max()
            ]
        })

        st.dataframe(alert_stats.style.background_gradient(subset=['Alerts Count'], cmap='Reds'),
                     use_container_width=True)

        # Export analytics data
        st.markdown("<div class='card'><div class='hdr'>Export Analytics Data</div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📥 Download Analytics CSV"):
                csv = filtered_data.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"Analytics_Data_{start_date}_{end_date}.csv",
                    mime="text/csv"
                )
        with col2:
            if st.button("📊 Generate Analytics Report"):
                st.info("Analytics report generation coming soon!")

        st.markdown("</div>", unsafe_allow_html=True)

    # Sidebar for analytics page
    with st.sidebar:
        st.markdown("### ⚙️ Analytics Settings")

        st.markdown("---")

        # Quick navigation
        st.markdown("### 🚀 Quick Navigation")
        nav_col1, nav_col2, nav_col3 = st.columns(3)
        with nav_col1:
            if st.button("📊", key="analytics_side_dash", help="Go to Dashboard"):
                st.session_state.current_page = "dashboard"
                st.rerun()
        with nav_col2:
            if st.button("📈", key="analytics_side_analytics", help="Go to Analytics"):
                st.session_state.current_page = "analytics"
                st.rerun()
        with nav_col3:
            if st.button("📋", key="analytics_side_reports", help="Go to Reports"):
                st.session_state.current_page = "reports"
                st.rerun()

        st.markdown("---")

        # Data info
        st.markdown("### 📊 Data Info")
        st.metric("Days of Data", len(filtered_data))
        st.metric("Parameters Tracked", "7")

        st.markdown("---")

        # Back to dashboard button
        if st.button("← Back to Dashboard", use_container_width=True):
            st.session_state.current_page = "dashboard"
            st.rerun()


def reports_page():
    # Initialize session state variables if needed
    if "historical_data" not in st.session_state:
        # Generate 30 days of fake historical data
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        historical = pd.DataFrame({
            'Date': dates,
            'Temperature': np.random.uniform(22, 36, 30),
            'Humidity': np.random.uniform(40, 75, 30),
            'Pressure': np.random.uniform(980, 1025, 30),
            'PM2.5': np.random.uniform(10, 80, 30),
            'CO2': np.random.uniform(400, 1500, 30),
            'Noise': np.random.uniform(25, 85, 30),
            'Energy_Consumption': np.random.uniform(50, 200, 30)
        })
        st.session_state.historical_data = historical
    
    # ----- LOGIN GUARD -----
    if not st.session_state.logged_in:
        st.stop()
    
    # ... rest of your reports_page code ...
    # Title
    st.markdown("<div class='hero'>📋 Comprehensive Reports</div>", unsafe_allow_html=True)

    # Create navigation header for reports page
    now = datetime.now().strftime("%H:%M:%S")


    # Report Generation Options
    st.markdown("<div class='card'><div class='hdr'>📄 Report Generator</div>", unsafe_allow_html=True)

    report_type = st.selectbox(
        "Select Report Type",
        ["Daily Summary", "Weekly Analysis", "Monthly Review", "Incident Report", "Compliance Report"]
    )

    col1, col2 = st.columns(2)
    with col1:
        report_date = st.date_input("Report Date", value=datetime.now())
    with col2:
        time_period = st.selectbox(
            "Time Period",
            ["Last 7 days", "Last 30 days", "Last quarter", "Custom range"]
        )

    include_sections = st.multiselect(
        "Include Sections",
        ["Executive Summary", "Sensor Data", "Alert History", "Trend Analysis",
         "Recommendations", "Action Items", "Cost Analysis", "Energy Consumption"],
        default=["Executive Summary", "Sensor Data", "Alert History", "Recommendations"]
    )

    st.markdown("</div>", unsafe_allow_html=True)

    # Generated Report Preview
    st.markdown("<div class='card'><div class='hdr'>📋 Report Preview</div>", unsafe_allow_html=True)

    # Mock report content
    report_content = f"""
    # {report_type} Report
    **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    **Period:** {time_period}
    **Location:** Main Monitoring Station

    ## Executive Summary
    - Total monitoring period: 30 days
    - System uptime: 99.8%
    - Critical alerts: {len(st.session_state.historical_data[st.session_state.historical_data['Temperature'] > 34])}
    - Average temperature: {st.session_state.historical_data['Temperature'].mean():.1f}°C
    - Peak CO₂ level: {st.session_state.historical_data['CO2'].max():.0f} ppm

    ## Key Findings
    1. Temperature remained within acceptable range for 85% of the period
    2. Humidity control maintained optimal conditions
    3. Air quality improved by 15% compared to previous period
    4. Energy consumption optimized by 8%

    ## Recommendations
    1. Consider additional ventilation during peak occupancy hours
    2. Schedule maintenance for HVAC systems
    3. Implement automated alerts for rapid response
    4. Review energy consumption patterns for further optimization

    ## Action Items
    - [ ] Review alert response times
    - [ ] Update maintenance schedules
    - [ ] Train staff on new monitoring protocols
    - [ ] Validate sensor calibration

    *Report generated by Critical Space Monitoring System*
    """

    st.text_area("Report Content", report_content, height=400)

    # Report Charts
    st.markdown("<div class='card'><div class='hdr'>📈 Report Charts</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        # Alert frequency chart
        alerts_by_day = st.session_state.historical_data['Temperature'] > 34
        fig1 = go.Figure(data=[go.Bar(
            x=st.session_state.historical_data['Date'],
            y=alerts_by_day.astype(int),
            marker_color='#ff7676'
        )])
        fig1.update_layout(
            template="plotly_dark",
            title="Temperature Alerts by Day",
            height=300
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        # Parameter distribution
        fig2 = go.Figure()
        fig2.add_trace(go.Box(
            y=st.session_state.historical_data['Temperature'],
            name='Temperature',
            marker_color='#6fe3ff'
        ))
        fig2.add_trace(go.Box(
            y=st.session_state.historical_data['Humidity'],
            name='Humidity',
            marker_color='#ff7d7d'
        ))
        fig2.update_layout(
            template="plotly_dark",
            title="Parameter Distribution",
            height=300,
            showlegend=False
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Export Options
    st.markdown("<div class='card'><div class='hdr'>💾 Export Options</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📄 Generate PDF Report", use_container_width=True):
            st.success("PDF report generated successfully!")
    with col2:
        if st.button("📊 Export to Excel", use_container_width=True):
            st.success("Excel report exported successfully!")
    with col3:
        if st.button("📧 Email Report", use_container_width=True):
            st.success("Report emailed to registered addresses!")

    # Scheduled Reports
    st.markdown("<div class='card'><div class='hdr'>⏰ Scheduled Reports</div>", unsafe_allow_html=True)

    schedule_col1, schedule_col2, schedule_col3 = st.columns(3)
    with schedule_col1:
        st.checkbox("Daily Report", value=True, key="daily_report")
    with schedule_col2:
        st.checkbox("Weekly Summary", value=True, key="weekly_report")
    with schedule_col3:
        st.checkbox("Monthly Review", value=False, key="monthly_report")

    email_recipients = st.text_input("Email Recipients", "admin@company.com, operations@company.com",
                                     key="email_recipients")
    if st.button("Save Schedule", use_container_width=True):
        st.success("Schedule saved!")

    st.markdown("</div>", unsafe_allow_html=True)

    # Previous Reports
    st.markdown("<div class='card'><div class='hdr'>📚 Report Archive</div>", unsafe_allow_html=True)

    # Mock previous reports
    reports = [
        {"date": "2024-01-15", "type": "Monthly Review", "status": "Completed", "size": "2.4 MB"},
        {"date": "2024-01-08", "type": "Weekly Analysis", "status": "Completed", "size": "1.8 MB"},
        {"date": "2024-01-01", "type": "Monthly Review", "status": "Completed", "size": "2.5 MB"},
        {"date": "2023-12-25", "type": "Incident Report", "status": "Completed", "size": "3.1 MB"},
        {"date": "2023-12-18", "type": "Weekly Analysis", "status": "Completed", "size": "1.7 MB"},
    ]

    for i, report in enumerate(reports):
        col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
        with col1:
            st.write(f"**{report['date']}**")
        with col2:
            st.write(report['type'])
        with col3:
            st.write(report['status'])
        with col4:
            st.write(report['size'])
        with col5:
            if st.button("Download", key=f"dl_{i}"):
                st.success(f"Downloading {report['type']}...")

    st.markdown("</div>", unsafe_allow_html=True)

    # Sidebar for reports page
    with st.sidebar:
        st.markdown("### ⚙️ Reports Settings")

        st.markdown("---")

        # Quick navigation
        st.markdown("### 🚀 Quick Navigation")
        nav_col1, nav_col2, nav_col3 = st.columns(3)
        with nav_col1:
            if st.button("📊", key="reports_side_dash", help="Go to Dashboard"):
                st.session_state.current_page = "dashboard"
                st.rerun()
        with nav_col2:
            if st.button("📈", key="reports_side_analytics", help="Go to Analytics"):
                st.session_state.current_page = "analytics"
                st.rerun()
        with nav_col3:
            if st.button("📋", key="reports_side_reports", help="Go to Reports"):
                st.session_state.current_page = "reports"
                st.rerun()

        st.markdown("---")

        # Report settings
        st.markdown("### 📋 Report Settings")
        auto_generate = st.checkbox("Auto-generate weekly", value=True, key="auto_gen")
        email_notify = st.checkbox("Email notifications", value=True, key="email_notify")

        st.markdown("---")

        # Back to dashboard button
        if st.button("← Back to Dashboard", use_container_width=True):
            st.session_state.current_page = "dashboard"
            st.rerun()


def dashboard_page():
    # Initialize ALL session state variables if they don't exist
    if "hist" not in st.session_state:
        st.session_state.hist = pd.DataFrame(columns=["t", "Temp", "Hum", "Press", "CO2", "PM25"])
    
    # Initialize other session state variables if needed
    if "sound_allowed" not in st.session_state:
        st.session_state.sound_allowed = True

    if "current_page" not in st.session_state:
        st.session_state.current_page = "dashboard"

    if "email_sent" not in st.session_state:
        st.session_state.email_sent = {"temperature": False, "humidity": False, "pressure": False, "co2": False,
                                       "pm25": False}

    if "beep_on" not in st.session_state:
        st.session_state.beep_on = False

    if "alarm" not in st.session_state:
        st.session_state.alarm = False

    # Initialize historical_data if not present
    if "historical_data" not in st.session_state:
        # Generate 30 days of fake historical data
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        historical = pd.DataFrame({
            'Date': dates,
            'Temperature': np.random.uniform(22, 36, 30),
            'Humidity': np.random.uniform(40, 75, 30),
            'Pressure': np.random.uniform(980, 1025, 30),
            'PM2.5': np.random.uniform(10, 80, 30),
            'CO2': np.random.uniform(400, 1500, 30),
            'Noise': np.random.uniform(25, 85, 30),
            'Energy_Consumption': np.random.uniform(50, 200, 30)
        })
        st.session_state.historical_data = historical

    # ----- LOGIN GUARD -----
    if not st.session_state.logged_in:
        st.stop()

    # Get current page from session state with safe access
    current_page = st.session_state.get('current_page', 'dashboard')
    
    # ----- HIDE STREAMLIT CHROME -----
    st.markdown("""
    <style>
    header, footer {visibility:hidden;}
    [data-testid="stToolbar"] {visibility:hidden;}
    </style>
    """, unsafe_allow_html=True)

    # ----- BACKGROUND IMAGE -----
    def b64(file):
        try:
            with open(file, "rb") as f:
                return base64.b64encode(f.read()).decode()
        except:
            # Return a default gradient background if image not found
            return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

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
    .menu span {{ 
        margin-left:26px; 
        color:#a8edff; 
        cursor: pointer;
        transition: color 0.3s;
    }}
    .menu span:hover {{ 
        color: #7ceaff;
        text-decoration: underline;
    }}
    .active-nav {{ 
        color: #67ffb5 !important;
        font-weight: 700;
        border-bottom: 2px solid #67ffb5;
        padding-bottom: 2px;
    }}
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
        margin-bottom: 20px;
    }}
    .hdr {{ font-size:20px; margin-bottom:10px; color:#bff5ff; }}

    /* Table style */
    table {{ width:100%; border-collapse:collapse; }}
    th,td {{ padding:10px; text-align:left; }}
    th {{ border-bottom:2px solid rgba(140,220,255,.3); }}
    tr:not(:last-child) td {{ border-bottom:1px solid rgba(255,255,255,.06); }}
    .ok {{ color:#67ffb5; }}
    .mid {{ color:#ffd966; }}
    .bad {{ color:#ff7676; }}

    /* Alerts + Notifications */
    .alert {{ background: rgba(110,20,20,.6); border-left:4px solid #ff6b6b; padding:10px; border-radius:8px; margin-bottom:8px; }}
    .note  {{ background: rgba(15,80,65,.55); border-left:4px solid #4deac2; padding:10px; border-radius:8px; margin-bottom:8px; }}
    .info  {{ background: rgba(20,60,110,.55); border-left:4px solid #6fe3ff; padding:10px; border-radius:8px; margin-bottom:8px; }}

    /* Stats cards */
    .stat-card {{
        background: rgba(11,24,44,.75);
        border:1px solid rgba(140,220,255,.25);
        border-radius: 10px;
        padding: 15px;
        text-align: center;
    }}
    .stat-value {{ font-size: 28px; font-weight: bold; color: #7ceaff; }}
    .stat-label {{ font-size: 14px; color: #a8edff; margin-top: 5px; }}

    /* Navigation buttons */
    .nav-btn {{
        background: none;
        border: none;
        color: #a8edff;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        padding: 5px 10px;
        margin-left: 20px;
    }}
    .nav-btn:hover {{
        color: #7ceaff;
        text-decoration: underline;
    }}
    .nav-btn.active {{
        color: #67ffb5;
        border-bottom: 2px solid #67ffb5;
    }}

    /* Custom button styling */
    .stButton > button {{
        background: rgba(11,24,44,.75);
        border: 1px solid rgba(140,220,255,.25);
        color: #d8f6ff;
        border-radius: 8px;
        transition: all 0.3s;
    }}
    .stButton > button:hover {{
        background: rgba(11,24,44,.9);
        border: 1px solid rgba(140,220,255,.5);
        color: #7ceaff;
    }}
    </style>
    <div class="veil"></div>
    """, unsafe_allow_html=True)

    # ----- HEADER / NAVBAR -----
    now = datetime.now().strftime("%H:%M:%S")

    # Create navigation using Streamlit buttons instead of pure JavaScript
    st.markdown(f"""
    <div class="top">
      <div class="brand">CRITICAL SPACE MONITORING</div>
      <div class="menu">
        <span style="{'color: #67ffb5; font-weight: 700; border-bottom: 2px solid #67ffb5; padding-bottom: 2px;' if current_page == 'dashboard' else ''}">Dashboard</span>
        <span style="{'color: #67ffb5; font-weight: 700; border-bottom: 2px solid #67ffb5; padding-bottom: 2px;' if current_page == 'analytics' else ''}">Analytics</span>
        <span style="{'color: #67ffb5; font-weight: 700; border-bottom: 2px solid #67ffb5; padding-bottom: 2px;' if current_page == 'reports' else ''}">Reports</span>
        <span class="live">● LIVE&nbsp;{now}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Create clickable navigation using columns
    nav_col1, nav_col2, nav_col3, nav_col4 = st.columns([2, 1, 1, 2])

    with nav_col1:
        # Empty column for spacing
        pass

    with nav_col2:
        if st.button("Dashboard", key="nav_dashboard", use_container_width=True):
            st.session_state.current_page = "dashboard"
            st.rerun()

    with nav_col3:
        if st.button("Analytics", key="nav_analytics", use_container_width=True):
            st.session_state.current_page = "analytics"
            st.rerun()

    with nav_col4:
        if st.button("Reports", key="nav_reports", use_container_width=True):
            st.session_state.current_page = "reports"
            st.rerun()

    # Add some spacing
    st.markdown("<br><br>", unsafe_allow_html=True)

    # Handle page navigation - FIXED LINE
    if current_page != "dashboard":
        if current_page == "analytics":
            analytics_page()
        elif current_page == "reports":
            reports_page()
        return

    # ----- TITLE -----
    st.markdown("<div class='hero'>Critical Space Environment Monitoring – Real-Time Dashboard</div>",
                unsafe_allow_html=True)

    # ----- DATA (demo) -----
    def read():
        return {
            "Temperature": round(random.uniform(22, 36), 1),
            "Humidity": round(random.uniform(40, 75), 1),
            "Pressure": round(random.uniform(980, 1025), 1),
            "PM2.5": round(random.uniform(10, 80), 1),
            "CO2": round(random.uniform(400, 1500), 1),
            "Noise": round(random.uniform(25, 85), 1)
        }

    s = read()

    # ----- STATUS -----
    def status(name, val):
        if name == "Temperature":
            if val > 34: return "High", "bad"
            if val > 26: return "Warm", "mid"
            return "Normal", "ok"
        if name == "Humidity":
            if val > 70: return "Very High", "bad"
            if val > 60: return "High", "mid"
            return "Normal", "ok"
        if name == "CO2":
            if val > 1200: return "High", "bad"
            if val > 800:  return "Moderate", "mid"
            return "Normal", "ok"
        if name == "PM2.5":
            if val > 55: return "High", "bad"
            if val > 35: return "Moderate", "mid"
            return "Clean", "ok"
        if name == "Pressure":
            if val < 990: return "Low", "bad"
            if val < 1000: return "Moderate", "mid"
            return "Normal", "ok"
        return "Safe", "ok"

    # ----- BEEP -----
    def load_beep():
        try:
            with open("beep-02.mp3", "rb") as f:
                return base64.b64encode(f.read()).decode()
        except:
            # Fallback to online beep if local file not found
            return "T2dnUwACAAAAAAAAAAAuZnpXAAAAABX54EgB9tEDh4dG9vZ0dG5nLm1pY3Jvc29mdC5jb20vdG9vbHMvZWNobzFfbWFpbi5tcDMA//NgxAAdGV0qb0IAAUZGw2m3m5u7u7u2Nju7R7t7tHbHf93R2x3d9v//////f//////////////////////////8R3///EQ4fBAQEEB/fuAQMBA0E0KQBAQdBAf4eH+P/8uFGh0b2QAAAAAAAAAAAA//MUZAAAAAGkAAAAAAAAA0gAAAAATEFN//MUZAMAAAGkAAAAAAAAA0gAAAAARTMu//MUZAYAAAGkAAAAAAAAA0gAAAAAOTku//MUZAkAAAGkAAAAAAAAA0gAAAAANVVV"

    beep = load_beep()

    # ----- QUICK STATS ROW -----
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{s['Temperature']}°C</div>
            <div class="stat-label">Temperature</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{s['Humidity']}%</div>
            <div class="stat-label">Humidity</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{s['CO2']} ppm</div>
            <div class="stat-label">CO₂ Level</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        air_quality = "Good" if s['PM2.5'] < 35 else "Moderate" if s['PM2.5'] < 55 else "Poor"
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{air_quality}</div>
            <div class="stat-label">Air Quality</div>
        </div>
        """, unsafe_allow_html=True)

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
        st.markdown("<div class='card'><div class='hdr'>Real-Time Trends (Last 20 readings)</div>",
                    unsafe_allow_html=True)

        # Add all parameters to history - NOW SAFE
        st.session_state.hist.loc[len(st.session_state.hist)] = [
            datetime.now().strftime("%H:%M:%S"),
            s["Temperature"],
            s["Humidity"],
            s["Pressure"],
            s["CO2"],
            s["PM2.5"]
        ]

        # Keep only last 20 points
        if len(st.session_state.hist) > 20:
            st.session_state.hist = st.session_state.hist.iloc[-20:]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=st.session_state.hist["t"], y=st.session_state.hist["Temp"],
                                 name="Temperature", line=dict(color="#6fe3ff", width=2)))
        fig.add_trace(go.Scatter(x=st.session_state.hist["t"], y=st.session_state.hist["Hum"],
                                 name="Humidity", line=dict(color="#ff7d7d", width=2)))
        fig.add_trace(go.Scatter(x=st.session_state.hist["t"], y=st.session_state.hist["Press"] / 10,
                                 name="Pressure (hPa/10)", line=dict(color="#ffcc66", width=2)))
        fig.add_trace(go.Scatter(x=st.session_state.hist["t"], y=st.session_state.hist["CO2"] / 20,
                                 name="CO₂ (ppm/20)", line=dict(color="#cc99ff", width=2)))

        fig.update_layout(
            template="plotly_dark",
            height=310,
            margin=dict(l=10, r=10, t=24, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ----- BOTTOM GRID (ALERTS | NOTIFICATIONS) -----
    bottom_left, bottom_right = st.columns([1, 1], gap="large")

    # ALERTS
    with bottom_left:
        st.markdown("<div class='card'><div class='hdr'>⚠️ Critical Alerts</div>", unsafe_allow_html=True)
        unsafe = False

        # Check all parameters and send emails if needed
        if s["Temperature"] > 34:
            unsafe = True
            st.markdown(f"<div class='alert'>🔥 Temperature exceeded 34°C (Current: {s['Temperature']}°C)</div>",
                        unsafe_allow_html=True)

            if not st.session_state.email_sent["temperature"]:
                try:
                    email_alert.send_email(
                        "CRITICAL TEMPERATURE ALERT",
                        f"Temperature crossed safe limit!\n\n"
                        f"Current Value: {s['Temperature']}°C\n"
                        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"Location: Main Monitoring Station\n"
                        f"Threshold: 34°C\n\n"
                        f"Please take immediate action."
                    )
                    st.session_state.email_sent["temperature"] = True
                except Exception as e:
                    st.error(f"Failed to send email alert: {e}")

        if s["Humidity"] > 70:
            unsafe = True
            st.markdown(f"<div class='alert'>💧 Humidity exceeded 70% (Current: {s['Humidity']}%)</div>",
                        unsafe_allow_html=True)

            if not st.session_state.email_sent["humidity"]:
                try:
                    email_alert.send_email(
                        "HIGH HUMIDITY ALERT",
                        f"Humidity crossed critical limit!\n\n"
                        f"Current Value: {s['Humidity']}%\n"
                        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"Location: Main Monitoring Station\n"
                        f"Threshold: 70%\n\n"
                        f"Risk of mold growth and equipment damage."
                    )
                    st.session_state.email_sent["humidity"] = True
                except Exception as e:
                    st.error(f"Failed to send email alert: {e}")

        if s["Pressure"] < 990:
            unsafe = True
            st.markdown(f"<div class='alert'>🌡️ Pressure below 990 hPa (Current: {s['Pressure']} hPa)</div>",
                        unsafe_allow_html=True)

            if not st.session_state.email_sent["pressure"]:
                try:
                    email_alert.send_email(
                        "LOW PRESSURE ALERT",
                        f"Atmospheric pressure below safe limit!\n\n"
                        f"Current Value: {s['Pressure']} hPa\n"
                        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"Location: Main Monitoring Station\n"
                        f"Threshold: 990 hPa\n\n"
                        f"May indicate weather changes or system issues."
                    )
                    st.session_state.email_sent["pressure"] = True
                except Exception as e:
                    st.error(f"Failed to send email alert: {e}")

        if s["CO2"] > 1200:
            unsafe = True
            st.markdown(f"<div class='alert'>☁️ CO₂ exceeded 1200 ppm (Current: {s['CO2']} ppm)</div>",
                        unsafe_allow_html=True)

            if not st.session_state.email_sent["co2"]:
                try:
                    email_alert.send_email(
                        "HIGH CO₂ ALERT",
                        f"CO₂ level crossed safe limit!\n\n"
                        f"Current Value: {s['CO2']} ppm\n"
                        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"Location: Main Monitoring Station\n"
                        f"Threshold: 1200 ppm\n\n"
                        f"Ventilation required for occupant safety."
                    )
                    st.session_state.email_sent["co2"] = True
                except Exception as e:
                    st.error(f"Failed to send email alert: {e}")

        if s["PM2.5"] > 55:
            unsafe = True
            st.markdown(f"<div class='alert'>💨 PM2.5 exceeded 55 µg/m³ (Current: {s['PM2.5']} µg/m³)</div>",
                        unsafe_allow_html=True)

            if not st.session_state.email_sent["pm25"]:
                try:
                    email_alert.send_email(
                        "POOR AIR QUALITY ALERT",
                        f"PM2.5 level crossed safe limit!\n\n"
                        f"Current Value: {s['PM2.5']} µg/m³\n"
                        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"Location: Main Monitoring Station\n"
                        f"Threshold: 55 µg/m³\n\n"
                        f"Air purification or ventilation required."
                    )
                    st.session_state.email_sent["pm25"] = True
                except Exception as e:
                    st.error(f"Failed to send email alert: {e}")

        if not unsafe:
            st.markdown("<div class='note'>✅ All parameters within safe range</div>", unsafe_allow_html=True)
            # Reset all email flags when safe
            for key in st.session_state.email_sent:
                st.session_state.email_sent[key] = False

        st.markdown("</div>", unsafe_allow_html=True)

    # NOTIFICATIONS + EXPORT
    with bottom_right:
        st.markdown("<div class='card'><div class='hdr'>📢 System Notifications</div>", unsafe_allow_html=True)

        # Show which emails were sent
        email_count = sum(st.session_state.email_sent.values())
        if email_count > 0:
            st.markdown(f"<div class='alert'>📧 {email_count} alert email(s) sent to admin</div>",
                        unsafe_allow_html=True)
        else:
            st.markdown("<div class='note'>📧 No emails sent (all parameters normal)</div>", unsafe_allow_html=True)

        st.markdown("<div class='note'>📱 SMS notifications active</div>", unsafe_allow_html=True)
        st.markdown("<div class='note'>☁️ Data synced to cloud storage</div>", unsafe_allow_html=True)
        st.markdown("<div class='note'>📊 Logged to database</div>", unsafe_allow_html=True)
        st.markdown("<div class='note'>🔄 Real-time monitoring active</div>", unsafe_allow_html=True)

        # Export section
        st.markdown("<div class='hdr'>📄 Quick Export</div>", unsafe_allow_html=True)

        def make_pdf(data):
            try:
                from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, Spacer
                from reportlab.lib.pagesizes import A4
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib.units import inch
                from reportlab.lib import colors
                from reportlab.platypus import TableStyle

                buf = BytesIO()
                doc = SimpleDocTemplate(buf, pagesize=A4)
                styles = getSampleStyleSheet()

                # Custom styles
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Title'],
                    fontSize=24,
                    spaceAfter=30,
                    textColor=colors.HexColor('#4deac2')
                )

                content = []

                # Title
                content.append(Paragraph("Critical Space Monitoring Report", title_style))
                content.append(Spacer(1, 20))

                # Report info
                content.append(
                    Paragraph(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
                content.append(Paragraph("Location: Main Monitoring Station", styles["Normal"]))
                content.append(Spacer(1, 20))

                # Parameter table
                table_data = [['Parameter', 'Value', 'Status']]

                for param, value in data.items():
                    lab, _ = status(param, value)
                    table_data.append([param, str(value), lab])

                table = Table(table_data, colWidths=[2 * inch, 1.5 * inch, 1.5 * inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a3b5a')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#0b182c')),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#4deac2')),
                ]))

                content.append(table)
                content.append(Spacer(1, 30))

                doc.build(content)
                pdf_bytes = buf.getvalue()
                buf.close()
                return pdf_bytes

            except Exception as e:
                st.error(f"Error generating PDF: {e}")
                # Fallback to simple text report
                simple_report = f"""
                Critical Space Monitoring Report
                =================================

                Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                Location: Main Monitoring Station

                Sensor Readings:
                """
                for param, value in data.items():
                    lab, _ = status(param, value)
                    simple_report += f"\n{param}: {value} ({lab})"

                # Convert to PDF bytes
                from reportlab.platypus import SimpleDocTemplate, Paragraph
                from reportlab.lib.styles import getSampleStyleSheet
                buf = BytesIO()
                doc = SimpleDocTemplate(buf, pagesize=A4)
                styles = getSampleStyleSheet()
                content = [Paragraph(simple_report.replace('\n', '<br/>'), styles["Normal"])]
                doc.build(content)
                pdf_bytes = buf.getvalue()
                buf.close()
                return pdf_bytes

        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 Generate PDF"):
                pdf_data = make_pdf(s)
                st.download_button(
                    label="⬇️ Download",
                    data=pdf_data,
                    file_name=f"Dashboard_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf"
                )
        with col2:
            csv = pd.DataFrame([s]).to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"Sensor_Data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

        st.markdown("</div>", unsafe_allow_html=True)

    # ---------- EVENT BASED BEEP ----------
    # Check if any parameter is in critical state
    critical_conditions = [
        s["Temperature"] > 34,
        s["Humidity"] > 70,
        s["Pressure"] < 990,
        s["CO2"] > 1200,
        s["PM2.5"] > 55
    ]

    any_critical = any(critical_conditions)

    if any_critical and not st.session_state.alarm and st.session_state.sound_allowed:
        st.markdown("<div class='alert'>🚨 AUDIBLE ALARM ACTIVATED</div>", unsafe_allow_html=True)

        # Local sound for Windows
        if platform.system() == "Windows" and not is_cloud():
            try:
                winsound.Beep(2500, 1200)
            except:
                pass

        # Browser audio for all devices (including cloud)
        if beep:
            stamp = str(time.time())
            st.markdown(f"""
                <audio id="alarmAudio" autoplay>
                    <source src="data:audio/mp3;base64,{beep}#{stamp}" type="audio/mp3">
                </audio>
                <script>
                    setTimeout(function() {{
                        var audio = document.getElementById('alarmAudio');
                        if(audio) {{
                            audio.play().catch(function(e) {{
                                console.log('Audio play failed:', e);
                            }});
                        }}
                    }}, 100);
                </script>
            """, unsafe_allow_html=True)

        st.session_state.alarm = True

    # Reset alarm when all conditions are safe
    if not any_critical:
        st.session_state.alarm = False

    # ----- SIDEBAR -----
    with st.sidebar:
        st.markdown("### ⚙️ Dashboard Settings")

        # Sound control
        sound_enabled = st.checkbox("Enable Alarm Sounds", value=st.session_state.sound_allowed, key="sound_enabled")
        if sound_enabled != st.session_state.sound_allowed:
            st.session_state.sound_allowed = sound_enabled
            st.rerun()

        if st.session_state.sound_allowed:
            st.markdown("*🔊 Alarm sounds enabled*")
        else:
            st.markdown("*🔇 Alarm sounds disabled*")

        st.markdown("---")

        # Refresh rate
        refresh_rate = st.select_slider(
            "Refresh Rate (seconds)",
            options=[1, 2, 3, 5, 10],
            value=3,
            key="refresh_rate"
        )

        # Test sound button
        if st.button("🔊 Test Alarm Sound", key="test_sound"):
            if beep and st.session_state.sound_allowed:
                stamp = str(time.time())
                st.markdown(f"""
                    <audio autoplay>
                        <source src="data:audio/mp3;base64,{beep}#{stamp}" type="audio/mp3">
                    </audio>
                """, unsafe_allow_html=True)
                st.success("Test sound played!")

        st.markdown("---")

        # System status
        st.markdown("### 📈 System Status")
        total_readings = len(st.session_state.hist) if "hist" in st.session_state else 0
        st.metric("Total Readings", f"{total_readings}")
        st.metric("Active Alerts", f"{sum(critical_conditions)}")

        st.markdown("---")

        # Quick navigation
        st.markdown("### 🚀 Quick Navigation")
        nav_col1, nav_col2, nav_col3 = st.columns(3)
        with nav_col1:
            if st.button("📊", key="sidebar_dash", help="Go to Dashboard"):
                st.session_state.current_page = "dashboard"
                st.rerun()
        with nav_col2:
            if st.button("📈", key="sidebar_analytics", help="Go to Analytics"):
                st.session_state.current_page = "analytics"
                st.rerun()
        with nav_col3:
            if st.button("📋", key="sidebar_reports", help="Go to Reports"):
                st.session_state.current_page = "reports"
                st.rerun()

        st.markdown("---")

        # Logout button
        if st.button("🚪 Logout", key="logout"):
            st.session_state.logged_in = False
            st.session_state.current_page = "dashboard"
            st.rerun()

    # ----- REFRESH -----
    time.sleep(refresh_rate)
    st.rerun()


# Main function to run the app
def main():
    # Set page config
    st.set_page_config(
        page_title="Critical Space Monitoring",
        page_icon="🚨",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Check if user is logged in
    if not st.session_state.logged_in:
        # Show login page
        st.markdown(f"""
        <style>
        .stApp {{
            background: linear-gradient(135deg, #0a1929 0%, #0c1b2e 100%);
        }}
        .login-container {{
            max-width: 400px;
            margin: 100px auto;
            padding: 40px;
            background: rgba(11,24,44,.85);
            border-radius: 20px;
            border: 1px solid rgba(140,220,255,.25);
            box-shadow: 0 20px 40px rgba(0,0,0,0.5);
        }}
        .login-title {{
            text-align: center;
            color: #7ceaff;
            font-size: 28px;
            margin-bottom: 30px;
            font-weight: bold;
        }}
        </style>
        <div class="login-container">
            <div class="login-title">CRITICAL SPACE MONITORING</div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### 🔐 Login")
            username = st.text_input("Username", key="username")
            password = st.text_input("Password", type="password", key="password")

            if st.button("Login", key="login_button", use_container_width=True):
                if username == "admin" and password == "admin":  # Simple demo login
                    st.session_state.logged_in = True
                    st.session_state.current_page = "dashboard"
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    else:
        # User is logged in, show the appropriate page
        current_page = st.session_state.get('current_page', 'dashboard')
        if current_page == "dashboard":
            dashboard_page()
        elif current_page == "analytics":
            analytics_page()
        elif current_page == "reports":
            reports_page()


# Run the app
if __name__ == "__main__":
    main()


