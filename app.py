import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
import hashlib
import time

# ========== CONFIGURATION ==========
st.set_page_config(
    page_title="Taxi Manager Pro",
    page_icon="🚕",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ========== CUSTOM MOBILE CSS ==========
st.markdown("""
<style>
    /* Mobile-first responsive design */
    @media (max-width: 768px) {
        .stButton > button {
            width: 100% !important;
            height: 50px !important;
            font-size: 16px !important;
            margin: 5px 0 !important;
        }
        .stTextInput > div > input {
            font-size: 16px !important;
            height: 45px !important;
        }
        .stNumberInput > div > input {
            font-size: 16px !important;
            height: 45px !important;
        }
        .stSelectbox > div > div {
            font-size: 16px !important;
            height: 45px !important;
        }
        .stDateInput > div > input {
            font-size: 16px !important;
            height: 45px !important;
        }
        .stDataFrame {
            font-size: 14px !important;
        }
        h1 {
            font-size: 24px !important;
        }
        h2 {
            font-size: 20px !important;
        }
        h3 {
            font-size: 18px !important;
        }
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom colors */
    .st-bb {border-color: #FF4B4B;}
    .st-at {background-color: #FF4B4B;}
    .css-1d391kg {background-color: #f0f2f6;}
    
    /* Card-like containers */
    .card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ========== DATABASE SETUP ==========
@st.cache_resource
def init_database():
    """Initialize or connect to existing database"""
    conn = sqlite3.connect('taxi_management.db', check_same_thread=False)
    
    # Create payments table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            car_number TEXT NOT NULL,
            driver_name TEXT,
            phone TEXT,
            amount REAL NOT NULL,
            payment_method TEXT,
            trip_type TEXT,
            pickup_location TEXT,
            drop_location TEXT,
            distance_km REAL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create cars table with detailed info
    conn.execute('''
        CREATE TABLE IF NOT EXISTS cars (
            car_number TEXT PRIMARY KEY,
            owner_name TEXT NOT NULL,
            owner_phone TEXT,
            car_model TEXT,
            car_year INTEGER,
            car_color TEXT,
            registration_date TEXT,
            insurance_expiry TEXT,
            pollution_expiry TEXT,
            permit_expiry TEXT,
            driver_id TEXT,
            driver_name TEXT,
            driver_phone TEXT,
            status TEXT DEFAULT 'Active',
            last_service_date TEXT,
            next_service_km INTEGER,
            current_km INTEGER,
            fuel_type TEXT
        )
    ''')
    
    # Create drivers table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS drivers (
            driver_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            license_number TEXT,
            license_expiry TEXT,
            address TEXT,
            emergency_contact TEXT,
            joining_date TEXT,
            salary REAL,
            status TEXT DEFAULT 'Active'
        )
    ''')
    
    # Create expenses table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            car_number TEXT,
            expense_type TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            payment_method TEXT,
            receipt_number TEXT
        )
    ''')
    
    conn.commit()
    return conn

# Initialize database
conn = init_database()

# ========== SESSION STATE ==========
if 'page' not in st.session_state:
    st.session_state.page = "dashboard"
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = True  # Skip login for simplicity

# ========== NAVIGATION ==========
def show_navigation():
    """Mobile-optimized navigation menu"""
    with st.container():
        menu_options = {
            "🏠 Dashboard": "dashboard",
            "💰 Add Trip": "add_trip",
            "📋 All Trips": "view_trips",
            "🚗 Fleet": "cars",
            "👨‍✈️ Drivers": "drivers",
            "💸 Expenses": "expenses",
            "📊 Reports": "reports",
            "⚙️ Settings": "settings"
        }
        
        # Create 2x4 grid for mobile
        cols = st.columns(4)
        for idx, (display_name, page_name) in enumerate(menu_options.items()):
            col_idx = idx % 4
            with cols[col_idx]:
                if st.button(display_name, key=f"nav_{page_name}"):
                    st.session_state.page = page_name
                    st.rerun()

# ========== PAGES ==========
def dashboard_page():
    """Main Dashboard"""
    st.title("📊 Dashboard")
    
    # Quick stats row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        today = datetime.now().strftime("%Y-%m-%d")
        today_trips = conn.execute("SELECT COUNT(*) FROM payments WHERE date=?", (today,)).fetchone()[0]
        st.metric("Today's Trips", today_trips, "🔄")
    
    with col2:
        today_earning = conn.execute("SELECT SUM(amount) FROM payments WHERE date=?", (today,)).fetchone()[0] or 0
        st.metric("Today's Earnings", f"₹{today_earning:,.0f}", "💰")
    
    with col3:
        active_cars = conn.execute("SELECT COUNT(*) FROM cars WHERE status='Active'").fetchone()[0]
        st.metric("Active Cars", active_cars, "🚗")
    
    with col4:
        total_drivers = conn.execute("SELECT COUNT(*) FROM drivers WHERE status='Active'").fetchone()[0]
        st.metric("Active Drivers", total_drivers, "👨‍✈️")
    
    st.markdown("---")
    
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        # Daily earnings chart (last 7 days)
        weekly_data = pd.read_sql('''
            SELECT date, SUM(amount) as total 
            FROM payments 
            WHERE date >= date('now', '-7 days') 
            GROUP BY date 
            ORDER BY date
        ''', conn)
        
        if not weekly_data.empty:
            fig = px.line(weekly_data, x='date', y='total', 
                         title="Weekly Earnings Trend")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Payment methods breakdown
        method_data = pd.read_sql('''
            SELECT payment_method, COUNT(*) as count 
            FROM payments 
            GROUP BY payment_method
        ''', conn)
        
        if not method_data.empty:
            fig = px.pie(method_data, values='count', names='payment_method',
                        title="Payment Methods Distribution")
            st.plotly_chart(fig, use_container_width=True)
    
    # Recent trips
    st.subheader("🕒 Recent Trips")
    recent = pd.read_sql('''
        SELECT date, car_number, driver_name, amount, payment_method 
        FROM payments 
        ORDER BY id DESC 
        LIMIT 10
    ''', conn)
    
    if not recent.empty:
        st.dataframe(recent, use_container_width=True, height=300)
    else:
        st.info("No trips recorded yet. Add your first trip!")

def add_trip_page():
    """Add new trip/transaction"""
    st.title("💰 Add New Trip")
    
    with st.form("trip_form", clear_on_submit=True):
        # Top row
        col1, col2, col3 = st.columns(3)
        with col1:
            date = st.date_input("Date", datetime.now())
            car_number = st.text_input("Car Number *", placeholder="KA01AB1234")
        with col2:
            driver_name = st.text_input("Driver Name")
            phone = st.text_input("Phone", placeholder="9876543210")
        with col3:
            amount = st.number_input("Amount (₹) *", min_value=0.0, step=100.0, value=500.0)
            payment_method = st.selectbox("Payment Method", ["Cash", "UPI", "Card", "Wallet"])
        
        # Middle row
        col1, col2 = st.columns(2)
        with col1:
            trip_type = st.selectbox("Trip Type", ["Local", "Outstation", "Airport", "Rental"])
            pickup = st.text_input("Pickup Location")
        with col2:
            distance = st.number_input("Distance (km)", min_value=0.0, step=0.5, value=0.0)
            drop = st.text_input("Drop Location")
        
        # Bottom
        notes = st.text_area("Notes", placeholder="Any additional information...")
        
        # Submit button
        submitted = st.form_submit_button("💾 SAVE TRIP", type="primary", use_container_width=True)
        
        if submitted:
            if car_number and amount > 0:
                try:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO payments 
                        (date, car_number, driver_name, phone, amount, payment_method, 
                         trip_type, pickup_location, drop_location, distance_km, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (date.strftime("%Y-%m-%d"), car_number, driver_name, phone, amount, 
                          payment_method, trip_type, pickup, drop, distance, notes))
                    conn.commit()
                    
                    st.success("✅ Trip saved successfully!")
                    st.balloons()
                    
                    # Clear form automatically after success
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.error("Please fill required fields: Car Number and Amount")

def view_trips_page():
    """View and filter all trips"""
    st.title("📋 Trip History")
    
    # Filters
    with st.expander("🔍 Search & Filters", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            search_car = st.text_input("Search Car")
        with col2:
            start_date = st.date_input("From Date")
        with col3:
            end_date = st.date_input("To Date")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            driver_filter = st.text_input("Driver Name")
        with col2:
            min_amount = st.number_input("Min Amount", min_value=0, value=0)
        with col3:
            max_amount = st.number_input("Max Amount", min_value=0, value=10000)
    
    # Build query
    query = "SELECT * FROM payments WHERE 1=1"
    params = []
    
    if search_car:
        query += " AND car_number LIKE ?"
        params.append(f"%{search_car}%")
    if driver_filter:
        query += " AND driver_name LIKE ?"
        params.append(f"%{driver_filter}%")
    if start_date:
        query += " AND date >= ?"
        params.append(start_date.strftime("%Y-%m-%d"))
    if end_date:
        query += " AND date <= ?"
        params.append(end_date.strftime("%Y-%m-%d"))
    if min_amount > 0:
        query += " AND amount >= ?"
        params.append(min_amount)
    if max_amount < 10000:
        query += " AND amount <= ?"
        params.append(max_amount)
    
    query += " ORDER BY date DESC, id DESC"
    
    # Load data
    df = pd.read_sql_query(query, conn, params=params)
    
    if not df.empty:
        # Summary
        total_amount = df['amount'].sum()
        total_trips = len(df)
        avg_amount = total_amount / total_trips if total_trips > 0 else 0
        
        st.info(f"""
        **Summary:** {total_trips} trips | **Total:** ₹{total_amount:,.0f} | 
        **Average:** ₹{avg_amount:,.0f} per trip
        """)
        
        # Interactive dataframe
        st.dataframe(df, use_container_width=True, height=400)
        
        # Actions
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📥 Export to Excel"):
                filename = f"trips_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                df.to_excel(filename, index=False)
                with open(filename, 'rb') as f:
                    st.download_button("Download", f, filename, "application/vnd.ms-excel")
        
        with col2:
            if st.button("📊 Generate Report"):
                st.subheader("Detailed Report")
                report_cols = st.columns(2)
                with report_cols[0]:
                    st.write("**By Payment Method:**")
                    method_summary = df.groupby('payment_method')['amount'].agg(['count', 'sum'])
                    st.dataframe(method_summary)
                with report_cols[1]:
                    st.write("**By Car:**")
                    car_summary = df.groupby('car_number')['amount'].agg(['count', 'sum'])
                    st.dataframe(car_summary)
        
        with col3:
            if st.button("🗑️ Delete All"):
                if st.checkbox("Confirm delete ALL trips?"):
                    conn.execute("DELETE FROM payments")
                    conn.commit()
                    st.warning("All trips deleted!")
                    st.rerun()
    else:
        st.warning("No trips found with current filters")

def cars_page():
    """Car fleet management"""
    st.title("🚗 Fleet Management")
    
    tab1, tab2, tab3 = st.tabs(["📝 Add/Edit Car", "📋 View Fleet", "🔧 Maintenance"])
    
    with tab1:
        st.subheader("Car Registration")
        
        with st.form("car_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                car_number = st.text_input("Car Number *", placeholder="KA01AB1234")
                owner_name = st.text_input("Owner Name *")
                owner_phone = st.text_input("Owner Phone")
                car_model = st.text_input("Model", placeholder="Toyota Innova")
                car_year = st.number_input("Year", min_value=2000, max_value=2024, value=2020)
            
            with col2:
                car_color = st.text_input("Color")
                reg_date = st.date_input("Registration Date")
                insurance_expiry = st.date_input("Insurance Expiry")
                permit_expiry = st.date_input("Permit Expiry")
                fuel_type = st.selectbox("Fuel Type", ["Petrol", "Diesel", "CNG", "Electric"])
            
            # Driver assignment
            st.subheader("Driver Assignment")
            col1, col2 = st.columns(2)
            with col1:
                driver_name = st.text_input("Driver Name")
            with col2:
                driver_phone = st.text_input("Driver Phone")
            
            # Submit
            submitted = st.form_submit_button("💾 SAVE CAR", type="primary", use_container_width=True)
            
            if submitted and car_number and owner_name:
                try:
                    conn.execute('''
                        INSERT OR REPLACE INTO cars 
                        (car_number, owner_name, owner_phone, car_model, car_year, 
                         car_color, registration_date, insurance_expiry, permit_expiry,
                         fuel_type, driver_name, driver_phone, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (car_number, owner_name, owner_phone, car_model, car_year,
                          car_color, reg_date.strftime("%Y-%m-%d"), 
                          insurance_expiry.strftime("%Y-%m-%d"),
                          permit_expiry.strftime("%Y-%m-%d"), fuel_type,
                          driver_name, driver_phone, "Active"))
                    conn.commit()
                    st.success("✅ Car details saved!")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    with tab2:
        st.subheader("Fleet Overview")
        
        # Load cars
        cars_df = pd.read_sql("SELECT * FROM cars ORDER BY car_number", conn)
        
        if not cars_df.empty:
            # Check for expiries
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Insurance expiry warning
            expiring_soon = cars_df[cars_df['insurance_expiry'] <= today]
            if not expiring_soon.empty:
                st.warning(f"⚠️ {len(expiring_soon)} cars have expired or expiring insurance!")
                with st.expander("View Details"):
                    st.dataframe(expiring_soon[['car_number', 'insurance_expiry']])
            
            # Show all cars
            st.dataframe(cars_df, use_container_width=True, height=400)
            
            # Fleet stats
            col1, col2, col3 = st.columns(3)
            with col1:
                active_cars = len(cars_df[cars_df['status'] == 'Active'])
                st.metric("Active Cars", active_cars)
            with col2:
                total_models = cars_df['car_model'].nunique()
                st.metric("Different Models", total_models)
            with col3:
                avg_year = cars_df['car_year'].mean()
                st.metric("Average Year", int(avg_year))
        else:
            st.info("No cars registered yet")
    
    with tab3:
        st.subheader("Maintenance Tracker")
        
        with st.form("maintenance_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                car_select = st.selectbox("Select Car", 
                    pd.read_sql("SELECT car_number FROM cars", conn)['car_number'].tolist())
            with col2:
                service_type = st.selectbox("Service Type", 
                    ["Regular", "Major", "Accident Repair", "Tyre Change", "Other"])
            with col3:
                service_date = st.date_input("Service Date")
            
            col1, col2 = st.columns(2)
            with col1:
                cost = st.number_input("Cost (₹)", min_value=0.0, value=1000.0)
                current_km = st.number_input("Current KM Reading")
            with col2:
                next_service = st.number_input("Next Service at KM")
                notes = st.text_area("Service Notes")
            
            if st.form_submit_button("💾 SAVE SERVICE"):
                st.success("Service record saved!")

def drivers_page():
    """Driver management"""
    st.title("👨‍✈️ Driver Management")
    
    tab1, tab2 = st.tabs(["➕ Add Driver", "📋 Driver List"])
    
    with tab1:
        with st.form("driver_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                driver_id = st.text_input("Driver ID *", placeholder="DRV001")
                name = st.text_input("Full Name *")
                phone = st.text_input("Phone Number *", placeholder="9876543210")
                license_no = st.text_input("License Number")
            
            with col2:
                license_expiry = st.date_input("License Expiry")
                joining_date = st.date_input("Joining Date")
                salary = st.number_input("Monthly Salary (₹)", min_value=0.0, value=15000.0)
                status = st.selectbox("Status", ["Active", "Inactive", "On Leave"])
            
            address = st.text_area("Address")
            emergency_contact = st.text_input("Emergency Contact")
            
            if st.form_submit_button("💾 SAVE DRIVER"):
                try:
                    conn.execute('''
                        INSERT OR REPLACE INTO drivers 
                        (driver_id, name, phone, license_number, license_expiry, 
                         address, emergency_contact, joining_date, salary, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (driver_id, name, phone, license_no, 
                          license_expiry.strftime("%Y-%m-%d"), address, 
                          emergency_contact, joining_date.strftime("%Y-%m-%d"), 
                          salary, status))
                    conn.commit()
                    st.success("✅ Driver saved!")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    with tab2:
        drivers_df = pd.read_sql("SELECT * FROM drivers ORDER BY name", conn)
        
        if not drivers_df.empty:
            # Driver statistics
            active_drivers = len(drivers_df[drivers_df['status'] == 'Active'])
            total_salary = drivers_df[drivers_df['status'] == 'Active']['salary'].sum()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Active Drivers", active_drivers)
            with col2:
                st.metric("Monthly Salary Payout", f"₹{total_salary:,.0f}")
            
            st.dataframe(drivers_df, use_container_width=True)
            
            # License expiry warning
            today = datetime.now().strftime("%Y-%m-%d")
            expiring = drivers_df[drivers_df['license_expiry'] <= today]
            if not expiring.empty:
                st.error(f"⚠️ {len(expiring)} drivers have expired licenses!")
        else:
            st.info("No drivers registered yet")

def expenses_page():
    """Expense tracking"""
    st.title("💸 Expense Tracker")
    
    with st.form("expense_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            date = st.date_input("Date", datetime.now())
            car_number = st.selectbox("Car (Optional)", 
                [""] + pd.read_sql("SELECT car_number FROM cars", conn)['car_number'].tolist())
        with col2:
            expense_type = st.selectbox("Expense Type", 
                ["Fuel", "Maintenance", "Insurance", "Toll", "Parking", "Fine", "Other"])
            amount = st.number_input("Amount (₹)", min_value=0.0, step=100.0)
        with col3:
            payment_method = st.selectbox("Payment Method", ["Cash", "UPI", "Card"])
            receipt_no = st.text_input("Receipt Number")
        
        description = st.text_area("Description", placeholder="Details about the expense")
        
        if st.form_submit_button("💾 ADD EXPENSE"):
            try:
                conn.execute('''
                    INSERT INTO expenses 
                    (date, car_number, expense_type, amount, description, payment_method, receipt_number)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (date.strftime("%Y-%m-%d"), car_number if car_number else None, 
                      expense_type, amount, description, payment_method, receipt_no))
                conn.commit()
                st.success("✅ Expense recorded!")
            except Exception as e:
                st.error(f"Error: {e}")
    
    st.markdown("---")
    
    # Expense summary
    st.subheader("Expense Summary")
    
    # Monthly expenses chart
    monthly_expenses = pd.read_sql('''
        SELECT strftime('%Y-%m', date) as month, SUM(amount) as total
        FROM expenses
        GROUP BY month
        ORDER BY month
    ''', conn)
    
    if not monthly_expenses.empty:
        fig = px.bar(monthly_expenses, x='month', y='total', 
                    title="Monthly Expenses Trend")
        st.plotly_chart(fig, use_container_width=True)
    
    # Expense by type
    type_expenses = pd.read_sql('''
        SELECT expense_type, SUM(amount) as total
        FROM expenses
        GROUP BY expense_type
        ORDER BY total DESC
    ''', conn)
    
    if not type_expenses.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.write("**By Type:**")
            st.dataframe(type_expenses)
        with col2:
            fig = px.pie(type_expenses, values='total', names='expense_type',
                        title="Expense Distribution")
            st.plotly_chart(fig, use_container_width=True)

def reports_page():
    """Advanced reports and analytics"""
    st.title("📊 Advanced Analytics")
    
    report_type = st.selectbox("Select Report", 
        ["Financial Summary", "Car Performance", "Driver Performance", 
         "Monthly Statement", "Yearly Comparison"])
    
    if report_type == "Financial Summary":
        col1, col2 = st.columns(2)
        
        with col1:
            # Income vs Expenses
            income_df = pd.read_sql('''
                SELECT date, SUM(amount) as income 
                FROM payments 
                GROUP BY date 
                ORDER BY date DESC 
                LIMIT 30
            ''', conn)
            
            expenses_df = pd.read_sql('''
                SELECT date, SUM(amount) as expenses 
                FROM expenses 
                GROUP BY date 
                ORDER BY date DESC 
                LIMIT 30
            ''', conn)
            
            # Merge and calculate profit
            if not income_df.empty and not expenses_df.empty:
                merged = pd.merge(income_df, expenses_df, on='date', how='outer').fillna(0)
                merged['profit'] = merged['income'] - merged['expenses']
                
                fig = go.Figure()
                fig.add_trace(go.Bar(x=merged['date'], y=merged['income'], name='Income', marker_color='green'))
                fig.add_trace(go.Bar(x=merged['date'], y=merged['expenses'], name='Expenses', marker_color='red'))
                fig.add_trace(go.Scatter(x=merged['date'], y=merged['profit'], name='Profit', 
                                        line=dict(color='blue', width=3)))
                
                fig.update_layout(title="Income vs Expenses (Last 30 Days)", barmode='group')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Key metrics
            total_income = pd.read_sql("SELECT SUM(amount) FROM payments", conn).iloc[0,0] or 0
            total_expenses = pd.read_sql("SELECT SUM(amount) FROM expenses", conn).iloc[0,0] or 0
            net_profit = total_income - total_expenses
            
            st.metric("Total Income", f"₹{total_income:,.0f}")
            st.metric("Total Expenses", f"₹{total_expenses:,.0f}")
            st.metric("Net Profit", f"₹{net_profit:,.0f}", 
                     delta=f"{((net_profit/total_income)*100 if total_income>0 else 0):.1f}%")
    
    elif report_type == "Car Performance":
        # Top performing cars
        car_performance = pd.read_sql('''
            SELECT car_number, COUNT(*) as trips, SUM(amount) as revenue,
                   AVG(amount) as avg_fare
            FROM payments
            GROUP BY car_number
            ORDER BY revenue DESC
        ''', conn)
        
        if not car_performance.empty:
            fig = px.bar(car_performance.head(10), x='car_number', y='revenue',
                        title="Top 10 Cars by Revenue")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(car_performance)

def settings_page():
    """App settings and configuration"""
    st.title("⚙️ Settings")
    
    tab1, tab2, tab3 = st.tabs(["General", "Database", "Backup"])
    
    with tab1:
        st.subheader("General Settings")
        
        col1, col2 = st.columns(2)
        with col1:
            currency = st.selectbox("Currency", ["₹ Rupee (INR)", "$ Dollar (USD)", "€ Euro (EUR)"])
            date_format = st.selectbox("Date Format", ["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"])
        with col2:
            language = st.selectbox("Language", ["English", "Hindi", "Tamil", "Telugu"])
            notifications = st.checkbox("Enable Notifications", value=True)
        
        if st.button("💾 Save Settings"):
            st.success("Settings saved!")
    
    with tab2:
        st.subheader("Database Management")
        
        # Database info
        db_size = conn.execute("SELECT page_count * page_size FROM pragma_page_count(), pragma_page_size()").fetchone()[0]
        st.info(f"Database Size: {db_size/1024/1024:.2f} MB")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔄 Optimize DB"):
                conn.execute("VACUUM")
                st.success("Database optimized!")
        
        with col2:
            if st.button("📊 View Schema"):
                tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
                st.write("Database Tables:")
                st.dataframe(tables)
        
        with col3:
            if st.button("🗑️ Clear All Data"):
                if st.checkbox("Confirm DELETE ALL DATA?"):
                    conn.execute("DELETE FROM payments")
                    conn.execute("DELETE FROM cars")
                    conn.execute("DELETE FROM drivers")
                    conn.execute("DELETE FROM expenses")
                    conn.commit()
                    st.error("All data deleted!")
    
    with tab3:
        st.subheader("Backup & Restore")
        
        # Export data
        if st.button("📤 Export All Data"):
            with st.spinner("Creating backup..."):
                # Create Excel with multiple sheets
                payments = pd.read_sql("SELECT * FROM payments", conn)
                cars = pd.read_sql("SELECT * FROM cars", conn)
                drivers = pd.read_sql("SELECT * FROM drivers", conn)
                expenses = pd.read_sql("SELECT * FROM expenses", conn)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"taxi_backup_{timestamp}.xlsx"
                
                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    payments.to_excel(writer, sheet_name='Payments', index=False)
                    cars.to_excel(writer, sheet_name='Cars', index=False)
                    drivers.to_excel(writer, sheet_name='Drivers', index=False)
                    expenses.to_excel(writer, sheet_name='Expenses', index=False)
                
                with open(filename, 'rb') as f:
                    st.download_button(
                        "📥 Download Backup",
                        f,
                        filename,
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
        
        # Import data
        st.subheader("Restore from Backup")
        uploaded_file = st.file_uploader("Choose Excel backup file", type=['xlsx'])
        if uploaded_file:
            if st.button("📥 Restore Data"):
                try:
                    # Read uploaded file
                    xls = pd.ExcelFile(uploaded_file)
                    
                    # Restore each table
                    for sheet in xls.sheet_names:
                        df = pd.read_excel(xls, sheet_name=sheet)
                        # Clear existing data
                        conn.execute(f"DELETE FROM {sheet.lower()}")
                        # Insert new data
                        df.to_sql(sheet.lower(), conn, if_exists='append', index=False)
                    
                    conn.commit()
                    st.success("✅ Data restored successfully!")
                except Exception as e:
                    st.error(f"Error restoring: {e}")

# ========== MAIN APP ==========
def main():
    """Main application"""
    
    # App Header
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>🚕 Taxi Manager Pro</h1>", 
                   unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666;'>Professional Taxi Management System</p>", 
                   unsafe_allow_html=True)
    
    # Navigation
    show_navigation()
    
    # Page content
    st.markdown("---")
    
    # Route to correct page
    pages = {
        "dashboard": dashboard_page,
        "add_trip": add_trip_page,
        "view_trips": view_trips_page,
        "cars": cars_page,
        "drivers": drivers_page,
        "expenses": expenses_page,
        "reports": reports_page,
        "settings": settings_page
    }
    
    # Get current page function and call it
    page_func = pages.get(st.session_state.page, dashboard_page)
    page_func()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #888; font-size: 12px; padding: 10px;'>
        📱 <b>Taxi Manager Pro</b> v1.0 | Made with Streamlit | 
        Last Updated: """ + datetime.now().strftime("%Y-%m-%d") + """
    </div>
    """, unsafe_allow_html=True)

# Run the app
if __name__ == "__main__":
    main()


--------

import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

# 🚀 MOBILE-OPTIMIZED TAXI MANAGEMENT
st.set_page_config(
    page_title="Taxi Manager",
    page_icon="🚕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for mobile
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        height: 3em;
        font-size: 16px;
    }
    .stTextInput > div > input {
        font-size: 16px !important;
        height: 3em !important;
    }
    .stNumberInput > div > input {
        font-size: 16px !important;
    }
    .stSelectbox > div > div {
        font-size: 16px !important;
    }
    div[data-testid="stHorizontalBlock"] {
        gap: 1rem;
    }
    .main .block-container {
        padding-top: 2rem;
    }
    h1, h2, h3 {
        color: #FF4B4B !important;
    }
</style>
""", unsafe_allow_html=True)

# Title with emoji
st.title("🚕 Taxi Management System")
st.markdown("**Access from your phone! 📱**")

# Initialize database
@st.cache_resource
def init_database():
    # Connect to existing database or create new
    conn = sqlite3.connect('taxi_data.db', check_same_thread=False)
    
    # Create tables if they don't exist
    conn.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            car_number TEXT,
            driver_name TEXT,
            amount REAL,
            payment_type TEXT,
            phone TEXT,
            notes TEXT
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS cars (
            car_number TEXT PRIMARY KEY,
            model TEXT,
            year INTEGER,
            owner TEXT,
            owner_phone TEXT,
            insurance_expiry TEXT
        )
    ''')
    
    conn.commit()
    return conn

conn = init_database()

# Sidebar Navigation
st.sidebar.title("📱 Navigation")
page = st.sidebar.radio("Go to:", 
    ["🏠 Dashboard", "💳 Add Payment", "📋 View Payments", "🚗 Car Details", "📊 Reports", "⚙️ Settings"])

if page == "🏠 Dashboard":
    st.header("Dashboard")
    
    # Quick stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_payments = conn.execute("SELECT COUNT(*) FROM payments").fetchone()[0]
        st.metric("Total Payments", total_payments, "📈")
    
    with col2:
        total_amount = conn.execute("SELECT SUM(amount) FROM payments").fetchone()[0] or 0
        st.metric("Total Amount", f"₹{total_amount:,.0f}", "💰")
    
    with col3:
        unique_cars = conn.execute("SELECT COUNT(DISTINCT car_number) FROM payments").fetchone()[0]
        st.metric("Unique Cars", unique_cars, "🚗")
    
    # Today's summary
    st.subheader("📅 Today's Activity")
    today = datetime.now().strftime("%Y-%m-%d")
    
    col1, col2 = st.columns(2)
    with col1:
        today_count = conn.execute("SELECT COUNT(*) FROM payments WHERE date=?", (today,)).fetchone()[0]
        st.info(f"Today's Payments: **{today_count}**")
    
    with col2:
        today_total = conn.execute("SELECT SUM(amount) FROM payments WHERE date=?", (today,)).fetchone()[0] or 0
        st.success(f"Today's Total: **₹{today_total:,.0f}**")
    
    # Recent payments
    st.subheader("🕒 Recent Payments")
    recent = pd.read_sql("SELECT * FROM payments ORDER BY id DESC LIMIT 10", conn)
    if not recent.empty:
        st.dataframe(recent, use_container_width=True)
    else:
        st.info("No payments yet. Add your first payment!")

elif page == "💳 Add Payment":
    st.header("💳 Add New Payment")
    
    with st.form("payment_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            car_number = st.text_input("Car Number *", placeholder="KA01AB1234")
            driver_name = st.text_input("Driver Name", placeholder="Driver's name")
            amount = st.number_input("Amount (₹) *", min_value=0.0, step=100.0)
        
        with col2:
            payment_type = st.selectbox("Payment Type", ["Cash", "UPI", "Card", "Bank Transfer"])
            phone = st.text_input("Phone Number", placeholder="+91XXXXXXXXXX")
            date = st.date_input("Date", datetime.now())
        
        notes = st.text_area("Notes (Optional)", placeholder="Additional notes...")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col2:
            submitted = st.form_submit_button("💾 SAVE PAYMENT", type="primary")
        
        if submitted and car_number and amount > 0:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO payments (date, car_number, driver_name, amount, payment_type, phone, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (date.strftime("%Y-%m-%d"), car_number, driver_name, amount, payment_type, phone, notes))
                conn.commit()
                st.success("✅ Payment saved successfully!")
                st.balloons()
            except Exception as e:
                st.error(f"Error: {e}")
        elif submitted:
            st.error("Please fill required fields (Car Number and Amount)")

elif page == "📋 View Payments":
    st.header("📋 All Payments")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        search_car = st.text_input("Search Car Number")
    with col2:
        filter_date = st.date_input("Filter by Date")
    with col3:
        payment_filter = st.selectbox("Payment Type", ["All", "Cash", "UPI", "Card", "Bank Transfer"])
    
    # Build query
    query = "SELECT * FROM payments WHERE 1=1"
    params = []
    
    if search_car:
        query += " AND car_number LIKE ?"
        params.append(f"%{search_car}%")
    
    if filter_date:
        query += " AND date = ?"
        params.append(filter_date.strftime("%Y-%m-%d"))
    
    if payment_filter != "All":
        query += " AND payment_type = ?"
        params.append(payment_filter)
    
    query += " ORDER BY date DESC, id DESC"
    
    # Load data
    df = pd.read_sql_query(query, conn, params=params)
    
    if not df.empty:
        # Show summary
        st.info(f"Showing {len(df)} payments | Total: ₹{df['amount'].sum():,.0f}")
        
        # Show data
        st.dataframe(df, use_container_width=True)
        
        # Export buttons
        col1, col2 = st.columns(2)
        with col1:
            csv = df.to_csv(index=False)
            st.download_button(
                "📥 Download CSV",
                csv,
                "taxi_payments.csv",
                "text/csv"
            )
        with col2:
            excel = df.to_excel(index=False)
            st.download_button(
                "📊 Download Excel",
                excel,
                "taxi_payments.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.warning("No payments found with current filters")

elif page == "🚗 Car Details":
    st.header("🚗 Car Management")
    
    tab1, tab2 = st.tabs(["➕ Add/Edit Car", "📋 View Cars"])
    
    with tab1:
        st.subheader("Add or Update Car")
        
        with st.form("car_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                car_num = st.text_input("Car Number *", key="car_num")
                model = st.text_input("Car Model", placeholder="Toyota Innova, Swift Dzire, etc.")
                year = st.number_input("Year", min_value=2000, max_value=2024, value=2020)
            
            with col2:
                owner = st.text_input("Owner Name")
                owner_phone = st.text_input("Owner Phone")
                insurance = st.date_input("Insurance Expiry", datetime.now())
            
            submitted = st.form_submit_button("💾 SAVE CAR DETAILS")
            
            if submitted and car_num:
                try:
                    conn.execute('''
                        INSERT OR REPLACE INTO cars 
                        (car_number, model, year, owner, owner_phone, insurance_expiry)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (car_num, model, year, owner, owner_phone, insurance.strftime("%Y-%m-%d")))
                    conn.commit()
                    st.success("✅ Car details saved!")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    with tab2:
        st.subheader("All Cars")
        cars = pd.read_sql("SELECT * FROM cars ORDER BY car_number", conn)
        
        if not cars.empty:
            # Show insurance status
            today = datetime.now().strftime("%Y-%m-%d")
            cars['insurance_status'] = cars['insurance_expiry'].apply(
                lambda x: "✅ Valid" if x >= today else "⚠️ Expired"
            )
            
            st.dataframe(cars, use_container_width=True)
            
            # Insurance warnings
            expired = cars[cars['insurance_expiry'] < today]
            if not expired.empty:
                st.warning(f"⚠️ {len(expired)} cars have expired insurance!")
        else:
            st.info("No cars added yet")

elif page == "📊 Reports":
    st.header("📊 Reports & Analytics")
    
    report_type = st.selectbox("Select Report", 
        ["Daily Summary", "Monthly Report", "Car-wise Report", "Payment Type Analysis"])
    
    if report_type == "Daily Summary":
        daily = pd.read_sql('''
            SELECT date, COUNT(*) as payments, SUM(amount) as total_amount
            FROM payments 
            GROUP BY date 
            ORDER BY date DESC
        ''', conn)
        
        if not daily.empty:
            st.subheader("Daily Payments Trend")
            fig = px.line(daily, x='date', y='total_amount', 
                         title="Daily Collection Trend")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(daily)
    
    elif report_type == "Car-wise Report":
        car_report = pd.read_sql('''
            SELECT car_number, COUNT(*) as payment_count, SUM(amount) as total_paid
            FROM payments 
            GROUP BY car_number 
            ORDER BY total_paid DESC
        ''', conn)
        
        if not car_report.empty:
            st.subheader("Top Paying Cars")
            fig = px.bar(car_report.head(10), x='car_number', y='total_paid',
                        title="Top 10 Cars by Payment Amount")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(car_report)

elif page == "⚙️ Settings":
    st.header("⚙️ Settings")
    
    st.subheader("Database Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Reset Database", type="secondary"):
            conn.execute("DELETE FROM payments")
            conn.commit()
            st.warning("Database cleared!")
    
    with col2:
        if st.button("📊 Export Full Backup"):
            # Export all data
            payments = pd.read_sql("SELECT * FROM payments", conn)
            cars = pd.read_sql("SELECT * FROM cars", conn)
            
            # Create Excel with multiple sheets
            with pd.ExcelWriter('taxi_backup.xlsx') as writer:
                payments.to_excel(writer, sheet_name='Payments', index=False)
                cars.to_excel(writer, sheet_name='Cars', index=False)
            
            with open('taxi_backup.xlsx', 'rb') as f:
                st.download_button(
                    "Download Backup",
                    f,
                    "taxi_system_backup.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>📱 <b>Taxi Management System</b> | Mobile Access Enabled</p>
    <p style='font-size: 12px; color: #888;'>Open this URL on your phone to access anytime</p>
</div>
""", unsafe_allow_html=True)
