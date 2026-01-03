# app.py - COMPLETELY FIXED Taxi Manager
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
    
    # Create trips table
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
    # SIMPLE QUERY that works with any schema
    return execute_query("SELECT * FROM letters ORDER BY id DESC", fetch=True)

def get_letters_with_names():
    # Try to get letters with driver names, but fall back if join fails
    try:
        return execute_query("""
            SELECT letters.*, drivers.name 
            FROM letters 
            LEFT JOIN drivers ON letters.driver_id = drivers.id 
            ORDER BY letters.id DESC
        """, fetch=True)
    except:
        # Fallback to simple query
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
        # Get data for metrics
        drivers = get_drivers()
        cars = get_cars()
        letters = get_letters()  # Use simple query
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
        
        # Recent Drivers
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

# [REST OF THE CODE - Data Entry, Balance, Driver Management, etc.]
# The rest of the code remains the same as before...
# Continue with the rest of your menu options...

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
            letters = get_letters()  # Use simple query
            if letters:
                # Try to get driver names
                try:
                    letters_with_names = get_letters_with_names()
                    if len(letters_with_names[0]) > 5:  # Has driver name column
                        letters_df = pd.DataFrame(letters_with_names, columns=['ID', 'Driver ID', 'Type', 'Date', 'Content', 'Created', 'Driver Name'])
                        st.dataframe(letters_df[['Driver Name', 'Type', 'Date', 'Created']])
                    else:
                        letters_df = pd.DataFrame(letters, columns=['ID', 'Driver ID', 'Type', 'Date', 'Content', 'Created'])
                        st.dataframe(letters_df[['Type', 'Date', 'Created']])
                except:
                    letters_df = pd.DataFrame(letters, columns=['ID', 'Driver ID', 'Type', 'Date', 'Content', 'Created'])
                    st.dataframe(letters_df[['Type', 'Date', 'Created']])
                
                # View specific letter
                if st.checkbox("View Letter Details"):
                    if letters:
                        letter_options = [f"{l[0]} - {l[2]}" for l in letters]
                        letter_id = st.selectbox("Select Letter", letter_options)
                        if letter_id:
                            selected_id = int(letter_id.split(" - ")[0])
                            selected = [l for l in letters if l[0] == selected_id][0]
                            st.text_area("Letter Content", value=selected[4], height=300, disabled=True)
    else:
        st.info("No drivers found. Add drivers first.")

# [Add the rest of the menu options here...]
# Driver Management, Car Management, Delete Driver, Reports, Settings, Balance

# For now, let me add a simple version of the other menus:

elif menu == "Driver Management":
    st.title("👨‍✈️ Driver Management")
    drivers = get_drivers()
    if drivers:
        drivers_df = pd.DataFrame(drivers, columns=['ID', 'Name', 'License', 'Phone', 'Email', 'Address', 'Status', 'Join Date'])
        st.dataframe(drivers_df)
    else:
        st.info("No drivers found")

elif menu == "Car Management":
    st.title("🚗 Car Management")
    cars = get_cars()
    if cars:
        cars_df = pd.DataFrame(cars, columns=['ID', 'Model', 'Make', 'CPNC#', 'Plate', 'Year', 'Color', 'Status', 'Driver ID', 'Purchase Date'])
        st.dataframe(cars_df)
    else:
        st.info("No cars found")

elif menu == "Delete Driver":
    st.title("🗑️ Delete Driver")
    drivers = get_drivers()
    if drivers:
        driver_options = {f"{d[1]} (License: {d[2]})": d[0] for d in drivers}
        driver_to_delete = st.selectbox("Select Driver to Delete", list(driver_options.keys()))
        if st.button("Delete Driver", type="secondary"):
            driver_id = driver_options[driver_to_delete]
            if delete_driver(driver_id):
                st.success("Driver deleted successfully!")
                st.rerun()
    else:
        st.info("No drivers found")

elif menu == "Balance":
    st.title("💰 Balance")
    st.info("Balance feature coming soon!")

elif menu == "Reports":
    st.title("📊 Reports")
    st.info("Reports feature coming soon!")

elif menu == "Settings":
    st.title("⚙️ Settings")
    st.info("Settings feature coming soon!")

# Footer
st.sidebar.markdown("---")
st.sidebar.info("**Taxi Manager**\n\nClick 'Reset Database' if you see any errors.")
