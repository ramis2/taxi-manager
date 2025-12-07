# app.py - Your main Streamlit application

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# ========== PAGE CONFIG ==========
st.set_page_config(
    page_title="Taxi Manager Dashboard",
    page_icon="🚖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== SIDEBAR NAVIGATION ==========
with st.sidebar:
    st.title("🚖 Taxi Manager")
    page = st.radio(
        "Navigation",
        ["Dashboard", "Data Entry", "Reports", "Settings"],
        key="nav"
    )
    
    st.divider()
    
    # Add some filters or controls in sidebar
    date_range = st.date_input(
        "Select Date Range",
        value=(datetime.now() - timedelta(days=30), datetime.now()),
        key="date_filter"
    )
    
    st.divider()
    st.caption("© 2024 Taxi Manager App")

# ========== DASHBOARD PAGE ==========
if page == "Dashboard":
    st.title("📊 Taxi Management Dashboard")
    
    # Generate sample data for metrics
    np.random.seed(42)
    
    # Create sample metrics
    total_revenue = 15289.50
    total_expenses = 9876.25
    total_profit = total_revenue - total_expenses
    total_unpaid = -1250.75  # Negative for overpaid
    
    # Display metrics in columns
    st.header("Financial Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # FIXED METRIC FORMATTING: Using :,.2f (NOT :%.2f)
        st.metric(
            label="TOTAL REVENUE",
            value=f"${total_revenue:,.2f}",
            delta="+12.5%",
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            label="TOTAL EXPENSES",
            value=f"${total_expenses:,.2f}",
            delta="-3.2%",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            label="NET PROFIT",
            value=f"${total_profit:,.2f}",
            delta="+8.7%",
            delta_color="normal"
        )
    
    with col4:
        # THIS IS THE FIX FOR YOUR ERROR: Using :,.2f instead of :%.2f
        st.metric(
            label="OVERPAID AMOUNT",
            value=f"${total_unpaid:,.2f}",  # FIXED!
            delta_color="off"
        )
    
    # Charts section
    st.header("Revenue Trends")
    
    # Create sample chart data
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    revenue_data = np.random.normal(500, 150, 30).cumsum() + 10000
    expense_data = np.random.normal(300, 100, 30).cumsum() + 7000
    
    chart_df = pd.DataFrame({
        'Date': dates,
        'Revenue': revenue_data,
        'Expenses': expense_data
    })
    
    # Display chart
    st.line_chart(chart_df.set_index('Date'))
    
    # Data table
    st.header("Recent Transactions")
    st.dataframe(chart_df.tail(10), use_container_width=True)

# ========== DATA ENTRY PAGE ==========
elif page == "Data Entry":
    st.title("📝 Add New Transaction")
    
    # CREATE A FORM WITH SUBMIT BUTTON
    with st.form("transaction_form", clear_on_submit=True):
        st.subheader("Transaction Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Form fields
            transaction_date = st.date_input("Date", datetime.now())
            transaction_type = st.selectbox(
                "Type",
                ["Fare", "Maintenance", "Fuel", "Insurance", "Other"]
            )
            amount = st.number_input(
                "Amount ($)",
                min_value=0.0,
                step=10.0,
                value=100.0
            )
        
        with col2:
            driver_id = st.text_input("Driver ID")
            vehicle_id = st.text_input("Vehicle ID")
            payment_method = st.selectbox(
                "Payment Method",
                ["Cash", "Credit Card", "Digital Wallet", "Other"]
            )
        
        # Additional details
        description = st.text_area("Description", height=100)
        
        # ATTENTION: THIS IS THE CRITICAL PART - MUST HAVE SUBMIT BUTTON
        submitted = st.form_submit_button("💾 Save Transaction")
        
        # Form validation and processing
        if submitted:
            if amount <= 0:
                st.error("❌ Amount must be greater than 0!")
            elif not driver_id or not vehicle_id:
                st.error("❌ Please enter Driver ID and Vehicle ID!")
            else:
                # Save the transaction (in real app, save to database)
                st.success("✅ Transaction saved successfully!")
                
                # Show summary
                st.subheader("Transaction Summary")
                summary_col1, summary_col2 = st.columns(2)
                
                with summary_col1:
                    st.write(f"**Date:** {transaction_date}")
                    st.write(f"**Type:** {transaction_type}")
                    st.write(f"**Amount:** ${amount:,.2f}")
                
                with summary_col2:
                    st.write(f"**Driver ID:** {driver_id}")
                    st.write(f"**Vehicle ID:** {vehicle_id}")
                    st.write(f"**Payment Method:** {payment_method}")

# ========== REPORTS PAGE ==========
elif page == "Reports":
    st.title("📄 Generate Reports")
    
    # Another form example for report generation
    with st.form("report_form"):
        st.subheader("Report Parameters")
        
        report_type = st.selectbox(
            "Report Type",
            ["Daily Summary", "Weekly Summary", "Monthly Summary", "Driver Performance"]
        )
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date")
        with col2:
            end_date = st.date_input("End Date")
        
        # Form submit button - REQUIRED
        generate_report = st.form_submit_button("📊 Generate Report")
        
        if generate_report:
            if start_date > end_date:
                st.error("❌ Start date must be before end date!")
            else:
                st.success(f"✅ Generating {report_type} report for {start_date} to {end_date}")
                
                # Sample report data
                report_data = {
                    "Period": f"{start_date} to {end_date}",
                    "Total Trips": np.random.randint(100, 500),
                    "Total Revenue": f"${np.random.uniform(5000, 25000):,.2f}",
                    "Average Fare": f"${np.random.uniform(15, 45):,.2f}",
                    "Fuel Efficiency": f"{np.random.uniform(8, 15):.1f} km/L"
                }
                
                # Display report
                st.subheader("Report Summary")
                for key, value in report_data.items():
                    st.write(f"**{key}:** {value}")

# ========== SETTINGS PAGE ==========
else:
    st.title("⚙️ Settings")
    
    with st.form("settings_form"):
        st.subheader("Application Settings")
        
        # Settings options
        currency = st.selectbox("Currency", ["USD", "EUR", "GBP", "JPY"])
        date_format = st.selectbox("Date Format", ["YYYY-MM-DD", "MM/DD/YYYY", "DD/MM/YYYY"])
        notifications = st.checkbox("Enable Email Notifications", value=True)
        
        # Form submit button - REQUIRED
        save_settings = st.form_submit_button("💾 Save Settings")
        
        if save_settings:
            st.success("✅ Settings saved successfully!")
            
            # Display saved settings
            st.info(f"""
            **Saved Settings:**
            - Currency: {currency}
            - Date Format: {date_format}
            - Email Notifications: {'Enabled' if notifications else 'Disabled'}
            """)

# ========== FOOTER ==========
st.divider()
st.caption("Taxi Manager Dashboard v1.0 | For support contact: admin@taximanager.com")
```

2. Requirements File (requirements.txt)

Create a requirements.txt file in the same folder:

```txt
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
```

3. How to Run the Application:

Option A: Local Computer

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

Option B: Streamlit Cloud (Deployment)

1. Upload both files (app.py and requirements.txt) to GitHub
2. Go to share.streamlit.io
3. Connect your GitHub repository
4. Point to app.py as the main file

KEY TAKEAWAYS:

1. All code goes in app.py - This is your main file
2. Forms MUST have st.form_submit_button() - Always add this inside your forms
3. Metric formatting uses :,.2f NOT :%.2f - This was your specific error
4. Every page/section should be controlled - Use if/elif statements with sidebar navigation

For Your Specific Error Fix:

Replace line 467 (from your error message) with:

```python
# WRONG (causes error):
st.metric("OVERPAID", f"${total_unpaid:%.0f}")

# CORRECT (fixed):
st.metric("OVERPAID", f"${total_unpaid:,.0f}")
```

This application is complete and ready to run. Copy all the code into app.py, create the requirements.txt, and run with streamlit run app.py.


---------------------
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import io

# Page setup
st.set_page_config(
    page_title="Taxi Manager",
    page_icon="🚕",
    layout="centered"
)

# Big fonts for mobile
st.markdown("""
<style>
    /* BIG EVERYTHING FOR MOBILE */
    html, body { font-size: 24px !important; }
    
    .stButton > button {
        width: 100% !important;
        height: 70px !important;
        font-size: 26px !important;
        margin: 10px 0 !important;
    }
    
    .stTextInput > div > input {
        font-size: 26px !important;
        height: 70px !important;
    }
    
    .stNumberInput > div > input {
        font-size: 26px !important;
        height: 70px !important;
    }
    
    h1 {
        font-size: 40px !important;
        text-align: center !important;
    }
    
    h2 {
        font-size: 34px !important;
    }
    
    h3 {
        font-size: 30px !important;
    }
    
    .stRadio > div {
        font-size: 28px !important;
    }
    
    .stDataFrame {
        font-size: 24px !important;
    }
    
    .stMetric {
        font-size: 30px !important;
    }
    
    .red-balance {
        color: #FF0000 !important;
        font-weight: bold !important;
    }
    
    .green-balance {
        color: #00AA00 !important;
        font-weight: bold !important;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Database
@st.cache_resource
def init_db():
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    
    # Payments table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            car_number TEXT,
            driver_name TEXT,
            amount REAL,
            payment_type TEXT,
            status TEXT DEFAULT 'paid',
            commission_rate INTEGER DEFAULT 20
        )
    ''')
    
    # Cars table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            car_number TEXT UNIQUE,
            car_model TEXT,
            car_year INTEGER,
            owner_name TEXT,
            owner_phone TEXT
        )
    ''')
    
    # Drivers table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS drivers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            driver_name TEXT,
            driver_phone TEXT,
            license_number TEXT,
            address TEXT,
            joining_date TEXT
        )
    ''')
    
    # Driver payments (advance/payments made to drivers)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS driver_payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            driver_name TEXT,
            amount REAL,
            payment_type TEXT,
            notes TEXT
        )
    ''')
    
    return conn

conn = init_db()

# Title
st.title("TAXI MANAGER")

# Navigation with 6 options
page = st.radio(
    "NAVIGATION:",
    ["DASHBOARD", "ADD PAYMENT", "VIEW PAYMENTS", "CAR REGISTRATION", 
     "DRIVER REGISTRATION", "BALANCE & REPORTS"],
    horizontal=False
)

st.markdown("---")

# DASHBOARD PAGE
if page == "DASHBOARD":
    st.header("DASHBOARD")
    
    # Calculate balances
    total_earnings_result = conn.execute("SELECT SUM(amount) FROM payments").fetchone()[0] or 0
    total_paid_to_drivers_result = conn.execute("SELECT SUM(amount) FROM driver_payments").fetchone()[0] or 0
    unpaid_balance = total_earnings_result - total_paid_to_drivers_result
    
    # Stats row 1
    col1, col2, col3 = st.columns(3)
    
    with col1:
        today_trips = conn.execute("SELECT COUNT(*) FROM payments WHERE date=date('now')").fetchone()[0]
        st.metric("TODAY'S TRIPS", today_trips)
    
    with col2:
        today_earning = conn.execute("SELECT SUM(amount) FROM payments WHERE date=date('now')").fetchone()[0] or 0
        st.metric("TODAY'S EARNINGS", f"₹{today_earning}")
    
    with col3:
        total_cars = conn.execute("SELECT COUNT(*) FROM cars").fetchone()[0]
        st.metric("TOTAL CARS", total_cars)
    
    # Stats row 2 - BALANCES
    st.markdown("---")
    st.subheader("FINANCIAL BALANCES")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("TOTAL EARNINGS", f"₹{total_earnings_result:,.0f}")
    
    with col2:
        st.metric("PAID TO DRIVERS", f"₹{total_paid_to_drivers_result:,.0f}")
    
    with col3:
        balance_color = "normal"
        if unpaid_balance > 0:
            balance_color = "green"
        elif unpaid_balance < 0:
            balance_color = "red"
        
        st.metric("UNPAID BALANCE", f"₹{unpaid_balance:,.0f}", delta_color=balance_color)
    
    # Driver-wise unpaid
    st.subheader("DRIVER BALANCES")
    
    # Calculate per driver
    driver_earnings = pd.read_sql('''
        SELECT driver_name, SUM(amount) as total_earnings
        FROM payments 
        GROUP BY driver_name
    ''', conn)
    
    driver_payments = pd.read_sql('''
        SELECT driver_name, SUM(amount) as total_paid
        FROM driver_payments 
        GROUP BY driver_name
    ''', conn)
    
    if not driver_earnings.empty:
        # Merge and calculate balance
        if not driver_payments.empty:
            df = pd.merge(driver_earnings, driver_payments, on='driver_name', how='left').fillna(0)
            df['unpaid'] = df['total_earnings'] - df['total_paid']
        else:
            df = driver_earnings.copy()
            df['total_paid'] = 0
            df['unpaid'] = df['total_earnings']
        
        # Display
        for _, row in df.iterrows():
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.write(f"**{row['driver_name']}**")
            with col2:
                st.write(f"Earned: ₹{row['total_earnings']:,.0f}")
            with col3:
                st.write(f"Paid: ₹{row['total_paid']:,.0f}")
            with col4:
                if row['unpaid'] > 0:
                    st.markdown(f"<span class='red-balance'>Unpaid: ₹{row['unpaid']:,.0f}</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<span class='green-balance'>Balance: ₹{row['unpaid']:,.0f}</span>", unsafe_allow_html=True)

# ADD PAYMENT PAGE
elif page == "ADD PAYMENT":
    st.header("ADD PAYMENT")
    
    with st.form("add_form"):
        st.subheader("Payment Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            date = st.date_input("DATE", datetime.now())
            
        with col2:
            cars = pd.read_sql("SELECT car_number FROM cars", conn)
            if not cars.empty:
                car = st.selectbox("CAR NUMBER", cars['car_number'].tolist())
            else:
                car = st.text_input("CAR NUMBER", "KA01AB1234")
        
        col1, col2 = st.columns(2)
        
        with col1:
            drivers = pd.read_sql("SELECT driver_name FROM drivers", conn)
            if not drivers.empty:
                driver = st.selectbox("DRIVER", drivers['driver_name'].tolist())
            else:
                driver = st.text_input("DRIVER NAME", "Rajesh Kumar")
        
        with col2:
            amount = st.number_input("AMOUNT (₹)", 0.0, 100000.0, 500.0, step=100.0)
        
        col1, col2 = st.columns(2)
        
        with col1:
            payment_type = st.selectbox("PAYMENT TYPE", ["Cash", "UPI", "Card", "Bank Transfer"])
        
        with col2:
            status = st.selectbox("STATUS", ["paid", "unpaid"])
        
        commission = st.slider("COMMISSION %", 0, 50, 20)
        
        if st.form_submit_button("SAVE PAYMENT", use_container_width=True):
            conn.execute(
                "INSERT INTO payments (date, car_number, driver_name, amount, payment_type, status, commission_rate) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (date.strftime("%Y-%m-%d"), car, driver, amount, payment_type, status, commission)
            )
            conn.commit()
            st.success("PAYMENT SAVED SUCCESSFULLY!")
            st.balloons()

# VIEW PAYMENTS PAGE
elif page == "VIEW PAYMENTS":
    st.header("ALL PAYMENTS")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        search = st.text_input("SEARCH BY CAR OR DRIVER")
    with col2:
        status_filter = st.selectbox("FILTER BY STATUS", ["All", "paid", "unpaid"])
    
    # Build query
    if search:
        query = "SELECT * FROM payments WHERE car_number LIKE ? OR driver_name LIKE ?"
        params = [f"%{search}%", f"%{search}%"]
    else:
        query = "SELECT * FROM payments WHERE 1=1"
        params = []
    
    if status_filter != "All":
        query += " AND status = ?"
        params.append(status_filter)
    
    query += " ORDER BY date DESC"
    
    df = pd.read_sql_query(query, conn, params=params)
    
    if not df.empty:
        # Summary
        total = df['amount'].sum()
        unpaid_total = df[df['status'] == 'unpaid']['amount'].sum()
        count = len(df)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("TOTAL PAYMENTS", count)
        with col2:
            st.metric("TOTAL AMOUNT", f"₹{total:,.0f}")
        with col3:
            st.metric("UNPAID AMOUNT", f"₹{unpaid_total:,.0f}")
        
        # Show data
        st.dataframe(df, use_container_width=True, height=500)
    else:
        st.info("No payments found.")

# CAR REGISTRATION PAGE
elif page == "CAR REGISTRATION":
    st.header("CAR REGISTRATION")
    
    tab1, tab2 = st.tabs(["ADD NEW CAR", "VIEW ALL CARS"])
    
    with tab1:
        st.subheader("REGISTER NEW CAR")
        with st.form("car_form"):
            car_no = st.text_input("CAR NUMBER", "KA01AB1234")
            model = st.text_input("CAR MODEL", "Toyota Innova")
            year = st.number_input("YEAR", 2000, 2030, 2020)
            owner = st.text_input("OWNER NAME", "Mr. Sharma")
            phone = st.text_input("PHONE NUMBER", "9876543210")
            
            if st.form_submit_button("REGISTER CAR", use_container_width=True):
                try:
                    conn.execute(
                        "INSERT INTO cars (car_number, car_model, car_year, owner_name, owner_phone) VALUES (?, ?, ?, ?, ?)",
                        (car_no, model, year, owner, phone)
                    )
                    conn.commit()
                    st.success(f"Car {car_no} registered successfully!")
                except:
                    st.error("Car already exists!")
    
    with tab2:
        st.subheader("REGISTERED CARS")
        cars = pd.read_sql("SELECT * FROM cars ORDER BY car_number", conn)
        
        if not cars.empty:
            st.dataframe(cars, use_container_width=True)
        else:
            st.info("No cars registered yet.")

# DRIVER REGISTRATION PAGE
elif page == "DRIVER REGISTRATION":
    st.header("DRIVER REGISTRATION")
    
    tab1, tab2 = st.tabs(["ADD NEW DRIVER", "VIEW ALL DRIVERS"])
    
    with tab1:
        st.subheader("REGISTER NEW DRIVER")
        with st.form("driver_form"):
            driver_name = st.text_input("DRIVER FULL NAME", "Rajesh Kumar")
            driver_phone = st.text_input("PHONE NUMBER", "9876543210")
            license_no = st.text_input("LICENSE NUMBER", "DL1234567890123")
            address = st.text_area("ADDRESS", "Mumbai, Maharashtra")
            joining_date = st.date_input("JOINING DATE", datetime.now())
            
            if st.form_submit_button("REGISTER DRIVER", use_container_width=True):
                conn.execute(
                    "INSERT INTO drivers (driver_name, driver_phone, license_number, address, joining_date) VALUES (?, ?, ?, ?, ?)",
                    (driver_name, driver_phone, license_no, address, joining_date.strftime("%Y-%m-%d"))
                )
                conn.commit()
                st.success(f"Driver {driver_name} registered successfully!")
    
    with tab2:
        st.subheader("REGISTERED DRIVERS")
        drivers = pd.read_sql("SELECT * FROM drivers ORDER BY driver_name", conn)
        
        if not drivers.empty:
            st.dataframe(drivers, use_container_width=True)
        else:
            st.info("No drivers registered yet.")

# BALANCE & REPORTS PAGE
elif page == "BALANCE & REPORTS":
    st.header("BALANCE & REPORTS")
    
    tab1, tab2, tab3 = st.tabs(["PAY DRIVER", "BALANCE SUMMARY", "DRIVER LETTER"])
    
    with tab1:
        st.subheader("PAY DRIVER (Reduce Unpaid)")
        
        with st.form("pay_driver_form"):
            drivers = pd.read_sql("SELECT driver_name FROM drivers", conn)
            
            if not drivers.empty:
                driver = st.selectbox("SELECT DRIVER", drivers['driver_name'].tolist())
                
                # Calculate driver's unpaid balance
                driver_earnings = conn.execute(
                    "SELECT SUM(amount) FROM payments WHERE driver_name = ?",
                    (driver,)
                ).fetchone()[0] or 0
                
                driver_paid = conn.execute(
                    "SELECT SUM(amount) FROM driver_payments WHERE driver_name = ?",
                    (driver,)
                ).fetchone()[0] or 0
                
                unpaid_balance = driver_earnings - driver_paid
                
                st.info(f"**{driver}** - Unpaid Balance: ₹{unpaid_balance:,.0f}")
                
                col1, col2 = st.columns(2)
                with col1:
                    date = st.date_input("PAYMENT DATE", datetime.now())
                with col2:
                    amount = st.number_input("PAYMENT AMOUNT (₹)", 0.0, float(unpaid_balance), 0.0)
                
                payment_type = st.selectbox("PAYMENT METHOD", ["Cash", "Bank Transfer", "UPI"])
                notes = st.text_area("NOTES", "Payment for services")
                
                if st.form_submit_button("PAY DRIVER", use_container_width=True):
                    if amount > 0:
                        conn.execute(
                            "INSERT INTO driver_payments (date, driver_name, amount, payment_type, notes) VALUES (?, ?, ?, ?, ?)",
                            (date.strftime("%Y-%m-%d"), driver, amount, payment_type, notes)
                        )
                        conn.commit()
                        st.success(f"Paid ₹{amount:,.0f} to {driver}")
                    else:
                        st.warning("Please enter payment amount")
            else:
                st.info("No drivers registered yet.")
    
    with tab2:
        st.subheader("BALANCE SUMMARY")
        
        # Overall summary
        total_earnings = conn.execute("SELECT SUM(amount) FROM payments").fetchone()[0] or 0
        total_driver_payments = conn.execute("SELECT SUM(amount) FROM driver_payments").fetchone()[0] or 0
        total_unpaid = total_earnings - total_driver_payments
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("TOTAL EARNINGS", f"₹{total_earnings:,.0f}")
        with col2:
            st.metric("TOTAL PAID", f"₹{total_driver_payments:,.0f}")
        with col3:
            if total_unpaid > 0:
                st.metric("TOTAL UNPAID", f"₹{total_unpaid:,.0f}", delta_color="green")
            else:
                st.metric("OVERPAID", f"₹{-total_unpaid:,.0f}", delta_color="red")
        
        # Driver-wise details
        st.subheader("DRIVER-WISE BALANCE")
        
        # Get all drivers with their balances
        query = '''
            SELECT 
                d.driver_name,
                d.driver_phone,
                COALESCE(SUM(p.amount), 0) as total_earnings,
                COALESCE(SUM(dp.amount), 0) as total_paid,
                COALESCE(SUM(p.amount), 0) - COALESCE(SUM(dp.amount), 0) as balance
            FROM drivers d
            LEFT JOIN payments p ON d.driver_name = p.driver_name
            LEFT JOIN driver_payments dp ON d.driver_name = dp.driver_name
            GROUP BY d.driver_name, d.driver_phone
        '''
        
        balance_df = pd.read_sql(query, conn)
        
        if not balance_df.empty:
            # Color code balances
            def color_balance(val):
                color = 'green' if val >= 0 else 'red'
                return f'color: {color}; font-weight: bold'
            
            styled_df = balance_df.style.applymap(color_balance, subset=['balance'])
            st.dataframe(styled_df, use_container_width=True)
        else:
            st.info("No balance data available.")
    
    with tab3:
        st.subheader("GENERATE DRIVER LETTER")
        
        drivers = pd.read_sql("SELECT driver_name FROM drivers", conn)
        
        if not drivers.empty:
            driver = st.selectbox("SELECT DRIVER FOR LETTER", drivers['driver_name'].tolist())
            
            # Calculate driver details
            driver_info = conn.execute(
                "SELECT * FROM drivers WHERE driver_name = ?", (driver,)
            ).fetchone()
            
            driver_earnings = conn.execute(
                "SELECT SUM(amount) FROM payments WHERE driver_name = ?", (driver,)
            ).fetchone()[0] or 0
            
            driver_paid = conn.execute(
                "SELECT SUM(amount) FROM driver_payments WHERE driver_name = ?", (driver,)
            ).fetchone()[0] or 0
            
            unpaid_balance = driver_earnings - driver_paid
            
            # Generate letter
            if st.button("GENERATE LETTER", use_container_width=True):
                letter = f"""
                TAXI MANAGEMENT SYSTEM
                DRIVER PAYMENT STATEMENT
                Date: {datetime.now().strftime('%d/%m/%Y')}
                
                Driver Name: {driver}
                Phone: {driver_info[2] if driver_info else 'N/A'}
                License: {driver_info[3] if driver_info else 'N/A'}
                
                SUMMARY:
                --------------
                Total Earnings: ₹{driver_earnings:,.0f}
                Total Paid: ₹{driver_paid:,.0f}
                Current Balance: ₹{unpaid_balance:,.0f}
                
                STATUS: {"PENDING PAYMENT" if unpaid_balance > 0 else "PAID IN FULL"}
                
                Please review the above statement. Contact us for any discrepancies.
                
                Thank you,
                Taxi Management Team
                """
                
                st.text_area("DRIVER LETTER", letter, height=400)
                
                # Download button
                st.download_button(
                    "DOWNLOAD LETTER",
                    letter,
                    f"{driver}_statement_{datetime.now().strftime('%Y%m%d')}.txt",
                    "text/plain"
                )
        else:
            st.info("No drivers registered yet.")

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; font-size: 20px;'>TAXI MANAGER - MOBILE APP</div>", unsafe_allow_html=True)
