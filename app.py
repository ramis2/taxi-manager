import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

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

# For deletion logs
if 'deletion_logs' not in st.session_state:
    st.session_state.deletion_logs = []

# ========== SIDEBAR NAVIGATION ==========
with st.sidebar:
    st.title("🚖 Taxi Manager")
    
    # Navigation
    page = st.radio(
        "📌 NAVIGATION",
        ["Dashboard", "Data Entry", "Balance Summary", "Driver Management", "Delete Driver", "Reports", "Settings"],
        key="nav"
    )
    
    st.divider()
    
    # Quick stats in sidebar
    st.subheader("📊 Quick Stats")
    active_drivers = len(st.session_state.drivers_db[st.session_state.drivers_db['Status'] == 'Active'])
    total_balance = st.session_state.drivers_db['Balance'].sum()
    
    st.metric("Active Drivers", active_drivers)
    st.metric("Total Balance", f"${total_balance:,.2f}")
    
    st.divider()
    
    # Date filter
    date_range = st.date_input(
        "📅 Select Date Range",
        value=(datetime.now() - timedelta(days=30), datetime.now()),
        key="date_filter"
    )
    
    st.divider()
    st.caption("© 2024 Taxi Manager Pro v1.0")

# ========== DASHBOARD PAGE ==========
if page == "Dashboard":
    st.title("📊 Dashboard Overview")
    
    # Generate metrics
    total_revenue = 15289.50
    total_expenses = 9876.25
    total_profit = total_revenue - total_expenses
    total_unpaid = -1250.75
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("TOTAL REVENUE", f"${total_revenue:,.2f}", delta="+12.5%")
    
    with col2:
        st.metric("TOTAL EXPENSES", f"${total_expenses:,.2f}", delta="-3.2%")
    
    with col3:
        st.metric("NET PROFIT", f"${total_profit:,.2f}", delta="+8.7%")
    
    with col4:
        st.metric("OVERPAID", f"${total_unpaid:,.2f}", delta_color="off")
    
    # Recent activity
    st.subheader("Recent Activity")
    
    # Sample activity data
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
            vehicle_id = st.text_input("Vehicle ID", placeholder="VH-001")
            payment_method = st.selectbox("Payment Method", ["Cash", "Credit Card", "Digital"])
        
        description = st.text_area("Description")
        
        # SUBMIT BUTTON
        submitted = st.form_submit_button("💾 Save Transaction")
        
        if submitted:
            if amount <= 0:
                st.error("Amount must be greater than 0!")
            else:
                st.success(f"Transaction saved: ${amount:,.2f}")
                # In real app, save to database here

# ========== BALANCE SUMMARY PAGE ==========
elif page == "Balance Summary":
    st.title("💰 Balance Summary")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Overview", "👤 Driver Balances", "📈 Trends"])
    
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
    
    with tab2:
        st.subheader("Driver Balances")
        
        # Display driver balances
        st.dataframe(
            st.session_state.drivers_db[['ID', 'Name', 'Status', 'Balance']].style.format({
                'Balance': '${:,.2f}'
            }),
            use_container_width=True,
            hide_index=True
        )
        
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
        st.subheader("Trend Analysis")
        
        # Sample trend data
        dates = pd.date_range(start='2023-07-01', end='2024-01-15', freq='W')
        revenue_trend = np.random.normal(20000, 5000, len(dates)).cumsum() + 100000
        
        df_trend = pd.DataFrame({
            'Date': dates,
            'Revenue': revenue_trend
        })
        
        # Create chart
        fig = px.line(df_trend, x='Date', y='Revenue', title="Revenue Trend")
        st.plotly_chart(fig, use_container_width=True)

# ========== DRIVER MANAGEMENT PAGE ==========
elif page == "Driver Management":
    st.title("👥 Driver Management")
    
    # Tabs for different actions
    tab1, tab2, tab3 = st.tabs(["📋 View All Drivers", "➕ Add New Driver", "✏️ Edit Driver"])
    
    with tab1:
        st.subheader("All Drivers")
        st.dataframe(st.session_state.drivers_db, use_container_width=True, hide_index=True)
        
        # Export option
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
                    # Add new driver
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
                    # Update driver in database
                    idx = st.session_state.drivers_db[st.session_state.drivers_db['Name'] == driver_to_edit].index[0]
                    
                    st.session_state.drivers_db.at[idx, 'Name'] = edit_name
                    st.session_state.drivers_db.at[idx, 'Phone'] = edit_phone
                    st.session_state.drivers_db.at[idx, 'Status'] = edit_status
                    st.session_state.drivers_db.at[idx, 'Email'] = edit_email
                    st.session_state.drivers_db.at[idx, 'License'] = edit_license
                    st.session_state.drivers_db.at[idx, 'Balance'] = edit_balance
                    
                    st.success(f"✅ Driver {edit_name} updated successfully!")
                    st.rerun()

# ========== DELETE DRIVER PAGE ==========
elif page == "Delete Driver":
    st.title("🗑️ Delete Driver")
    
    # Display current drivers
    st.subheader("📋 Current Drivers")
    
    if st.session_state.drivers_db.empty:
        st.warning("No drivers in the system.")
    else:
        st.dataframe(st.session_state.drivers_db, use_container_width=True, hide_index=True)
    
    # DELETE FORM
    with st.form("delete_driver_form"):
        st.subheader("🚨 Delete Driver")
        
        # Get list of drivers for deletion
        driver_options = st.session_state.drivers_db['Name'].tolist()
        
        if driver_options:
            selected_driver = st.selectbox("Select Driver to Delete", driver_options)
            
            # Get driver details
            driver_data = st.session_state.drivers_db[
                st.session_state.drivers_db['Name'] == selected_driver
            ].iloc[0]
            
            # Show warning
            st.warning(f"**You are about to delete:**")
            
            col_info1, col_info2 = st.columns(2)
            with col_info1:
                st.write(f"**Name:** {driver_data['Name']}")
                st.write(f"**ID:** {driver_data['ID']}")
            with col_info2:
                st.write(f"**Status:** {driver_data['Status']}")
                st.write(f"**Balance:** ${driver_data['Balance']:,.2f}")
            
            # Confirmation
            confirmation = st.checkbox(
                "⚠️ I understand this action cannot be undone",
                value=False
            )
            
            reason = st.selectbox(
                "Reason for Deletion",
                ["Resignation", "Termination", "Inactivity", "Duplicate Entry", "Other"]
            )
            
            notes = st.text_area("Additional Notes")
            
            # SUBMIT BUTTON (disabled until confirmation)
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
                
                # Show confirmation
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
        report_type = st.selectbox("Report Type", ["Daily", "Weekly", "Monthly", "Driver Performance"])
        start_date = st.date_input("Start Date")
        end_date = st.date_input("End Date")
        
        # SUBMIT BUTTON
        generate = st.form_submit_button("📊 Generate Report")
        
        if generate:
            st.success(f"Generating {report_type} report...")

# ========== SETTINGS PAGE ==========
elif page == "Settings":
    st.title("⚙️ Settings")
    
    with st.form("settings_form"):
        company_name = st.text_input("Company Name", "Taxi Manager Pro")
        currency = st.selectbox("Currency", ["USD", "EUR", "GBP", "JPY"])
        date_format = st.selectbox("Date Format", ["YYYY-MM-DD", "MM/DD/YYYY", "DD/MM/YYYY"])
        
        # SUBMIT BUTTON
        save_settings = st.form_submit_button("💾 Save Settings")
        
        if save_settings:
            st.success("Settings saved!")

# ========== FOOTER ==========
st.divider()
st.caption("Taxi Manager Pro © 2024 | All data is stored locally in your session")
