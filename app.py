# ==================== IMPORTS ====================
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
        # Load drivers
        if os.path.exists('drivers.csv'):
            drivers_df = pd.read_csv('drivers.csv')
            # Convert NaN to empty string
            drivers_df = drivers_df.fillna('')
            st.session_state.drivers = drivers_df.to_dict('records')
        else:
            st.session_state.drivers = []
        
        # Load cars
        if os.path.exists('cars.csv'):
            cars_df = pd.read_csv('cars.csv')
            cars_df = cars_df.fillna('')
            st.session_state.cars = cars_df.to_dict('records')
        else:
            st.session_state.cars = []
        
        # Load transactions
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
        # Save drivers
        if 'drivers' in st.session_state and st.session_state.drivers:
            drivers_df = pd.DataFrame(st.session_state.drivers)
            drivers_df.to_csv('drivers.csv', index=False)
        
        # Save cars
        if 'cars' in st.session_state and st.session_state.cars:
            cars_df = pd.DataFrame(st.session_state.cars)
            cars_df.to_csv('cars.csv', index=False)
        
        # Save transactions
        if 'balance_data' in st.session_state and st.session_state.balance_data:
            transactions_df = pd.DataFrame(st.session_state.balance_data)
            transactions_df.to_csv('transactions.csv', index=False)
            
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
if 'reports' not in st.session_state:
    st.session_state.reports = []

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
        active_drivers = len([d for d in st.session_state.drivers if str(d.get('status', '')).lower() == 'active'])
        st.metric("Active Drivers", active_drivers)
    
    with col4:
        available_cars = len([c for c in st.session_state.cars if str(c.get('status', '')).lower() == 'available'])
        st.metric("Available Cars", available_cars)
    
    st.divider()
    
    # Recent Data Tables
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("Recent Drivers")
        if st.session_state.drivers:
            drivers_df = pd.DataFrame(st.session_state.drivers[-5:])  # Last 5
            display_cols = ['name', 'license', 'phone', 'status']
            available_cols = [col for col in display_cols if col in drivers_df.columns]
            if available_cols:
                st.dataframe(drivers_df[available_cols], use_container_width=True)
            else:
                st.dataframe(drivers_df, use_container_width=True)
        else:
            st.info("No drivers added yet")
    
    with col_right:
        st.subheader("Recent Cars")
        if st.session_state.cars:
            cars_df = pd.DataFrame(st.session_state.cars[-5:])  # Last 5
            display_cols = ['model', 'cpnc', 'plate', 'status']
            available_cols = [col for col in display_cols if col in cars_df.columns]
            if available_cols:
                st.dataframe(cars_df[available_cols], use_container_width=True)
            else:
                st.dataframe(cars_df, use_container_width=True)
        else:
            st.info("No cars added yet")

# ==================== DATA ENTRY ====================
elif menu == "📝 Data Entry":
    st.title("Data Entry")
    
    tab1, tab2, tab3 = st.tabs(["➕ Add Driver", "➕ Add Car", "➕ Add Transaction"])
    
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
            
            submitted = st.form_submit_button("➕ Add Driver")
            
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
                    save_data()  # Save to CSV
                    st.success(f"✅ Driver '{name}' added successfully!")
                    st.rerun()
                else:
                    st.error("❌ Please fill required fields (*)")
    
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
            
            submitted = st.form_submit_button("➕ Add Car")
            
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
                    save_data()  # Save to CSV
                    st.success(f"✅ Car '{model}' added successfully!")
                    st.rerun()
                else:
                    st.error("❌ Please fill required fields (*)")
    
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
            
            submitted = st.form_submit_button("➕ Add Transaction")
            
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
                save_data()  # Save to CSV
                st.success(f"✅ Transaction added successfully!")
                st.rerun()

# ==================== BALANCE ====================
elif menu == "💰 Balance":
    st.title("Balance & Finance")
    
    if st.session_state.balance_data:
        # Summary metrics
        income = sum(t['amount'] for t in st.session_state.balance_data if t['type'] == 'Income')
        expenses = sum(t['amount'] for t in st.session_state.balance_data if t['type'] in ['Expense', 'Salary', 'Maintenance'])
        balance = income - expenses
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Income", f"${income:,.2f}")
        with col2:
            st.metric("Total Expenses", f"${expenses:,.2f}")
        with col3:
            st.metric("Balance", f"${balance:,.2f}", delta=f"{balance:,.2f}")
        
        # Transactions table
        st.subheader("All Transactions")
        balance_df = pd.DataFrame(st.session_state.balance_data)
        st.dataframe(balance_df, use_container_width=True)
        
        # Export option
        if st.button("📥 Export to CSV"):
            csv = balance_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="transactions.csv",
                mime="text/csv"
            )
    else:
        st.info("💸 No financial transactions recorded yet.")
        st.write("Go to **Data Entry → Add Transaction** to record income and expenses.")

# ==================== DRIVER MANAGEMENT ====================
elif menu == "👨‍✈️ Driver Management":
    st.title("Driver Management")
    
    if st.session_state.drivers:
        for i, driver in enumerate(st.session_state.drivers):
            with st.expander(f"👤 {driver['name']} - {driver['license']} ({driver['status']})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    new_name = st.text_input("Name", value=driver.get('name', ''), key=f"dr_name_{i}")
                    new_license = st.text_input("License", value=driver.get('license', ''), key=f"dr_license_{i}")
                    new_phone = st.text_input("Phone", value=driver.get('phone', ''), key=f"dr_phone_{i}")
                
                with col2:
                    current_status = driver.get('status', 'Active')
                    status_options = ["Active", "Inactive", "On Leave"]
                    status_index = status_options.index(current_status) if current_status in status_options else 0
                    new_status = st.selectbox(
                        "Status",
                        status_options,
                        index=status_index,
                        key=f"dr_status_{i}"
                    )
                    new_email = st.text_input("Email", value=driver.get('email', ''), key=f"dr_email_{i}")
                    new_address = st.text_input("Address", value=driver.get('address', ''), key=f"dr_address_{i}")
                
                col_save, col_delete = st.columns(2)
                with col_save:
                    if st.button("💾 Save Changes", key=f"save_dr_{i}"):
                        st.session_state.drivers[i].update({
                            'name': new_name,
                            'license': new_license,
                            'phone': new_phone,
                            'status': new_status,
                            'email': new_email,
                            'address': new_address
                        })
                        save_data()  # Save to CSV
                        st.success("✅ Driver updated successfully!")
                        st.rerun()
                
                with col_delete:
                    if st.button("🗑️ Delete", key=f"delete_dr_{i}", type="secondary"):
                        del st.session_state.drivers[i]
                        save_data()  # Save to CSV
                        st.success("✅ Driver deleted!")
                        st.rerun()
    else:
        st.info("👥 No drivers to manage. Add drivers in **Data Entry**.")

# ==================== CAR MANAGEMENT ====================
elif menu == "🚗 Car Management":
    st.title("Car Management")
    
    if st.session_state.cars:
        for i, car in enumerate(st.session_state.cars):
            with st.expander(f"🚗 {car['model']} - {car['plate']} ({car['status']})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    new_model = st.text_input("Model", value=car.get('model', ''), key=f"car_model_{i}")
                    new_year = st.number_input("Year", value=int(car.get('year', 2024)), key=f"car_year_{i}")
                    new_cpnc = st.text_input("CPNC", value=car.get('cpnc', ''), key=f"car_cpnc_{i}")
                
                with col2:
                    new_plate = st.text_input("Plate", value=car.get('plate', ''), key=f"car_plate_{i}")
                    new_color = st.text_input("Color", value=car.get('color', ''), key=f"car_color_{i}")
                    new_mileage = st.number_input("Mileage", value=int(car.get('mileage', 0)), key=f"car_mileage_{i}")
                    
                    current_status = car.get('status', 'Available')
                    status_options = ["Available", "In Service", "Maintenance"]
                    status_index = status_options.index(current_status) if current_status in status_options else 0
                    new_status = st.selectbox(
                        "Status",
                        status_options,
                        index=status_index,
                        key=f"car_status_{i}"
                    )
                
                col_save, col_delete = st.columns(2)
                with col_save:
                    if st.button("💾 Save Changes", key=f"save_car_{i}"):
                        st.session_state.cars[i].update({
                            'model': new_model,
                            'year': int(new_year),
                            'cpnc': new_cpnc,
                            'plate': new_plate,
                            'color': new_color,
                            'mileage': int(new_mileage),
                            'status': new_status
                        })
                        save_data()  # Save to CSV
                        st.success("✅ Car updated successfully!")
                        st.rerun()
                
                with col_delete:
                    if st.button("🗑️ Delete", key=f"delete_car_{i}", type="secondary"):
                        del st.session_state.cars[i]
                        save_data()  # Save to CSV
                        st.success("✅ Car deleted!")
                        st.rerun()
    else:
        st.info("🚙 No cars to manage. Add cars in **Data Entry**.")

# ==================== DRIVER LETTER ====================
elif menu == "📄 Driver Letter":
    st.title("Driver Letter Generator")
    
    if st.session_state.drivers:
        # Create driver selection options
        driver_options = [f"{d.get('name', '')} ({d.get('license', '')})" for d in st.session_state.drivers]
        selected_driver = st.selectbox("Select Driver", driver_options)
        
        letter_type = st.selectbox("Letter Type", 
                                  ["Employment Certificate", 
                                   "Salary Certificate", 
                                   "Warning Letter",
                                   "Appreciation Letter",
                                   "Custom Letter"])
        
        st.subheader("Letter Content")
        
        # Default letter content based on type
        default_content = ""
        if letter_type == "Employment Certificate":
            default_content = f"This is to certify that {selected_driver.split('(')[0].strip()} is employed as a driver with our company.\n\n"
            default_content += f"License Number: {selected_driver.split('(')[1].replace(')', '')}\n"
            default_content += "Position: Professional Driver\n"
            default_content += f"Date: {datetime.now().strftime('%B %d, %Y')}\n\n"
            default_content += "Sincerely,\nTaxi Manager"
        
        elif letter_type == "Salary Certificate":
            default_content = f"SALARY CERTIFICATE\n\n"
            default_content += f"This certifies that {selected_driver.split('(')[0].strip()} has been receiving a monthly salary of $XXXX.\n\n"
            default_content += "For any queries, please contact our office.\n\n"
            default_content += f"Date: {datetime.now().strftime('%B %d, %Y')}"
        
        letter_content = st.text_area("Enter letter content", 
                                     value=default_content,
                                     height=250)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📄 Preview Letter"):
                st.subheader("Letter Preview")
                st.text(letter_content)
        
        with col2:
            if st.button("📥 Generate & Download Letter"):
                driver_name_clean = selected_driver.split('(')[0].strip().replace(" ", "_")
                file_name = f"{driver_name_clean}_{letter_type.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.txt"
                
                st.success(f"✅ Letter generated successfully!")
                st.download_button(
                    label="📥 Download Letter",
                    data=letter_content,
                    file_name=file_name,
                    mime="text/plain"
                )
    else:
        st.info("👥 No drivers available. Please add drivers first in the **Data Entry** section.")

# ==================== DELETE DRIVER ====================
elif menu == "🗑️ Delete Driver":
    st.title("Delete Driver")
    
    if st.session_state.drivers:
        driver_options = {f"{d.get('name', '')} ({d.get('license', '')})": i for i, d in enumerate(st.session_state.drivers)}
        selected = st.selectbox("Select driver to delete:", list(driver_options.keys()))
        
        if selected:
            idx = driver_options[selected]
            driver = st.session_state.drivers[idx]
            
            st.warning(f"⚠️ You are about to delete: **{driver.get('name', '')}**")
            st.write(f"License: {driver.get('license', '')}")
            st.write(f"Status: {driver.get('status', '')}")
            
            confirm = st.checkbox("I confirm I want to delete this driver")
            
            if confirm and st.button("🗑️ DELETE DRIVER", type="primary"):
                del st.session_state.drivers[idx]
                save_data()  # Save to CSV
                st.success("✅ Driver deleted successfully!")
                st.rerun()
    else:
        st.info("👥 No drivers to delete.")

# ==================== REPORTS ====================
elif menu == "📈 Reports":
    st.title("Reports & Analytics")
    
    report_type = st.selectbox("Select Report Type", 
                              ["Driver Performance", 
                               "Car Utilization", 
                               "Financial Summary",
                               "Monthly Summary"])
    
    if report_type == "Driver Performance":
        st.subheader("Driver Performance Report")
        if st.session_state.drivers:
            drivers_df = pd.DataFrame(st.session_state.drivers)
            st.dataframe(drivers_df, use_container_width=True)
        else:
            st.info("No driver data available")
    
    elif report_type == "Car Utilization":
        st.subheader("Car Utilization Report")
        if st.session_state.cars:
            cars_df = pd.DataFrame(st.session_state.cars)
            st.dataframe(cars_df, use_container_width=True)
        else:
            st.info("No car data available")
    
    elif report_type == "Financial Summary":
        st.subheader("Financial Summary Report")
        if st.session_state.balance_data:
            balance_df = pd.DataFrame(st.session_state.balance_data)
            
            # Summary by category
            if 'category' in balance_df.columns and 'amount' in balance_df.columns:
                summary = balance_df.groupby('category')['amount'].sum().reset_index()
                if not summary.empty:
                    st.bar_chart(summary.set_index('category'))
            
            st.dataframe(balance_df, use_container_width=True)
        else:
            st.info("No financial data available")
    
    elif report_type == "Monthly Summary":
        st.subheader("Monthly Summary Report")
        st.info("Monthly reports will be available when you have more data.")

# ==================== SETTINGS ====================
elif menu == "⚙️ Settings":
    st.title("Settings")
    
    st.subheader("Data Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Save/Load Data**")
        if st.button("💾 Save All Data Now"):
            if save_data():
                st.success("✅ All data saved successfully!")
            else:
                st.error("❌ Error saving data")
        
        if st.button("🔄 Load Saved Data"):
            load_data()
            st.success("✅ Data loaded successfully!")
            st.rerun()
    
    with col2:
        st.write("**Export Data**")
        if st.button("📤 Export to JSON"):
            export_data = {
                'drivers': st.session_state.drivers,
                'cars': st.session_state.cars,
                'transactions': st.session_state.balance_data,
                'export_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            json_data = json.dumps(export_data, indent=2)
            st.download_button(
                label="📥 Download JSON",
                data=json_data,
                file_name=f"taxi_manager_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col3:
        st.write("**Clear All Data**")
        st.warning("⚠️ This will delete ALL data!")
        if st.button("🗑️ Clear All Data", type="secondary"):
            if st.button("⚠️ CONFIRM CLEAR ALL", type="primary"):
                st.session_state.drivers = []
                st.session_state.cars = []
                st.session_state.balance_data = []
                # Also delete CSV files
                for file in ['drivers.csv', 'cars.csv', 'transactions.csv']:
                    if os.path.exists(file):
                        os.remove(file)
                st.success("✅ All data cleared successfully!")
                st.rerun()
    
    st.subheader("App Configuration")
    app_name = st.text_input("App Name", value="Taxi Manager")
    currency = st.selectbox("Currency", ["USD", "EUR", "GBP", "Other"])
    language = st.selectbox("Language", ["English", "Spanish", "French", "Arabic"])
    
    if st.button("💾 Save Settings"):
        st.success("✅ Settings saved successfully!")
