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





_____________________________________
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py



----------------

streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0


-----------
Here's where and how to put all the code above in your Streamlit application:

WHERE TO PUT THE CODE:

File Structure:

```
your-project/
│
├── app.py              # Main Streamlit application file
├── requirements.txt    # Dependencies file
└── .streamlit/
    └── config.toml    # Streamlit configuration (optional)
```

1. Main Application File (app.py)

Put ALL your Streamlit code in one file called app.py:

```python
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
