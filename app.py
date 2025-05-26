# app.py
import streamlit as st
import pandas as pd
import time
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors

# Constants
PRICE_PER_UNIT = 7.4  # INR per kWh
CO2_EMISSION_FACTOR = 0.82  # kg CO2 per kWh
CARBON_CREDIT_RATE = 0.15  # Credit per kg of CO2 saved (example value)

# Load latest data function
def load_data():
    try:
        df = pd.read_csv("energy_data.csv")
        df.dropna(inplace=True)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df
    except Exception as e:
        st.error("Error loading data: {}".format(e))
        return pd.DataFrame(columns=["timestamp", "Vrms", "Irms"])

# Calculate derived metrics
def calculate_metrics(df, solar_share):
    df["Power_W"] = df["Vrms"] * df["Irms"]
    df["kWh"] = df["Power_W"] / 1000  # Convert to kWh
    df["Cost_INR"] = df["kWh"] * PRICE_PER_UNIT
    df["CO2_kg"] = df["kWh"] * CO2_EMISSION_FACTOR

    renewable_kWh = df["kWh"] * (solar_share / 100)
    CO2_saved = renewable_kWh * CO2_EMISSION_FACTOR
    carbon_credits = CO2_saved * CARBON_CREDIT_RATE

    total_energy = df["kWh"].sum()
    total_cost = df["Cost_INR"].sum()
    total_co2 = df["CO2_kg"].sum()
    total_co2_saved = CO2_saved.sum()
    total_credits = carbon_credits.sum()
    peak_time = df.loc[df["Power_W"].idxmax()]["timestamp"] if not df.empty else None

    # Modified time formatting with line break
    peak_time_display = peak_time.strftime("%d-%m-%Y\n%I:%M %p") if peak_time else "N/A"
    return {
        "Total Energy (kWh)": total_energy,
        "Total Cost (INR)": total_cost,
        "Total CO2 Emission (kg)": total_co2,
        "Cumulative CO2 Saved (kg)": total_co2_saved,
        "Estimated Carbon Credits": total_credits,
        "Peak Load Time": peak_time_display,
    }

# PDF generation function
def generate_canva_style_pdf(metrics):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    page_width, page_height = A4
    margin = inch

    # --- TOP SECTION (Logo + Title) ---
    logo_path = "static/images/RVCE_new_logo.png"  # corrected slash
    logo_width = 0.8 * inch
    logo_height = 0.8 * inch
    logo_x = margin
    logo_y = page_height - margin - logo_height + 10

    c.drawImage(logo_path, logo_x, logo_y, width=logo_width, height=logo_height, preserveAspectRatio=True)

    title = "🌱 Green Audit Report"
    c.setFont("Helvetica-Bold", 17)
    c.setFillColor(colors.green)
    title_x = logo_x + logo_width + 15
    title_y = logo_y + logo_height / 2.5
    c.drawString(title_x, title_y, title)

    # --- Green line below header ---
    c.setStrokeColor(colors.green)
    c.setLineWidth(2)
    line_y = title_y - 35
    c.line(margin, line_y, page_width - margin, line_y)

    # --- METRICS SECTION (Left-aligned Text) ---
    c.setFont("Helvetica", 12)
    c.setFillColor(colors.black)
    y_position = line_y - 40  # below the green line

    divider = "---------------------------------------------------"
    c.drawString(margin, y_position, divider)
    y_position -= 20

    for key, value in metrics.items():
        line = f"{key}: {value:.2f}" if isinstance(value, float) else f"{key}: {value}"
        c.drawString(margin, y_position, line)
        y_position -= 20

    c.drawString(margin, y_position, divider)

    # --- Green Line above Footer ---
    footer_line_y = margin + 15
    c.setStrokeColor(colors.green)
    c.setLineWidth(2)
    c.line(margin, footer_line_y, page_width - margin, footer_line_y)

    # --- FOOTER TEXT (Centered) ---
    footer_text = "@ElectriCheck Innovators"
    c.setFont("Helvetica-Oblique", 10)
    footer_width = c.stringWidth(footer_text, "Helvetica-Oblique", 10)
    c.drawString((page_width - footer_width) / 2, margin / 2, footer_text)

    # --- Finalize PDF ---
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# UI Layout
st.set_page_config(page_title="Green Audit Dashboard", layout="wide")

# Enhanced CSS with layout adjustments
st.markdown("""
    <style>
        .reportview-container {
            background-color: #e9f7ef;
            padding-top: 2rem;
        }
        .sidebar .sidebar-content {
            padding: 2rem 1rem;
        }
        .block-container {
            padding-top: 4rem;
        }
        .stMetric {
            padding: 15px 0;
            border-radius: 8px;
            background-color: #f8f9fa;
        }
        .stMetric label {
            font-size: 14px !important;
            font-weight: 600 !important;
            color: #2c3e50 !important;
        }
        .stMetric div {
            font-size: 20px !important;
            font-weight: 700 !important;
            color: #27ae60 !important;
            white-space: pre-line;
        }
        .stImage {
            margin-top: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

# Header section with adjusted spacing
col_logo, col_title = st.columns([1, 6])
with col_logo:
    st.image("static/images/Black RV Logo.png", width=150)
with col_title:
    st.markdown("<div style='height: 30px'></div>", unsafe_allow_html=True)  # Spacer
    st.title("🌱 Real-Time Green Audit Dashboard")
    st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)  # Additional spacing

# Sidebar input
with st.sidebar:
    st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)  # Spacer
    solar_share = st.slider("% of Energy from Solar/Green Source", 0, 100, 25)
    st.markdown("<hr style='margin: 25px 0'>", unsafe_allow_html=True)

# Load and process data
df = load_data()
if not df.empty:
    metrics = calculate_metrics(df, solar_share)

    # KPIs with improved spacing
    st.subheader("📊 Key Performance Indicators")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Energy (kWh)", f"{metrics['Total Energy (kWh)']:.2f}")
    col2.metric("Total Cost (INR)", f"₹{metrics['Total Cost (INR)']:.2f}")
    col3.metric("Total CO₂ Emission (kg)", f"{metrics['Total CO2 Emission (kg)']:.2f}")

    col4, col5, col6 = st.columns(3)
    col4.metric("Cumulative CO₂ Saved (kg)", f"{metrics['Cumulative CO2 Saved (kg)']:.2f}")
    col5.metric("Carbon Credits Earned", f"{metrics['Estimated Carbon Credits']:.2f}")
    col6.metric("Peak Load Time", metrics['Peak Load Time'])

    # Visualizations
    st.subheader("📈 Visual Insights")
    st.line_chart(df.set_index("timestamp")["Power_W"], use_container_width=True)
    st.bar_chart(df.set_index("timestamp")["kWh"], use_container_width=True)
    st.area_chart(df.set_index("timestamp")["CO2_kg"], use_container_width=True)

    # PDF Report Download
    st.subheader("📄 Export Report")
    pdf = generate_canva_style_pdf(metrics)
    st.download_button(
        label="📥 Download Report as PDF",
        data=pdf,
        file_name="green_audit_report.pdf",
        mime="application/pdf"
    )
else:
    st.warning("Waiting for data... Please keep the data simulator running.")

# Auto-refresh every 1 second
time.sleep(1)
st.rerun()