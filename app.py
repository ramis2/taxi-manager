

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(page_title="Taxi Manager", layout="wide")

# Initialize session state
if 'drivers' not in st.session_state:
    st.session_state.drivers = []
if 'cars' not in st.session_state:
    st.session_state.cars = []

# ==================== SIDEBAR MENU ====================
st.sidebar.title("📋 TaxiManager")

menu = st.sidebar.radio(
    "Navigation",
    [
        "📊 Dashboard",
        "📝 Data Entry", 
        "💰 Balance",
        "👨‍✈️ Driver Management",
        "🚗 Car Management",
        "📄 Driver Letter",
        "🗑️ Delete Driver",
        "📈 Reports",
        "⚙️ Settings"
    ]
)

# ==================== DASHBOARD ====================
if menu == "📊 Dashboard":
    st.title("Dashboard")
    
    # Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Drivers", len(st.session_state.drivers))
    
    with col2:
        st.metric("Total Cars", len(st.session_state.cars))
    
    with col3:
        active_drivers = len([d for d in st.session_state.drivers if d.get('status', '').lower() == 'active'])
        st.metric("Active Drivers", active_drivers)
    
    with col4:
        available_cars = len([c for c in st.session_state.cars if c.get('status', '').lower() == 'available'])
        st.metric("Available Cars", available_cars)
    
    st.divider()
    
    # Recent Data Tables
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("Recent Drivers")
        if st.session_state.drivers:
            drivers_df = pd.DataFrame(st.session_state.drivers)
            st.dataframe(drivers_df, use_container_width=True)
        else:
            st.info("No drivers added yet")
    
    with col_right:
        st.subheader("Recent Cars")
        if st.session_state.cars:
            cars_df = pd.DataFrame(st.session_state.cars)
            st.dataframe(cars_df, use_container_width=True)
        else:
            st.info("No cars added yet")

# ==================== DATA ENTRY ====================
elif menu == "📝 Data Entry":
    st.title("Data Entry")
    
    tab1, tab2 = st.tabs(["➕ Add Driver", "➕ Add Car"])
    
    with tab1:
        st.subheader("Add New Driver")
        
        with st.form("add_driver_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Driver Name *")
                license_num = st.text_input("License Number *")
                phone = st.text_input("Phone Number")
            
            with col2:
                status = st.selectbox("Status", ["Active", "Inactive", "On Leave"])
                email = st.text_input("Email")
                address = st.text_input("Address")
            
            if st.form_submit_button("➕ Add Driver"):
                if name and license_num:
                    new_driver = {
                        'id': len(st.session_state.drivers) + 1,
                        'name': name,
                        'license': license_num,
                        'phone': phone,
                        'status': status,
                        'email': email,
                        'address': address,
                        'date_added': datetime.now().strftime("%Y-%m-%d")
                    }
                    st.session_state.drivers.append(new_driver)
                    st.success(f"Driver '{name}' added successfully!")
                else:
                    st.error("Please fill required fields (*)")
    
    with tab2:
        st.subheader("Add New Car")
        
        with st.form("add_car_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                model = st.text_input("Car Model *", placeholder="Ford Fusion")
                year = st.number_input("Year *", min_value=2000, max_value=2026, value=2024)
                cpnc = st.text_input("CPNC Number *", placeholder="CPNC2001")
            
            with col2:
                plate = st.text_input("License Plate *", placeholder="DEF-456")
                color = st.text_input("Color")
                mileage = st.number_input("Mileage (km)", min_value=0, value=0)
                status = st.selectbox("Status", ["Available", "In Service", "Maintenance"])
            
            if st.form_submit_button("➕ Add Car"):
                if model and cpnc and plate:
                    new_car = {
                        'id': len(st.session_state.cars) + 1,
                        'model': model,
                        'year': year,
                        'cpnc': cpnc,
                        'plate': plate,
                        'color': color,
                        'mileage': mileage,
                        'status': status,
                        'date_added': datetime.now().strftime("%Y-%m-%d")
                    }
                    st.session_state.cars.append(new_car)
                    st.success(f"Car '{model}' added successfully!")
                else:
                    st.error("Please fill required fields (*)")

# ==================== SIMPLE OTHER PAGES ====================
elif menu == "💰 Balance":
    st.title("Balance")
    st.write("Financial balance section")
    
elif menu == "👨‍✈️ Driver Management":
    st.title("Driver Management")
    st.write("Manage drivers here")
    
elif menu == "🚗 Car Management":
    st.title("Car Management")
    st.write("Manage cars here")
    
elif menu == "📄 Driver Letter":
    st.title("Driver Letter")
    st.write("Generate driver letters")
    
elif menu == "🗑️ Delete Driver":
    st.title("Delete Driver")
    st.write("Delete drivers here")
    
elif menu == "📈 Reports":
    st.title("Reports")
    st.write("Generate reports here")
    
elif menu == "⚙️ Settings":
    st.title("Settings")
    st.write("App settings here")

