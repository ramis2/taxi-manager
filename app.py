import streamlit as st
import os
import sys
import sqlite3  # FIXED: Changed from "sqlites" to "sqlite3"
import pandas as pd
from datetime import datetime

# Set page config FIRST
st.set_page_config(
    page_title="Taxi Manager",
    page_icon="🚕",
    layout="wide"
)

# DEBUG: Show what's happening
st.sidebar.title("DEBUG INFO")
st.sidebar.write(f"Python: {sys.version}")  # ✅ FIXED
st.sidebar.write(f"Current dir: {os.getcwd()}")  # ✅ FIXED
st.sidebar.write(f"Files in dir: {os.listdir('.')}")  # ✅ FIXED

# Check for common folders
folders_to_check = ['templates', 'data', 'letters', 'docs']
for folder in folders_to_check:
    exists = os.path.exists(folder)
    st.sidebar.write(f"{folder}: {'✅' if exists else '❌'}")  # ✅ FIXED

st.sidebar.divider()

# ============ DATABASE SETUP ============
def init_db():
    conn = sqlite3.connect('taxi_manager.db')
    c = conn.cursor()
    
    # Create drivers table if not exists
    c.execute('''CREATE TABLE IF NOT EXISTS drivers
                 (id INTEGER PRIMARY KEY,
                  name TEXT,
                  license TEXT,
                  phone TEXT,
                  status TEXT,
                  join_date TEXT)''')
    
    # Create cars table if not exists
    c.execute('''CREATE TABLE IF NOT EXISTS cars
                 (id INTEGER PRIMARY KEY,
                  plate TEXT,
                  model TEXT,
                  driver_id INTEGER,
                  status TEXT)''')
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

# ============ SIMPLE NAVIGATION ============
st.sidebar.title("🚕 Taxi Manager")
menu = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Data Entry", "Balance", "Driver Management", 
     "Car Management", "Driver Letter", "Delete Driver", "Reports", "Settings"]
)

# ============ DASHBOARD ============
if menu == "Dashboard":
    st.title("📊 Dashboard")
    
    # Get stats
    conn = sqlite3.connect('taxi_manager.db')
    total_drivers = pd.read_sql_query("SELECT COUNT(*) as count FROM drivers", conn).iloc[0]['count']
    total_cars = pd.read_sql_query("SELECT COUNT(*) as count FROM cars", conn).iloc[0]['count']
    active_drivers = pd.read_sql_query("SELECT COUNT(*) as count FROM drivers WHERE status='active'", conn).iloc[0]['count']
    conn.close()
    
    # Display stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Drivers", total_drivers)
    with col2:
        st.metric("Total Cars", total_cars)
    with col3:
        st.metric("Active Drivers", active_drivers)
    
    # Show recent drivers
    st.subheader("Recent Drivers")
    conn = sqlite3.connect('taxi_manager.db')
    drivers_df = pd.read_sql_query("SELECT * FROM drivers ORDER BY id DESC LIMIT 10", conn)
    conn.close()
    st.dataframe(drivers_df, use_container_width=True)

# ============ DATA ENTRY ============
elif menu == "Data Entry":
    st.title("📝 Data Entry")
    
    tab1, tab2 = st.tabs(["Add Driver", "Add Car"])
    
    with tab1:
        with st.form("driver_form"):
            name = st.text_input("Driver Name")
            license_no = st.text_input("License Number")
            phone = st.text_input("Phone Number")
            status = st.selectbox("Status", ["active", "inactive"])
            
            if st.form_submit_button("Add Driver"):
                if name and license_no:
                    conn = sqlite3.connect('taxi_manager.db')
                    c = conn.cursor()
                    c.execute("INSERT INTO drivers (name, license, phone, status, join_date) VALUES (?, ?, ?, ?, ?)",
                             (name, license_no, phone, status, datetime.now().strftime("%Y-%m-%d")))
                    conn.commit()
                    conn.close()
                    st.success(f"Driver {name} added successfully!")
                else:
                    st.error("Please fill in all required fields")
    
    with tab2:
        with st.form("car_form"):
            plate = st.text_input("Plate Number")
            model = st.text_input("Car Model")
            driver_id = st.number_input("Driver ID", min_value=1, step=1)
            status = st.selectbox("Car Status", ["active", "maintenance", "retired"])
            
            if st.form_submit_button("Add Car"):
                if plate and model:
                    conn = sqlite3.connect('taxi_manager.db')
                    c = conn.cursor()
                    c.execute("INSERT INTO cars (plate, model, driver_id, status) VALUES (?, ?, ?, ?)",
                             (plate, model, driver_id, status))
                    conn.commit()
                    conn.close()
                    st.success(f"Car {plate} added successfully!")
                else:
                    st.error("Please fill in all required fields")

# ============ DRIVER LETTER ============
elif menu == "Driver Letter":
    st.title("📄 Driver Letter Generator")
    
    # Get drivers for selection
    conn = sqlite3.connect('taxi_manager.db')
    drivers = pd.read_sql_query("SELECT id, name, license FROM drivers", conn)
    conn.close()
    
    if not drivers.empty:
        # Driver selection
        selected_driver = st.selectbox(
            "Select Driver",
            drivers.apply(lambda x: f"{x['id']} - {x['name']} (License: {x['license']})", axis=1)
        )
        
        driver_id = int(selected_driver.split(" - ")[0]) if selected_driver else None
        
        # Letter type
        letter_type = st.selectbox("Letter Type", 
                                  ["Employment Verification", 
                                   "License Confirmation",
                                   "General Certificate"])
        
        # Generate letter
        if st.button("Generate Letter", type="primary"):
            if driver_id:
                # Get driver details
                conn = sqlite3.connect('taxi_manager.db')
                driver_details = pd.read_sql_query(f"SELECT * FROM drivers WHERE id={driver_id}", conn)
                conn.close()
                
                if not driver_details.empty:
                    driver = driver_details.iloc[0]
                    
                    # Create letter content
                    letter = f"""
                    TO WHOM IT MAY CONCERN
                    
                    Date: {datetime.now().strftime('%B %d, %Y')}
                    
                    Subject: {letter_type} for {driver['name']}
                    
                    This is to certify that {driver['name']} (License Number: {driver['license']}) 
                    is a registered taxi driver with our company.
                    
                    The driver joined on {driver['join_date']} and is currently {driver['status']}.
                    
                    For any further information, please contact our office.
                    
                    Sincerely,
                    Taxi Manager
                    """
                    
                    st.text_area("Generated Letter", letter, height=300)
                    
                    # Download button
                    st.download_button(
                        "📥 Download Letter",
                        letter,
                        file_name=f"letter_{driver['name']}_{datetime.now().strftime('%Y%m%d')}.txt",
                        mime="text/plain"
                    )
                else:
                    st.error("Driver not found!")
            else:
                st.error("Please select a driver")
    else:
        st.warning("No drivers found. Please add drivers first in Data Entry.")

# ============ OTHER PAGES (PLACEHOLDERS) ============
elif menu == "Balance":
    st.title("💰 Balance")
    st.write("Balance management coming soon...")

elif menu == "Driver Management":
    st.title("👤 Driver Management")
    st.write("Driver management coming soon...")

elif menu == "Car Management":
    st.title("🚗 Car Management")
    st.write("Car management coming soon...")

elif menu == "Delete Driver":
    st.title("🗑️ Delete Driver")
    st.write("Driver deletion coming soon...")

elif menu == "Reports":
    st.title("📈 Reports")
    st.write("Reports coming soon...")

elif menu == "Settings":
    st.title("⚙️ Settings")
    st.write("Settings coming soon...")

# ============ RESET DATABASE (BOTTOM) ============
st.sidebar.divider()
if st.sidebar.button("🔄 Reset Database", type="secondary"):
    if st.sidebar.checkbox("I understand this will delete all data"):
        try:
            os.remove('taxi_manager.db')
            st.sidebar.success("Database reset successfully!")
            st.rerun()
        except:
            st.sidebar.error("Error resetting database")
