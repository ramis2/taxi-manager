import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta  # FIXED: changed times@elta to timedelta

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Taxi Manager Pro",
    page_icon="🚕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INITIALIZE SESSION STATE ---
# For driver management
if 'drivers_db' not in st.session_state:
    st.session_state.drivers_db = pd.DataFrame({
        'ID': ["DRV-001", "DRV-002", "DRV-003", "DRV-004", "DRV-005"],  # FIXED: quote consistency
        'Name': ["John Smith", "Maria Garcia", "Robert Johnson", "Sarah Williams", "Michael Brown"],
        'Phone': ["555-0101", "555-0102", "555-0103", "555-0104", "555-0105"],
        'Email': ["john@email.com", "maria@email.com", "robert@email.com", "sarah@email.com", "michael@email.com"],
        'License': ["ABC123", "DEF456", "GHI789", "JKL012", "MNO345"],
        'Status': ["Available", "On Trip", "Available", "Break", "Offline"],
        'Rating': [4.8, 4.9, 4.7, 5.0, 4.6],
        'Total Trips': [125, 98, 156, 87, 203],
        'Total Earnings': [4250.75, 3125.50, 4890.25, 2750.00, 6525.75]
    })

# For car management
if 'cars_db' not in st.session_state:
    st.session_state.cars_db = pd.DataFrame({
        'Plate': ["GA-ABC123", "GA-DEF456", "GA-GHI789"],
        'Model': ["Toyota Camry", "Honda Accord", "Ford Fusion"],
        'Year': [2020, 2019, 2021],
        'Driver': ["John Smith", "Maria Garcia", "Robert Johnson"],
        'Status': ["Active", "Active", "Maintenance"],
        'Last Service': ["2025-11-15", "2025-12-01", "2025-10-30"]
    })

# For trip records
if 'trips_db' not in st.session_state:
    # Generate some sample trip data
    dates = pd.date_range(end=datetime.now(), periods=50, freq='D')
    trips_data = []
    for i in range(50):
        trips_data.append({
            'Trip ID': f"TRIP-{dates[i].strftime('%Y%m%d')}-{i:03d}",
            'Date': dates[i].strftime('%Y-%m-%d'),
            'Driver': np.random.choice(["John Smith", "Maria Garcia", "Robert Johnson", "Sarah Williams"]),
            'Customer': f"Customer {i+1}",
            'Pickup': np.random.choice(["Downtown", "Airport", "Midtown", "Buckhead"]),
            'Dropoff': np.random.choice(["Midtown", "Airport", "Decatur", "Downtown"]),
            'Fare': round(np.random.uniform(15, 75), 2),
            'Duration': np.random.randint(10, 60),
            'Status': np.random.choice(["Completed", "Completed", "Completed", "Cancelled"])
        })
    
    st.session_state.trips_db = pd.DataFrame(trips_data)

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3097/3097140.png", width=100)
    st.title("🚕 Taxi Manager Pro")
    
    st.markdown("---")
    
    # Navigation menu
    page = st.radio(
        "NAVIGATION",
        ["Dashboard", "Driver Management", "Car Management", "Reports", "Settings"],
        index=0
    )
    
    st.markdown("---")
    
    # Quick stats in sidebar
    st.subheader("Quick Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Drivers", len(st.session_state.drivers_db))
    with col2:
        st.metric("Cars", len(st.session_state.cars_db))
    
    total_balance = st.session_state.trips_db['Fare'].sum()
    st.metric("Total Balance", f"${total_balance:,.2f}")
    
    # Date range selector
    st.markdown("---")
    st.subheader("Date Range")
    start_date = st.date_input(
        "From",
        value=datetime.now() - timedelta(days=30)  # FIXED: using timedelta
    )
    end_date = st.date_input(
        "To",
        value=datetime.now()
    )
    
    st.markdown("---")
    st.caption(f"© {datetime.now().year} Taxi Manager Pro")

# --- MAIN CONTENT AREA ---
if page == "Dashboard":
    st.title("📊 Dashboard")
    
    # Top metrics
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
        active_cars = len(st.session_state.cars_db[st.session_state.cars_db['Status'] == 'Active'])
        st.metric("Active Cars", active_cars)
    
    st.markdown("---")
    
    # Charts and data visualization
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Driver Status Distribution")
        status_counts = st.session_state.drivers_db['Status'].value_counts()
        st.bar_chart(status_counts)
    
    with col2:
        st.subheader("Daily Revenue (Last 30 days)")
        # Aggregate revenue by date
        revenue_by_date = st.session_state.trips_db.groupby('Date')['Fare'].sum()
        st.line_chart(revenue_by_date.tail(30))
    
    # Recent trips table
    st.subheader("Recent Trips")
    recent_trips = st.session_state.trips_db.sort_values('Date', ascending=False).head(10)
    st.dataframe(
        recent_trips[['Trip ID', 'Date', 'Driver', 'Customer', 'Fare', 'Status']],
        hide_index=True,
        use_container_width=True
    )

elif page == "Driver Management":
    st.title("👥 Driver Management")
    
    tab1, tab2, tab3 = st.tabs(["All Drivers", "Add New Driver", "Driver Analytics"])
    
    with tab1:
        # Search and filter
        col1, col2 = st.columns(2)
        with col1:
            search_term = st.text_input("Search Drivers", placeholder="Search by name or ID...")
        with col2:
            status_filter = st.multiselect(
                "Filter by Status",
                options=["All", "Available", "On Trip", "Break", "Offline"],
                default=["All"]
            )
        
        # Apply filters
        filtered_df = st.session_state.drivers_db.copy()
        
        if search_term:
            filtered_df = filtered_df[
                filtered_df['Name'].str.contains(search_term, case=False) |
                filtered_df['ID'].str.contains(search_term, case=False)
            ]
        
        if "All" not in status_filter and status_filter:
            filtered_df = filtered_df[filtered_df['Status'].isin(status_filter)]
        
        # Display drivers
        st.dataframe(
            filtered_df,
            column_config={
                "ID": "Driver ID",
                "Name": "Full Name",
                "Phone": "Phone",
                "Email": "Email",
                "License": "License #",
                "Status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["Available", "On Trip", "Break", "Offline"],
                    required=True
                ),
                "Rating": st.column_config.NumberColumn(
                    "Rating",
                    format="%.1f ⭐",
                    min_value=0,
                    max_value=5
                ),
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
        with st.form("add_driver_form"):
            st.subheader("Add New Driver")
            
            col1, col2 = st.columns(2)
            
            with col1:
                driver_id = st.text_input("Driver ID *", value=f"DRV-{len(st.session_state.drivers_db) + 1:03d}")
                name = st.text_input("Full Name *")
                phone = st.text_input("Phone Number *")
                email = st.text_input("Email Address")
            
            with col2:
                license_number = st.text_input("License Number *")
                initial_status = st.selectbox(
                    "Initial Status",
                    options=["Available", "On Trip", "Break", "Offline"],
                    index=0
                )
                initial_rating = st.slider("Initial Rating", 1.0, 5.0, 5.0, 0.1)
            
            submitted = st.form_submit_button("➕ Add Driver", type="primary")
            
            if submitted:
                if not all([driver_id, name, phone, license_number]):
                    st.error("Please fill in all required fields (*)")
                else:
                    # Add new driver to session state
                    new_driver = {
                        'ID': driver_id,
                        'Name': name,
                        'Phone': phone,
                        'Email': email,
                        'License': license_number,
                        'Status': initial_status,
                        'Rating': initial_rating,
                        'Total Trips': 0,
                        'Total Earnings': 0.0
                    }
                    
                    # Update the DataFrame
                    st.session_state.drivers_db = pd.concat([
                        st.session_state.drivers_db,
                        pd.DataFrame([new_driver])
                    ], ignore_index=True)
                    
                    st.success(f"Driver {name} added successfully!")
                    st.balloons()
                    st.rerun()

elif page == "Car Management":
    st.title("🚗 Car Management")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Fleet Overview")
        st.dataframe(
            st.session_state.cars_db,
            column_config={
                "Plate": "License Plate",
                "Model": "Car Model",
                "Year": "Year",
                "Driver": "Assigned Driver",
                "Status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["Active", "Maintenance", "Retired"],
                    required=True
                ),
                "Last Service": "Last Service Date"
            },
            hide_index=True,
            use_container_width=True
        )
    
    with col2:
        st.subheader("Add New Car")
        with st.form("add_car_form"):
            plate = st.text_input("License Plate *")
            model = st.text_input("Car Model *")
            year = st.number_input("Year", min_value=2000, max_value=2025, value=2023)
            driver = st.selectbox(
                "Assign Driver",
                options=["Unassigned"] + list(st.session_state.drivers_db['Name'])
            )
            
            submitted = st.form_submit_button("➕ Add Car")
            
            if submitted and plate and model:
                new_car = {
                    'Plate': plate,
                    'Model': model,
                    'Year': year,
                    'Driver': driver if driver != "Unassigned" else "",
                    'Status': "Active",
                    'Last Service': datetime.now().strftime('%Y-%m-%d')
                }
                
                st.session_state.cars_db = pd.concat([
                    st.session_state.cars_db,
                    pd.DataFrame([new_car])
                ], ignore_index=True)
                
                st.success(f"Car {plate} added to fleet!")
                st.rerun()

elif page == "Reports":
    st.title("📈 Reports")
    
    tab1, tab2, tab3 = st.tabs(["Revenue Report", "Driver Performance", "Trip Analysis"])
    
    with tab1:
        st.subheader("Revenue Report")
        
        # Date range for report
        report_col1, report_col2 = st.columns(2)
        with report_col1:
            report_start = st.date_input("Report Start", value=datetime.now() - timedelta(days=30))
        with report_col2:
            report_end = st.date_input("Report End", value=datetime.now())
        
        # Filter trips by date
        filtered_trips = st.session_state.trips_db[
            (st.session_state.trips_db['Date'] >= report_start.strftime('%Y-%m-%d')) &
            (st.session_state.trips_db['Date'] <= report_end.strftime('%Y-%m-%d'))
        ]
        
        # Calculate metrics
        total_revenue = filtered_trips['Fare'].sum()
        total_trips = len(filtered_trips)
        avg_fare = total_revenue / total_trips if total_trips > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Revenue", f"${total_revenue:,.2f}")
        with col2:
            st.metric("Total Trips", total_trips)
        with col3:
            st.metric("Average Fare", f"${avg_fare:,.2f}")
        
        # Revenue by driver
        st.subheader("Revenue by Driver")
        revenue_by_driver = filtered_trips.groupby('Driver')['Fare'].sum().sort_values(ascending=False)
        st.bar_chart(revenue_by_driver)
    
    with tab2:
        st.subheader("Driver Performance")
        
        # Performance metrics
        performance_df = st.session_state.drivers_db.copy()
        performance_df = performance_df.sort_values('Rating', ascending=False)
        
        st.dataframe(
            performance_df[['Name', 'Rating', 'Total Trips', 'Total Earnings']],
            column_config={
                "Name": "Driver",
                "Rating": st.column_config.NumberColumn("Rating", format="%.1f ⭐"),
                "Total Trips": "Total Trips",
                "Total Earnings": st.column_config.NumberColumn("Total Earnings", format="$%.2f")
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Rating distribution
        st.subheader("Rating Distribution")
        rating_counts = performance_df['Rating'].value_counts().sort_index()
        st.bar_chart(rating_counts)

elif page == "Settings":
    st.title("⚙️ Settings")
    
    st.subheader("Application Settings")
    
    # General settings
    company_name = st.text_input("Company Name", value="Taxi Manager Pro")
    currency = st.selectbox("Currency", ["USD", "EUR", "GBP", "CAD"], index=0)
    timezone = st.selectbox("Timezone", ["EST", "CST", "PST", "GMT"], index=0)
    
    # Data management
    st.subheader("Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Reset Demo Data", type="secondary"):
            # Reset all session states
            keys = list(st.session_state.keys())
            for key in keys:
                del st.session_state[key]
            st.rerun()
    
    with col2:
        if st.button("💾 Export All Data", type="secondary"):
            # Create downloadable files
            drivers_csv = st.session_state.drivers_db.to_csv(index=False)
            cars_csv = st.session_state.cars_db.to_csv(index=False)
            trips_csv = st.session_state.trips_db.to_csv(index=False)
            
            st.download_button(
                label="Download Drivers CSV",
                data=drivers_csv,
                file_name="drivers_export.csv",
                mime="text/csv"
            )
            
            st.download_button(
                label="Download Cars CSV",
                data=cars_csv,
                file_name="cars_export.csv",
                mime="text/csv"
            )
            
            st.download_button(
                label="Download Trips CSV",
                data=trips_csv,
                file_name="trips_export.csv",
                mime="text/csv"
            )
    
    # About section
    st.subheader("About")
    st.markdown("""
    **Taxi Manager Pro v1.0**
    
    A comprehensive taxi fleet management solution.
    
    Features:
    - Driver management and tracking
    - Car fleet management
    - Trip dispatch and tracking
    - Revenue reporting and analytics
    - Real-time dashboard
    
    © 2025 Taxi Manager Pro. All rights reserved.
    """)

# --- FOOTER ---
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns(3)
with footer_col1:
    st.caption(f"© {datetime.now().year} Taxi Manager Pro")
with footer_col2:
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
with footer_col3:
    st.caption(f"v1.0.0 • {len(st.session_state.drivers_db)} drivers • {len(st.session_state.cars_db)} cars")
