import streamlit as st
import pandas as pd
from io import BytesIO
import datetime

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    st.error("ReportLab is not installed. PDF export will not work.")

# Branding info
COMPANY = "Annur Tech"
MOTTO = "Illuminating Innovation"
ADDRESS = "No 6 Kolo Drive, Behind Zuma Barrack, Tafa LGA, Niger State, Nigeria"
PHONE = "09051693000"
EMAIL = "albataskumyjr@gmail.com"

st.set_page_config(page_title="Annur Tech Solar Planner", layout="wide")

st.title("⚡ Annur Tech Solar System Planner")
st.caption(MOTTO)

st.sidebar.header("Client Information")
client_name = st.sidebar.text_input("Client Name")
client_address = st.sidebar.text_area("Client Address")
client_phone = st.sidebar.text_input("Client Phone")
client_email = st.sidebar.text_input("Client Email")

st.header("🔋 Load Audit")
st.write("Enter appliances, power ratings, quantities, and usage hours.")

col1, col2, col3, col4 = st.columns(4)
with col1:
    appliance = st.text_input("Appliance name")
with col2:
    watt = st.number_input("Power rating (W)", 0, 5000, 100)
with col3:
    quantity = st.number_input("Quantity", 1, 100, 1)
with col4:
    hours = st.number_input("Hours per day", 0.0, 24.0, 5.0)

calculate = st.button("➕ Add to load")

if "load_data" not in st.session_state:
    st.session_state.load_data = []

if calculate and appliance:
    total_watt = watt * quantity
    daily_wh = total_watt * hours
    st.session_state.load_data.append({
        "appliance": appliance,
        "watt": watt,
        "quantity": quantity,
        "total_watt": total_watt,
        "hours": hours,
        "wh": daily_wh
    })

# Add a button to clear all items
if st.button("🗑️ Clear All Items"):
    st.session_state.load_data = []
    st.rerun()

if st.session_state.load_data:
    st.subheader("Load Summary")
    total_wh = sum(item["wh"] for item in st.session_state.load_data)
    total_watt = sum(item["total_watt"] for item in st.session_state.load_data)
    
    # Convert load data to DataFrame for better display
    df = pd.DataFrame(st.session_state.load_data)
    st.table(df)
    
    st.write(f"**Total Power Demand:** {total_watt} W")
    st.write(f"**Total Energy Demand:** {total_wh} Wh/day")

st.header("🔋 Battery Sizing")
backup_time = st.number_input("Backup time (hours)", 1, 72, 5)
battery_voltage = st.selectbox("Battery bank voltage (V)", [12, 24, 48])
dod_limit = st.slider("Depth of Discharge Limit (%)", 50, 100, 80)
if st.session_state.load_data:
    # Calculate battery capacity considering depth of discharge
    battery_capacity_ah = (total_wh * backup_time) / (battery_voltage * (dod_limit/100))
    st.write(f"Required Battery Capacity: {battery_capacity_ah:.2f} Ah at {battery_voltage}V")
    
    # Recommend number of batteries (assuming 200Ah batteries)
    battery_size = st.number_input("Standard Battery Size (Ah)", 50, 500, 200)
    num_batteries = battery_capacity_ah / battery_size
    st.write(f"Recommended Batteries: {num_batteries:.1f} × {battery_size}Ah batteries")

st.header("☀️ Solar Panel Sizing")
panel_type = st.selectbox("Panel Type (Wattage)", [100, 150, 250, 300, 350, 400, 500, 550])
sun_hours = st.number_input("Sun hours per day", 1.0, 12.0, 5.0)
system_efficiency = st.slider("System Efficiency (%)", 50, 95, 75)
if st.session_state.load_data:
    # Calculate required solar panel capacity
    required_solar = total_wh / (sun_hours * (system_efficiency/100))
    st.write(f"Required Solar Capacity: {required_solar:.2f} W")
    
    # Calculate number of panels needed
    num_panels = required_solar / panel_type
    st.write(f"Recommended Panels: {num_panels:.1f} × {panel_type}W panels")
    
    # Calculate charge controller size
    panel_vmp = st.number_input("Panel Vmp (Volts)", 12, 50, 18)
    controller_current = (panel_type * num_panels) / (battery_voltage * 0.8)  # 0.8 for efficiency
    st.write(f"Charge Controller Size: {controller_current:.2f} A at {battery_voltage}V")
    
    # Calculate inverter size
    inverter_size = total_watt * 1.2  # 20% safety margin
    st.write(f"Inverter Size: {inverter_size:.2f} W")

# PDF Export Function
def create_pdf():
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # Center
    )
    story.append(Paragraph(COMPANY, title_style))
    story.append(Paragraph(MOTTO, styles['Heading2']))
    story.append(Spacer(1, 20))
    
    # Client Information
    story.append(Paragraph("CLIENT INFORMATION", styles['Heading2']))
    client_data = [
        ["Name:", client_name],
        ["Address:", client_address],
        ["Phone:", client_phone],
        ["Email:", client_email if client_email else "Not provided"],
        ["Date:", datetime.datetime.now().strftime("%Y-%m-%d %H:%M")]
    ]
    client_table = Table(client_data, colWidths=[100, 300])
    client_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(client_table)
    story.append(Spacer(1, 20))
    
    # Load Audit
    story.append(Paragraph("LOAD AUDIT", styles['Heading2']))
    load_data = [["Appliance", "Wattage (W)", "Qty", "Total Watt", "Hours/Day", "Wh/Day"]]
    for item in st.session_state.load_data:
        load_data.append([
            item['appliance'],
            str(item['watt']),
            str(item['quantity']),
            str(item['total_watt']),
            str(item['hours']),
            str(item['wh'])
        ])
    
    # Add total row
    load_data.append([
        "TOTAL",
        "",
        "",
        str(total_watt),
        "",
        str(total_wh)
    ])
    
    load_table = Table(load_data, colWidths=[100, 70, 40, 70, 70, 70])
    load_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    story.append(load_table)
    story.append(Spacer(1, 20))
    
    # System Sizing
    story.append(Paragraph("SYSTEM SIZING", styles['Heading2']))
    sizing_data = [
        ["Parameter", "Value", "Unit"],
        ["Total Energy Demand", f"{total_wh:.2f}", "Wh/day"],
        ["Backup Time", str(backup_time), "hours"],
        ["Battery Voltage", str(battery_voltage), "V"],
        ["Battery Capacity", f"{battery_capacity_ah:.2f}", "Ah"],
        ["Solar Panel Type", str(panel_type), "W"],
        ["Sun Hours", str(sun_hours), "hours/day"],
        ["Required Solar Capacity", f"{required_solar:.2f}", "W"],
        ["Number of Panels", f"{num_panels:.1f}", ""],
        ["Charge Controller Size", f"{controller_current:.2f}", "A"],
        ["Inverter Size", f"{inverter_size:.2f}", "W"]
    ]
    
    sizing_table = Table(sizing_data, colWidths=[150, 100, 50])
    sizing_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
    ]))
    story.append(sizing_table)
    story.append(Spacer(1, 30))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        alignment=1  # Center
    )
    story.append(Paragraph(f"{COMPANY} | {MOTTO} | {PHONE} | {EMAIL}", footer_style))
    story.append(Paragraph(ADDRESS, footer_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# PDF Export Section
if st.button("📄 Generate PDF Report"):
    if not REPORTLAB_AVAILABLE:
        st.error("PDF export is not available. Please install reportlab.")
    elif not client_name or not st.session_state.load_data:
        st.warning("Please fill in client information and add at least one appliance first.")
    else:
        with st.spinner("Generating report..."):
            pdf = create_pdf()
            st.success("Report generated successfully!")
            st.download_button(
                "Download Report", 
                data=pdf, 
                file_name=f"AnnurTech_Solar_Report_{client_name.replace(' ', '_')}.pdf", 
                mime="application/pdf"
            )

# Add some styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #0e1117;
        text-align: center;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
    }
    div[data-testid="stHorizontalBlock"] {
        align-items: center;
    }
</style>
""", unsafe_allow_html=True)
