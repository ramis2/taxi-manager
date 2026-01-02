import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json

# --- DATA PERSISTENCE FUNCTIONS ---
def save_data():
    """Save all data to CSV files"""
    try:
        if 'drivers_db' in st.session_state:
            st.session_state.drivers_db.to_csv('drivers.csv', index=False)
        if 'cars_db' in st.session_state:
            st.session_state.cars_db.to_csv('cars.csv', index=False)
        if 'trips_db' in st.session_state:
            st.session_state.trips_db.to_csv('trips.csv', index=False)
        if 'payments_db' in st.session_state:
            st.session_state.payments_db.to_csv('payments.csv', index=False)
        return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False

def load_data():
    """Load data from CSV files if they exist"""
    # Load drivers
    if os.path.exists('drivers.csv'):
        try:
            st.session_state.drivers_db = pd.read_csv('drivers.csv')
        except:
            st.session_state.drivers_db = create_sample_drivers()
    else:
        st.session_state.drivers_db = create_sample_drivers()
    
    # Load cars
    if os.path.exists('cars.csv'):
        try:
            st.session_state.cars_db = pd.read_csv('cars.csv')
        except:
            st.session_state.cars_db = create_sample_cars()
    else:
        st.session_state.cars_db = create_sample_cars()
    
    # Load trips
    if os.path.exists('trips.csv'):
        try:
            st.session_state.trips_db = pd.read_csv('trips.csv')
        except:
            st.session_state.trips_db = create_sample_trips()
    else:
        st.session_state.trips_db = create_sample_trips()
    
    # Load payments
    if os.path.exists('payments.csv'):
        try:
            st.session_state.payments_db = pd.read_csv('payments.csv')
        except:
            st.session_state.payments_db = create_sample_payments()
    else:
        st.session_state.payments_db = create_sample_payments()

def create_sample_drivers():
    """Create sample driver data with Atlanta locations"""
    return pd.DataFrame({
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
        'Total Earnings': [4250.75, 3125.50, 4890.25, 2750.00, 6525.75],
        'Latitude': [33.7550, 33.7860, 33.8460, 33.6407, 33.7756],  # Atlanta locations
        'Longitude': [-84.3900, -84.3870, -84.3680, -84.4277, -84.3963]
    })

def create_sample_cars():
    return pd.DataFrame({
        'Plate': ["GA-ABC123", "GA-DEF456", "GA-GHI789"],
        'Model': ["Toyota Camry", "Honda Accord", "Ford Fusion"],
        'Year': [2020, 2019, 2021],
        'Driver': ["John Smith", "Maria Garcia", "Robert Johnson"],
        'Driver ID': ["DRV-001", "DRV-002", "DRV-003"],
        'CPNC': ["CPNC-1001", "CPNC-1002", "CPNC-1003"],
        'Status': ["Active", "Active", "Maintenance"],
        'Last Service': ["2025-11-15", "2025-12-01", "2025-10-30"]
    })

def create_sample_trips():
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
    
    return pd.DataFrame(trips_data)

def create_sample_payments():
    return pd.DataFrame({
        'Payment ID': ["PAY-001", "PAY-002", "PAY-003", "PAY-004", "PAY-005"],
        'Date': ["2025-12-01", "2025-12-05", "2025-12-10", "2025-12-15", "2025-12-20"],
        'Driver ID': ["DRV-001", "DRV-002", "DRV-003", "DRV-001", "DRV-004"],
        'Driver Name': ["John Smith", "Maria Garcia", "Robert Johnson", "John Smith", "Sarah Williams"],
        'Amount': [800.00, 850.00, 780.00, 800.00, 870.00],
        'Method': ["Cash", "Bank Transfer", "Cash", "Credit Card", "Bank Transfer"],
        'Status': ["Completed", "Completed", "Completed", "Completed", "Pending"],
        'Description': ["Monthly Payment", "Monthly Payment", "Monthly Payment", "Balance Payment", "Monthly Payment"]
    })

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Taxi Manager Pro - Atlanta",
    page_icon="🚕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INITIALIZE DATA ---
if 'data_initialized' not in st.session_state:
    load_data()
    st.session_state.data_initialized = True

# --- HELPER FUNCTIONS ---
def add_driver_record(driver_data):
    """Add new driver and auto-save"""
    new_record = pd.DataFrame([driver_data])
    st.session_state.drivers_db = pd.concat([st.session_state.drivers_db, new_record], ignore_index=True)
    save_data()
    return True

def add_car_record(car_data):
    """Add new car and auto-save"""
    new_record = pd.DataFrame([car_data])
    st.session_state.cars_db = pd.concat([st.session_state.cars_db, new_record], ignore_index=True)
    save_data()
    return True

def add_payment_record(payment_data):
    """Add new payment and auto-save"""
    new_record = pd.DataFrame([payment_data])
    st.session_state.payments_db = pd.concat([st.session_state.payments_db, new_record], ignore_index=True)
    save_data()
    return True

def update_driver_location(driver_id):
    """Move driver to random Atlanta location"""
    if driver_id in st.session_state.drivers_db['ID'].values:
        idx = st.session_state.drivers_db[st.session_state.drivers_db['ID'] == driver_id].index[0]
        
        # Atlanta area coordinates
        atlanta_locations = [
            (33.7550, -84.3900),  # Downtown
            (33.7860, -84.3870),  # Midtown
            (33.8460, -84.3680),  # Buckhead
            (33.6407, -84.4277),  # Airport
            (33.7756, -84.3963),  # Georgia Tech
            (33.7850, -84.3740),  # Piedmont Park
            (33.7370, -84.4130),  # West End
            (33.8490, -84.3630)   # Lenox Square
        ]
        
        # Pick random location
        lat, lon = atlanta_locations[np.random.randint(0, len(atlanta_locations))]
        
        # Add small random offset
        lat += np.random.uniform(-0.01, 0.01)
        lon += np.random.uniform(-0.01, 0.01)
        
        st.session_state.drivers_db.at[idx, 'Latitude'] = lat
        st.session_state.drivers_db.at[idx, 'Longitude'] = lon
        save_data()
        return lat, lon
    return None, None

def generate_atlanta_map():
    """Generate Atlanta map with driver locations"""
    if 'drivers_db' in st.session_state and not st.session_state.drivers_db.empty:
        # Create map dataframe
        map_df = st.session_state.drivers_db[['Latitude', 'Longitude', 'Name', 'Status', 'CPNC']].copy()
        map_df.columns = ['lat', 'lon', 'driver', 'status', 'cpnc']
        
        # Filter out drivers without coordinates
        map_df = map_df.dropna(subset=['lat', 'lon'])
        
        if not map_df.empty:
            return map_df
    return pd.DataFrame(columns=['lat', 'lon', 'driver', 'status', 'cpnc'])

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3097/3097140.png", width=100)
    st.title("🚕 Atlanta Taxi Manager")
    
    st.markdown("---")
    
    # Navigation menu - NOW INCLUDES LIVE MAP
    page = st.radio(
        "NAVIGATION",
        ["Dashboard", "Live Map", "Driver Management", "Car Management", "Payments", "Reports", "Settings"],
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
        
        # Calculate available drivers
        if 'Status' in st.session_state.drivers_db.columns:
            available_drivers = len(st.session_state.drivers_db[
                st.session_state.drivers_db['Status'] == 'Available'
            ])
            st.metric("Available Now", available_drivers)
        
        total_balance = st.session_state.drivers_db['Balance'].sum() if 'Balance' in st.session_state.drivers_db.columns else 0
        st.metric("Balance Due", f"${total_balance:,.2f}")
    
    # Save button
    st.markdown("---")
    if st.button("💾 Save All Data", type="secondary", use_container_width=True):
        if save_data():
            st.success("Data saved!", icon="✅")
        else:
            st.error("Save failed")
    
    st.markdown("---")
    st.caption(f"© {datetime.now().year} Atlanta Taxi Manager")

# --- MAIN CONTENT AREA ---
if page == "Dashboard":
    st.title("📊 Dashboard - Atlanta Dispatch")
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if 'drivers_db' in st.session_state and 'Status' in st.session_state.drivers_db.columns:
            available_drivers = len(st.session_state.drivers_db[
                st.session_state.drivers_db['Status'] == 'Available'
            ])
            st.metric("Available Drivers", available_drivers)
        else:
            st.metric("Available Drivers", 0)
    
    with col2:
        if 'trips_db' in st.session_state:
            active_trips = len(st.session_state.trips_db[
                st.session_state.trips_db['Status'] == 'Completed'
            ])
            st.metric("Completed Trips", active_trips)
        else:
            st.metric("Active Trips", 0)
    
    with col3:
        today = datetime.now().strftime('%Y-%m-%d')
        today_revenue = 0
        if 'trips_db' in st.session_state:
            today_trips = st.session_state.trips_db[
                (st.session_state.trips_db['Date'] == today) & 
                (st.session_state.trips_db['Status'] == 'Completed')
            ]
            if not today_trips.empty and 'Fare' in today_trips.columns:
                today_revenue = today_trips['Fare'].sum()
        st.metric("Today's Revenue", f"${today_revenue:,.2f}")
    
    with col4:
        if 'drivers_db' in st.session_state and 'Payment Status' in st.session_state.drivers_db.columns:
            pending_payments = len(st.session_state.drivers_db[
                st.session_state.drivers_db['Payment Status'] == 'Pending'
            ])
            st.metric("Pending Payments", pending_payments)
        else:
            st.metric("Pending Payments", 0)
    
    st.markdown("---")
    
    # Mini Atlanta Map Preview
    st.subheader("📍 Atlanta Driver Locations")
    map_df = generate_atlanta_map()
    
    if not map_df.empty:
        # Center on Atlanta
        st.map(map_df, latitude=33.7490, longitude=-84.3880, zoom=11)
        
        # Map legend
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("🟢 **Available**")
        with col2:
            st.markdown("🔴 **On Trip**")
        with col3:
            st.markdown("🟡 **Other Status**")
        
        # Driver list under map
        st.subheader("Active Drivers")
        cols = st.columns(4)
        for idx, (_, driver) in enumerate(st.session_state.drivers_db.iterrows()):
            with cols[idx % 4]:
                status_color = {
                    'Available': '🟢',
                    'On Trip': '🔴',
                    'Break': '🟡',
                    'Offline': '⚫'
                }.get(driver.get('Status', 'Unknown'), '⚫')
                
                st.markdown(f"""
                **{status_color} {driver['Name']}**
                - ID: {driver['ID']}
                - CPNC: {driver.get('CPNC', 'N/A')}
                - Status: {driver.get('Status', 'Unknown')}
                """)
    else:
        st.info("No driver locations available")
    
    # Quick actions
    st.markdown("---")
    st.subheader("Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Update All Locations", type="primary"):
            for driver_id in st.session_state.drivers_db['ID']:
                update_driver_location(driver_id)
            st.success("Driver locations updated!")
            st.rerun()
    
    with col2:
        if st.button("📊 View Full Map", type="secondary"):
            st.session_state.page = "Live Map"
            st.rerun()
    
    with col3:
        if st.button("👥 Add New Driver", type="secondary"):
            st.session_state.page = "Driver Management"
            st.rerun()

elif page == "Live Map":
    st.title("📍 Atlanta Live Driver Map")
    
    # Refresh controls
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        refresh_rate = st.selectbox("Auto-refresh", ["30 seconds", "1 minute", "5 minutes", "Manual"], index=1)
    with col2:
        if st.button("🔄 Refresh Now"):
            for driver_id in st.session_state.drivers_db['ID']:
                if np.random.random() > 0.7:  # 30% chance to move each driver
                    update_driver_location(driver_id)
            st.rerun()
    with col3:
        show_details = st.checkbox("Show Details", value=True)
    
    # Generate map data
    map_df = generate_atlanta_map()
    
    if not map_df.empty:
        # Display the map
        st.map(map_df, latitude=33.7490, longitude=-84.3880, zoom=11, use_container_width=True)
        
        # Atlanta landmarks
        landmarks_df = pd.DataFrame({
            'lat': [33.7550, 33.6407, 33.7756, 33.7850, 33.8460],
            'lon': [-84.3900, -84.4277, -84.3963, -84.3740, -84.3680],
            'name': ['Downtown', 'Airport', 'Georgia Tech', 'Piedmont Park', 'Buckhead']
        })
        
        # Display landmarks
        with st.expander("🗺️ Atlanta Landmarks"):
            st.map(landmarks_df)
            for _, landmark in landmarks_df.iterrows():
                st.write(f"**{landmark['name']}**: {landmark['lat']:.4f}, {landmark['lon']:.4f}")
        
        # Driver details table
        if show_details:
            st.subheader("Driver Locations")
            display_df = map_df.copy()
            display_df['Coordinates'] = display_df.apply(lambda row: f"{row['lat']:.4f}, {row['lon']:.4f}", axis=1)
            st.dataframe(
                display_df[['driver', 'cpnc', 'status', 'Coordinates']],
                column_config={
                    'driver': 'Driver Name',
                    'cpnc': 'CPNC #',
                    'status': 'Status',
                    'Coordinates': 'Location'
                },
                hide_index=True,
                use_container_width=True
            )
        
        # Simulate movement
        st.subheader("Driver Simulation")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚗 Simulate Driver Movement", type="primary"):
                drivers_to_move = np.random.choice(
                    st.session_state.drivers_db['ID'].tolist(),
                    size=min(3, len(st.session_state.drivers_db)),
                    replace=False
                )
                for driver_id in drivers_to_move:
                    update_driver_location(driver_id)
                st.success(f"Moved {len(drivers_to_move)} drivers!")
                st.rerun()
        
        with col2:
            if st.button("📍 Reset to Atlanta Center"):
                for idx, driver in st.session_state.drivers_db.iterrows():
                    st.session_state.drivers_db.at[idx, 'Latitude'] = 33.7490 + np.random.uniform(-0.05, 0.05)
                    st.session_state.drivers_db.at[idx, 'Longitude'] = -84.3880 + np.random.uniform(-0.05, 0.05)
                save_data()
                st.success("All drivers reset to Atlanta!")
                st.rerun()
        
        # Auto-refresh
        if refresh_rate != "Manual":
            import time
            seconds = {
                "30 seconds": 30,
                "1 minute": 60,
                "5 minutes": 300
            }[refresh_rate]
            time.sleep(seconds)
            st.rerun()
    
    else:
        st.warning("No driver locations available. Add drivers first.")
        if st.button("Add Sample Drivers"):
            load_data()
            st.rerun()

elif page == "Driver Management":
    st.title("👥 Driver Management")
    
    # Quick stats
    if 'drivers_db' in st.session_state:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Drivers", len(st.session_state.drivers_db))
        with col2:
            if 'CPNC' in st.session_state.drivers_db.columns:
                unique_cpnc = st.session_state.drivers_db['CPNC'].nunique()
                st.metric("Unique CPNC", unique_cpnc)
        with col3:
            if 'Balance' in st.session_state.drivers_db.columns:
                total_balance = st.session_state.drivers_db['Balance'].sum()
                st.metric("Total Balance Due", f"${total_balance:,.2f}")
    
    tab1, tab2, tab3, tab4 = st.tabs(["All Drivers", "Add New Driver", "Edit Driver", "CPNC Management"])
    
    with tab1:
        # Search and filter
        col1, col2 = st.columns(2)
        with col1:
            search_term = st.text_input("🔍 Search Drivers", placeholder="Name, ID, or CPNC...", key="search_drivers")
        with col2:
            status_filter = st.multiselect(
                "Filter by Status",
                options=["All", "Available", "On Trip", "Break", "Offline"],
                default=["All"]
            )
        
        # Apply filters
        filtered_df = st.session_state.drivers_db.copy()
        
        if search_term:
            mask = (
                filtered_df['Name'].str.contains(search_term, case=False, na=False) |
                filtered_df['ID'].str.contains(search_term, case=False, na=False) |
                filtered_df['CPNC'].str.contains(search_term, case=False, na=False)
            )
            filtered_df = filtered_df[mask]
        
        if "All" not in status_filter and status_filter:
            filtered_df = filtered_df[filtered_df['Status'].isin(status_filter)]
        
        # Display drivers
        if not filtered_df.empty:
            st.dataframe(
                filtered_df,
                column_config={
                    "ID": "Driver ID",
                    "Name": "Full Name",
                    "Phone": "Phone",
                    "Email": "Email",
                    "License": "License #",
                    "CPNC": st.column_config.TextColumn(
                        "CPNC #",
                        help="City Public Vehicle for Hire Certificate Number"
                    ),
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
            if st.button("📥 Export Drivers CSV"):
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="atlanta_drivers.csv",
                    mime="text/csv"
                )
        else:
            st.info("No drivers found matching your search criteria.")
    
    with tab2:
        st.subheader("➕ Add New Driver")
        
        with st.form("add_driver_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                # Generate next driver ID
                if not st.session_state.drivers_db.empty:
                    last_id = 0
                    for id_str in st.session_state.drivers_db['ID']:
                        if id_str.startswith('DRV-'):
                            try:
                                num = int(id_str.split('-')[1])
                                last_id = max(last_id, num)
                            except:
                                pass
                    next_id = f"DRV-{last_id + 1:03d}"
                else:
                    next_id = "DRV-001"
                
                driver_id = st.text_input("Driver ID *", value=next_id)
                name = st.text_input("Full Name *", placeholder="John Smith")
                phone = st.text_input("Phone Number *", placeholder="(404) 555-0123")
                email = st.text_input("Email Address", placeholder="driver@email.com")
                license_number = st.text_input("License Number *", placeholder="GA123456")
                
                # CPNC NUMBER FIELD WITH PLACEHOLDER
                cpnc_number = st.text_input(
                    "CPNC Number *", 
                    placeholder="CPNC-0000",
                    help="City Public Vehicle for Hire Certificate Number"
                )
                
                if not cpnc_number or cpnc_number == "CPNC-0000":
                    # Generate next CPNC
                    if not st.session_state.drivers_db.empty and 'CPNC' in st.session_state.drivers_db.columns:
                        last_cpnc = 1000
                        for cpnc in st.session_state.drivers_db['CPNC']:
                            if isinstance(cpnc, str) and cpnc.startswith('CPNC-'):
                                try:
                                    num = int(cpnc.split('-')[1])
                                    last_cpnc = max(last_cpnc, num)
                                except:
                                    pass
                        cpnc_number = f"CPNC-{last_cpnc + 1}"
                    else:
                        cpnc_number = "CPNC-1001"
            
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
                
                # Atlanta location
                st.markdown("**Atlanta Location**")
                use_random_location = st.checkbox("Use random Atlanta location", value=True)
                if not use_random_location:
                    lat = st.number_input("Latitude", value=33.7490, format="%.6f")
                    lon = st.number_input("Longitude", value=-84.3880, format="%.6f")
                else:
                    lat = 33.7490 + np.random.uniform(-0.05, 0.05)
                    lon = -84.3880 + np.random.uniform(-0.05, 0.05)
            
            submitted = st.form_submit_button("➕ Add Driver to Atlanta Fleet", type="primary")
            
            if submitted:
                if not all([driver_id, name, phone, license_number]):
                    st.error("❌ Please fill in all required fields (*)")
                else:
                    # Check if ID already exists
                    if driver_id in st.session_state.drivers_db['ID'].values:
                        st.error(f"❌ Driver ID {driver_id} already exists!")
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
                            'Total Earnings': 0.0,
                            'Latitude': lat,
                            'Longitude': lon
                        }
                        
                        if add_driver_record(new_driver):
                            st.success(f"✅ Driver {name} added to Atlanta fleet!")
                            st.balloons()
                            st.rerun()
    
    with tab3:
        st.subheader("✏️ Edit Driver Information")
        
        if st.session_state.drivers_db.empty:
            st.info("No drivers to edit. Add a driver first.")
        else:
            driver_list = st.session_state.drivers_db['Name'].tolist()
            selected_driver = st.selectbox("Select Driver to Edit", driver_list, key="edit_driver_select")
            
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
                        
                        # CPNC EDIT FIELD
                        edit_cpnc = st.text_input(
                            "CPNC Number", 
                            value=driver_data.get('CPNC', 'CPNC-0000'),
                            placeholder="CPNC-0000"
                        )
                    
                    with col2:
                        edit_status = st.selectbox(
                            "Driver Status",
                            options=["Available", "On Trip", "Break", "Offline"],
                            index=["Available", "On Trip", "Break", "Offline"].index(
                                driver_data.get('Status', 'Available')
                            )
                        )
                        edit_daily_rate = st.number_input(
                            "Daily Rate ($)", 
                            min_value=0.0, 
                            value=float(driver_data.get('Daily Rate', 80.0)), 
                            step=5.0
                        )
                        edit_amount_due = st.number_input(
                            "Amount Due ($)", 
                            min_value=0.0, 
                            value=float(driver_data.get('Amount Due', 0.0)), 
                            step=50.0
                        )
                        edit_payment_status = st.selectbox(
                            "Payment Status",
                            options=["Paid", "Partially Paid", "Pending"],
                            index=["Paid", "Partially Paid", "Pending"].index(
                                driver_data.get('Payment Status', 'Pending')
                            )
                        )
                        edit_rating = st.slider(
                            "Rating", 
                            1.0, 5.0, 
                            float(driver_data.get('Rating', 5.0)), 
                            0.1
                        )
                    
                    # Correct way - form submit button
submit_button = st.form_submit_button("💾 Save to Database")
if submit_button:
    # save logic

                    
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
                        
                        # Recalculate balance
                        if edit_payment_status == "Paid":
                            st.session_state.drivers_db.at[idx, 'Balance'] = 0
                            st.session_state.drivers_db.at[idx, 'Amount Paid'] = edit_amount_due
                        elif edit_payment_status == "Partially Paid":
                            st.session_state.drivers_db.at[idx, 'Amount Paid'] = edit_amount_due * 0.5
                            st.session_state.drivers_db.at[idx, 'Balance'] = edit_amount_due * 0.5
                        else:
                            st.session_state.drivers_db.at[idx, 'Amount Paid'] = 0
                            st.session_state.drivers_db.at[idx, 'Balance'] = edit_amount_due
                        
                        save_data()
                        st.success(f"✅ Driver {edit_name} updated!")
                        st.rerun()
    
    with tab4:
        st.subheader("📋 CPNC Management")
        
        if 'drivers_db' in st.session_state and 'CPNC' in st.session_state.drivers_db.columns:
            # Show CPNC summary
            cpnc_summary = st.session_state.drivers_db[['Name', 'CPNC', 'Status']].copy()
            cpnc_summary = cpnc_summary.sort_values('CPNC')
            
            st.dataframe(
                cpnc_summary,
                column_config={
                    "Name": "Driver Name",
                    "CPNC": "CPNC Number",
                    "Status": "Status"
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Check for duplicate CPNC
            duplicate_cpnc = cpnc_summary['CPNC'].duplicated()
            if duplicate_cpnc.any():
                st.warning("⚠️ Duplicate CPNC numbers found!")
                st.write(cpnc_summary[duplicate_cpnc])
            
            # Generate new CPNC
            st.subheader("Generate New CPNC")
            if st.button("🔄 Generate Next CPNC Number"):
                last_cpnc = 1000
                for cpnc in st.session_state.drivers_db['CPNC']:
                    if isinstance(cpnc, str) and cpnc.startswith('CPNC-'):
                        try:
                            num = int(cpnc.split('-')[1])
                            last_cpnc = max(last_cpnc, num)
                        except:
                            pass
                next_cpnc = f"CPNC-{last_cpnc + 1}"
                st.info(f"Next available CPNC: **{next_cpnc}**")
                st.code(next_cpnc)
        else:
            st.info("No CPNC data available.")

# ... [Rest of your code for Car Management, Payments, Reports, Settings remains the same]
# Make sure to copy the existing code for those sections

elif page == "Car Management":
    # Your existing car management code
    st.title("🚗 Car Management")
    # ... [rest of car management code]

elif page == "Payments":
    # Your existing payments code
    st.title("💰 Payment Management")
    # ... [rest of payments code]

elif page == "Reports":
    # Your existing reports code
    st.title("📈 Reports")
    # ... [rest of reports code]

elif page == "Settings":
    st.title("⚙️ Settings")
    
    # Data management
    st.subheader("Data Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Save All Data", type="primary"):
            if save_data():
                st.success("✅ All data saved!")
            else:
                st.error("❌ Save failed")
    
    with col2:
        if st.button("🔄 Reload Data", type="secondary"):
            load_data()
            st.success("✅ Data reloaded!")
            st.rerun()
    
    with col3:
        if st.button("📁 Reset Data", type="secondary"):
            for file in ['drivers.csv', 'cars.csv', 'trips.csv', 'payments.csv']:
                if os.path.exists(file):
                    os.remove(file)
            keys = list(st.session_state.keys())
            for key in keys:
                del st.session_state[key]
            load_data()
            st.success("✅ Reset to sample data!")
            st.rerun()
    
    # Atlanta Settings
    st.subheader("Atlanta Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        center_lat = st.number_input("Map Center Latitude", value=33.7490, format="%.6f")
        center_lon = st.number_input("Map Center Longitude", value=-84.3880, format="%.6f")
        default_zoom = st.slider("Default Zoom Level", 1, 20, 11)
    
    with col2:
        cpnc_prefix = st.text_input("CPNC Prefix", value="CPNC-")
        next_cpnc = st.number_input("Next CPNC Number", min_value=1000, value=1006)
        auto_refresh = st.checkbox("Enable Auto-refresh on Live Map", value=True)
    
    # About
    st.subheader("About")
    st.markdown("""
    **Atlanta Taxi Manager v2.1**
    
    Features:
    - 📍 Live Atlanta driver map
    - 👥 Driver management with CPNC tracking
    - 🚗 Car fleet management
    - 💰 Payment and balance tracking
    - 📊 Financial reporting
    - 💾 Data persistence (saves to CSV)
    
    **Atlanta Coverage:**
    - Downtown Atlanta
    - Hartsfield-Jackson Airport
    - Midtown
    - Buckhead
    - Georgia Tech Area
    - Piedmont Park
    - West End
    
    © 2025 Atlanta Taxi Manager. All rights reserved.
    """)

# --- FOOTER ---
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns(3)
with footer_col1:
    st.caption(f"© {datetime.now().year} Atlanta Taxi Manager")
with footer_col2:
    if 'drivers_db' in st.session_state:
        total_drivers = len(st.session_state.drivers_db)
        total_balance = st.session_state.drivers_db['Balance'].sum() if 'Balance' in st.session_state.drivers_db.columns else 0
        st.caption(f"🚕 {total_drivers} drivers | 💰 ${total_balance:,.2f} due")
with footer_col3:
    st.caption(f"📍 Atlanta, GA | 🕐 {datetime.now().strftime('%I:%M %p')}")
