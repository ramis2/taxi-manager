import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import json
import os

# ==================== DATA PERSISTENCE FUNCTIONS ====================
def load_data():
    """Load data from CSV files if they exist"""
    try:
        if os.path.exists('drivers.csv'):
            drivers_df = pd.read_csv('drivers.csv')
            drivers_df = drivers_df.fillna('')
            st.session_state.drivers = drivers_df.to_dict('records')
        else:
            st.session_state.drivers = []
        
        if os.path.exists('cars.csv'):
            cars_df = pd.read_csv('cars.csv')
            cars_df = cars_df.fillna('')
            st.session_state.cars = cars_df.to_dict('records')
        else:
            st.session_state.cars = []
        
        if os.path.exists('transactions.csv'):
            transactions_df = pd.read_csv('transactions.csv')
            transactions_df = transactions_df.fillna('')
            st.session_state.balance_data = transactions_df.to_dict('records')
        else:
            st.session_state.balance_data = []
            
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.session_state.drivers = []
        st.session_state.cars = []
        st.session_state.balance_data = []

def save_data():
    """Save all data to CSV files"""
    try:
        if 'drivers' in st.session_state and st.session_state.drivers:
            pd.DataFrame(st.session_state.drivers).to_csv('drivers.csv', index=False)
        
        if 'cars' in st.session_state and st.session_state.cars:
            pd.DataFrame(st.session_state.cars).to_csv('cars.csv', index=False)
        
        if 'balance_data' in st.session_state and st.session_state.balance_data:
            pd.DataFrame(st.session_state.balance_data).to_csv('transactions.csv', index=False)
            
        return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False

# ==================== INITIALIZE APP ====================
st.set_page_config(page_title="Taxi Manager", layout="wide")

# Load existing data on app start
if 'data_loaded' not in st.session_state:
    load_data()
    st.session_state.data_loaded = True

# Initialize empty lists if they don't exist
if 'drivers' not in st.session_state:
    st.session_state.drivers = []
if 'cars' not in st.session_state:
    st.session_state.cars = []
if 'balance_data' not in st.session_state:
    st.session_state.balance_data = []

# ==================== SIDEBAR MENU ====================
st.sidebar.title("TaxiManager")

menu = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Data Entry", 
        "Balance",
        "Driver Management",
        "Car Management",
        "Driver Letter",
        "Delete Driver",
        "Reports",
        "Settings"
    ]
)

# ==================== DASHBOARD ====================
if menu == "Dashboard":
    st.title("Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Drivers", len(st.session_state.drivers))
    
    with col2:
        st.metric("Total Cars", len(st.session_state.cars))
    
    with col3:
        active_drivers = len([d for d in st.session_state.drivers if str(d.get('status', '')).lower() == 'active'])
        st.metric("Active Drivers", active_drivers)
    
    with col4:
        available_cars = len([c for c in st.session_state.cars if str(c.get('status', '')).lower() == 'available'])
        st.metric("Available Cars", available_cars)
    
    st.divider()
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("Recent Drivers")
        if st.session_state.drivers:
            drivers_df = pd.DataFrame(st.session_state.drivers[-5:])
            st.dataframe(drivers_df, use_container_width=True)
        else:
            st.info("No drivers added yet")
    
    with col_right:
        st.subheader("Recent Cars")
        if st.session_state.cars:
            cars_df = pd.DataFrame(st.session_state.cars[-5:])
            st.dataframe(cars_df, use_container_width=True)
        else:
            st.info("No cars added yet")

# ==================== DATA ENTRY ====================
elif menu == "Data Entry":
    st.title("Data Entry")
    
    tab1, tab2, tab3 = st.tabs(["Add Driver", "Add Car", "Add Transaction"])
    
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
            
            submitted = st.form_submit_button("Add Driver")
            
            if submitted:
                if name and license_num:
                    new_driver = {
                        'id': len(st.session_state.drivers) + 1,
                        'name': name,
                        'license': license_num,
                        'phone': phone,
                        'status': status,
                        'email': email,
                        'address': address,
                        'date_added': datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    st.session_state.drivers.append(new_driver)
                    save_data()
                    st.success(f"Driver '{name}' added successfully!")
                    st.rerun()
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
            
            submitted = st.form_submit_button("Add Car")
            
            if submitted:
                if model and cpnc and plate:
                    new_car = {
                        'id': len(st.session_state.cars) + 1,
                        'model': model,
                        'year': int(year),
                        'cpnc': cpnc,
                        'plate': plate,
                        'color': color,
                        'mileage': int(mileage),
                        'status': status,
                        'date_added': datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    st.session_state.cars.append(new_car)
                    save_data()
                    st.success(f"Car '{model}' added successfully!")
                    st.rerun()
                else:
                    st.error("Please fill required fields (*)")
    
    with tab3:
        st.subheader("Add Financial Transaction")
        
        with st.form("add_transaction_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                transaction_type = st.selectbox("Type", ["Income", "Expense", "Salary", "Maintenance"])
                amount = st.number_input("Amount ($)", min_value=0.0, value=0.0, step=10.0)
                description = st.text_area("Description")
            
            with col2:
                date = st.date_input("Date", value=datetime.now())
                category = st.selectbox("Category", ["Fuel", "Repairs", "Insurance", "Driver Payment", "Other"])
                driver_options = ["None"] + [d['name'] for d in st.session_state.drivers]
                driver_name = st.selectbox("Driver (if applicable)", driver_options)
            
            submitted = st.form_submit_button("Add Transaction")
            
            if submitted:
                new_transaction = {
                    'id': len(st.session_state.balance_data) + 1,
                    'type': transaction_type,
                    'amount': float(amount),
                    'description': description,
                    'date': date.strftime("%Y-%m-%d"),
                    'category': category,
                    'driver': driver_name if driver_name != "None" else "",
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                st.session_state.balance_data.append(new_transaction)
                save_data()
                st.success(f"Transaction added successfully!")
                st.rerun()

# ==================== BALANCE ====================
elif menu == "Balance":
    st.title("Balance & Finance")
    
    if st.session_state.balance_data:
        income = sum(t['amount'] for t in st.session_state.balance_data if t['type'] == 'Income')
        expenses = sum(t['amount'] for t in st.session_state.balance_data if t['type'] in ['Expense', 'Salary', 'Maintenance'])
        balance = income - expenses
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Income", f"${income:,.2f}")
        with col2:
            st.metric("Total Expenses", f"${expenses:,.2f}")
        with col3:
            st.metric("Balance", f"${balance:,.2f}")
        
        st.subheader("All Transactions")
        balance_df = pd.DataFrame(st.session_state.balance_data)
        st.dataframe(balance_df, use_container_width=True)
        
        if st.button("Export to CSV"):
            csv = balance_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="transactions.csv",
                mime="text/csv"
            )
    else:
        st.info("No financial transactions recorded yet.")

# ==================== DRIVER MANAGEMENT ====================
elif menu == "Driver Management":
    st.title("Driver Management")
    
    if st.session_state.drivers:
        for i, driver in enumerate(st.session_state.drivers):
            with st.expander(f"{driver.get('name', '')} - {driver.get('license', '')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    new_name = st.text_input("Name", value=driver.get('name', ''), key=f"dr_name_{i}")
                    new_license = st.text_input("License", value=driver.get('license', ''), key=f"dr_license_{i}")
                    new_phone = st.text_input("Phone", value=driver.get('phone', ''), key=f"dr_phone_{i}")
                
                with col2:
                    new_status = st.selectbox("Status", ["Active", "Inactive", "On Leave"], 
                                             index=["Active", "Inactive", "On Leave"].index(driver.get('status', 'Active')), 
                                             key=f"dr_status_{i}")
                    new_email = st.text_input("Email", value=driver.get('email', ''), key=f"dr_email_{i}")
                    new_address = st.text_input("Address", value=driver.get('address', ''), key=f"dr_address_{i}")
                
                if st.button("Save Changes", key=f"save_dr_{i}"):
                    st.session_state.drivers[i].update({
                        'name': new_name,
                        'license': new_license,
                        'phone': new_phone,
                        'status': new_status,
                        'email': new_email,
                        'address': new_address
                    })
                    save_data()
                    st.success("Driver updated!")
                    st.rerun()
    else:
        st.info("No drivers to manage.")

# ==================== CONTINUE WITH SIMPLE VERSIONS ====================
elif menu == "Car Management":
    st.title("Car Management")
    st.write("Car management functionality here")

elif menu == "Driver Letter":
    st.title("Driver Letter")
    st.write("Driver letter generator here")

elif menu == "Delete Driver":
    st.title("Delete Driver")
    st.write("Delete driver functionality here")

elif menu == "Reports":
    st.title("Reports")
    st.write("Reports and analytics here")

elif menu == "Settings":
    st.title("Settings")
    st.write("App settings here")
