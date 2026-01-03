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

# ==================== DRIVER MANAGEMENT ====================
elif menu == "👨‍✈️ Driver Management":
    st.title("Driver Management")
    
    if st.session_state.drivers:
        for i, driver in enumerate(st.session_state.drivers):
            with st.expander(f"{driver['name']} - {driver['license']} ({driver['status']})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    new_name = st.text_input("Name", value=driver['name'], key=f"dr_name_{i}")
                    new_license = st.text_input("License", value=driver['license'], key=f"dr_license_{i}")
                    new_phone = st.text_input("Phone", value=driver['phone'], key=f"dr_phone_{i}")
                
                with col2:
                    new_status = st.selectbox(
                        "Status",
                        ["Active", "Inactive", "On Leave"],
                        index=["Active", "Inactive", "On Leave"].index(driver['status']),
                        key=f"dr_status_{i}"
                    )
                    new_email = st.text_input("Email", value=driver.get('email', ''), key=f"dr_email_{i}")
                    new_address = st.text_input("Address", value=driver.get('address', ''), key=f"dr_address_{i}")
                
                if st.button("💾 Save Changes", key=f"save_dr_{i}"):
                    st.session_state.drivers[i].update({
                        'name': new_name,
                        'license': new_license,
                        'phone': new_phone,
                        'status': new_status,
                        'email': new_email,
                        'address': new_address
                    })
                    st.success("✅ Driver updated successfully!")
                    st.rerun()
    else:
        st.info("No drivers to manage")

# ==================== CAR MANAGEMENT ====================
elif menu == "🚗 Car Management":
    st.title("Car Management")
    
    if st.session_state.cars:
        for i, car in enumerate(st.session_state.cars):
            with st.expander(f"{car['model']} - {car['plate']} ({car['status']})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    new_model = st.text_input("Model", value=car['model'], key=f"car_model_{i}")
                    new_year = st.number_input("Year", value=car['year'], key=f"car_year_{i}")
                    new_cpnc = st.text_input("CPNC", value=car['cpnc'], key=f"car_cpnc_{i}")
                
                with col2:
                    new_plate = st.text_input("Plate", value=car['plate'], key=f"car_plate_{i}")
                    new_color = st.text_input("Color", value=car['color'], key=f"car_color_{i}")
                    new_mileage = st.number_input("Mileage", value=car['mileage'], key=f"car_mileage_{i}")
                    new_status = st.selectbox(
                        "Status",
                        ["Available", "In Service", "Maintenance"],
                        index=["Available", "In Service", "Maintenance"].index(car['status']),
                        key=f"car_status_{i}"
                    )
                
                if st.button("💾 Save Changes", key=f"save_car_{i}"):
                    st.session_state.cars[i].update({
                        'model': new_model,
                        'year': new_year,
                        'cpnc': new_cpnc,
                        'plate': new_plate,
                        'color': new_color,
                        'mileage': new_mileage,
                        'status': new_status
                    })
                    st.success("✅ Car updated successfully!")
                    st.rerun()
    else:
        st.info("No cars to manage")

# ==================== OTHER PAGES ====================
elif menu == "💰 Balance":
    st.title("Balance")
    st.write("Financial balance and transactions will appear here")
    
elif menu == "📄 Driver Letter":
    st.title("Driver Letter")
    st.write("Generate letters and documents for drivers")
    
elif menu == "🗑️ Delete Driver":
    st.title("Delete Driver")
    
    if st.session_state.drivers:
        driver_options = {f"{d['name']} ({d['license']})": i for i, d in enumerate(st.session_state.drivers)}
        selected = st.selectbox("Select driver to delete:", list(driver_options.keys()))
        
        if selected:
            idx = driver_options[selected]
            st.warning(f"⚠️ Delete {selected}?")
            
            if st.button("🗑️ Confirm Delete", type="primary"):
                del st.session_state.drivers[idx]
                st.success("✅ Driver deleted successfully!")
                st.rerun()
    else:
        st.info("No drivers to delete")
    
elif menu == "📈 Reports":
    st.title("Reports")
    st.write("Generate various reports here")
    
elif menu == "⚙️ Settings":
    st.title("Settings")
    st.write("App settings and configuration")
