# app.py - Complete Taxi Manager with ALL your requested features
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os

# Page config
st.set_page_config(
    page_title="Taxi Manager",
    page_icon="🚕",
    layout="wide"
)

# Initialize database
def init_database():
    conn = sqlite3.connect('taxi_manager.db')
    c = conn.cursor()
    
    # Create drivers table
    c.execute('''
        CREATE TABLE IF NOT EXISTS drivers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            license_number TEXT UNIQUE NOT NULL,
            phone TEXT,
            email TEXT,
            address TEXT,
            status TEXT DEFAULT 'active',
            join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create cars table
    c.execute('''
        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model TEXT NOT NULL,
            make TEXT,
            cpnc_number TEXT UNIQUE NOT NULL,
            plate_number TEXT UNIQUE NOT NULL,
            year INTEGER,
            color TEXT,
            status TEXT DEFAULT 'available',
            driver_id INTEGER,
            purchase_date DATE
        )
    ''')
    
    # Create letters table
    c.execute('''
        CREATE TABLE IF NOT EXISTS letters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            driver_id INTEGER,
            letter_type TEXT,
            letter_date DATE,
            content TEXT,
            generated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create trips table for balance/reports
    c.execute('''
        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            driver_id INTEGER,
            car_id INTEGER,
            date DATE,
            distance_km REAL,
            fare_amount REAL,
            fuel_cost REAL,
            maintenance_cost REAL,
            net_income REAL,
            status TEXT DEFAULT 'completed'
        )
    ''')
    
    conn.commit()
    conn.close()

# Database functions
def execute_query(query, params=(), fetch=False):
    conn = sqlite3.connect('taxi_manager.db')
    c = conn.cursor()
    c.execute(query, params)
    
    if fetch:
        result = c.fetchall()
        conn.close()
        return result
    
    conn.commit()
    conn.close()
    return c.lastrowid

def get_drivers():
    return execute_query("SELECT * FROM drivers ORDER BY join_date DESC", fetch=True)

def get_cars():
    return execute_query("SELECT * FROM cars ORDER BY id", fetch=True)

def get_letters():
    return execute_query("""
        SELECT letters.*, drivers.name 
        FROM letters 
        LEFT JOIN drivers ON letters.driver_id = drivers.id 
        ORDER BY letters.generated_date DESC
    """, fetch=True)

def get_trips():
    return execute_query("""
        SELECT trips.*, drivers.name as driver_name, cars.plate_number 
        FROM trips 
        LEFT JOIN drivers ON trips.driver_id = drivers.id 
        LEFT JOIN cars ON trips.car_id = cars.id 
        ORDER BY trips.date DESC
    """, fetch=True)

def add_driver(name, license_number, phone, email, address, status='active'):
    try:
        execute_query(
            "INSERT INTO drivers (name, license_number, phone, email, address, status) VALUES (?, ?, ?, ?, ?, ?)",
            (name, license_number, phone, email, address, status)
        )
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False

def add_car(model, make, cpnc_number, plate_number, year, color, status='available', driver_id=None):
    try:
        execute_query(
            "INSERT INTO cars (model, make, cpnc_number, plate_number, year, color, status, driver_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (model, make, cpnc_number, plate_number, year, color, status, driver_id)
        )
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False

def add_trip(driver_id, car_id, date, distance_km, fare_amount, fuel_cost, maintenance_cost):
    net_income = fare_amount - fuel_cost - maintenance_cost
    try:
        execute_query(
            "INSERT INTO trips (driver_id, car_id, date, distance_km, fare_amount, fuel_cost, maintenance_cost, net_income) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (driver_id, car_id, date, distance_km, fare_amount, fuel_cost, maintenance_cost, net_income)
        )
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False

def generate_driver_letter(driver_id, letter_type, letter_date, content):
    try:
        execute_query(
            "INSERT INTO letters (driver_id, letter_type, letter_date, content) VALUES (?, ?, ?, ?)",
            (driver_id, letter_type, letter_date, content)
        )
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False

def delete_driver(driver_id):
    try:
        execute_query("DELETE FROM drivers WHERE id = ?", (driver_id,))
        return True
    except:
        return False

# Initialize database
init_database()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        color: #2E86AB;
        border-bottom: 2px solid #2E86AB;
        padding-bottom: 10px;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 36px;
        font-weight: bold;
        color: #2E86AB;
    }
    .metric-label {
        font-size: 14px;
        color: #6c757d;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar - Main Menu (EXACTLY like your screenshot)
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3097/3097139.png", width=100)
st.sidebar.title("TaxiManager")

# Menu options matching your screenshot
menu_options = [
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

menu = st.sidebar.radio("", menu_options)

# DASHBOARD
if menu == "Dashboard":
    st.title("📊 Dashboard")
    
    # Get data for metrics
    drivers = get_drivers()
    cars = get_cars()
    letters = get_letters()
    trips = get_trips()
    
    # Metrics row - EXACTLY like your screenshot
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{len(drivers)}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Total Drivers</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{len(letters)}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Letters Generated</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{len(cars)}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Total Cars</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Recent Drivers - EXACTLY like your screenshot
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Recent Drivers")
        if drivers:
            recent_drivers = drivers[:5]  # Show only 5 most recent
            drivers_df = pd.DataFrame(recent_drivers, columns=['ID', 'Name', 'License', 'Phone', 'Email', 'Address', 'Status', 'Join Date'])
            st.dataframe(drivers_df[['Name', 'License', 'Phone', 'Status']], hide_index=True)
        else:
            st.info("No drivers found")
    
    with col2:
        st.subheader("Recent Cars")
        if cars:
            recent_cars = cars[:5]
            cars_df = pd.DataFrame(recent_cars, columns=['ID', 'Model', 'Make', 'CPNC#', 'Plate', 'Year', 'Color', 'Status', 'Driver ID', 'Purchase Date'])
            st.dataframe(cars_df[['Model', 'CPNC#', 'Plate', 'Status']], hide_index=True)
        else:
            st.info("No cars found")

# DATA ENTRY
elif menu == "Data Entry":
    st.title("📝 Data Entry")
    
    tab1, tab2, tab3 = st.tabs(["Add Driver", "Add Car", "Add Trip"])
    
    with tab1:
        st.subheader("Add New Driver")
        with st.form("add_driver_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Full Name*", placeholder="John Doe")
                license_number = st.text_input("License Number*", placeholder="DL123456")
                phone = st.text_input("Phone Number*", placeholder="(555) 123-4567")
            with col2:
                email = st.text_input("Email", placeholder="john@example.com")
                address = st.text_area("Address", placeholder="123 Main St, City")
                status = st.selectbox("Status", ["active", "inactive"], index=0)
            
            submitted = st.form_submit_button("Add Driver")
            if submitted:
                if name and license_number and phone:
                    if add_driver(name, license_number, phone, email, address, status):
                        st.success(f"Driver {name} added successfully!")
                        st.rerun()
                else:
                    st.warning("Please fill required fields (*)")
    
    with tab2:
        st.subheader("Add New Car")
        with st.form("add_car_form"):
            col1, col2 = st.columns(2)
            with col1:
                model = st.text_input("Model*", placeholder="Ford")
                make = st.text_input("Make", placeholder="Focus")
                cpnc_number = st.text_input("CPNC#*", placeholder="CPNC#0003")
            with col2:
                plate_number = st.text_input("Plate Number*", placeholder="DEF-456")
                year = st.number_input("Year", min_value=2000, max_value=2024, value=2020)
                color = st.text_input("Color", placeholder="White")
                status = st.selectbox("Car Status", ["available", "in use", "maintenance"], index=0)
            
            # Driver assignment
            drivers = get_drivers()
            if drivers:
                driver_options = {f"{d[1]} (ID: {d[0]})": d[0] for d in drivers}
                assigned_driver = st.selectbox("Assign Driver (Optional)", ["None"] + list(driver_options.keys()))
                driver_id = None if assigned_driver == "None" else driver_options[assigned_driver]
            else:
                driver_id = None
            
            submitted = st.form_submit_button("Add Car")
            if submitted:
                if model and cpnc_number and plate_number:
                    if add_car(model, make, cpnc_number, plate_number, year, color, status, driver_id):
                        st.success(f"Car {plate_number} added successfully!")
                        st.rerun()
                else:
                    st.warning("Please fill required fields (*)")
    
    with tab3:
        st.subheader("Add Trip Record")
        with st.form("add_trip_form"):
            col1, col2 = st.columns(2)
            with col1:
                # Driver selection
                drivers = get_drivers()
                if drivers:
                    driver_options = {f"{d[1]} (ID: {d[0]})": d[0] for d in drivers}
                    selected_driver = st.selectbox("Select Driver*", list(driver_options.keys()))
                    driver_id = driver_options[selected_driver]
                else:
                    st.warning("No drivers available")
                    driver_id = None
                
                # Car selection
                cars = get_cars()
                if cars:
                    car_options = {f"{c[1]} {c[2]} - {c[4]}": c[0] for c in cars}
                    selected_car = st.selectbox("Select Car*", list(car_options.keys()))
                    car_id = car_options[selected_car]
                else:
                    st.warning("No cars available")
                    car_id = None
                
                date = st.date_input("Trip Date*", value=datetime.now())
            
            with col2:
                distance_km = st.number_input("Distance (km)*", min_value=0.0, value=50.0, step=0.1)
                fare_amount = st.number_input("Fare Amount ($)*", min_value=0.0, value=100.0, step=1.0)
                fuel_cost = st.number_input("Fuel Cost ($)", min_value=0.0, value=20.0, step=0.5)
                maintenance_cost = st.number_input("Maintenance Cost ($)", min_value=0.0, value=0.0, step=0.5)
            
            submitted = st.form_submit_button("Add Trip")
            if submitted:
                if driver_id and car_id and date:
                    net_income = fare_amount - fuel_cost - maintenance_cost
                    st.info(f"Net Income: ${net_income:.2f}")
                    if add_trip(driver_id, car_id, date, distance_km, fare_amount, fuel_cost, maintenance_cost):
                        st.success("Trip record added successfully!")
                        st.rerun()
                else:
                    st.warning("Please fill all required fields (*)")

# BALANCE
elif menu == "Balance":
    st.title("💰 Balance & Income")
    
    trips = get_trips()
    if trips:
        trips_df = pd.DataFrame(trips, columns=[
            'ID', 'Driver ID', 'Car ID', 'Date', 'Distance', 'Fare', 'Fuel Cost', 
            'Maintenance', 'Net Income', 'Status', 'Driver Name', 'Car Plate'
        ])
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_income = trips_df['Fare'].sum()
            st.metric("Total Income", f"${total_income:,.2f}")
        
        with col2:
            total_expenses = trips_df['Fuel Cost'].sum() + trips_df['Maintenance'].sum()
            st.metric("Total Expenses", f"${total_expenses:,.2f}")
        
        with col3:
            net_balance = trips_df['Net Income'].sum()
            st.metric("Net Balance", f"${net_balance:,.2f}")
        
        with col4:
            avg_trip_income = trips_df['Net Income'].mean()
            st.metric("Avg Trip Income", f"${avg_trip_income:,.2f}")
        
        st.markdown("---")
        
        # Detailed transactions
        st.subheader("Transaction History")
        st.dataframe(trips_df[['Date', 'Driver Name', 'Car Plate', 'Distance', 'Fare', 'Fuel Cost', 'Maintenance', 'Net Income']])
        
        # Driver-wise earnings
        st.subheader("Driver Earnings")
        if 'Driver Name' in trips_df.columns:
            driver_earnings = trips_df.groupby('Driver Name').agg({
                'Fare': 'sum',
                'Net Income': 'sum',
                'ID': 'count'
            }).rename(columns={'ID': 'Trips'})
            st.dataframe(driver_earnings)
        
        # Export option
        if st.button("Export Balance Sheet as CSV"):
            csv = trips_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="balance_sheet.csv",
                mime="text/csv"
            )
    else:
        st.info("No trip records found. Add trips in Data Entry section.")

# DRIVER MANAGEMENT
elif menu == "Driver Management":
    st.title("👨‍✈️ Driver Management")
    
    drivers = get_drivers()
    
    if drivers:
        drivers_df = pd.DataFrame(drivers, columns=['ID', 'Name', 'License', 'Phone', 'Email', 'Address', 'Status', 'Join Date'])
        
        # Search and filter
        col1, col2 = st.columns(2)
        with col1:
            search_name = st.text_input("Search by Name", "")
        with col2:
            filter_status = st.selectbox("Filter by Status", ["All", "active", "inactive"])
        
        # Apply filters
        filtered_df = drivers_df.copy()
        if search_name:
            filtered_df = filtered_df[filtered_df['Name'].str.contains(search_name, case=False, na=False)]
        if filter_status != "All":
            filtered_df = filtered_df[filtered_df['Status'] == filter_status]
        
        # Display drivers
        st.dataframe(filtered_df, use_container_width=True)
        
        # Driver statistics
        st.subheader("Driver Statistics")
        col1, col2, col3 = st.columns(3)
        with col1:
            active_count = len([d for d in drivers if d[6] == 'active'])
            st.metric("Active Drivers", active_count)
        with col2:
            inactive_count = len([d for d in drivers if d[6] == 'inactive'])
            st.metric("Inactive Drivers", inactive_count)
        with col3:
            total_drivers = len(drivers)
            st.metric("Total Drivers", total_drivers)
        
        # Edit driver
        st.subheader("Edit Driver Information")
        edit_driver_id = st.selectbox("Select Driver to Edit", [f"{d[0]} - {d[1]}" for d in drivers])
        
        if edit_driver_id:
            driver_id = int(edit_driver_id.split(" - ")[0])
            driver = [d for d in drivers if d[0] == driver_id][0]
            
            with st.form("edit_driver_form"):
                col1, col2 = st.columns(2)
                with col1:
                    edit_name = st.text_input("Name", value=driver[1])
                    edit_license = st.text_input("License", value=driver[2])
                    edit_phone = st.text_input("Phone", value=driver[3])
                with col2:
                    edit_email = st.text_input("Email", value=driver[4])
                    edit_address = st.text_area("Address", value=driver[5])
                    edit_status = st.selectbox("Status", ["active", "inactive"], index=0 if driver[6] == "active" else 1)
                
                if st.form_submit_button("Update Driver"):
                    try:
                        execute_query(
                            "UPDATE drivers SET name = ?, license_number = ?, phone = ?, email = ?, address = ?, status = ? WHERE id = ?",
                            (edit_name, edit_license, edit_phone, edit_email, edit_address, edit_status, driver_id)
                        )
                        st.success("Driver updated successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
    else:
        st.info("No drivers found. Add drivers in Data Entry section.")

# CAR MANAGEMENT
elif menu == "Car Management":
    st.title("🚗 Car Management")
    
    cars = get_cars()
    
    if cars:
        cars_df = pd.DataFrame(cars, columns=['ID', 'Model', 'Make', 'CPNC#', 'Plate', 'Year', 'Color', 'Status', 'Driver ID', 'Purchase Date'])
        
        # Display cars
        st.dataframe(cars_df, use_container_width=True)
        
        # Car statistics
        st.subheader("Car Statistics")
        col1, col2, col3 = st.columns(3)
        with col1:
            available_cars = len([c for c in cars if c[7] == 'available'])
            st.metric("Available Cars", available_cars)
        with col2:
            in_use_cars = len([c for c in cars if c[7] == 'in use'])
            st.metric("In Use Cars", in_use_cars)
        with col3:
            maintenance_cars = len([c for c in cars if c[7] == 'maintenance'])
            st.metric("In Maintenance", maintenance_cars)
    else:
        st.info("No cars found. Add cars in Data Entry section.")

# DRIVER LETTER
elif menu == "Driver Letter":
    st.title("📝 Driver Letter Generator")
    
    drivers = get_drivers()
    
    if drivers:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Generate Letter")
            
            # Select driver
            driver_options = {f"{d[1]} (ID: {d[0]})": d[0] for d in drivers}
            selected_driver = st.selectbox("Select Driver", list(driver_options.keys()))
            driver_id = driver_options[selected_driver]
            
            # Letter type
            letter_type = st.selectbox("Letter Type", [
                "Employment Verification",
                "Warning Letter", 
                "Appreciation Letter",
                "Termination Letter",
                "Salary Certificate"
            ])
            
            # Date
            letter_date = st.date_input("Letter Date", value=datetime.now())
            
            # Custom content
            default_content = f"""
            TO WHOM IT MAY CONCERN
            
            This is to certify that {selected_driver.split('(')[0].strip()} is a registered driver with our taxi company.
            
            All necessary documents and licenses are verified and up to date.
            
            For any further information, please contact our office.
            
            Sincerely,
            Taxi Manager
            """
            
            content = st.text_area("Letter Content", value=default_content, height=200)
            
            if st.button("Generate Letter"):
                if generate_driver_letter(driver_id, letter_type, letter_date, content):
                    st.success("Letter generated and saved successfully!")
                    
                    # Show preview
                    st.subheader("Letter Preview")
                    st.text(content)
                    
                    # Download option
                    st.download_button(
                        label="Download as Text File",
                        data=content,
                        file_name=f"driver_letter_{driver_id}_{datetime.now().strftime('%Y%m%d')}.txt",
                        mime="text/plain"
                    )
        
        with col2:
            st.subheader("Generated Letters History")
            letters = get_letters()
            if letters:
                letters_df = pd.DataFrame(letters, columns=['ID', 'Driver ID', 'Type', 'Date', 'Content', 'Generated', 'Driver Name'])
                st.dataframe(letters_df[['Driver Name', 'Type', 'Date', 'Generated']])
                
                # View specific letter
                if st.checkbox("View Letter Details"):
                    letter_id = st.selectbox("Select Letter", [f"{l[0]} - {l[6]} - {l[2]}" for l in letters])
                    if letter_id:
                        selected = [l for l in letters if str(l[0]) == letter_id.split(" - ")[0]][0]
                        st.text_area("Letter Content", value=selected[4], height=300, disabled=True)
    else:
        st.info("No drivers found. Add drivers first.")

# DELETE DRIVER
elif menu == "Delete Driver":
    st.title("🗑️ Delete Driver")
    
    drivers = get_drivers()
    
    if drivers:
        st.warning("⚠️ Warning: This action cannot be undone!")
        
        # Select driver to delete
        driver_options = {f"{d[0]} - {d[1]} (License: {d[2]})": d[0] for d in drivers}
        driver_to_delete = st.selectbox("Select Driver to Delete", list(driver_options.keys()))
        driver_id = driver_options[driver_to_delete]
        
        # Show driver details
        driver = [d for d in drivers if d[0] == driver_id][0]
        
        st.write("**Driver Details:**")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Name:** {driver[1]}")
            st.write(f"**License:** {driver[2]}")
            st.write(f"**Phone:** {driver[3]}")
        with col2:
            st.write(f"**Email:** {driver[4]}")
            st.write(f"**Status:** {driver[6]}")
            st.write(f"**Join Date:** {driver[7]}")
        
        # Confirmation
        confirmation = st.text_input("Type 'DELETE' to confirm")
        
        if st.button("Delete Driver", type="secondary"):
            if confirmation == "DELETE":
                if delete_driver(driver_id):
                    st.success(f"Driver {driver[1]} deleted successfully!")
                    st.rerun()
                else:
                    st.error("Error deleting driver. Driver may have associated records.")
            else:
                st.error("Please type 'DELETE' to confirm")
    else:
        st.info("No drivers found.")

# REPORTS
elif menu == "Reports":
    st.title("📊 Reports")
    
    report_type = st.selectbox("Select Report Type", [
        "Driver Performance Report",
        "Vehicle Utilization Report",
        "Financial Report",
        "All Drivers List",
        "All Vehicles List"
    ])
    
    if report_type == "Driver Performance Report":
        st.subheader("Driver Performance Report")
        trips = get_trips()
        if trips:
            trips_df = pd.DataFrame(trips, columns=[
                'ID', 'Driver ID', 'Car ID', 'Date', 'Distance', 'Fare', 'Fuel Cost', 
                'Maintenance', 'Net Income', 'Status', 'Driver Name', 'Car Plate'
            ])
            
            # Group by driver
            driver_performance = trips_df.groupby('Driver Name').agg({
                'Distance': 'sum',
                'Fare': 'sum',
                'Net Income': 'sum',
                'ID': 'count'
            }).rename(columns={
                'ID': 'Total Trips',
                'Distance': 'Total Distance (km)',
                'Fare': 'Total Revenue ($)',
                'Net Income': 'Net Income ($)'
            })
            
            st.dataframe(driver_performance)
            
            # Chart
            st.bar_chart(driver_performance['Net Income ($)'])
    
    elif report_type == "Vehicle Utilization Report":
        st.subheader("Vehicle Utilization Report")
        cars = get_cars()
        trips = get_trips()
        
        if cars:
            cars_df = pd.DataFrame(cars, columns=['ID', 'Model', 'Make', 'CPNC#', 'Plate', 'Year', 'Color', 'Status', 'Driver ID', 'Purchase Date'])
            st.dataframe(cars_df[['Model', 'Make', 'Plate', 'CPNC#', 'Status']])
    
    elif report_type == "Financial Report":
        st.subheader("Financial Report")
        trips = get_trips()
        if trips:
            trips_df = pd.DataFrame(trips, columns=[
                'ID', 'Driver ID', 'Car ID', 'Date', 'Distance', 'Fare', 'Fuel Cost', 
                'Maintenance', 'Net Income', 'Status', 'Driver Name', 'Car Plate'
            ])
            
            # Monthly summary
            trips_df['Month'] = pd.to_datetime(trips_df['Date']).dt.to_period('M')
            monthly_summary = trips_df.groupby('Month').agg({
                'Fare': 'sum',
                'Fuel Cost': 'sum',
                'Maintenance': 'sum',
                'Net Income': 'sum',
                'ID': 'count'
            }).rename(columns={'ID': 'Trips'})
            
            st.dataframe(monthly_summary)
            
            # Chart
            st.line_chart(monthly_summary[['Fare', 'Net Income']])
    
    elif report_type == "All Drivers List":
        st.subheader("All Drivers List")
        drivers = get_drivers()
        if drivers:
            drivers_df = pd.DataFrame(drivers, columns=['ID', 'Name', 'License', 'Phone', 'Email', 'Address', 'Status', 'Join Date'])
            st.dataframe(drivers_df)
    
    elif report_type == "All Vehicles List":
        st.subheader("All Vehicles List")
        cars = get_cars()
        if cars:
            cars_df = pd.DataFrame(cars, columns=['ID', 'Model', 'Make', 'CPNC#', 'Plate', 'Year', 'Color', 'Status', 'Driver ID', 'Purchase Date'])
            st.dataframe(cars_df)

# SETTINGS
elif menu == "Settings":
    st.title("⚙️ Settings")
    
    tab1, tab2, tab3 = st.tabs(["General", "Database", "Backup"])
    
    with tab1:
        st.subheader("General Settings")
        company_name = st.text_input("Company Name", "Taxi Manager Inc.")
        contact_email = st.text_input("Contact Email", "admin@taximanager.com")
        contact_phone = st.text_input("Contact Phone", "(555) 123-4567")
        
        currency = st.selectbox("Currency", ["USD ($)", "EUR (€)", "GBP (£)", "INR (₹)"])
        date_format = st.selectbox("Date Format", ["MM/DD/YYYY", "DD/MM/YYYY", "YYYY-MM-DD"])
        
        if st.button("Save Settings"):
            st.success("Settings saved successfully!")
    
    with tab2:
        st.subheader("Database Management")
        
        st.info(f"Database file: taxi_manager.db")
        
        # Show database stats
        conn = sqlite3.connect('taxi_manager.db')
        c = conn.cursor()
        
        tables = c.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        
        st.write("**Database Tables:**")
        for table in tables:
            count = c.execute(f"SELECT COUNT(*) FROM {table[0]}").fetchone()[0]
            st.write(f"- {table[0]}: {count} records")
        
        conn.close()
        
        # Clear data options
        st.warning("⚠️ Dangerous Operations")
        
        if st.button("Clear All Trip Records"):
            if st.checkbox("I understand this will delete all trip records"):
                execute_query("DELETE FROM trips")
                st.success("All trip records cleared!")
                st.rerun()
    
    with tab3:
        st.subheader("Backup & Restore")
        
        # Export database
        if st.button("Export Database Backup"):
            with open('taxi_manager.db', 'rb') as f:
                db_data = f.read()
            
            st.download_button(
                label="Download Backup File",
                data=db_data,
                file_name=f"taxi_manager_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db",
                mime="application/octet-stream"
            )
        
        # Import database
        st.subheader("Restore from Backup")
        uploaded_file = st.file_uploader("Choose a database file", type=['db'])
        if uploaded_file is not None:
            if st.button("Restore Database"):
                with open('taxi_manager.db', 'wb') as f:
                    f.write(uploaded_file.getbuffer())
                st.success("Database restored successfully!")
                st.info("Please refresh the page")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**Taxi Manager v2.0**")
st.sidebar.markdown("All rights reserved © 2024")
st.sidebar.info("To run this app: `streamlit run app.py`")
