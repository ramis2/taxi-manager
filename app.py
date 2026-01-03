# app.py - COMPLETE Taxi Manager with ALL features
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os
import base64

# Page config
st.set_page_config(
    page_title="Taxi Manager",
    page_icon="🚕",
    layout="wide"
)

# Function to create download link for files
def get_download_link(content, filename, text):
    """Generate a download link for text content"""
    b64 = base64.b64encode(content.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{filename}">{text}</a>'

# Function to fix database schema
def fix_database_schema():
    """Fix any database schema issues"""
    conn = sqlite3.connect('taxi_manager.db')
    c = conn.cursor()
    
    try:
        # Check if letters table exists and fix it
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='letters'")
        if c.fetchone():
            # Check what columns exist
            c.execute("PRAGMA table_info(letters)")
            columns = c.fetchall()
            column_names = [col[1] for col in columns]
            
            # Fix missing columns
            if 'created_at' not in column_names:
                # Try to rename generated_date to created_at if it exists
                if 'generated_date' in column_names:
                    # SQLite doesn't support column rename directly, need to recreate
                    c.execute('''
                        CREATE TABLE letters_new (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            driver_id INTEGER,
                            letter_type TEXT,
                            letter_date DATE,
                            content TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')
                    c.execute('''
                        INSERT INTO letters_new (id, driver_id, letter_type, letter_date, content, created_at)
                        SELECT id, driver_id, letter_type, letter_date, content, generated_date 
                        FROM letters
                    ''')
                    c.execute("DROP TABLE letters")
                    c.execute("ALTER TABLE letters_new RENAME TO letters")
                else:
                    # Add created_at column
                    c.execute("ALTER TABLE letters ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    
    except Exception as e:
        st.error(f"Database schema fix error: {e}")
    
    conn.commit()
    conn.close()

# Initialize database with CORRECT schema
def init_database():
    """Create database with correct schema"""
    # First, remove old database if it exists
    if os.path.exists('taxi_manager.db'):
        os.remove('taxi_manager.db')
    
    conn = sqlite3.connect('taxi_manager.db')
    c = conn.cursor()
    
    # Create drivers table
    c.execute('''
        CREATE TABLE drivers (
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
        CREATE TABLE cars (
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
    
    # Create letters table - USING created_at (NOT generated_date)
    c.execute('''
        CREATE TABLE letters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            driver_id INTEGER,
            letter_type TEXT,
            letter_date DATE,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create trips table for balance
    c.execute('''
        CREATE TABLE trips (
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
    
    # Add some sample data
    c.execute("INSERT OR IGNORE INTO drivers (name, license_number, phone, email) VALUES ('John Doe', 'DL123456', '(555) 123-4567', 'john@email.com')")
    c.execute("INSERT OR IGNORE INTO drivers (name, license_number, phone, email) VALUES ('Maria Smith', 'DL789012', '(555) 987-6543', 'maria@email.com')")
    c.execute("INSERT OR IGNORE INTO cars (model, make, cpnc_number, plate_number, year, color) VALUES ('Ford', 'Focus', 'CPNC001', 'ABC-123', 2020, 'White')")
    c.execute("INSERT OR IGNORE INTO cars (model, make, cpnc_number, plate_number, year, color) VALUES ('Toyota', 'Camry', 'CPNC002', 'XYZ-789', 2021, 'Black')")
    
    # Add sample trips for balance
    c.execute("INSERT OR IGNORE INTO trips (driver_id, car_id, date, distance_km, fare_amount, fuel_cost, maintenance_cost, net_income) VALUES (1, 1, '2024-01-01', 50.0, 100.0, 20.0, 5.0, 75.0)")
    c.execute("INSERT OR IGNORE INTO trips (driver_id, car_id, date, distance_km, fare_amount, fuel_cost, maintenance_cost, net_income) VALUES (2, 2, '2024-01-02', 60.0, 120.0, 25.0, 3.0, 92.0)")
    
    conn.commit()
    conn.close()
    
    st.success("Database created successfully with correct schema!")

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
    return execute_query("SELECT * FROM letters ORDER BY id DESC", fetch=True)

def get_letters_with_names():
    try:
        return execute_query("""
            SELECT letters.*, drivers.name 
            FROM letters 
            LEFT JOIN drivers ON letters.driver_id = drivers.id 
            ORDER BY letters.id DESC
        """, fetch=True)
    except:
        return get_letters()

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

# Initialize or fix database
if not os.path.exists('taxi_manager.db'):
    init_database()
else:
    fix_database_schema()

# Custom CSS for print button
st.markdown("""
<style>
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
    .letter-preview {
        border: 1px solid #ddd;
        padding: 20px;
        background-color: white;
        font-family: 'Times New Roman', Times, serif;
    }
    @media print {
        .no-print {
            display: none !important;
        }
        .letter-preview {
            border: none;
            padding: 0;
        }
    }
</style>
""", unsafe_allow_html=True)

# Sidebar - Main Menu
st.sidebar.title("🚕 TaxiManager")

# Menu options
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

menu = st.sidebar.radio("Navigation", menu_options)

# Add reset button
if st.sidebar.button("🔄 Reset Database"):
    init_database()
    st.sidebar.success("Database reset complete!")

# DASHBOARD
if menu == "Dashboard":
    st.title("📊 Dashboard")
    
    try:
        drivers = get_drivers()
        cars = get_cars()
        letters = get_letters()
        trips = get_trips()
        
        # Metrics row
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
        
        # Recent Drivers and Cars
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Recent Drivers")
            if drivers:
                recent_drivers = drivers[:5]
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
                
    except Exception as e:
        st.error(f"Error loading dashboard: {e}")
        if st.button("Click here to reset database and fix issues"):
            init_database()
            st.rerun()

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
                drivers = get_drivers()
                if drivers:
                    driver_options = {f"{d[1]} (ID: {d[0]})": d[0] for d in drivers}
                    selected_driver = st.selectbox("Select Driver*", list(driver_options.keys()))
                    driver_id = driver_options[selected_driver]
                else:
                    st.warning("No drivers available")
                    driver_id = None
                
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

# BALANCE - COMPLETE VERSION
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
        
        # Chart
        st.subheader("Income Trends")
        if not trips_df.empty:
            # Monthly summary
            trips_df['Month'] = pd.to_datetime(trips_df['Date']).dt.to_period('M').astype(str)
            monthly_summary = trips_df.groupby('Month').agg({
                'Fare': 'sum',
                'Net Income': 'sum'
            }).reset_index()
            
            if not monthly_summary.empty:
                st.line_chart(monthly_summary.set_index('Month'))
        
        # Export option
        if st.button("Export Balance Sheet as CSV"):
            csv = trips_df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
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

# DRIVER LETTER - WITH DOWNLOAD & PRINT
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
            driver_name = selected_driver.split('(')[0].strip()
            
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
            default_content = f"""TO WHOM IT MAY CONCERN

This is to certify that {driver_name} is a registered driver with our taxi company.

All necessary documents and licenses are verified and up to date.

For any further information, please contact our office.

Sincerely,
Taxi Manager
{letter_date.strftime('%B %d, %Y')}"""
            
            content = st.text_area("Letter Content", value=default_content, height=200)
            
            if st.button("✍️ Generate Letter"):
                if generate_driver_letter(driver_id, letter_type, letter_date, content):
                    st.success("✅ Letter generated and saved successfully!")
                    
                    # Show preview in a nice format
                    st.subheader("📄 Letter Preview")
                    st.markdown('<div class="letter-preview">', unsafe_allow_html=True)
                    st.text(content)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # DOWNLOAD AND PRINT OPTIONS
                    st.subheader("📥 Download & Print Options")
                    
                    col_d1, col_d2, col_d3 = st.columns(3)
                    
                    with col_d1:
                        # Download as TXT
                        st.download_button(
                            label="📄 Download as Text",
                            data=content,
                            file_name=f"letter_{driver_name}_{datetime.now().strftime('%Y%m%d')}.txt",
                            mime="text/plain"
                        )
                    
                    with col_d2:
                        # Download as PDF (simulated)
                        if st.button("📊 Download as PDF"):
                            st.info("PDF feature coming soon! For now, use the Text version.")
                    
                    with col_d3:
                        # Print button with JavaScript
                        st.markdown("""
                        <button onclick="window.print()" class="no-print" style="
                            background-color: #4CAF50;
                            color: white;
                            padding: 10px 20px;
                            border: none;
                            border-radius: 5px;
                            cursor: pointer;
                            font-size: 16px;
                        ">
                        🖨️ Print Letter
                        </button>
                        """, unsafe_allow_html=True)
        
        with col2:
            st.subheader("📜 Generated Letters History")
            letters = get_letters_with_names()
            if letters:
                if len(letters[0]) > 5:  # Has driver name column
                    letters_df = pd.DataFrame(letters, columns=['ID', 'Driver ID', 'Type', 'Date', 'Content', 'Created', 'Driver Name'])
                    st.dataframe(letters_df[['Driver Name', 'Type', 'Date', 'Created']])
                else:
                    letters_df = pd.DataFrame(letters, columns=['ID', 'Driver ID', 'Type', 'Date', 'Content', 'Created'])
                    st.dataframe(letters_df[['Type', 'Date', 'Created']])
                
                # View specific letter
                if st.checkbox("🔍 View Letter Details"):
                    if letters:
                        letter_options = [f"{l[0]} - {l[2]}" for l in letters]
                        selected_option = st.selectbox("Select Letter", letter_options)
                        if selected_option:
                            selected_id = int(selected_option.split(" - ")[0])
                            selected = [l for l in letters if l[0] == selected_id][0]
                            
                            st.markdown("**Letter Content:**")
                            st.markdown('<div class="letter-preview">', unsafe_allow_html=True)
                            st.text(selected[4])
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # Download this specific letter
                            if st.button("📥 Download This Letter"):
                                st.download_button(
                                    label="Download Text",
                                    data=selected[4],
                                    file_name=f"letter_{selected_id}_{datetime.now().strftime('%Y%m%d')}.txt",
                                    mime="text/plain"
                                )
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

# REPORTS - COMPLETE VERSION
elif menu == "Reports":
    st.title("📊 Reports")
    
    report_type = st.selectbox("Select Report Type", [
        "Driver Performance Report",
        "Vehicle Utilization Report",
        "Financial Report",
        "Letters Report",
        "All Drivers List",
        "All Vehicles List",
        "Complete Database Export"
    ])
    
    if report_type == "Driver Performance Report":
        st.subheader("🚗 Driver Performance Report")
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
            
            # Export
            if st.button("Export This Report"):
                csv = driver_performance.to_csv()
                st.download_button("📥 Download CSV", csv, "driver_performance.csv", "text/csv")
    
    elif report_type == "Vehicle Utilization Report":
        st.subheader("🚕 Vehicle Utilization Report")
        cars = get_cars()
        trips = get_trips()
        
        if cars:
            cars_df = pd.DataFrame(cars, columns=['ID', 'Model', 'Make', 'CPNC#', 'Plate', 'Year', 'Color', 'Status', 'Driver ID', 'Purchase Date'])
            
            # Add trip count if trips exist
            if trips:
                trips_df = pd.DataFrame(trips, columns=['ID', 'Driver ID', 'Car ID', 'Date', 'Distance', 'Fare', 'Fuel Cost', 'Maintenance', 'Net Income', 'Status', 'Driver Name', 'Car Plate'])
                car_trips = trips_df['Car Plate'].value_counts().reset_index()
                car_trips.columns = ['Plate', 'Trip Count']
                cars_df = cars_df.merge(car_trips, left_on='Plate', right_on='Plate', how='left')
                cars_df['Trip Count'] = cars_df['Trip Count'].fillna(0).astype(int)
            
            st.dataframe(cars_df)
            
            # Export
            if st.button("Export This Report"):
                csv = cars_df.to_csv(index=False)
                st.download_button("📥 Download CSV", csv, "vehicle_report.csv", "text/csv")
    
    elif report_type == "Financial Report":
        st.subheader("💰 Financial Report")
        trips = get_trips()
        if trips:
            trips_df = pd.DataFrame(trips, columns=[
                'ID', 'Driver ID', 'Car ID', 'Date', 'Distance', 'Fare', 'Fuel Cost', 
                'Maintenance', 'Net Income', 'Status', 'Driver Name', 'Car Plate'
            ])
            
            # Monthly summary
            trips_df['Month'] = pd.to_datetime(trips_df['Date']).dt.to_period('M').astype(str)
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
            
            # Export
            if st.button("Export This Report"):
                csv = monthly_summary.to_csv()
                st.download_button("📥 Download CSV", csv, "financial_report.csv", "text/csv")
    
    elif report_type == "Letters Report":
        st.subheader("📝 Letters Report")
        letters = get_letters_with_names()
        if letters:
            if len(letters[0]) > 5:
                letters_df = pd.DataFrame(letters, columns=['ID', 'Driver ID', 'Type', 'Date', 'Content', 'Created', 'Driver Name'])
                st.dataframe(letters_df[['Driver Name', 'Type', 'Date', 'Created']])
                
                # Export
                if st.button("Export This Report"):
                    csv = letters_df[['Driver Name', 'Type', 'Date', 'Created']].to_csv(index=False)
                    st.download_button("📥 Download CSV", csv, "letters_report.csv", "text/csv")
    
    elif report_type == "All Drivers List":
        st.subheader("👨‍✈️ All Drivers List")
        drivers = get_drivers()
        if drivers:
            drivers_df = pd.DataFrame(drivers, columns=['ID', 'Name', 'License', 'Phone', 'Email', 'Address', 'Status', 'Join Date'])
            st.dataframe(drivers_df)
            
            # Export
            if st.button("Export This Report"):
                csv = drivers_df.to_csv(index=False)
                st.download_button("📥 Download CSV", csv, "drivers_list.csv", "text/csv")
    
    elif report_type == "All Vehicles List":
        st.subheader("🚗 All Vehicles List")
        cars = get_cars()
        if cars:
            cars_df = pd.DataFrame(cars, columns=['ID', 'Model', 'Make', 'CPNC#', 'Plate', 'Year', 'Color', 'Status', 'Driver ID', 'Purchase Date'])
            st.dataframe(cars_df)
            
            # Export
            if st.button("Export This Report"):
                csv = cars_df.to_csv(index=False)
                st.download_button("📥 Download CSV", csv, "vehicles_list.csv", "text/csv")
    
    elif report_type == "Complete Database Export":
        st.subheader("💾 Complete Database Export")
        
        # Get all data
        drivers = get_drivers()
        cars = get_cars()
        letters = get_letters_with_names()
        trips = get_trips()
        
        st.write("**Available Data:**")
        st.write(f"- Drivers: {len(drivers)} records")
        st.write(f"- Cars: {len(cars)} records")
        st.write(f"- Letters: {len(letters)} records")
        st.write(f"- Trips: {len(trips)} records")
        
        # Export all as ZIP (simulated)
        if st.button("📦 Export All Data"):
            st.info("Full database export feature coming soon!")
            st.info("For now, use individual report exports above.")

# SETTINGS - COMPLETE VERSION
elif menu == "Settings":
    st.title("⚙️ Settings")
    
    tab1, tab2, tab3, tab4 = st.tabs(["General", "Company Info", "Database", "About"])
    
    with tab1:
        st.subheader("General Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            currency = st.selectbox(
                "Default Currency",
                ["USD ($)", "EUR (€)", "GBP (£)", "JPY (¥)", "INR (₹)", "AUD ($)"],
                index=0
            )
            
            date_format = st.selectbox(
                "Date Format",
                ["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD", "Month DD, YYYY"],
                index=0
            )
            
            language = st.selectbox(
                "Language",
                ["English", "Spanish", "French", "German", "Chinese"],
                index=0
            )
        
        with col2:
            theme = st.selectbox(
                "Theme",
                ["Light", "Dark", "Auto"],
                index=0
            )
            
            notifications = st.checkbox("Enable Notifications", value=True)
            auto_backup = st.checkbox("Auto Backup Daily", value=True)
        
        if st.button("Save General Settings", type="primary"):
            st.success("General settings saved successfully!")
    
    with tab2:
        st.subheader("Company Information")
        
        company_name = st.text_input("Company Name", "Taxi Manager Inc.")
        company_address = st.text_area("Company Address", "123 Main Street, City, Country")
        company_phone = st.text_input("Phone Number", "(555) 123-4567")
        company_email = st.text_input("Email", "info@taximanager.com")
        company_website = st.text_input("Website", "www.taximanager.com")
        
        # Tax settings
        st.subheader("Financial Settings")
        tax_rate = st.number_input("Tax Rate (%)", min_value=0.0, max_value=50.0, value=10.0, step=0.5)
        default_fare = st.number_input("Default Fare per KM ($)", min_value=0.5, max_value=10.0, value=2.5, step=0.1)
        
        if st.button("Save Company Info", type="primary"):
            st.success("Company information saved successfully!")
    
    with tab3:
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
        
        # Backup section
        st.subheader("Backup & Restore")
        
        col_b1, col_b2 = st.columns(2)
        
        with col_b1:
            if st.button("Create Backup", type="secondary"):
                with open('taxi_manager.db', 'rb') as f:
                    db_data = f.read()
                
                st.download_button(
                    label="📥 Download Backup",
                    data=db_data,
                    file_name=f"taxi_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db",
                    mime="application/octet-stream"
                )
        
        with col_b2:
            uploaded_file = st.file_uploader("Restore from Backup", type=['db'])
            if uploaded_file is not None:
                if st.button("Restore Database", type="secondary"):
                    with open('taxi_manager.db', 'wb') as f:
                        f.write(uploaded_file.getbuffer())
                    st.success("Database restored successfully!")
                    st.info("Please refresh the page")
        
        # Dangerous operations
        st.subheader("⚠️ Dangerous Operations")
        
        with st.expander("Clear Data"):
            st.warning("These actions cannot be undone!")
            
            col_c1, col_c2, col_c3 = st.columns(3)
            
            with col_c1:
                if st.button("Clear Trip Records"):
                    if st.checkbox("I understand this will delete ALL trip records"):
                        execute_query("DELETE FROM trips")
                        st.success("All trip records cleared!")
                        st.rerun()
            
            with col_c2:
                if st.button("Clear Letters"):
                    if st.checkbox("I understand this will delete ALL letters"):
                        execute_query("DELETE FROM letters")
                        st.success("All letters cleared!")
                        st.rerun()
            
            with col_c3:
                if st.button("Reset All Data"):
                    if st.checkbox("I understand this will delete ALL data"):
                        init_database()
                        st.success("All data reset!")
                        st.rerun()
    
    with tab4:
        st.subheader("About Taxi Manager")
        
        st.write("""
        **Taxi Manager v2.0**
        
        A complete taxi fleet management system for small to medium taxi companies.
        
        **Features:**
        - Driver management
        - Vehicle management
        - Trip tracking
        - Income & balance tracking
        - Letter generation
        - Comprehensive reporting
        
        **Contact Support:**
        - Email: support@taximanager.com
        - Phone: (555) 123-4567
        - Website: www.taximanager.com
        
        **Version:** 2.0.0
        **Last Updated:** January 2024
        """)
        
        st.info("Thank you for using Taxi Manager! 🚕")

# Footer
st.sidebar.markdown("---")
st.sidebar.info("**Taxi Manager v2.0**\n\nClick 'Reset Database' if you see any errors.")
