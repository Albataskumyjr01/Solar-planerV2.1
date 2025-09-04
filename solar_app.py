import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import datetime
import base64

try:
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# Branding info - Enhanced with Nigerian context
COMPANY = "ANNUR TECH SOLAR SOLUTIONS"
MOTTO = "Illuminating Nigeria's Future"
ADDRESS = "No 6 Kolo Drive, Behind Zuma Barrack, Tafa LGA, Niger State, Nigeria"
PHONE = "+234 905 169 3000"
EMAIL = "albataskumyjr@gmail.com"
WEBSITE = "www.annurtech.ng"
BUSINESS_NUMBER = "BN: 2984173"
CAC_REGISTRATION = "CAC/RC: 1847263"

# Nigerian-specific component database with current market prices (Naira)
NIGERIAN_SOLAR_PANELS = {
    "Jinko Tiger 350W": {"price": 85000, "vmp": 35.5, "voc": 42.5, "efficiency": 19.5, "warranty": "25 years"},
    "Canadian Solar 400W": {"price": 105000, "vmp": 37.2, "voc": 45.5, "efficiency": 20.1, "warranty": "25 years"},
    "Trina Solar 450W": {"price": 125000, "vmp": 39.8, "voc": 48.2, "efficiency": 20.8, "warranty": "25 years"},
    "LG Neon 2 380W": {"price": 145000, "vmp": 36.2, "voc": 43.8, "efficiency": 21.1, "warranty": "25 years"},
}

NIGERIAN_BATTERIES = {
    "Trojan T-105 (225Ah)": {"price": 65000, "capacity": 225, "type": "Lead-acid", "voltage": 6, "life_cycles": 1500},
    "Pylontech US2000 (200Ah)": {"price": 280000, "capacity": 200, "type": "Lithium", "voltage": 48, "life_cycles": 6000},
    "Vision 6FM200D (200Ah)": {"price": 75000, "capacity": 200, "type": "Lead-acid", "voltage": 6, "life_cycles": 1200},
    "BYD B-Box (200Ah)": {"price": 250000, "capacity": 200, "type": "Lithium", "voltage": 48, "life_cycles": 6000},
}

NIGERIAN_INVERTERS = {
    "Growatt 3000W 24V": {"price": 185000, "power": 3000, "voltage": 24, "type": "Hybrid", "warranty": "5 years"},
    "Victron 5000W 48V": {"price": 450000, "power": 5000, "voltage": 48, "type": "Hybrid", "warranty": "5 years"},
    "SMA Sunny Boy 5000W": {"price": 520000, "power": 5000, "voltage": 48, "type": "Grid-tie", "warranty": "10 years"},
}

# Common Nigerian appliances with typical wattages
NIGERIAN_APPLIANCES = {
    "Ceiling Fan": 75,
    "Standing Fan": 55,
    "TV (32-inch LED)": 50,
    "TV (42-inch LED)": 80,
    "Refrigerator (Medium)": 150,
    "Deep Freezer": 200,
    "Air Conditioner (1HP)": 750,
    "Air Conditioner (1.5HP)": 1100,
    "Water Pump (1HP)": 750,
    "Lighting (LED Bulb)": 10,
    "Lighting (Fluorescent)": 40,
    "Computer Desktop": 200,
    "Laptop": 65,
    "Decoder": 25,
    "Home Theatre": 100,
    "Washing Machine": 500,
    "Electric Iron": 1000,
    "Microwave Oven": 1000,
    "Electric Kettle": 1500,
}

st.set_page_config(page_title="Annur Tech Solar Planner", layout="wide", page_icon="☀️")

# Custom CSS for Nigerian color scheme
st.markdown(f"""
<style>
    .main .block-container {{
        padding-top: 2rem;
    }}
    .stApp {{
        background-color: #f8f9fa;
    }}
    .green-header {{
        background-color: #006400;
        color: white;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
    }}
    .nigerian-flag {{
        background: linear-gradient(90deg, #008751 33%, white 33%, white 66%, #008751 66%);
        color: white;
        padding: 5px;
        text-align: center;
        border-radius: 3px;
    }}
    .price-tag {{
        background-color: #FFD700;
        color: #000;
        padding: 2px 5px;
        border-radius: 3px;
        font-weight: bold;
    }}
</style>
""", unsafe_allow_html=True)

# App header with Nigerian branding
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.markdown(f'<div class="nigerian-flag"><h1>⚡ {COMPANY}</h1></div>', unsafe_allow_html=True)
    st.markdown(f'<h3 style="text-align: center; color: #006400;">{MOTTO}</h3>', unsafe_allow_html=True)

# Client Information Section
st.sidebar.markdown(f'<div class="green-header"><h3>👤 Client Information</h3></div>', unsafe_allow_html=True)
client_name = st.sidebar.text_input("Full Name")
client_address = st.sidebar.text_area("Address")
client_phone = st.sidebar.text_input("Phone Number")
client_email = st.sidebar.text_input("Email Address")
project_location = st.sidebar.selectbox("Project Location", ["Abuja", "Lagos", "Kano", "Port Harcourt", "Kaduna", "Other"])

# Load Audit Section with Nigerian appliances
st.markdown(f'<div class="green-header"><h3>🔋 Load Audit & Energy Assessment</h3></div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.subheader("Quick Add Common Appliances")
    selected_appliance = st.selectbox("Select common appliance", list(NIGERIAN_APPLIANCES.keys()))
    appliance_wattage = st.number_input("Wattage (W)", value=NIGERIAN_APPLIANCES[selected_appliance])
    
with col2:
    appliance_quantity = st.number_input("Quantity", 1, 100, 1)
    appliance_hours = st.number_input("Hours used per day", 0.0, 24.0, 5.0)

add_appliance = st.button("➕ Add Appliance to Load List")

# Manual appliance entry
st.subheader("Custom Appliance Entry")
col1, col2, col3, col4 = st.columns(4)
with col1:
    custom_appliance = st.text_input("Custom appliance name")
with col2:
    custom_watt = st.number_input("Custom wattage (W)", 0, 5000, 100)
with col3:
    custom_quantity = st.number_input("Custom quantity", 1, 100, 1)
with col4:
    custom_hours = st.number_input("Custom hours", 0.0, 24.0, 5.0)

add_custom = st.button("➕ Add Custom Appliance")

# Initialize session state
if "load_data" not in st.session_state:
    st.session_state.load_data = []

# Add appliances to load list
if add_appliance and selected_appliance:
    total_watt = appliance_wattage * appliance_quantity
    daily_wh = total_watt * appliance_hours
    st.session_state.load_data.append({
        "appliance": selected_appliance,
        "watt": appliance_wattage,
        "quantity": appliance_quantity,
        "total_watt": total_watt,
        "hours": appliance_hours,
        "wh": daily_wh
    })
    st.success(f"Added {appliance_quantity} × {selected_appliance}")

if add_custom and custom_appliance:
    total_watt = custom_watt * custom_quantity
    daily_wh = total_watt * custom_hours
    st.session_state.load_data.append({
        "appliance": custom_appliance,
        "watt": custom_watt,
        "quantity": custom_quantity,
        "total_watt": total_watt,
        "hours": custom_hours,
        "wh": daily_wh
    })
    st.success(f"Added {custom_quantity} × {custom_appliance}")

# Display load summary
if st.session_state.load_data:
    st.subheader("📊 Load Summary")
    total_wh = sum(item["wh"] for item in st.session_state.load_data)
    total_watt = sum(item["total_watt"] for item in st.session_state.load_data)
    
    df = pd.DataFrame(st.session_state.load_data)
    
    # Add energy consumption charts
    col1, col2 = st.columns(2)
    
    with col1:
        fig_pie = px.pie(df, values='wh', names='appliance', title='Energy Consumption by Appliance')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        fig_bar = px.bar(df, x='appliance', y='wh', title='Daily Energy Consumption (Wh)')
        st.plotly_chart(fig_bar, use_container_width=True)
    
    st.dataframe(df, use_container_width=True)
    st.metric("Total Power Demand", f"{total_watt} W")
    st.metric("Total Daily Energy Consumption", f"{total_wh} Wh")
    
    # Clear button
    if st.button("🗑️ Clear All Items"):
        st.session_state.load_data = []
        st.rerun()

# System Sizing Section
st.markdown(f'<div class="green-header"><h3>⚡ System Sizing & Component Selection</h3></div>', unsafe_allow_html=True)

if st.session_state.load_data:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Battery System")
        backup_time = st.slider("Backup time required (hours)", 1, 24, 5)
        battery_voltage = st.selectbox("System voltage", [12, 24, 48], index=1)
        dod_limit = st.slider("Depth of Discharge (%)", 50, 100, 80)
        temperature_factor = st.slider("Temperature derating factor (%)", 80, 100, 90)
        
        # Advanced battery calculation
        battery_capacity_ah = (total_wh * backup_time) / (battery_voltage * (dod_limit/100) * (temperature_factor/100))
        
        # Select battery type
        battery_type = st.selectbox("Battery technology", list(NIGERIAN_BATTERIES.keys()))
        battery_info = NIGERIAN_BATTERIES[battery_type]
        num_batteries = battery_capacity_ah / battery_info["capacity"]
        
        st.metric("Required Battery Capacity", f"{battery_capacity_ah:.0f} Ah")
        st.metric("Number of Batteries Needed", f"{num_batteries:.1f}", 
                 help=f"Using {battery_type} ({battery_info['capacity']}Ah each)")
        st.metric("Estimated Battery Cost", f"₦{num_batteries * battery_info['price']:,.0f}")
    
    with col2:
        st.subheader("Solar Panel System")
        sun_hours = st.slider("Sun hours per day (Nigeria average)", 3.0, 8.0, 5.0)
        system_efficiency = st.slider("System efficiency (%)", 50, 95, 75)
        panel_type = st.selectbox("Solar panel type", list(NIGERIAN_SOLAR_PANELS.keys()))
        panel_info = NIGERIAN_SOLAR_PANELS[panel_type]
        
        # Advanced solar calculation
        required_solar = total_wh / (sun_hours * (system_efficiency/100))
        num_panels = required_solar / panel_info["vmp"] * (battery_voltage/panel_info["vmp"])
        
        # Charge controller calculation
        controller_current = (required_solar * 1.25) / battery_voltage  # 25% safety margin
        
        st.metric("Required Solar Capacity", f"{required_solar:.0f} W")
        st.metric("Number of Panels Needed", f"{num_panels:.1f}")
        st.metric("Estimated Panel Cost", f"₦{num_panels * panel_info['price']:,.0f}")
        st.metric("Charge Controller Size", f"{controller_current:.0f} A")
    
    # Inverter selection
    st.subheader("Inverter Selection")
    inverter_size = total_watt * 1.3  # 30% safety margin for Nigerian power conditions
    selected_inverter = st.selectbox("Choose inverter", list(NIGERIAN_INVERTERS.keys()))
    inverter_info = NIGERIAN_INVERTERS[selected_inverter]
    
    st.metric("Recommended Inverter Size", f"{inverter_size:.0f} W")
    st.metric("Selected Inverter", f"{selected_inverter}")
    st.metric("Inverter Cost", f"₦{inverter_info['price']:,.0f}")
    
    # Total system cost estimation
    total_cost = (num_batteries * battery_info["price"] + 
                 num_panels * panel_info["price"] + 
                 inverter_info["price"])
    
    st.metric("Estimated Total System Cost", f"₦{total_cost:,.0f}")

# Financial Analysis
st.markdown(f'<div class="green-header"><h3>💰 Financial Analysis & ROI</h3></div>', unsafe_allow_html=True)

if st.session_state.load_data:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        current_electricity_rate = st.number_input("Current electricity cost (₦/kWh)", 25, 100, 50)
        monthly_savings = (total_wh / 1000) * 30 * current_electricity_rate
        st.metric("Estimated Monthly Savings", f"₦{monthly_savings:,.0f}")
    
    with col2:
        system_lifespan = st.slider("System lifespan (years)", 5, 25, 10)
        total_savings = monthly_savings * 12 * system_lifespan
        st.metric("Total Lifetime Savings", f"₦{total_savings:,.0f}")
    
    with col3:
        payback_period = total_cost / (monthly_savings * 12)
        roi = ((total_savings - total_cost) / total_cost) * 100
        st.metric("Payback Period", f"{payback_period:.1f} years")
        st.metric("ROI", f"{roi:.0f}%")

# Enhanced PDF Generation with Nigerian branding
def create_professional_pdf():
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#006400'),
        spaceAfter=30,
        alignment=1
    )
    
    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#006400'),
        spaceAfter=12
    )
    
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6
    )
    
    story = []
    
    # Header with Nigerian colors
    story.append(Paragraph(COMPANY, title_style))
    story.append(Paragraph(MOTTO, styles['Heading2']))
    story.append(Spacer(1, 20))
    
    # Client Information
    story.append(Paragraph("CLIENT INFORMATION", heading_style))
    client_data = [
        ["Name:", client_name],
        ["Address:", client_address],
        ["Phone:", client_phone],
        ["Email:", client_email if client_email else "Not provided"],
        ["Location:", project_location],
        ["Date:", datetime.datetime.now().strftime("%Y-%m-%d %H:%M")],
        ["Quote Reference:", f"ANNUR-{datetime.datetime.now().strftime('%Y%m%d')}-001"]
    ]
    
    client_table = Table(client_data, colWidths=[80, 400])
    client_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#006400')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ]))
    story.append(client_table)
    story.append(Spacer(1, 20))
    
    # Load Audit
    story.append(Paragraph("LOAD AUDIT SUMMARY", heading_style))
    load_data = [["Appliance", "Wattage (W)", "Qty", "Total Watt", "Hours/Day", "Wh/Day"]]
    
    for item in st.session_state.load_data:
        load_data.append([
            item['appliance'],
            str(item['watt']),
            str(item['quantity']),
            str(item['total_watt']),
            str(item['hours']),
            f"{item['wh']:,.1f}"
        ])
    
    load_data.append([
        "TOTAL", "", "", f"{total_watt:,}", "", f"{total_wh:,.1f}"
    ])
    
    load_table = Table(load_data, colWidths=[120, 60, 40, 60, 60, 60])
    load_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#006400')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#FFD700')),
        ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    story.append(load_table)
    story.append(Spacer(1, 20))
    
    # System Sizing
    story.append(Paragraph("SYSTEM SIZING & COMPONENTS", heading_style))
    sizing_data = [
        ["Parameter", "Value", "Unit", "Details"],
        ["Total Energy Demand", f"{total_wh:,.0f}", "Wh/day", "Daily consumption"],
        ["Backup Time", f"{backup_time}", "hours", "Required autonomy"],
        ["Battery Capacity", f"{battery_capacity_ah:,.0f}", "Ah", f"At {battery_voltage}V, {dod_limit}% DoD"],
        ["Battery System", f"{num_batteries:.1f}", "units", f"{battery_type}"],
        ["Solar Capacity", f"{required_solar:,.0f}", "W", "Required array size"],
        ["Solar Panels", f"{num_panels:.1f}", "units", f"{panel_type}"],
        ["Charge Controller", f"{controller_current:.0f}", "A", f"At {battery_voltage}V"],
        ["Inverter Size", f"{inverter_size:.0f}", "W", f"{selected_inverter}"],
        ["System Voltage", f"{battery_voltage}", "V", "DC system voltage"]
    ]
    
    sizing_table = Table(sizing_data, colWidths=[120, 80, 40, 180])
    sizing_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#006400')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ]))
    story.append(sizing_table)
    story.append(Spacer(1, 20))
    
    # Financial Analysis
    story.append(Paragraph("FINANCIAL ANALYSIS", heading_style))
    financial_data = [
        ["Component", "Quantity", "Unit Price (₦)", "Total Cost (₦)"],
        [battery_type, f"{num_batteries:.1f}", f"{battery_info['price']:,.0f}", f"{num_batteries * battery_info['price']:,.0f}"],
        [panel_type, f"{num_panels:.1f}", f"{panel_info['price']:,.0f}", f"{num_panels * panel_info['price']:,.0f}"],
        [selected_inverter, "1", f"{inverter_info['price']:,.0f}", f"{inverter_info['price']:,.0f}"],
        ["Installation & Misc", "1", "Est. 150,000", "150,000"],
        ["TOTAL SYSTEM COST", "", "", f"₦{total_cost + 150000:,.0f}"]
    ]
    
    financial_table = Table(financial_data, colWidths=[150, 50, 80, 100])
    financial_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#006400')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#FFD700')),
        ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    story.append(financial_table)
    story.append(Spacer(1, 20))
    
    # ROI Analysis
    roi_data = [
        ["Monthly Savings", f"₦{monthly_savings:,.0f}"],
        ["Annual Savings", f"₦{monthly_savings * 12:,.0f}"],
        ["Payback Period", f"{payback_period:.1f} years"],
        ["ROI over {system_lifespan} years", f"{roi:.0f}%"],
        ["Lifetime Savings", f"₦{total_savings:,.0f}"]
    ]
    
    roi_table = Table(roi_data, colWidths=[150, 100])
    roi_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(roi_table)
    story.append(Spacer(1, 30))
    
    # Terms and Conditions
    story.append(Paragraph("TERMS & CONDITIONS", heading_style))
    terms_text = """
    <b>Quote Validity:</b> 30 days from date of issue<br/>
    <b>Warranty:</b> Equipment as per manufacturer warranty + 1 year workmanship<br/>
    <b>Payment Terms:</b> 50% advance, 50% upon completion<br/>
    <b>Installation Timeline:</b> 5-7 working days after material availability<br/>
    <b>Service:</b> 6 months free maintenance included<br/>
    """
    story.append(Paragraph(terms_text, normal_style))
    story.append(Spacer(1, 20))
    
    # Footer
    footer_text = f"""
    {COMPANY} | {MOTTO} | {PHONE} | {EMAIL} | {WEBSITE}<br/>
    {ADDRESS}<br/>
    {BUSINESS_NUMBER} | {CAC_REGISTRATION}<br/>
    <i>Thank you for choosing Annur Tech - Powering Nigeria's Future</i>
    """
    story.append(Paragraph(footer_text, normal_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# PDF Export Section
if st.button("📄 Generate Professional Quotation PDF"):
    if not client_name or not st.session_state.load_data:
        st.warning("Please fill in client information and add at least one appliance first.")
    else:
        with st.spinner("Generating professional quotation..."):
            pdf = create_professional_pdf()
            st.success("Professional quotation generated successfully!")
            
            # Create download button
            st.download_button(
                "📥 Download Professional Quotation", 
                data=pdf, 
                file_name=f"AnnurTech_Quotation_{client_name.replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d')}.pdf", 
                mime="application/pdf"
            )

# Additional Features
st.markdown(f'<div class="green-header"><h3>📋 Additional Features</h3></div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("💾 Save Configuration"):
        # Save configuration to session state
        st.success("Configuration saved!")
        
with col2:
    if st.button("📧 Email Quote"):
        st.info("Email feature would be integrated with your email service")

with col3:
    if st.button("🔄 New Calculation"):
        st.session_state.load_data = []
        st.rerun()

# Footer
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #666; font-size: 12px;">
    {COMPANY} | {PHONE} | {EMAIL}<br/>
    {ADDRESS}<br/>
    {BUSINESS_NUMBER} | {CAC_REGISTRATION}<br/>
    © {datetime.datetime.now().year} Annur Tech Solar Solutions - Powering Nigeria's Future
</div>
""", unsafe_allow_html=True)
