import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json

# --- DATA PERSISTENCE FUNCTIONS ---
def save_data():
    """Save all data to CSV files"""
    if 'drivers_db' in st.session_state:
        st.session_state.drivers_db.to_csv('drivers.csv', index=False)
    if 'cars_db' in st.session_state:
        st.session_state.cars_db.to_csv('cars.csv', index=False)
    if 'trips_db' in st.session_state:
        st.session_state.trips_db.to_csv('trips.csv', index=False)
    if 'payments_db' in st.session_state:
        st.session_state.payments_db.to_csv('payments.csv', index=False)

def load_data():
    """Load data from CSV files if they exist"""
    data_loaded = False
    
    # Load drivers
    if os.path.exists('drivers.csv'):
        st.session_state.drivers_db = pd.read_csv('drivers.csv')
        data_loaded = True
    else:
        st.session_state.drivers_db = pd.DataFrame({
            'ID': ["DRV-001", "DRV-002", "DRV-003", "DRV-004", "DRV-005"],
            'Name': ["John Smith", "Maria Garcia", "Robert Johnson", "Sarah Williams", "Michael Brown"],
            'Phone': ["555-0101", "555-0102", "555-0103", "555-0104", "555-0105"],
            'Email': ["john@email.com", "maria@email.com", "robert@email.com", "sarah@email.com", "michael@email.com"],
            'License': ["ABC123", "DEF456", "GHI789", "JKL012", "MNO345"],
            'CPNC': ["CPNC-1001", "CPNC-1002", "CPNC-1003", "CPNC-1004", "CPNC-1005"],
            'Status': ["Available", "On Trip", "Available", "Break", "Offline"],
            'Rating': [4.8, 4.9, 4.7, 5.0, 4.6],
            'Total Trips': [125, 98, 156, 87, 203],
            'Daily Rate': [80.00, 85.00, 75.00, 90.00, 70.00],
            'Amount Paid': [3200.00, 2550.00, 3900.00, 2610.00, 5075.00],
            'Amount Due': [4000.00, 3400.00, 4680.00, 3480.00, 6090.00],
            'Balance': [800.00, 850.00, 780.00, 870.00, 1015.00],
            'Payment Status': ["Pending", "Pending", "Pending", "Pending", "Pending"],
            'Total Earnings': [4250.75, 3125.50, 4890.25, 2750.00, 6525.75]
        })
    
    # Load cars
    if os.path.exists('cars.csv'):
        st.session_state.cars_db = pd.read_csv('cars.csv')
    else:
        st.session_state.cars_db = pd.DataFrame({
            'Plate': ["GA-ABC123", "GA-DEF456", "GA-GHI789"],
            'Model': ["Toyota Camry", "Honda Accord", "Ford Fusion"],
            'Year': [2020, 2019, 2021],
            'Driver': ["John Smith", "Maria Garcia", "Robert Johnson"],
            'Driver ID': ["DRV-001", "DRV-002", "DRV-003"],
            'CPNC': ["CPNC-1001", "CPNC-1002", "CPNC-1003"],
            'Status': ["Active", "Active", "Maintenance"],
            'Last Service': ["2025-11-15", "2025-12-01", "2025-10-30"]
        })
    
    # Load trips
    if os.path.exists('trips.csv'):
        st.session_state.trips_db = pd.read_csv('trips.csv')
    else:
        dates = pd.date_range(end=datetime.now(), periods=50, freq='D')
        trips_data = []
        for i in range(50):
            driver_id = np.random.choice(["DRV-001", "DRV-002", "DRV-003", "DRV-004"])
            driver_name = {
                "DRV-001": "John Smith",
                "DRV-002": "Maria Garcia", 
                "DRV-003": "Robert Johnson",
                "DRV-004": "Sarah Williams"
            }.get(driver_id, "Unknown")
            
            trips_data.append({
                'Trip ID': f"TRIP-{dates[i].strftime('%Y%m%d')}-{i:03d}",
                'Date': dates[i].strftime('%Y-%m-%d'),
                'Driver ID': driver_id,
                'Driver': driver_name,
                'Customer': f"Customer {i+1}",
                'Pickup': np.random.choice(["Downtown", "Airport", "Midtown", "Buckhead"]),
                'Dropoff': np.random.choice(["Midtown", "Airport", "Decatur", "Downtown"]),
                'Fare': round(np.random.uniform(15, 75), 2),
                'Duration': np.random.randint(10, 60),
                'Payment Status': np.random.choice(["Paid", "Unpaid", "Pending"], p=[0.7, 0.2, 0.1]),
                'Status': np.random.choice(["Completed", "Completed", "Completed", "Cancelled"])
            })
        
        st.session_state.trips_db = pd.DataFrame(trips_data)
    
    # Load payments
    if os.path.exists('payments.csv'):
        st.session_state.payments_db = pd.read_csv('payments.csv')
    else:
        st.session_state.payments_db = pd.DataFrame({
            'Payment ID': ["PAY-001", "PAY-002", "PAY-003", "PAY-004", "PAY-005"],
            'Date': ["2025-12-01", "2025-12-05", "2025-12-10", "2025-12-15", "2025-12-20"],
            'Driver ID': ["DRV-001", "DRV-002", "DRV-003", "DRV-001", "DRV-004"],
            'Driver Name': ["John Smith", "Maria Garcia", "Robert Johnson", "John Smith", "Sarah Williams"],
            'Amount': [800.00, 850.00, 780.00, 800.00, 870.00],
            'Method': ["Cash", "Bank Transfer", "Cash", "Credit Card", "Bank Transfer"],
            'Status': ["Completed", "Completed", "Completed", "Completed", "Pending"],
            'Description': ["Monthly Payment", "Monthly Payment", "Monthly Payment", "Balance Payment", "Monthly Payment"]
        })
    
    return data_loaded

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Taxi Manager Pro",
    page_icon="🚕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INITIALIZE DATA ---
# Load data from files (or create sample data)
if 'data_loaded' not in st.session_state:
    data_loaded = load_data()
    st.session_state.data_loaded = data_loaded
    if data_loaded:
        st.success("✅ Data loaded from saved files!")
    else:
        st.info("📁 Starting with sample data. New data will be saved automatically.")

# --- HELPER FUNCTIONS WITH AUTO-SAVE ---
def update_driver_balance(driver_id, amount_paid):
    """Update driver's balance when payment is made and auto-save"""
    if 'drivers_db' in st.session_state:
        df = st.session_state.drivers_db
        if driver_id in df['ID'].values:
            idx = df[df['ID'] == driver_id].index[0]
            current_paid = df.at[idx, 'Amount Paid']
            current_balance = df.at[idx, 'Balance']
            
            df.at[idx, 'Amount Paid'] = current_paid + amount_paid
            df.at[idx, 'Balance'] = max(0, current_balance - amount_paid)
            
            new_balance = df.at[idx, 'Balance']
            if new_balance <= 0:
                df.at[idx, 'Payment Status'] = "Paid"
            elif new_balance < df.at[idx, 'Amount Due'] * 0.5:
                df.at[idx, 'Payment Status'] = "Partially Paid"
            else:
                df.at[idx, 'Payment Status'] = "Pending"
            
            st.session_state.drivers_db = df
            save_data()  # AUTO-SAVE
            return True
    return False

def add_payment_record(payment_data):
    """Add new payment record and auto-save"""
    new_record = pd.DataFrame([payment_data])
    st.session_state.payments_db = pd.concat([st.session_state.payments_db, new_record], ignore_index=True)
    save_data()  # AUTO-SAVE

def add_driver_record(driver_data):
    """Add new driver and auto-save"""
    new_record = pd.DataFrame([driver_data])
    st.session_state.drivers_db = pd.concat([st.session_state.drivers_db, new_record], ignore_index=True)
    save_data()  # AUTO-SAVE
    return True

def add_car_record(car_data):
    """Add new car and auto-save"""
    new_record = pd.DataFrame([car_data])
    st.session_state.cars_db = pd.concat([st.session_state.cars_db, new_record], ignore_index=True)
    save_data()  # AUTO-SAVE
    return True

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3097/3097140.png", width=100)
    st.title("🚕 Taxi Manager Pro")
    
    st.markdown("---")
    
    page = st.radio(
        "NAVIGATION",
        ["Dashboard", "Driver Management", "Car Management", "Payments", "Reports", "Settings"],
        index=0
    )
    
    st.markdown("---")
    
    # Quick stats
    st.subheader("Quick Stats")
    if 'drivers_db' in st.session_state:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Drivers", len(st.session_state.drivers_db))
        with col2:
            st.metric("Cars", len(st.session_state.cars_db))
        
        total_balance = st.session_state.drivers_db['Balance'].sum()
        st.metric("Total Balance Due", f"${total_balance:,.2f}")
    
    # Save button
    st.markdown("---")
    if st.button("💾 Save All Data", type="secondary", use_container_width=True):
        save_data()
        st.success("All data saved successfully!")
    
    # Data info
    if 'drivers_db' in st.session_state:
        st.caption(f"Last saved: {datetime.now().strftime('%H:%M:%S')}")
    
    st.markdown("---")
    st.caption(f"© {datetime.now().year} Taxi Manager Pro")

# --- MAIN CONTENT AREA ---
if page == "Dashboard":
    st.title("📊 Dashboard")
    
    if 'drivers_db' not in st.session_state:
        st.warning("No data loaded. Please check data files.")
        if st.button("Load Sample Data"):
            load_data()
            st.rerun()
    else:
        # Your dashboard code here (same as before)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            available_drivers = len(st.session_state.drivers_db[st.session_state.drivers_db['Status'] == 'Available'])
            st.metric("Available Drivers", available_drivers)
        
        with col2:
            active_trips = len(st.session_state.trips_db[st.session_state.trips_db['Status'] == 'Completed'])
            st.metric("Active Trips", active_trips)
        
        with col3:
            today = datetime.now().strftime('%Y-%m-%d')
            today_revenue = st.session_state.trips_db[
                (st.session_state.trips_db['Date'] == today) & 
                (st.session_state.trips_db['Status'] == 'Completed')
            ]['Fare'].sum()
            st.metric("Today's Revenue", f"${today_revenue:,.2f}")
        
        with col4:
            pending_payments = len(st.session_state.drivers_db[st.session_state.drivers_db['Payment Status'] == 'Pending'])
            st.metric("Pending Payments", pending_payments)
        
        # ... rest of dashboard code

elif page == "Driver Management":
    st.title("👥 Driver Management")
    
    # Add manual save button at top
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("💾 Save Now", type="primary"):
            save_data()
            st.success("Data saved!")
    
    tab1, tab2, tab3, tab4 = st.tabs(["All Drivers", "Add New Driver", "Edit Driver", "Driver Analytics"])
    
    with tab1:
        # Search and filter
        col1, col2 = st.columns(2)
        with col1:
            search_term = st.text_input("Search Drivers", placeholder="Search by name, ID or CPNC...")
        with col2:
            status_filter = st.multiselect(
                "Filter by Payment Status",
                options=["All", "Paid", "Partially Paid", "Pending"],
                default=["All"]
            )
        
        # Apply filters
        filtered_df = st.session_state.drivers_db.copy()
        
        if search_term:
            filtered_df = filtered_df[
                filtered_df['Name'].str.contains(search_term, case=False) |
                filtered_df['ID'].str.contains(search_term, case=False) |
                filtered_df['CPNC'].str.contains(search_term, case=False)
            ]
        
        if "All" not in status_filter and status_filter:
            filtered_df = filtered_df[filtered_df['Payment Status'].isin(status_filter)]
        
        # Display drivers
        st.dataframe(
            filtered_df,
            column_config={
                "ID": "Driver ID",
                "Name": "Full Name",
                "Phone": "Phone",
                "Email": "Email",
                "License": "License #",
                "CPNC": "CPNC #",
                "Status": "Driver Status",
                "Rating": st.column_config.NumberColumn(
                    "Rating",
                    format="%.1f ⭐",
                    min_value=0,
                    max_value=5
                ),
                "Daily Rate": st.column_config.NumberColumn(
                    "Daily Rate",
                    format="$%.2f"
                ),
                "Amount Paid": st.column_config.NumberColumn(
                    "Amount Paid",
                    format="$%.2f"
                ),
                "Amount Due": st.column_config.NumberColumn(
                    "Amount Due",
                    format="$%.2f"
                ),
                "Balance": st.column_config.NumberColumn(
                    "Balance",
                    format="$%.2f"
                ),
                "Payment Status": "Payment Status",
                "Total Trips": "Total Trips",
                "Total Earnings": st.column_config.NumberColumn(
                    "Total Earnings",
                    format="$%.2f"
                )
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Export button
        if st.button("📥 Export Drivers Data"):
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="drivers_data.csv",
                mime="text/csv"
            )
    
    with tab2:
        with st.form("add_driver_form", clear_on_submit=True):
            st.subheader("Add New Driver")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Generate next driver ID
                if not st.session_state.drivers_db.empty:
                    last_id = st.session_state.drivers_db['ID'].str.extract(r'DRV-(\d+)').astype(int).max().iloc[0]
                    next_id = f"DRV-{last_id + 1:03d}"
                else:
                    next_id = "DRV-001"
                
                driver_id = st.text_input("Driver ID *", value=next_id)
                name = st.text_input("Full Name *")
                phone = st.text_input("Phone Number *")
                email = st.text_input("Email Address")
                license_number = st.text_input("License Number *")
                
                # Generate next CPNC number
                if not st.session_state.drivers_db.empty:
                    last_cpnc = st.session_state.drivers_db['CPNC'].str.extract(r'CPNC-(\d+)').astype(int).max().iloc[0]
                    next_cpnc = f"CPNC-{last_cpnc + 1}"
                else:
                    next_cpnc = "CPNC-1001"
                
                cpnc_number = st.text_input("CPNC Number *", value=next_cpnc)
            
            with col2:
                initial_status = st.selectbox(
                    "Initial Status",
                    options=["Available", "On Trip", "Break", "Offline"],
                    index=0
                )
                daily_rate = st.number_input("Daily Rate ($)", min_value=0.0, value=80.0, step=5.0)
                amount_paid = st.number_input("Initial Amount Paid ($)", min_value=0.0, value=0.0, step=50.0)
                amount_due = st.number_input("Amount Due ($)", min_value=0.0, value=0.0, step=50.0)
                initial_rating = st.slider("Initial Rating", 1.0, 5.0, 5.0, 0.1)
            
            submitted = st.form_submit_button("➕ Add Driver", type="primary")
            
            if submitted:
                if not all([driver_id, name, phone, license_number, cpnc_number]):
                    st.error("Please fill in all required fields (*)")
                else:
                    # Check if ID already exists
                    if driver_id in st.session_state.drivers_db['ID'].values:
                        st.error(f"Driver ID {driver_id} already exists!")
                    else:
                        # Calculate balance
                        balance = max(0, amount_due - amount_paid)
                        payment_status = "Paid" if balance <= 0 else "Partially Paid" if amount_paid > 0 else "Pending"
                        
                        # Add new driver
                        new_driver = {
                            'ID': driver_id,
                            'Name': name,
                            'Phone': phone,
                            'Email': email,
                            'License': license_number,
                            'CPNC': cpnc_number,
                            'Status': initial_status,
                            'Rating': initial_rating,
                            'Daily Rate': daily_rate,
                            'Amount Paid': amount_paid,
                            'Amount Due': amount_due,
                            'Balance': balance,
                            'Payment Status': payment_status,
                            'Total Trips': 0,
                            'Total Earnings': 0.0
                        }
                        
                        if add_driver_record(new_driver):
                            st.success(f"Driver {name} added successfully!")
                            st.balloons()
                            st.rerun()
    
    with tab3:
        st.subheader("Edit Driver Information")
        
        if st.session_state.drivers_db.empty:
            st.info("No drivers to edit. Add a driver first.")
        else:
            driver_list = st.session_state.drivers_db['Name'].tolist()
            selected_driver = st.selectbox("Select Driver to Edit", driver_list)
            
            if selected_driver:
                driver_data = st.session_state.drivers_db[
                    st.session_state.drivers_db['Name'] == selected_driver
                ].iloc[0]
                
                with st.form("edit_driver_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        edit_name = st.text_input("Full Name", value=driver_data['Name'])
                        edit_phone = st.text_input("Phone Number", value=driver_data['Phone'])
                        edit_email = st.text_input("Email", value=driver_data['Email'])
                        edit_license = st.text_input("License Number", value=driver_data['License'])
                        edit_cpnc = st.text_input("CPNC Number", value=driver_data['CPNC'])
                    
                    with col2:
                        edit_status = st.selectbox(
                            "Driver Status",
                            options=["Available", "On Trip", "Break", "Offline"],
                            index=["Available", "On Trip", "Break", "Offline"].index(driver_data['Status'])
                        )
                        edit_daily_rate = st.number_input("Daily Rate ($)", min_value=0.0, 
                                                          value=float(driver_data['Daily Rate']), step=5.0)
                        edit_amount_due = st.number_input("Amount Due ($)", min_value=0.0, 
                                                         value=float(driver_data['Amount Due']), step=50.0)
                        edit_payment_status = st.selectbox(
                            "Payment Status",
                            options=["Paid", "Partially Paid", "Pending"],
                            index=["Paid", "Partially Paid", "Pending"].index(driver_data['Payment Status'])
                        )
                        edit_rating = st.slider("Rating", 1.0, 5.0, float(driver_data['Rating']), 0.1)
                    
                    submitted = st.form_submit_button("💾 Update Driver", type="primary")
                    
                    if submitted:
                        idx = st.session_state.drivers_db[
                            st.session_state.drivers_db['Name'] == selected_driver
                        ].index[0]
                        
                        st.session_state.drivers_db.at[idx, 'Name'] = edit_name
                        st.session_state.drivers_db.at[idx, 'Phone'] = edit_phone
                        st.session_state.drivers_db.at[idx, 'Email'] = edit_email
                        st.session_state.drivers_db.at[idx, 'License'] = edit_license
                        st.session_state.drivers_db.at[idx, 'CPNC'] = edit_cpnc
                        st.session_state.drivers_db.at[idx, 'Status'] = edit_status
                        st.session_state.drivers_db.at[idx, 'Daily Rate'] = edit_daily_rate
                        st.session_state.drivers_db.at[idx, 'Amount Due'] = edit_amount_due
                        st.session_state.drivers_db.at[idx, 'Payment Status'] = edit_payment_status
                        st.session_state.drivers_db.at[idx, 'Rating'] = edit_rating
                        
                        # Recalculate balance based on payment status
                        if edit_payment_status == "Paid":
                            st.session_state.drivers_db.at[idx, 'Balance'] = 0
                            st.session_state.drivers_db.at[idx, 'Amount Paid'] = edit_amount_due
                        elif edit_payment_status == "Partially Paid":
                            # Assume 50% paid if partially paid
                            st.session_state.drivers_db.at[idx, 'Amount Paid'] = edit_amount_due * 0.5
                            st.session_state.drivers_db.at[idx, 'Balance'] = edit_amount_due * 0.5
                        else:  # Pending
                            st.session_state.drivers_db.at[idx, 'Amount Paid'] = 0
                            st.session_state.drivers_db.at[idx, 'Balance'] = edit_amount_due
                        
                        save_data()  # Save after editing
                        st.success(f"Driver {edit_name} updated and saved!")
                        st.rerun()

# ... rest of your code for other pages (Car Management, Payments, etc.)
# Make sure to update all add/update functions to call save_data()

elif page == "Car Management":
    st.title("🚗 Car Management")
    
    # Add save button
    if st.button("💾 Save Car Data", type="secondary"):
        save_data()
        st.success("Car data saved!")
    
    # ... rest of car management code (update add_car_record to use add_car_record function)

elif page == "Payments":
    st.title("💰 Payment Management")
    
    # Add save button
    if st.button("💾 Save Payment Data", type="secondary"):
        save_data()
        st.success("Payment data saved!")
    
    # ... rest of payments code

elif page == "Settings":
    st.title("⚙️ Settings")
    
    st.subheader("Data Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Save All Data", type="primary"):
            save_data()
            st.success("All data saved successfully!")
    
    with col2:
        if st.button("🔄 Reload Data", type="secondary"):
            load_data()
            st.success("Data reloaded from files!")
            st.rerun()
    
    with col3:
        if st.button("📁 Reset to Sample", type="secondary"):
            # Remove existing CSV files
            for file in ['drivers.csv', 'cars.csv', 'trips.csv', 'payments.csv']:
                if os.path.exists(file):
                    os.remove(file)
            # Clear session state
            keys = list(st.session_state.keys())
            for key in keys:
                del st.session_state[key]
            # Load sample data
            load_data()
            st.success("Reset to sample data!")
            st.rerun()
    
    # Show file info
    st.subheader("Data Files")
    
    file_info = []
    for file_name in ['drivers.csv', 'cars.csv', 'trips.csv', 'payments.csv']:
        if os.path.exists(file_name):
            size = os.path.getsize(file_name)
            modified = datetime.fromtimestamp(os.path.getmtime(file_name))
            file_info.append({
                "File": file_name,
                "Size": f"{size:,} bytes",
                "Last Modified": modified.strftime("%Y-%m-%d %H:%M:%S")
            })
        else:
            file_info.append({
                "File": file_name,
                "Status": "Not found",
                "Last Modified": "N/A"
            })
    
    st.dataframe(pd.DataFrame(file_info), hide_index=True, use_container_width=True)
    
    # Export all data
    st.subheader("Export All Data")
    
    if st.button("📥 Export All as ZIP", type="secondary"):
        import zipfile
        from io import BytesIO
        
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for file_name in ['drivers.csv', 'cars.csv', 'trips.csv', 'payments.csv']:
                if os.path.exists(file_name):
                    zip_file.write(file_name)
        
        st.download_button(
            label="Download ZIP",
            data=zip_buffer.getvalue(),
            file_name="taxi_manager_data.zip",
            mime="application/zip"
        )

# --- FOOTER ---
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns(3)
with footer_col1:
    st.caption(f"© {datetime.now().year} Taxi Manager Pro")
with footer_col2:
    if 'drivers_db' in st.session_state:
        st.caption(f"{len(st.session_state.drivers_db)} drivers • {len(st.session_state.cars_db)} cars")
with footer_col3:
    # Auto-save reminder
    st.caption("💾 Auto-save enabled")
