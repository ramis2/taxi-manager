# app.py - Taxi Manager with Payments and Car Types (Fixed)
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import io

# Set page configuration
st.set_page_config(
    page_title="Taxi Manager",
    layout="wide"
)

# Initialize database
def init_db():
    conn = sqlite3.connect('taxi_manager.db')
    c = conn.cursor()
    
    # Drivers table with car type
    c.execute('''
        CREATE TABLE IF NOT EXISTS drivers (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT,
            vehicle_number TEXT,
            vehicle_type TEXT,
            license_number TEXT,
            join_date TEXT,
            status TEXT DEFAULT 'Active',
            total_trips INTEGER DEFAULT 0,
            total_earnings REAL DEFAULT 0,
            address TEXT,
            email TEXT,
            salary REAL DEFAULT 0,
            commission_rate REAL DEFAULT 0.15
        )
    ''')
    
    # Payments table
    c.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            driver_id TEXT,
            payment_date TEXT,
            amount REAL,
            payment_type TEXT,
            description TEXT,
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY (driver_id) REFERENCES drivers (id)
        )
    ''')
    
    # Car maintenance table
    c.execute('''
        CREATE TABLE IF NOT EXISTS maintenance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_number TEXT,
            vehicle_type TEXT,
            maintenance_date TEXT,
            service_type TEXT,
            cost REAL,
            description TEXT,
            next_service TEXT,
            status TEXT DEFAULT 'Completed'
        )
    ''')
    
    # Settings table
    c.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    
    default_settings = [
        ('company_name', 'Taxi Manager'),
        ('fare_per_km', '50'),
        ('currency', 'INR'),
        ('report_email', 'admin@taximanager.com'),
        ('company_address', '123 Taxi Street, Mumbai'),
        ('company_phone', '+91 22 12345678'),
        ('manager_name', 'Mr. Raj Sharma')
    ]
    
    c.executemany('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', default_settings)
    conn.commit()
    conn.close()

# Initialize session state
if 'edit_driver_id' not in st.session_state:
    st.session_state.edit_driver_id = None
if 'delete_confirm' not in st.session_state:
    st.session_state.delete_confirm = None
if 'current_payment_id' not in st.session_state:
    st.session_state.current_payment_id = None
if 'current_maintenance_id' not in st.session_state:
    st.session_state.current_maintenance_id = None
if 'report_data' not in st.session_state:
    st.session_state.report_data = None

init_db()

# Database functions
def get_db_connection():
    return sqlite3.connect('taxi_manager.db')

def get_drivers():
    conn = get_db_connection()
    df = pd.read_sql('SELECT * FROM drivers ORDER BY name', conn)
    conn.close()
    return df

def get_driver_by_id(driver_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM drivers WHERE id = ?', (driver_id,))
    driver = c.fetchone()
    conn.close()
    return driver

def add_driver(driver_data):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO drivers (id, name, phone, vehicle_number, vehicle_type, license_number, join_date, address, email, salary, commission_rate) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', driver_data)
    conn.commit()
    conn.close()

def update_driver(driver_id, update_data):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('UPDATE drivers SET name=?, phone=?, vehicle_number=?, vehicle_type=?, license_number=?, address=?, email=?, salary=?, commission_rate=? WHERE id=?', (*update_data, driver_id))
    conn.commit()
    conn.close()

def delete_driver(driver_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('DELETE FROM drivers WHERE id = ?', (driver_id,))
    conn.commit()
    conn.close()

# Payments functions
def get_payments():
    conn = get_db_connection()
    df = pd.read_sql('''
        SELECT p.*, d.name as driver_name 
        FROM payments p 
        LEFT JOIN drivers d ON p.driver_id = d.id 
        ORDER BY p.payment_date DESC
    ''', conn)
    conn.close()
    return df

def get_payment_by_id(payment_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM payments WHERE id = ?', (payment_id,))
    payment = c.fetchone()
    conn.close()
    return payment

def add_payment(payment_data):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO payments (driver_id, payment_date, amount, payment_type, description, status) VALUES (?, ?, ?, ?, ?, ?)', payment_data)
    conn.commit()
    conn.close()

def update_payment(payment_id, payment_data):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('UPDATE payments SET driver_id=?, payment_date=?, amount=?, payment_type=?, description=?, status=? WHERE id=?', (*payment_data, payment_id))
    conn.commit()
    conn.close()

def delete_payment(payment_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('DELETE FROM payments WHERE id = ?', (payment_id,))
    conn.commit()
    conn.close()

# Maintenance functions
def get_maintenance():
    conn = get_db_connection()
    df = pd.read_sql('SELECT * FROM maintenance ORDER BY maintenance_date DESC', conn)
    conn.close()
    return df

def get_maintenance_by_id(maintenance_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM maintenance WHERE id = ?', (maintenance_id,))
    maintenance = c.fetchone()
    conn.close()
    return maintenance

def add_maintenance(maintenance_data):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO maintenance (vehicle_number, vehicle_type, maintenance_date, service_type, cost, description, next_service, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', maintenance_data)
    conn.commit()
    conn.close()

def update_maintenance(maintenance_id, maintenance_data):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('UPDATE maintenance SET vehicle_number=?, vehicle_type=?, maintenance_date=?, service_type=?, cost=?, description=?, next_service=?, status=? WHERE id=?', (*maintenance_data, maintenance_id))
    conn.commit()
    conn.close()

def delete_maintenance(maintenance_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('DELETE FROM maintenance WHERE id = ?', (maintenance_id,))
    conn.commit()
    conn.close()

def get_settings():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT key, value FROM settings')
    settings = dict(c.fetchall())
    conn.close()
    return settings

def update_settings(settings_dict):
    conn = get_db_connection()
    c = conn.cursor()
    for key, value in settings_dict.items():
        c.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, value))
    conn.commit()
    conn.close()

# Sidebar Navigation
st.sidebar.title("TAXI MANAGER")
st.sidebar.divider()

menu = st.sidebar.radio(
    "NAVIGATION",
    ["DASHBOARD", "DRIVERS", "PAYMENTS", "MAINTENANCE", "REPORTS", "SETTINGS"]
)

# Dashboard Page
if menu == "DASHBOARD":
    st.title("DASHBOARD")
    
    drivers_df = get_drivers()
    payments_df = get_payments()
    maintenance_df = get_maintenance()
    
    # Key Metrics - Row 1
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        active_drivers = len(drivers_df[drivers_df['status'] == 'Active']) if not drivers_df.empty else 0
        st.metric(
            label="TOTAL DRIVERS",
            value=len(drivers_df),
            delta=f"+{active_drivers} Active"
        )
    
    with col2:
        total_earnings = drivers_df['total_earnings'].sum() if not drivers_df.empty else 0
        st.metric(
            label="TOTAL EARNINGS",
            value=f"₹{total_earnings:,.2f}",
            delta="This Month"
        )
    
    with col3:
        total_payments = payments_df['amount'].sum() if not payments_df.empty else 0
        st.metric(
            label="TOTAL PAYMENTS",
            value=f"₹{total_payments:,.2f}",
            delta="This Month"
        )
    
    with col4:
        total_maintenance = maintenance_df['cost'].sum() if not maintenance_df.empty else 0
        st.metric(
            label="MAINTENANCE COST",
            value=f"₹{total_maintenance:,.2f}",
            delta_color="inverse"
        )
    
    # Key Metrics - Row 2
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        pending_payments = payments_df[payments_df['status'] == 'Pending']['amount'].sum() if not payments_df.empty else 0
        st.metric(
            label="PENDING PAYMENTS",
            value=f"₹{pending_payments:,.2f}",
            delta_color="inverse"
        )
    
    with col2:
        total_trips = drivers_df['total_trips'].sum() if not drivers_df.empty else 0
        st.metric(
            label="TOTAL TRIPS",
            value=total_trips,
            delta="This Month"
        )
    
    with col3:
        upcoming_maintenance = len(maintenance_df[maintenance_df['status'] == 'Scheduled']) if not maintenance_df.empty else 0
        st.metric(
            label="UPCOMING SERVICES",
            value=upcoming_maintenance,
            delta_color="inverse"
        )
    
    with col4:
        net_profit = total_earnings - total_payments - total_maintenance
        st.metric(
            label="NET PROFIT",
            value=f"₹{net_profit:,.2f}",
            delta_color="normal" if net_profit >= 0 else "inverse"
        )
    
    st.divider()
    
    # Quick Actions
    st.subheader("QUICK ACTIONS")
    qcol1, qcol2, qcol3, qcol4 = st.columns(4)
    
    with qcol1:
        if st.button("ADD DRIVER", use_container_width=True, type="primary"):
            st.session_state.edit_driver_id = 'new'
            st.rerun()
    
    with qcol2:
        if st.button("ADD PAYMENT", use_container_width=True):
            st.session_state.current_payment_id = 'new'
            st.rerun()
    
    with qcol3:
        if st.button("ADD MAINTENANCE", use_container_width=True):
            st.session_state.current_maintenance_id = 'new'
            st.rerun()
    
    with qcol4:
        if st.button("VIEW REPORTS", use_container_width=True):
            st.session_state.page = 'reports'
            st.rerun()
    
    st.divider()
    
    # Recent Activity
    st.subheader("RECENT ACTIVITY")
    
    tab1, tab2, tab3 = st.tabs(["RECENT DRIVERS", "RECENT PAYMENTS", "RECENT MAINTENANCE"])
    
    with tab1:
        if not drivers_df.empty:
            recent_drivers = drivers_df[['id', 'name', 'vehicle_number', 'vehicle_type', 'status']].head(5)
            st.dataframe(recent_drivers, use_container_width=True)
        else:
            st.info("No drivers found")
    
    with tab2:
        if not payments_df.empty:
            recent_payments = payments_df[['driver_name', 'amount', 'payment_type', 'payment_date', 'status']].head(5)
            st.dataframe(recent_payments, use_container_width=True)
        else:
            st.info("No payments found")
    
    with tab3:
        if not maintenance_df.empty:
            recent_maintenance = maintenance_df[['vehicle_number', 'service_type', 'cost', 'maintenance_date', 'status']].head(5)
            st.dataframe(recent_maintenance, use_container_width=True)
        else:
            st.info("No maintenance records found")

# Drivers Management Page
elif menu == "DRIVERS":
    st.title("DRIVER MANAGEMENT")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_term = st.text_input("SEARCH DRIVERS", placeholder="Enter name or ID...")
    
    with col2:
        if st.button("ADD DRIVER", type="primary", use_container_width=True):
            st.session_state.edit_driver_id = 'new'
            st.rerun()
    
    with col3:
        if st.button("EXPORT DATA", use_container_width=True):
            drivers_df = get_drivers()
            if not drivers_df.empty:
                csv = drivers_df.to_csv(index=False)
                st.download_button(
                    label="DOWNLOAD CSV",
                    data=csv,
                    file_name=f"drivers_export_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    key="export_drivers"
                )
    
    st.divider()
    
    drivers_df = get_drivers()
    
    if search_term:
        mask = drivers_df['name'].str.contains(search_term, case=False) | drivers_df['id'].str.contains(search_term, case=False)
        drivers_df = drivers_df[mask]
    
    if not drivers_df.empty:
        for _, driver in drivers_df.iterrows():
            with st.container():
                cols = st.columns([1, 2, 2, 2, 2, 3])
                
                with cols[0]:
                    st.write(f"**{driver['id']}**")
                
                with cols[1]:
                    st.write(driver['name'])
                    st.write(driver['phone'])
                
                with cols[2]:
                    st.write(f"Vehicle: {driver['vehicle_number']}")
                    st.write(f"Type: {driver.get('vehicle_type', 'N/A')}")
                
                with cols[3]:
                    status_text = f"[ACTIVE]" if driver['status'] == 'Active' else f"[INACTIVE]"
                    st.write(status_text)
                    st.write(f"Trips: {driver['total_trips']}")
                
                with cols[4]:
                    st.write(f"Earnings: ₹{driver['total_earnings']:,.2f}")
                    st.write(f"Salary: ₹{driver.get('salary', 0):,.2f}")
                
                with cols[5]:
                    col_btn1, col_btn2, col_btn3 = st.columns(3)
                    with col_btn1:
                        if st.button("EDIT", key=f"edit_{driver['id']}", use_container_width=True):
                            st.session_state.edit_driver_id = driver['id']
                            st.rerun()
                    with col_btn2:
                        if st.button("ADD PAYMENT", key=f"pay_{driver['id']}", use_container_width=True):
                            st.session_state.current_payment_id = 'new'
                            st.session_state.selected_driver_for_payment = driver['id']
                            st.rerun()
                    with col_btn3:
                        if st.button("DELETE", key=f"del_{driver['id']}", use_container_width=True):
                            st.session_state.delete_confirm = driver['id']
                            st.rerun()
                
                st.divider()
    else:
        st.info("No drivers found. Add your first driver!")
    
    # Add/Edit Driver Form
    if st.session_state.edit_driver_id:
        st.subheader("ADD NEW DRIVER" if st.session_state.edit_driver_id == 'new' else "EDIT DRIVER")
        
        with st.form(key="driver_form"):
            # Vehicle types
            vehicle_types = ["SEDAN", "HATCHBACK", "SUV", "MINI VAN", "LUXURY", "AUTO RICKSHAW", "BIKE"]
            
            if st.session_state.edit_driver_id == 'new':
                driver_id = st.text_input("DRIVER ID*", placeholder="DRV001")
                name = st.text_input("FULL NAME*", placeholder="John Doe")
                phone = st.text_input("PHONE NUMBER*", placeholder="+91 9876543210")
                vehicle = st.text_input("VEHICLE NUMBER*", placeholder="MH01AB1234")
                vehicle_type = st.selectbox("VEHICLE TYPE", vehicle_types)
                license = st.text_input("LICENSE NUMBER", placeholder="DL123456789")
                address = st.text_area("ADDRESS", placeholder="Full postal address")
                email = st.text_input("EMAIL", placeholder="driver@email.com")
                salary = st.number_input("MONTHLY SALARY (₹)", value=15000.0, step=1000.0)
                commission = st.number_input("COMMISSION RATE (%)", value=15.0, step=0.5, min_value=0.0, max_value=100.0)
            else:
                driver_data = get_driver_by_id(st.session_state.edit_driver_id)
                driver_id = st.text_input("DRIVER ID*", value=driver_data[0], disabled=True)
                name = st.text_input("FULL NAME*", value=driver_data[1])
                phone = st.text_input("PHONE NUMBER*", value=driver_data[2])
                vehicle = st.text_input("VEHICLE NUMBER*", value=driver_data[3])
                vehicle_type = st.selectbox("VEHICLE TYPE", vehicle_types, index=vehicle_types.index(driver_data[4]) if driver_data[4] in vehicle_types else 0)
                license = st.text_input("LICENSE NUMBER", value=driver_data[5])
                address = st.text_area("ADDRESS", value=driver_data[9] if len(driver_data) > 9 else "")
                email = st.text_input("EMAIL", value=driver_data[10] if len(driver_data) > 10 else "")
                salary = st.number_input("MONTHLY SALARY (₹)", value=driver_data[11] if len(driver_data) > 11 else 15000.0, step=1000.0)
                commission = st.number_input("COMMISSION RATE (%)", value=driver_data[12] if len(driver_data) > 12 else 15.0, step=0.5)
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("SAVE DRIVER", type="primary", use_container_width=True)
            with col2:
                cancel = st.form_submit_button("CANCEL", use_container_width=True)
            
            if submit:
                if not all([driver_id, name, phone, vehicle]):
                    st.error("Please fill all required fields (*)")
                else:
                    try:
                        if st.session_state.edit_driver_id == 'new':
                            add_driver((driver_id, name, phone, vehicle, vehicle_type, license, datetime.now().strftime("%Y-%m-%d"), address, email, salary, commission/100))
                            st.success(f"Driver {name} added successfully!")
                        else:
                            update_driver(driver_id, (name, phone, vehicle, vehicle_type, license, address, email, salary, commission/100))
                            st.success(f"Driver {name} updated successfully!")
                        
                        st.session_state.edit_driver_id = None
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            
            if cancel:
                st.session_state.edit_driver_id = None
                st.rerun()
    
    # Delete Confirmation
    if st.session_state.delete_confirm:
        st.warning("CONFIRM DELETION")
        driver_data = get_driver_by_id(st.session_state.delete_confirm)
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write(f"Delete driver **{driver_data[1]}** (ID: {driver_data[0]})?")
        with col2:
            if st.button("YES, DELETE", type="primary", use_container_width=True):
                delete_driver(st.session_state.delete_confirm)
                st.success("Driver deleted successfully!")
                st.session_state.delete_confirm = None
                st.rerun()
        with col3:
            if st.button("CANCEL", use_container_width=True):
                st.session_state.delete_confirm = None
                st.rerun()

# PAYMENTS PAGE
elif menu == "PAYMENTS":
    st.title("PAYMENTS MANAGEMENT")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_term = st.text_input("SEARCH PAYMENTS", placeholder="Search by driver name or ID...")
    
    with col2:
        if st.button("ADD PAYMENT", type="primary", use_container_width=True):
            st.session_state.current_payment_id = 'new'
            st.rerun()
    
    with col3:
        if st.button("EXPORT DATA", use_container_width=True):
            payments_df = get_payments()
            if not payments_df.empty:
                csv = payments_df.to_csv(index=False)
                st.download_button(
                    label="DOWNLOAD CSV",
                    data=csv,
                    file_name=f"payments_export_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    key="export_payments"
                )
    
    st.divider()
    
    payments_df = get_payments()
    
    if not payments_df.empty:
        # Summary stats
        total_paid = payments_df[payments_df['status'] == 'Paid']['amount'].sum()
        total_pending = payments_df[payments_df['status'] == 'Pending']['amount'].sum()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("TOTAL PAYMENTS", f"₹{payments_df['amount'].sum():,.2f}")
        with col2:
            st.metric("PAID", f"₹{total_paid:,.2f}")
        with col3:
            st.metric("PENDING", f"₹{total_pending:,.2f}")
        
        st.divider()
        
        # Payments list
        st.subheader("PAYMENT HISTORY")
        
        for _, payment in payments_df.iterrows():
            with st.container():
                cols = st.columns([2, 1, 1, 1, 1, 1])
                
                with cols[0]:
                    st.write(f"**{payment['driver_name']}** ({payment['driver_id']})")
                    st.write(payment['description'])
                
                with cols[1]:
                    st.write(f"₹{payment['amount']:,.2f}")
                
                with cols[2]:
                    st.write(payment['payment_type'])
                
                with cols[3]:
                    st.write(payment['payment_date'])
                
                with cols[4]:
                    status_color = "green" if payment['status'] == 'Paid' else "orange"
                    st.write(f"<span style='color:{status_color}'><b>{payment['status']}</b></span>", unsafe_allow_html=True)
                
                with cols[5]:
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button("EDIT", key=f"edit_pay_{payment['id']}", use_container_width=True):
                            st.session_state.current_payment_id = payment['id']
                            st.rerun()
                    with col_btn2:
                        if st.button("DELETE", key=f"del_pay_{payment['id']}", use_container_width=True):
                            delete_payment(payment['id'])
                            st.success("Payment deleted!")
                            st.rerun()
                
                st.divider()
    else:
        st.info("No payments found. Add your first payment!")
    
    # Add/Edit Payment Form
    if st.session_state.current_payment_id:
        st.subheader("ADD NEW PAYMENT" if st.session_state.current_payment_id == 'new' else "EDIT PAYMENT")
        
        drivers_df = get_drivers()
        
        with st.form(key="payment_form"):
            if st.session_state.current_payment_id == 'new':
                # Auto-select driver if coming from driver page
                if hasattr(st.session_state, 'selected_driver_for_payment') and st.session_state.selected_driver_for_payment:
                    default_driver = st.session_state.selected_driver_for_payment
                else:
                    default_driver = None
                
                driver_options = list(drivers_df['id'].unique())
                driver_names = {row['id']: row['name'] for _, row in drivers_df.iterrows()}
                
                selected_driver = st.selectbox(
                    "SELECT DRIVER*",
                    driver_options,
                    format_func=lambda x: f"{x} - {driver_names.get(x, 'Unknown')}",
                    index=driver_options.index(default_driver) if default_driver in driver_options else 0
                )
                
                payment_date = st.date_input("PAYMENT DATE*", value=datetime.now())
                amount = st.number_input("AMOUNT (₹)*", value=0.0, step=100.0)
                payment_type = st.selectbox("PAYMENT TYPE*", ["SALARY", "BONUS", "ADVANCE", "COMMISSION", "REIMBURSEMENT", "OTHER"])
                description = st.text_input("DESCRIPTION", placeholder="Payment for monthly salary...")
                status = st.selectbox("STATUS", ["Pending", "Paid"])
            else:
                payment_data = get_payment_by_id(st.session_state.current_payment_id)
                selected_driver = st.text_input("DRIVER ID", value=payment_data[1] if payment_data else "")
                payment_date = st.date_input("PAYMENT DATE", value=datetime.strptime(payment_data[2], "%Y-%m-%d") if payment_data and payment_data[2] else datetime.now())
                amount = st.number_input("AMOUNT (₹)", value=payment_data[3] if payment_data else 0.0)
                payment_type = st.selectbox("PAYMENT TYPE", ["SALARY", "BONUS", "ADVANCE", "COMMISSION", "REIMBURSEMENT", "OTHER"], 
                                           index=["SALARY", "BONUS", "ADVANCE", "COMMISSION", "REIMBURSEMENT", "OTHER"].index(payment_data[4]) if payment_data and payment_data[4] in ["SALARY", "BONUS", "ADVANCE", "COMMISSION", "REIMBURSEMENT", "OTHER"] else 0)
                description = st.text_input("DESCRIPTION", value=payment_data[5] if payment_data else "")
                status = st.selectbox("STATUS", ["Pending", "Paid"], index=1 if payment_data and payment_data[6] == 'Paid' else 0)
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("SAVE PAYMENT", type="primary", use_container_width=True)
            with col2:
                cancel = st.form_submit_button("CANCEL", use_container_width=True)
            
            if submit:
                if not all([selected_driver, amount > 0]):
                    st.error("Please fill all required fields (*)")
                else:
                    try:
                        if st.session_state.current_payment_id == 'new':
                            add_payment((selected_driver, payment_date.strftime("%Y-%m-%d"), amount, payment_type, description, status))
                            st.success("Payment added successfully!")
                        else:
                            update_payment(st.session_state.current_payment_id, (selected_driver, payment_date.strftime("%Y-%m-%d"), amount, payment_type, description, status))
                            st.success("Payment updated successfully!")
                        
                        # Clear session state
                        if hasattr(st.session_state, 'selected_driver_for_payment'):
                            del st.session_state.selected_driver_for_payment
                        st.session_state.current_payment_id = None
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            
            if cancel:
                st.session_state.current_payment_id = None
                if hasattr(st.session_state, 'selected_driver_for_payment'):
                    del st.session_state.selected_driver_for_payment
                st.rerun()

# MAINTENANCE PAGE
elif menu == "MAINTENANCE":
    st.title("CAR MAINTENANCE")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_term = st.text_input("SEARCH MAINTENANCE", placeholder="Search by vehicle number...")
    
    with col2:
        if st.button("ADD MAINTENANCE", type="primary", use_container_width=True):
            st.session_state.current_maintenance_id = 'new'
            st.rerun()
    
    with col3:
        if st.button("EXPORT DATA", use_container_width=True):
            maintenance_df = get_maintenance()
            if not maintenance_df.empty:
                csv = maintenance_df.to_csv(index=False)
                st.download_button(
                    label="DOWNLOAD CSV",
                    data=csv,
                    file_name=f"maintenance_export_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    key="export_maintenance"
                )
    
    st.divider()
    
    maintenance_df = get_maintenance()
    
    if not maintenance_df.empty:
        # Summary stats
        total_cost = maintenance_df['cost'].sum()
        upcoming = len(maintenance_df[maintenance_df['status'] == 'Scheduled'])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("TOTAL MAINTENANCE COST", f"₹{total_cost:,.2f}")
        with col2:
            st.metric("TOTAL SERVICES", len(maintenance_df))
        with col3:
            st.metric("UPCOMING SERVICES", upcoming)
        
        st.divider()
        
        # Maintenance list
        st.subheader("MAINTENANCE HISTORY")
        
        for _, maint in maintenance_df.iterrows():
            with st.container():
                cols = st.columns([2, 1, 1, 1, 1, 1])
                
                with cols[0]:
                    st.write(f"**{maint['vehicle_number']}**")
                    st.write(f"Type: {maint.get('vehicle_type', 'N/A')}")
                    st.write(maint['description'])
                
                with cols[1]:
                    st.write(f"₹{maint['cost']:,.2f}")
                
                with cols[2]:
                    st.write(maint['service_type'])
                
                with cols[3]:
                    st.write(maint['maintenance_date'])
                
                with cols[4]:
                    st.write(f"Next: {maint['next_service']}")
                    status_color = "green" if maint['status'] == 'Completed' else "orange"
                    st.write(f"<span style='color:{status_color}'><b>{maint['status']}</b></span>", unsafe_allow_html=True)
                
                with cols[5]:
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button("EDIT", key=f"edit_maint_{maint['id']}", use_container_width=True):
                            st.session_state.current_maintenance_id = maint['id']
                            st.rerun()
                    with col_btn2:
                        if st.button("DELETE", key=f"del_maint_{maint['id']}", use_container_width=True):
                            delete_maintenance(maint['id'])
                            st.success("Maintenance record deleted!")
                            st.rerun()
                
                st.divider()
    else:
        st.info("No maintenance records found. Add your first record!")
    
    # Add/Edit Maintenance Form
    if st.session_state.current_maintenance_id:
        st.subheader("ADD MAINTENANCE" if st.session_state.current_maintenance_id == 'new' else "EDIT MAINTENANCE")
        
        drivers_df = get_drivers()
        vehicle_types = ["SEDAN", "HATCHBACK", "SUV", "MINI VAN", "LUXURY", "AUTO RICKSHAW", "BIKE"]
        service_types = ["OIL CHANGE", "TIRE REPLACEMENT", "BRAKE SERVICE", "ENGINE REPAIR", 
                        "AC SERVICE", "BATTERY REPLACEMENT", "GENERAL SERVICE", "INSURANCE", "OTHER"]
        
        with st.form(key="maintenance_form"):
            if st.session_state.current_maintenance_id == 'new':
                # Get unique vehicles from drivers
                vehicles = list(drivers_df['vehicle_number'].unique())
                vehicle_options = vehicles + ["OTHER"]
                
                vehicle_number = st.selectbox("VEHICLE NUMBER*", vehicle_options)
                if vehicle_number == "OTHER":
                    vehicle_number = st.text_input("ENTER VEHICLE NUMBER", placeholder="Enter vehicle number...")
                
                vehicle_type = st.selectbox("VEHICLE TYPE", vehicle_types)
                maintenance_date = st.date_input("SERVICE DATE*", value=datetime.now())
                service_type = st.selectbox("SERVICE TYPE*", service_types)
                cost = st.number_input("COST (₹)*", value=0.0, step=100.0)
                description = st.text_area("DESCRIPTION", placeholder="Details of service...")
                next_service = st.date_input("NEXT SERVICE DATE", value=datetime.now() + timedelta(days=90))
                status = st.selectbox("STATUS", ["Completed", "Scheduled", "In Progress"])
            else:
                maint_data = get_maintenance_by_id(st.session_state.current_maintenance_id)
                vehicle_number = st.text_input("VEHICLE NUMBER*", value=maint_data[1] if maint_data else "")
                vehicle_type = st.selectbox("VEHICLE TYPE", vehicle_types, index=vehicle_types.index(maint_data[2]) if maint_data and maint_data[2] in vehicle_types else 0)
                maintenance_date = st.date_input("SERVICE DATE", value=datetime.strptime(maint_data[3], "%Y-%m-%d") if maint_data and maint_data[3] else datetime.now())
                service_type = st.selectbox("SERVICE TYPE", service_types, index=service_types.index(maint_data[4]) if maint_data and maint_data[4] in service_types else 0)
                cost = st.number_input("COST (₹)", value=maint_data[5] if maint_data else 0.0)
                description = st.text_area("DESCRIPTION", value=maint_data[6] if maint_data else "")
                next_service = st.date_input("NEXT SERVICE DATE", value=datetime.strptime(maint_data[7], "%Y-%m-%d") if maint_data and maint_data[7] else datetime.now())
                status = st.selectbox("STATUS", ["Completed", "Scheduled", "In Progress"], index=["Completed", "Scheduled", "In Progress"].index(maint_data[8]) if maint_data and maint_data[8] in ["Completed", "Scheduled", "In Progress"] else 0)
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("SAVE MAINTENANCE", type="primary", use_container_width=True)
            with col2:
                cancel = st.form_submit_button("CANCEL", use_container_width=True)
            
            if submit:
                if not all([vehicle_number, cost > 0]):
                    st.error("Please fill all required fields (*)")
                else:
                    try:
                        if st.session_state.current_maintenance_id == 'new':
                            add_maintenance((vehicle_number, vehicle_type, maintenance_date.strftime("%Y-%m-%d"), service_type, cost, description, next_service.strftime("%Y-%m-%d"), status))
                            st.success("Maintenance record added successfully!")
                        else:
                            update_maintenance(st.session_state.current_maintenance_id, (vehicle_number, vehicle_type, maintenance_date.strftime("%Y-%m-%d"), service_type, cost, description, next_service.strftime("%Y-%m-%d"), status))
                            st.success("Maintenance record updated successfully!")
                        
                        st.session_state.current_maintenance_id = None
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            
            if cancel:
                st.session_state.current_maintenance_id = None
                st.rerun()

# REPORTS PAGE (FIXED - No download buttons inside forms)
elif menu == "REPORTS":
    st.title("REPORTS & ANALYTICS")
    
    report_type = st.selectbox(
        "SELECT REPORT TYPE",
        ["FINANCIAL SUMMARY", "DRIVER PERFORMANCE", "PAYMENTS REPORT", 
         "MAINTENANCE REPORT", "VEHICLE ANALYSIS", "COMPLETE EXPORT"]
    )
    
    drivers_df = get_drivers()
    payments_df = get_payments()
    maintenance_df = get_maintenance()
    
    # Store data in session state for download
    if report_type == "FINANCIAL SUMMARY":
        st.subheader("FINANCIAL SUMMARY REPORT")
        
        # Calculate financial metrics
        total_earnings = drivers_df['total_earnings'].sum() if not drivers_df.empty else 0
        total_payments = payments_df['amount'].sum() if not payments_df.empty else 0
        total_maintenance = maintenance_df['cost'].sum() if not maintenance_df.empty else 0
        net_profit = total_earnings - total_payments - total_maintenance
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("TOTAL EARNINGS", f"₹{total_earnings:,.2f}")
        with col2:
            st.metric("TOTAL PAYMENTS", f"₹{total_payments:,.2f}")
        with col3:
            st.metric("MAINTENANCE COST", f"₹{total_maintenance:,.2f}")
        with col4:
            st.metric("NET PROFIT", f"₹{net_profit:,.2f}", 
                     delta_color="normal" if net_profit >= 0 else "inverse")
        
        # Create summary dataframe
        summary_data = {
            'Metric': ['Total Earnings', 'Total Payments', 'Maintenance Cost', 'Net Profit'],
            'Amount (₹)': [total_earnings, total_payments, total_maintenance, net_profit]
        }
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True)
        
        # Store for download
        st.session_state.report_data = summary_df
    
    elif report_type == "DRIVER PERFORMANCE":
        st.subheader("DRIVER PERFORMANCE REPORT")
        
        if not drivers_df.empty:
            performance_df = drivers_df[['id', 'name', 'vehicle_type', 'total_trips', 
                                        'total_earnings', 'salary', 'status']].copy()
            performance_df['avg_per_trip'] = performance_df['total_earnings'] / performance_df['total_trips'].replace(0, 1)
            performance_df = performance_df.round(2)
            
            st.dataframe(performance_df, use_container_width=True)
            
            # Store for download
            st.session_state.report_data = performance_df
        else:
            st.info("No drivers found")
            st.session_state.report_data = None
    
    elif report_type == "PAYMENTS REPORT":
        st.subheader("PAYMENTS REPORT")
        
        if not payments_df.empty:
            st.dataframe(payments_df, use_container_width=True)
            
            # Store for download
            st.session_state.report_data = payments_df
        else:
            st.info("No payments found")
            st.session_state.report_data = None
    
    elif report_type == "MAINTENANCE REPORT":
        st.subheader("MAINTENANCE REPORT")
        
        if not maintenance_df.empty:
            st.dataframe(maintenance_df, use_container_width=True)
            
            # Store for download
            st.session_state.report_data = maintenance_df
        else:
            st.info("No maintenance records found")
            st.session_state.report_data = None
    
    elif report_type == "VEHICLE ANALYSIS":
        st.subheader("VEHICLE ANALYSIS REPORT")
        
        if not drivers_df.empty:
            # Group by vehicle type
            vehicle_analysis = drivers_df.groupby('vehicle_type').agg({
                'id': 'count',
                'total_trips': 'sum',
                'total_earnings': 'sum'
            }).reset_index()
            vehicle_analysis.columns = ['Vehicle Type', 'Count', 'Total Trips', 'Total Earnings']
            vehicle_analysis['Avg Earnings per Vehicle'] = vehicle_analysis['Total Earnings'] / vehicle_analysis['Count']
            vehicle_analysis = vehicle_analysis.round(2)
            
            st.dataframe(vehicle_analysis, use_container_width=True)
            
            # Store for download
            st.session_state.report_data = vehicle_analysis
        else:
            st.info("No drivers found")
            st.session_state.report_data = None
    
    elif report_type == "COMPLETE EXPORT":
        st.subheader("COMPLETE DATA EXPORT")
        
        tab1, tab2, tab3 = st.tabs(["DRIVERS", "PAYMENTS", "MAINTENANCE"])
        
        with tab1:
            if not drivers_df.empty:
                st.dataframe(drivers_df, use_container_width=True)
            else:
                st.info("No drivers found")
        
        with tab2:
            if not payments_df.empty:
                st.dataframe(payments_df, use_container_width=True)
            else:
                st.info("No payments found")
        
        with tab3:
            if not maintenance_df.empty:
                st.dataframe(maintenance_df, use_container_width=True)
            else:
                st.info("No maintenance records found")
        
        # Store all data
        st.session_state.report_data = {
            'drivers': drivers_df,
            'payments': payments_df,
            'maintenance': maintenance_df
        }
    
    # Download button (OUTSIDE any form)
    if st.session_state.report_data is not None:
        st.divider()
        
        if report_type == "COMPLETE EXPORT":
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if not drivers_df.empty:
                    csv = drivers_df.to_csv(index=False)
                    st.download_button(
                        label="DOWNLOAD DRIVERS CSV",
                        data=csv,
                        file_name=f"drivers_export_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
            
            with col2:
                if not payments_df.empty:
                    csv = payments_df.to_csv(index=False)
                    st.download_button(
                        label="DOWNLOAD PAYMENTS CSV",
                        data=csv,
                        file_name=f"payments_export_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
            
            with col3:
                if not maintenance_df.empty:
                    csv = maintenance_df.to_csv(index=False)
                    st.download_button(
                        label="DOWNLOAD MAINTENANCE CSV",
                        data=csv,
                        file_name=f"maintenance_export_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
        else:
            # Single report download
            csv = st.session_state.report_data.to_csv(index=False)
            st.download_button(
                label="DOWNLOAD REPORT AS CSV",
                data=csv,
                file_name=f"{report_type.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

# SETTINGS PAGE
elif menu == "SETTINGS":
    st.title("SETTINGS")
    
    current_settings = get_settings()
    
    with st.form(key="settings_form"):
        st.subheader("COMPANY SETTINGS")
        
        col1, col2 = st.columns(2)
        with col1:
            company_name = st.text_input("COMPANY NAME", value=current_settings.get('company_name', ''))
            fare_per_km = st.number_input("FARE PER KM (₹)", value=float(current_settings.get('fare_per_km', 50)))
            company_address = st.text_area("COMPANY ADDRESS", value=current_settings.get('company_address', ''))
        
        with col2:
            manager_name = st.text_input("MANAGER NAME", value=current_settings.get('manager_name', ''))
            company_phone = st.text_input("COMPANY PHONE", value=current_settings.get('company_phone', ''))
            report_email = st.text_input("REPORT EMAIL", value=current_settings.get('report_email', ''))
        
        st.subheader("FINANCIAL SETTINGS")
        col1, col2 = st.columns(2)
        with col1:
            default_salary = st.number_input("DEFAULT MONTHLY SALARY (₹)", value=15000.0, step=1000.0)
            default_commission = st.number_input("DEFAULT COMMISSION RATE (%)", value=15.0, step=0.5)
        
        with col2:
            tax_rate = st.number_input("TAX RATE (%)", value=18.0, step=0.5)
            insurance_rate = st.number_input("INSURANCE RATE (%)", value=5.0, step=0.5)
        
        col1, col2 = st.columns(2)
        with col1:
            save = st.form_submit_button("SAVE SETTINGS", type="primary", use_container_width=True)
        with col2:
            reset = st.form_submit_button("RESET TO DEFAULTS", use_container_width=True)
        
        if save:
            new_settings = {
                'company_name': company_name,
                'fare_per_km': str(fare_per_km),
                'company_address': company_address,
                'manager_name': manager_name,
                'company_phone': company_phone,
                'report_email': report_email,
                'default_salary': str(default_salary),
                'default_commission': str(default_commission),
                'tax_rate': str(tax_rate),
                'insurance_rate': str(insurance_rate)
            }
            update_settings(new_settings)
            st.success("Settings saved successfully!")
            st.rerun()
        
        if reset:
            update_settings({
                'company_name': 'Taxi Manager',
                'fare_per_km': '50',
                'currency': 'INR',
                'report_email': 'admin@taximanager.com'
            })
            st.success("Settings reset to defaults!")
            st.rerun()

# Footer
st.divider()
st.caption(f"Taxi Manager | Version 3.0 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
