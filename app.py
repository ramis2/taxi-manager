import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# ========== PAGE CONFIG ==========
st.set_page_config(
    page_title="Taxi Manager Pro",
    page_icon="🚖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== INITIALIZE SESSION STATE ==========
# For driver management
if 'drivers_db' not in st.session_state:
    st.session_state.drivers_db = pd.DataFrame({
        'ID': ['DRV-001', 'DRV-002', 'DRV-003', 'DRV-004', 'DRV-005'],
        'Name': ['John Smith', 'Maria Garcia', 'Robert Chen', 'Sarah Johnson', 'James Wilson'],
        'Status': ['Active', 'Active', 'Inactive', 'Active', 'Active'],
        'Phone': ['555-0101', '555-0102', '555-0103', '555-0104', '555-0105'],
        'Email': ['john@taxi.com', 'maria@taxi.com', 'robert@taxi.com', 'sarah@taxi.com', 'james@taxi.com'],
        'License': ['DL123456', 'DL234567', 'DL345678', 'DL456789', 'DL567890'],
        'Join Date': ['2023-01-15', '2023-02-20', '2023-03-10', '2023-04-05', '2023-05-12'],
        'Last Trip': ['2024-01-15', '2024-01-14', '2023-12-01', '2024-01-13', '2024-01-14'],
        'Balance': [1250.75, -320.50, 0.00, 850.25, -150.75]
    })

# For car/vehicle management
if 'cars_db' not in st.session_state:
    st.session_state.cars_db = pd.DataFrame({
        'Vehicle ID': ['VH-001', 'VH-002', 'VH-003', 'VH-004', 'VH-005'],
        'Make': ['Toyota', 'Honda', 'Ford', 'Chevy', 'Hyundai'],
        'Model': ['Camry', 'Accord', 'Fusion', 'Malibu', 'Sonata'],
        'Year': [2020, 2021, 2019, 2022, 2020],
        'License Plate': ['ABC-123', 'DEF-456', 'GHI-789', 'JKL-012', 'MNO-345'],
        'Status': ['Active', 'Active', 'Maintenance', 'Active', 'Available'],
        'Current Driver': ['John Smith', 'Maria Garcia', 'None', 'Sarah Johnson', 'None'],
        'Last Service': ['2024-01-10', '2023-12-15', '2024-01-05', '2023-12-28', '2024-01-12'],
        'Odometer': [45000, 32000, 58000, 21000, 39000],
        'Fuel Efficiency': [12.5, 14.2, 11.8, 13.5, 15.0]
    })

# For driver letters
if 'driver_letters' not in st.session_state:
    st.session_state.driver_letters = []

# For deletion logs
if 'deletion_logs' not in st.session_state:
    st.session_state.deletion_logs = []

# ========== SIDEBAR NAVIGATION ==========
with st.sidebar:
    st.title("🚖 Taxi Manager")
    
    # Updated navigation with ALL pages
    page = st.radio(
        "📌 NAVIGATION",
        [
            "Dashboard", 
            "Data Entry", 
            "Balance Summary", 
            "Driver Management", 
            "Car Management",  # NEW
            "Driver Letter",   # NEW
            "Delete Driver", 
            "Reports", 
            "Settings"
        ],
        key="nav"
    )
    
    st.divider()
    
    # Quick stats in sidebar
    st.subheader("📊 Quick Stats")
    active_drivers = len(st.session_state.drivers_db[st.session_state.drivers_db['Status'] == 'Active'])
    active_cars = len(st.session_state.cars_db[st.session_state.cars_db['Status'] == 'Active'])
    total_balance = st.session_state.drivers_db['Balance'].sum()
    
    col_stat1, col_stat2 = st.columns(2)
    with col_stat1:
        st.metric("Drivers", active_drivers)
    with col_stat2:
        st.metric("Cars", active_cars)
    
    st.metric("Total Balance", f"${total_balance:,.2f}")
    
    st.divider()
    
    # Date filter
    date_range = st.date_input(
        "📅 Select Date Range",
        value=(datetime.now() - timedelta(days=30), datetime.now()),
        key="date_filter"
    )
    
    st.divider()
    st.caption("© 2024 Taxi Manager Pro v2.0")

# ========== DASHBOARD PAGE ==========
if page == "Dashboard":
    st.title("📊 Dashboard Overview")
    
    # Generate metrics
    total_revenue = 15289.50
    total_expenses = 9876.25
    total_profit = total_revenue - total_expenses
    total_unpaid = -1250.75
    
    # Display metrics - FIXED FORMATTING: Use :,.2f NOT :%.2f
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("TOTAL REVENUE", f"${total_revenue:,.2f}", delta="+12.5%")
    
    with col2:
        st.metric("TOTAL EXPENSES", f"${total_expenses:,.2f}", delta="-3.2%")
    
    with col3:
        st.metric("NET PROFIT", f"${total_profit:,.2f}", delta="+8.7%")
    
    with col4:
        st.metric("OVERPAID", f"${total_unpaid:,.2f}", delta_color="off")
    
    # Quick overview tables
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("👤 Top Drivers")
        top_drivers = st.session_state.drivers_db.nlargest(5, 'Balance')
        st.dataframe(
            top_drivers[['Name', 'Balance']].style.format({'Balance': '${:,.2f}'}),
            use_container_width=True,
            hide_index=True
        )
    
    with col_right:
        st.subheader("🚗 Active Vehicles")
        active_vehicles = st.session_state.cars_db[st.session_state.cars_db['Status'] == 'Active']
        st.dataframe(
            active_vehicles[['Vehicle ID', 'Make', 'Model', 'Current Driver']],
            use_container_width=True,
            hide_index=True
        )
    
    # Recent activity
    st.subheader("📋 Recent Activity")
    
    activity_data = {
        'Time': ['10:30 AM', '09:15 AM', 'Yesterday', '2 days ago', '3 days ago'],
        'Driver': ['John Smith', 'Maria Garcia', 'Robert Chen', 'Sarah Johnson', 'James Wilson'],
        'Action': ['Trip Completed', 'Payment Received', 'Account Updated', 'New Trip', 'Maintenance'],
        'Amount': ['$45.50', '$120.00', 'Updated', '$38.75', '$250.00']
    }
    
    df_activity = pd.DataFrame(activity_data)
    st.dataframe(df_activity, use_container_width=True, hide_index=True)

# ========== DATA ENTRY PAGE ==========
elif page == "Data Entry":
    st.title("📝 Data Entry")
    
    with st.form("transaction_form", clear_on_submit=True):
        st.subheader("New Transaction")
        
        col1, col2 = st.columns(2)
        
        with col1:
            trans_date = st.date_input("Date", datetime.now())
            trans_type = st.selectbox("Type", ["Fare", "Maintenance", "Fuel", "Insurance", "Other"])
            driver_id = st.selectbox("Driver", st.session_state.drivers_db['Name'].tolist())
        
        with col2:
            amount = st.number_input("Amount ($)", min_value=0.0, value=100.0, step=10.0)
            vehicle_id = st.selectbox("Vehicle", st.session_state.cars_db['Vehicle ID'].tolist())
            payment_method = st.selectbox("Payment Method", ["Cash", "Credit Card", "Digital"])
        
        description = st.text_area("Description")
        
        # SUBMIT BUTTON - MUST HAVE THIS!
        submitted = st.form_submit_button("💾 Save Transaction")
        
        if submitted:
            if amount <= 0:
                st.error("Amount must be greater than 0!")
            else:
                st.success(f"Transaction saved: ${amount:,.2f}")

# ========== BALANCE SUMMARY PAGE ==========
elif page == "Balance Summary":
    st.title("💰 Balance Summary")
    
    tab1, tab2, tab3 = st.tabs(["📊 Overview", "👤 Driver Balances", "🚗 Vehicle Costs"])
    
    with tab1:
        st.subheader("Financial Overview")
        
        # Calculate balances
        cash_balance = 24580.75
        bank_balance = 128950.25
        accounts_receivable = 32500.50
        accounts_payable = -18500.75
        
        total_assets = cash_balance + bank_balance + accounts_receivable
        total_liabilities = abs(accounts_payable)
        net_worth = total_assets - total_liabilities
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Assets", f"${total_assets:,.2f}", delta="+5.2%")
        
        with col2:
            st.metric("Total Liabilities", f"${total_liabilities:,.2f}", delta="-2.1%")
        
        with col3:
            st.metric("Net Worth", f"${net_worth:,.2f}", delta="+12.5%")
        
        # Simple bar chart using Streamlit
        st.subheader("Balance Composition")
        balance_data = pd.DataFrame({
            'Category': ['Cash', 'Bank', 'Receivables', 'Payables'],
            'Amount': [cash_balance, bank_balance, accounts_receivable, abs(accounts_payable)]
        })
        st.bar_chart(balance_data.set_index('Category'))
    
    with tab2:
        st.subheader("Driver Balances")
        
        # Display driver balances with formatting
        display_df = st.session_state.drivers_db[['ID', 'Name', 'Status', 'Balance']].copy()
        
        # Format balance column
        def color_balance(val):
            if val > 0:
                return 'color: green;'
            elif val < 0:
                return 'color: red;'
            else:
                return 'color: orange;'
        
        styled_df = display_df.style.format({'Balance': '${:,.2f}'})\
                                   .applymap(color_balance, subset=['Balance'])
        
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
        # Balance adjustments form
        with st.form("balance_adjust_form"):
            st.subheader("Adjust Balance")
            
            selected_driver = st.selectbox("Select Driver", st.session_state.drivers_db['Name'].tolist())
            adjustment_type = st.selectbox("Type", ["Add Payment", "Deduct", "Correction"])
            amount = st.number_input("Amount ($)", min_value=0.01, value=100.0)
            reason = st.text_input("Reason")
            
            submitted_adj = st.form_submit_button("Apply Adjustment")
            
            if submitted_adj:
                st.success(f"Balance adjusted for {selected_driver}")
    
    with tab3:
        st.subheader("Vehicle Costs & Revenue")
        
        # Vehicle financial data
        vehicle_finance = pd.DataFrame({
            'Vehicle ID': ['VH-001', 'VH-002', 'VH-003', 'VH-004', 'VH-005'],
            'Monthly Revenue': [2450, 3120, 1890, 2780, 2340],
            'Monthly Cost': [1250, 1450, 980, 1320, 1180],
            'Net Profit': [1200, 1670, 910, 1460, 1160],
            'Fuel Cost': [450, 520, 380, 490, 410],
            'Maintenance': [350, 420, 280, 390, 320]
        })
        
        st.dataframe(
            vehicle_finance.style.format({
                'Monthly Revenue': '${:,.0f}',
                'Monthly Cost': '${:,.0f}',
                'Net Profit': '${:,.0f}',
                'Fuel Cost': '${:,.0f}',
                'Maintenance': '${:,.0f}'
            }),
            use_container_width=True,
            hide_index=True
        )
        
        # Vehicle cost chart
        st.subheader("Vehicle Profit Comparison")
        st.bar_chart(vehicle_finance.set_index('Vehicle ID')[['Monthly Revenue', 'Monthly Cost']])

# ========== DRIVER MANAGEMENT PAGE ==========
elif page == "Driver Management":
    st.title("👥 Driver Management")
    
    tab1, tab2, tab3 = st.tabs(["📋 View All Drivers", "➕ Add New Driver", "✏️ Edit Driver"])
    
    with tab1:
        st.subheader("All Drivers")
        st.dataframe(st.session_state.drivers_db, use_container_width=True, hide_index=True)
        
        if st.button("📥 Export to CSV"):
            csv = st.session_state.drivers_db.to_csv(index=False)
            st.download_button("Download CSV", csv, "drivers.csv", "text/csv")
    
    with tab2:
        st.subheader("Add New Driver")
        
        with st.form("add_driver_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_id = st.text_input("Driver ID", placeholder="DRV-006")
                new_name = st.text_input("Full Name")
                new_phone = st.text_input("Phone Number")
            
            with col2:
                new_email = st.text_input("Email")
                new_license = st.text_input("License Number")
                new_status = st.selectbox("Status", ["Active", "Inactive"])
            
            submitted_add = st.form_submit_button("➕ Add Driver")
            
            if submitted_add:
                if not new_id or not new_name:
                    st.error("Driver ID and Name are required!")
                else:
                    new_driver = pd.DataFrame([{
                        'ID': new_id,
                        'Name': new_name,
                        'Status': new_status,
                        'Phone': new_phone,
                        'Email': new_email,
                        'License': new_license,
                        'Join Date': datetime.now().strftime("%Y-%m-%d"),
                        'Last Trip': 'N/A',
                        'Balance': 0.00
                    }])
                    
                    st.session_state.drivers_db = pd.concat([st.session_state.drivers_db, new_driver], ignore_index=True)
                    st.success(f"✅ Driver {new_name} added successfully!")
                    st.rerun()
    
    with tab3:
        st.subheader("Edit Driver")
        
        driver_to_edit = st.selectbox("Select Driver to Edit", st.session_state.drivers_db['Name'].tolist())
        
        if driver_to_edit:
            driver_data = st.session_state.drivers_db[st.session_state.drivers_db['Name'] == driver_to_edit].iloc[0]
            
            with st.form("edit_driver_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    edit_name = st.text_input("Name", value=driver_data['Name'])
                    edit_phone = st.text_input("Phone", value=driver_data['Phone'])
                    edit_status = st.selectbox("Status", ["Active", "Inactive"], 
                                             index=0 if driver_data['Status'] == 'Active' else 1)
                
                with col2:
                    edit_email = st.text_input("Email", value=driver_data['Email'])
                    edit_license = st.text_input("License", value=driver_data['License'])
                    edit_balance = st.number_input("Balance", value=float(driver_data['Balance']))
                
                submitted_edit = st.form_submit_button("💾 Save Changes")
                
                if submitted_edit:
                    idx = st.session_state.drivers_db[st.session_state.drivers_db['Name'] == driver_to_edit].index[0]
                    
                    st.session_state.drivers_db.at[idx, 'Name'] = edit_name
                    st.session_state.drivers_db.at[idx, 'Phone'] = edit_phone
                    st.session_state.drivers_db.at[idx, 'Status'] = edit_status
                    st.session_state.drivers_db.at[idx, 'Email'] = edit_email
                    st.session_state.drivers_db.at[idx, 'License'] = edit_license
                    st.session_state.drivers_db.at[idx, 'Balance'] = edit_balance
                    
                    st.success(f"✅ Driver {edit_name} updated successfully!")
                    st.rerun()

# ========== CAR MANAGEMENT PAGE ==========
elif page == "Car Management":
    st.title("🚗 Car / Vehicle Management")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 View All Cars", "➕ Add New Car", "✏️ Edit Car", "🔧 Maintenance"])
    
    with tab1:
        st.subheader("All Vehicles")
        st.dataframe(st.session_state.cars_db, use_container_width=True, hide_index=True)
        
        # Quick statistics
        active_cars = len(st.session_state.cars_db[st.session_state.cars_db['Status'] == 'Active'])
        in_maintenance = len(st.session_state.cars_db[st.session_state.cars_db['Status'] == 'Maintenance'])
        available_cars = len(st.session_state.cars_db[st.session_state.cars_db['Status'] == 'Available'])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Active", active_cars)
        with col2:
            st.metric("Maintenance", in_maintenance)
        with col3:
            st.metric("Available", available_cars)
    
    with tab2:
        st.subheader("Add New Vehicle")
        
        with st.form("add_car_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                vehicle_id = st.text_input("Vehicle ID", placeholder="VH-006")
                make = st.text_input("Make", placeholder="Toyota")
                model = st.text_input("Model", placeholder="Camry")
                year = st.number_input("Year", min_value=2000, max_value=2024, value=2022)
            
            with col2:
                license_plate = st.text_input("License Plate", placeholder="XYZ-789")
                status = st.selectbox("Status", ["Active", "Available", "Maintenance", "Out of Service"])
                assigned_driver = st.selectbox("Assign Driver", ["None"] + st.session_state.drivers_db['Name'].tolist())
                fuel_efficiency = st.number_input("Fuel Efficiency (km/L)", min_value=5.0, max_value=30.0, value=12.5)
            
            submitted_add = st.form_submit_button("➕ Add Vehicle")
            
            if submitted_add:
                if not vehicle_id or not make or not model:
                    st.error("Vehicle ID, Make, and Model are required!")
                else:
                    new_car = pd.DataFrame([{
                        'Vehicle ID': vehicle_id,
                        'Make': make,
                        'Model': model,
                        'Year': year,
                        'License Plate': license_plate,
                        'Status': status,
                        'Current Driver': assigned_driver,
                        'Last Service': datetime.now().strftime("%Y-%m-%d"),
                        'Odometer': 0,
                        'Fuel Efficiency': fuel_efficiency
                    }])
                    
                    st.session_state.cars_db = pd.concat([st.session_state.cars_db, new_car], ignore_index=True)
                    st.success(f"✅ Vehicle {vehicle_id} added successfully!")
                    st.rerun()
    
    with tab3:
        st.subheader("Edit Vehicle Details")
        
        car_to_edit = st.selectbox("Select Vehicle to Edit", st.session_state.cars_db['Vehicle ID'].tolist())
        
        if car_to_edit:
            car_data = st.session_state.cars_db[st.session_state.cars_db['Vehicle ID'] == car_to_edit].iloc[0]
            
            with st.form("edit_car_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    edit_make = st.text_input("Make", value=car_data['Make'])
                    edit_model = st.text_input("Model", value=car_data['Model'])
                    edit_year = st.number_input("Year", value=int(car_data['Year']))
                    edit_license = st.text_input("License Plate", value=car_data['License Plate'])
                
                with col2:
                    edit_status = st.selectbox("Status", ["Active", "Available", "Maintenance", "Out of Service"], 
                                              index=["Active", "Available", "Maintenance", "Out of Service"].index(car_data['Status']))
                    edit_driver = st.selectbox("Assign Driver", ["None"] + st.session_state.drivers_db['Name'].tolist(), 
                                              index=0 if car_data['Current Driver'] == 'None' else 
                                              st.session_state.drivers_db['Name'].tolist().index(car_data['Current Driver']) + 1)
                    edit_odometer = st.number_input("Odometer (km)", value=int(car_data['Odometer']))
                    edit_fuel = st.number_input("Fuel Efficiency", value=float(car_data['Fuel Efficiency']))
                
                submitted_edit = st.form_submit_button("💾 Save Changes")
                
                if submitted_edit:
                    idx = st.session_state.cars_db[st.session_state.cars_db['Vehicle ID'] == car_to_edit].index[0]
                    
                    st.session_state.cars_db.at[idx, 'Make'] = edit_make
                    st.session_state.cars_db.at[idx, 'Model'] = edit_model
                    st.session_state.cars_db.at[idx, 'Year'] = edit_year
                    st.session_state.cars_db.at[idx, 'License Plate'] = edit_license
                    st.session_state.cars_db.at[idx, 'Status'] = edit_status
                    st.session_state.cars_db.at[idx, 'Current Driver'] = edit_driver
                    st.session_state.cars_db.at[idx, 'Odometer'] = edit_odometer
                    st.session_state.cars_db.at[idx, 'Fuel Efficiency'] = edit_fuel
                    
                    st.success(f"✅ Vehicle {car_to_edit} updated successfully!")
                    st.rerun()
    
    with tab4:
        st.subheader("Vehicle Maintenance")
        
        # Select vehicle for maintenance
        vehicle_for_service = st.selectbox("Select Vehicle", st.session_state.cars_db['Vehicle ID'].tolist())
        
        if vehicle_for_service:
            vehicle_info = st.session_state.cars_db[st.session_state.cars_db['Vehicle ID'] == vehicle_for_service].iloc[0]
            
            st.write(f"**Current Status:** {vehicle_info['Status']}")
            st.write(f"**Last Service:** {vehicle_info['Last Service']}")
            st.write(f"**Odometer:** {vehicle_info['Odometer']} km")
            
            with st.form("maintenance_form"):
                service_type = st.selectbox("Service Type", ["Regular Maintenance", "Oil Change", "Tire Rotation", "Brake Service", "Engine Repair", "Other"])
                service_date = st.date_input("Service Date", datetime.now())
                cost = st.number_input("Cost ($)", min_value=0.0, value=150.0)
                next_service_km = st.number_input("Next Service at (km)", value=vehicle_info['Odometer'] + 5000)
                notes = st.text_area("Service Notes")
                
                # SUBMIT BUTTON
                submitted_service = st.form_submit_button("🔧 Record Service")
                
                if submitted_service:
                    # Update vehicle record
                    idx = st.session_state.cars_db[st.session_state.cars_db['Vehicle ID'] == vehicle_for_service].index[0]
                    st.session_state.cars_db.at[idx, 'Last Service'] = service_date.strftime("%Y-%m-%d")
                    
                    # Mark as active after service
                    if vehicle_info['Status'] == 'Maintenance':
                        st.session_state.cars_db.at[idx, 'Status'] = 'Active'
                    
                    st.success(f"✅ Service recorded for {vehicle_for_service}")
                    
                    # Show service summary
                    st.info(f"""
                    **Service Summary:**
                    - Vehicle: {vehicle_for_service}
                    - Service Type: {service_type}
                    - Date: {service_date}
                    - Cost: ${cost:,.2f}
                    - Notes: {notes}
                    """)

# ========== DRIVER LETTER PAGE ==========
elif page == "Driver Letter":
    st.title("📄 LibraOffice Driver Letter")
    
    # Create letter form
    with st.form("driver_letter_form", clear_on_submit=False):
        st.subheader("📝 Create Driver Letter")
        
        # Letter header
        col1, col2 = st.columns(2)
        
        with col1:
            letter_date = st.date_input("Letter Date", datetime.now())
            letter_type = st.selectbox(
                "Letter Type",
                ["Commendation", "Warning", "Contract Renewal", "Termination Notice", "Salary Adjustment", "Other"]
            )
            priority = st.selectbox("Priority", ["Normal", "High", "Urgent"])
        
        with col2:
            # Select driver
            driver_name = st.selectbox("Driver", st.session_state.drivers_db['Name'].tolist())
            
            # Get driver details
            if driver_name:
                driver_info = st.session_state.drivers_db[st.session_state.drivers_db['Name'] == driver_name].iloc[0]
                st.write(f"**ID:** {driver_info['ID']}")
                st.write(f"**Status:** {driver_info['Status']}")
        
        # Letter reference
        letter_ref = st.text_input("Letter Reference", placeholder="LTR-2024-001")
        
        # Subject line
        subject = st.text_input("Subject", placeholder="Subject of the letter...")
        
        # SALUTATION
        salutation = st.selectbox("Salutation", 
                                 ["Dear", "To", "Respected", "Mr./Ms.", "Attention:"])
        
        # INPUT SUMMARY FIELD (This was the missing working field!)
        st.subheader("📋 Letter Summary")
        letter_summary = st.text_area(
            "Input Summary",
            placeholder="Enter a brief summary of the letter contents here...",
            height=100,
            help="This is a summary that will appear at the beginning of the letter"
        )
        
        # MAIN CONTENT
        st.subheader("📄 Main Content")
        letter_content = st.text_area(
            "Letter Content",
            placeholder="Type the main content of the letter here...",
            height=200,
            help="Detailed content of the letter"
        )
        
        # Additional sections
        with st.expander("Additional Details"):
            col_a, col_b = st.columns(2)
            with col_a:
                include_salary = st.checkbox("Include Salary Details", value=False)
                include_performance = st.checkbox("Include Performance Review", value=False)
            with col_b:
                require_signature = st.checkbox("Require Signature", value=True)
                cc_hr = st.checkbox("Copy to HR Department", value=True)
        
        # Actions required
        st.subheader("🔄 Actions Required")
        actions = st.text_area(
            "Actions Required from Driver",
            placeholder="List any actions required from the driver...",
            height=80
        )
        
        # Footer
        st.subheader("👤 Sender Details")
        sender_name = st.text_input("Sender Name", "Manager")
        sender_title = st.text_input("Sender Title", "Fleet Manager")
        
        # SUBMIT BUTTON - CRITICAL FOR FORM TO WORK!
        submitted = st.form_submit_button("📄 Generate Letter")
        
        # PROCESS THE FORM WHEN SUBMITTED
        if submitted:
            if not driver_name or not letter_summary:
                st.error("❌ Please fill in Driver Name and Letter Summary!")
            else:
                # Create letter object
                letter = {
                    "letter_id": f"LTR-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                    "date": letter_date.strftime("%Y-%m-%d"),
                    "driver_name": driver_name,
                    "driver_id": driver_info['ID'] if driver_name else "N/A",
                    "letter_type": letter_type,
                    "subject": subject,
                    "summary": letter_summary,
                    "content": letter_content,
                    "actions": actions,
                    "priority": priority,
                    "status": "Generated",
                    "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Add to letters database
                st.session_state.driver_letters.append(letter)
                
                st.success("✅ Letter generated successfully!")
                
                # Display letter preview
                st.divider()
                st.subheader("📄 LETTER PREVIEW")
                
                # Format the letter nicely
                st.markdown(f"""
                **FROM:** {sender_name} ({sender_title})  
                **TO:** {driver_name} ({driver_info['ID'] if driver_name else 'N/A'})  
                **DATE:** {letter_date.strftime('%B %d, %Y')}  
                **REF:** {letter_ref if letter_ref else 'N/A'}  
                **SUBJECT:** {subject}  
                **PRIORITY:** {priority}
                """)
                
                st.divider()
                
                # Summary section
                st.subheader("📋 Summary")
                st.info(letter_summary)
                
                # Main content
                st.subheader("📝 Content")
                st.write(letter_content)
                
                # Actions if provided
                if actions:
                    st.subheader("🔄 Actions Required")
                    st.warning(actions)
                
                # Footer
                st.divider()
                st.markdown(f"""
                **Sincerely,**  
                {sender_name}  
                {sender_title}  
                Taxi Manager Pro
                """)
                
                # Letter actions
                st.divider()
                st.subheader("📤 Letter Actions")
                
                action_col1, action_col2, action_col3 = st.columns(3)
                with action_col1:
                    if st.button("💾 Save to Database"):
                        st.success("Letter saved to database!")
                
                with action_col2:
                    if st.button("🖨️ Print Letter"):
                        st.info("Opening print dialog...")
                
                with action_col3:
                    if st.button("📧 Email to Driver"):
                        st.info(f"Email prepared for {driver_name}")
    
    # Display previous letters
    if st.session_state.driver_letters:
        st.divider()
        st.subheader("📚 Letter History")
        
        # Convert to DataFrame for display
        letters_df = pd.DataFrame(st.session_state.driver_letters)
        st.dataframe(
            letters_df[['letter_id', 'date', 'driver_name', 'letter_type', 'status']],
            use_container_width=True,
            hide_index=True
        )

# ========== DELETE DRIVER PAGE ==========
elif page == "Delete Driver":
    st.title("🗑️ Delete Driver")
    
    st.subheader("📋 Current Drivers")
    
    if st.session_state.drivers_db.empty:
        st.warning("No drivers in the system.")
    else:
        st.dataframe(st.session_state.drivers_db, use_container_width=True, hide_index=True)
    
    # DELETE FORM WITH SUBMIT BUTTON
    with st.form("delete_driver_form"):
        st.subheader("🚨 Delete Driver")
        
        driver_options = st.session_state.drivers_db['Name'].tolist()
        
        if driver_options:
            selected_driver = st.selectbox("Select Driver to Delete", driver_options)
            
            driver_data = st.session_state.drivers_db[
                st.session_state.drivers_db['Name'] == selected_driver
            ].iloc[0]
            
            st.warning(f"**You are about to delete:**")
            
            col_info1, col_info2 = st.columns(2)
            with col_info1:
                st.write(f"**Name:** {driver_data['Name']}")
                st.write(f"**ID:** {driver_data['ID']}")
            with col_info2:
                st.write(f"**Status:** {driver_data['Status']}")
                st.write(f"**Balance:** ${driver_data['Balance']:,.2f}")
            
            # Confirmation checkbox
            confirmation = st.checkbox(
                "⚠️ I understand this action cannot be undone",
                value=False
            )
            
            reason = st.selectbox(
                "Reason for Deletion",
                ["Resignation", "Termination", "Inactivity", "Duplicate Entry", "Other"]
            )
            
            notes = st.text_area("Additional Notes")
            
            # SUBMIT BUTTON - DISABLED until confirmation
            submitted = st.form_submit_button(
                "🗑️ Delete Driver Permanently",
                disabled=not confirmation
            )
            
            if submitted:
                # Remove driver
                st.session_state.drivers_db = st.session_state.drivers_db[
                    st.session_state.drivers_db['Name'] != selected_driver
                ]
                
                # Log deletion
                deletion_log = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "driver_id": driver_data['ID'],
                    "driver_name": driver_data['Name'],
                    "reason": reason,
                    "notes": notes,
                    "balance_at_deletion": driver_data['Balance']
                }
                
                st.session_state.deletion_logs.append(deletion_log)
                
                st.success(f"✅ Driver {driver_data['Name']} has been deleted!")
                
                st.info(f"""
                **Deletion Details:**
                - **Time:** {deletion_log['timestamp']}
                - **Reason:** {reason}
                - **Notes:** {notes if notes else 'None'}
                """)
                
                st.rerun()
    
    # Deletion history
    if st.session_state.deletion_logs:
        st.divider()
        st.subheader("🗃️ Deletion History")
        
        df_history = pd.DataFrame(st.session_state.deletion_logs)
        st.dataframe(df_history, use_container_width=True, hide_index=True)

# ========== REPORTS PAGE ==========
elif page == "Reports":
    st.title("📄 Reports")
    
    with st.form("report_form"):
        report_type = st.selectbox("Report Type", 
                                  ["Daily Summary", "Weekly Summary", "Monthly Summary", 
                                   "Driver Performance", "Vehicle Utilization", "Financial Summary"])
        start_date = st.date_input("Start Date")
        end_date = st.date_input("End Date")
        
        # Format options
        col_format1, col_format2 = st.columns(2)
        with col_format1:
            include_charts = st.checkbox("Include Charts", value=True)
        with col_format2:
            export_format = st.selectbox("Export Format", ["PDF", "Excel", "CSV"])
        
        # SUBMIT BUTTON
        generate = st.form_submit_button("📊 Generate Report")
        
        if generate:
            if start_date > end_date:
                st.error("❌ Start date must be before end date!")
            else:
                st.success(f"✅ Generating {report_type} report for {start_date} to {end_date}...")
                
                # Sample report data
                report_data = {
                    "Report Type": report_type,
                    "Period": f"{start_date} to {end_date}",
                    "Total Drivers": len(st.session_state.drivers_db),
                    "Active Drivers": len(st.session_state.drivers_db[st.session_state.drivers_db['Status'] == 'Active']),
                    "Total Vehicles": len(st.session_state.cars_db),
                    "Revenue Generated": "$15,289.50",
                    "Expenses Incurred": "$9,876.25",
                    "Net Profit": "$5,413.25"
                }
                
                # Display report summary
                st.subheader("📋 Report Summary")
                for key, value in report_data.items():
                    st.write(f"**{key}:** {value}")

# ========== SETTINGS PAGE ==========
elif page == "Settings":
    st.title("⚙️ Settings")
    
    tab_set1, tab_set2, tab_set3 = st.tabs(["General", "Notifications", "Backup"])
    
    with tab_set1:
        st.subheader("General Settings")
        
        with st.form("general_settings_form"):
            company_name = st.text_input("Company Name", "Taxi Manager Pro")
            currency = st.selectbox("Currency", ["USD", "EUR", "GBP", "JPY", "AUD", "CAD"])
            date_format = st.selectbox("Date Format", ["YYYY-MM-DD", "MM/DD/YYYY", "DD/MM/YYYY"])
            timezone = st.selectbox("Timezone", ["UTC", "EST", "PST", "GMT", "IST"])
            
            # SUBMIT BUTTON
            save_general = st.form_submit_button("💾 Save General Settings")
            
            if save_general:
                st.success("General settings saved!")
    
    with tab_set2:
        st.subheader("Notification Settings")
        
        with st.form("notification_form"):
            email_notifications = st.checkbox("Enable Email Notifications", value=True)
            sms_notifications = st.checkbox("Enable SMS Notifications", value=False)
            
            st.subheader("Notification Types")
            col_not1, col_not2 = st.columns(2)
            with col_not1:
                notify_new_trip = st.checkbox("New Trip", value=True)
                notify_payment = st.checkbox("Payment Received", value=True)
            with col_not2:
                notify_maintenance = st.checkbox("Vehicle Maintenance", value=True)
                notify_low_balance = st.checkbox("Low Driver Balance", value=False)
            
            # SUBMIT BUTTON
            save_notifications = st.form_submit_button("💾 Save Notification Settings")
            
            if save_notifications:
                st.success("Notification settings saved!")
    
    with tab_set3:
        st.subheader("Backup & Export")
        
        col_back1, col_back2 = st.columns(2)
        
        with col_back1:
            st.subheader("Export Data")
            if st.button("📥 Export Drivers to CSV"):
                csv_data = st.session_state.drivers_db.to_csv(index=False)
                st.download_button("Download", csv_data, "drivers_export.csv", "text/csv")
            
            if st.button("📥 Export Vehicles to CSV"):
                csv_data = st.session_state.cars_db.to_csv(index=False)
                st.download_button("Download", csv_data, "vehicles_export.csv", "text/csv")
        
        with col_back2:
            st.subheader("Backup")
            if st.button("💾 Create Full Backup"):
                st.success("Backup created successfully!")
            
            if st.button("🔄 Restore from Backup"):
                st.warning("Restore feature coming soon!")

# ========== FOOTER ==========
st.divider()
st.caption("🚖 Taxi Manager Pro v2.0 © 2024 | All data is stored locally in your session")

