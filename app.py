# app.py - Complete Taxi Manager Streamlit App
import streamlit as st
import pandas as pd
import sqlite3
import json
from datetime import datetime
import io

# Set page configuration
st.set_page_config(
    page_title="Taxi Manager Pro",
    page_icon="🚕",
    layout="wide"
)

# Initialize database
def init_db():
    conn = sqlite3.connect('taxi_manager.db')
    c = conn.cursor()
    
    # Drivers table
    c.execute('''
        CREATE TABLE IF NOT EXISTS drivers (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT,
            vehicle_number TEXT,
            license_number TEXT,
            join_date TEXT,
            status TEXT DEFAULT 'Active',
            total_trips INTEGER DEFAULT 0,
            total_earnings REAL DEFAULT 0
        )
    ''')
    
    # Settings table
    c.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    
    # Default settings
    default_settings = [
        ('company_name', 'Taxi Manager Pro'),
        ('fare_per_km', '50'),
        ('currency', '₹'),
        ('report_email', 'admin@taximanager.com')
    ]
    
    c.executemany('''
        INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)
    ''', default_settings)
    
    conn.commit()
    conn.close()

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'dashboard'
if 'edit_driver_id' not in st.session_state:
    st.session_state.edit_driver_id = None
if 'delete_confirm' not in st.session_state:
    st.session_state.delete_confirm = None

# Initialize database
init_db()

# Database helper functions
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
    c.execute('''
        INSERT INTO drivers (id, name, phone, vehicle_number, license_number, join_date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', driver_data)
    conn.commit()
    conn.close()

def update_driver(driver_id, update_data):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        UPDATE drivers 
        SET name=?, phone=?, vehicle_number=?, license_number=?
        WHERE id=?
    ''', (*update_data, driver_id))
    conn.commit()
    conn.close()

def delete_driver(driver_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('DELETE FROM drivers WHERE id = ?', (driver_id,))
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
        c.execute('''
            INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)
        ''', (key, value))
    conn.commit()
    conn.close()

# Sidebar Navigation
st.sidebar.title("🚕 Taxi Manager")
st.sidebar.divider()

menu = st.sidebar.radio(
    "Navigation",
    ["📊 Dashboard", "👨‍✈️ Drivers", "📝 Reports", "⚙️ Settings"]
)

# Dashboard Page
if menu == "📊 Dashboard":
    st.title("📊 Dashboard")
    
    # Get drivers data
    drivers_df = get_drivers()
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Drivers",
            value=len(drivers_df),
            delta=f"+{len(drivers_df[drivers_df['status'] == 'Active'])} Active"
        )
    
    with col2:
        total_trips = drivers_df['total_trips'].sum() if not drivers_df.empty else 0
        st.metric(
            label="Total Trips",
            value=total_trips,
            delta="This Month"
        )
    
    with col3:
        total_earnings = drivers_df['total_earnings'].sum() if not drivers_df.empty else 0
        st.metric(
            label="Total Earnings",
            value=f"₹{total_earnings:,.2f}",
            delta="+12.5%"
        )
    
    with col4:
        inactive = len(drivers_df[drivers_df['status'] == 'Inactive']) if not drivers_df.empty else 0
        st.metric(
            label="Inactive Drivers",
            value=inactive,
            delta_color="inverse"
        )
    
    st.divider()
    
    # Recent Drivers Table
    st.subheader("👨‍✈️ Recent Drivers")
    if not drivers_df.empty:
        # Display only key columns
        display_df = drivers_df[['id', 'name', 'phone', 'vehicle_number', 'status', 'total_trips']]
        display_df = display_df.rename(columns={
            'id': 'ID',
            'name': 'Name',
            'phone': 'Phone',
            'vehicle_number': 'Vehicle',
            'status': 'Status',
            'total_trips': 'Trips'
        })
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("No drivers found. Add your first driver!")
    
    # Quick Actions
    st.subheader("⚡ Quick Actions")
    qcol1, qcol2, qcol3 = st.columns(3)
    
    with qcol1:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
    
    with qcol2:
        if st.button("📊 View Full Report", use_container_width=True):
            st.session_state.page = 'reports'
            st.rerun()
    
    with qcol3:
        if st.button("➕ Add New Driver", use_container_width=True):
            st.session_state.edit_driver_id = 'new'
            st.rerun()

# Drivers Management Page
elif menu == "👨‍✈️ Drivers":
    st.title("👨‍✈️ Driver Management")
    
    # Action buttons at top
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_term = st.text_input("🔍 Search drivers by name or ID", placeholder="Enter name or ID...")
    
    with col2:
        if st.button("➕ Add New Driver", type="primary", use_container_width=True):
            st.session_state.edit_driver_id = 'new'
            st.rerun()
    
    st.divider()
    
    # Get and filter drivers
    drivers_df = get_drivers()
    
    if search_term:
        mask = drivers_df['name'].str.contains(search_term, case=False) | drivers_df['id'].str.contains(search_term, case=False)
        drivers_df = drivers_df[mask]
    
    # Display drivers table with actions
    if not drivers_df.empty:
        for _, driver in drivers_df.iterrows():
            with st.container():
                cols = st.columns([1, 2, 2, 2, 2, 3])
                
                with cols[0]:
                    st.write(f"**{driver['id']}**")
                
                with cols[1]:
                    st.write(driver['name'])
                
                with cols[2]:
                    st.write(driver['phone'])
                
                with cols[3]:
                    st.write(driver['vehicle_number'])
                
                with cols[4]:
                    status_color = "🟢" if driver['status'] == 'Active' else "🔴"
                    st.write(f"{status_color} {driver['status']}")
                
                with cols[5]:
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button("✏️ Edit", key=f"edit_{driver['id']}", use_container_width=True):
                            st.session_state.edit_driver_id = driver['id']
                            st.rerun()
                    with col_btn2:
                        if st.button("🗑️ Delete", key=f"del_{driver['id']}", use_container_width=True):
                            st.session_state.delete_confirm = driver['id']
                            st.rerun()
                
                st.divider()
    else:
        st.info("No drivers found. Add your first driver!")
    
    # Add/Edit Driver Form (shown when edit_driver_id is set)
    if st.session_state.edit_driver_id:
        st.subheader("➕ Add New Driver" if st.session_state.edit_driver_id == 'new' else "✏️ Edit Driver")
        
        with st.form(key="driver_form"):
            if st.session_state.edit_driver_id == 'new':
                driver_id = st.text_input("Driver ID*", placeholder="DRV001")
                name = st.text_input("Full Name*", placeholder="John Doe")
                phone = st.text_input("Phone Number*", placeholder="+91 9876543210")
                vehicle = st.text_input("Vehicle Number*", placeholder="MH01AB1234")
                license = st.text_input("License Number", placeholder="DL123456789")
            else:
                driver_data = get_driver_by_id(st.session_state.edit_driver_id)
                driver_id = st.text_input("Driver ID*", value=driver_data[0], disabled=True)
                name = st.text_input("Full Name*", value=driver_data[1])
                phone = st.text_input("Phone Number*", value=driver_data[2])
                vehicle = st.text_input("Vehicle Number*", value=driver_data[3])
                license = st.text_input("License Number", value=driver_data[4])
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("💾 Save Driver", type="primary", use_container_width=True)
            with col2:
                cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
            
            if submit:
                if not all([driver_id, name, phone, vehicle]):
                    st.error("Please fill all required fields (*)")
                else:
                    try:
                        if st.session_state.edit_driver_id == 'new':
                            add_driver((driver_id, name, phone, vehicle, license, datetime.now().strftime("%Y-%m-%d")))
                            st.success(f"Driver {name} added successfully!")
                        else:
                            update_driver(driver_id, (name, phone, vehicle, license))
                            st.success(f"Driver {name} updated successfully!")
                        
                        st.session_state.edit_driver_id = None
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            
            if cancel:
                st.session_state.edit_driver_id = None
                st.rerun()
    
    # Delete Confirmation Dialog
    if st.session_state.delete_confirm:
        st.warning("⚠️ Confirm Deletion")
        driver_data = get_driver_by_id(st.session_state.delete_confirm)
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write(f"Delete driver **{driver_data[1]}** (ID: {driver_data[0]})?")
        with col2:
            if st.button("✅ Yes, Delete", type="primary", use_container_width=True):
                delete_driver(st.session_state.delete_confirm)
                st.success("Driver deleted successfully!")
                st.session_state.delete_confirm = None
                st.rerun()
        with col3:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state.delete_confirm = None
                st.rerun()

# Reports Page
elif menu == "📝 Reports":
    st.title("📝 Reports")
    
    # Report type selection
    report_type = st.selectbox(
        "Select Report Type",
        ["Driver Performance", "Financial Summary", "Vehicle Statistics", "Complete Export"]
    )
    
    # Date range filter
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=datetime.now().replace(day=1))
    with col2:
        end_date = st.date_input("End Date", value=datetime.now())
    
    # Get drivers data
    drivers_df = get_drivers()
    
    if report_type == "Driver Performance":
        st.subheader("🚗 Driver Performance Report")
        
        if not drivers_df.empty:
            # Create performance metrics
            performance_df = drivers_df[['name', 'total_trips', 'total_earnings', 'status']].copy()
            performance_df['avg_per_trip'] = performance_df['total_earnings'] / performance_df['total_trips'].replace(0, 1)
            performance_df = performance_df.round(2)
            
            # Display metrics
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Drivers in Report", len(performance_df))
                st.metric("Total Trips", performance_df['total_trips'].sum())
            with col2:
                st.metric("Total Earnings", f"₹{performance_df['total_earnings'].sum():,.2f}")
                st.metric("Average per Trip", f"₹{performance_df['avg_per_trip'].mean():,.2f}")
            
            # Display table
            st.dataframe(performance_df, use_container_width=True)
            
            # Download button
            csv = performance_df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"driver_performance_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No data available for report")
    
    elif report_type == "Financial Summary":
        st.subheader("💰 Financial Summary")
        
        if not drivers_df.empty:
            # Calculate financial metrics
            total_earnings = drivers_df['total_earnings'].sum()
            active_drivers = len(drivers_df[drivers_df['status'] == 'Active'])
            avg_earnings_per_driver = total_earnings / active_drivers if active_drivers > 0 else 0
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Earnings", f"₹{total_earnings:,.2f}")
            with col2:
                st.metric("Active Drivers", active_drivers)
            with col3:
                st.metric("Avg per Driver", f"₹{avg_earnings_per_driver:,.2f}")
            
            # Earnings by driver chart
            earnings_chart_df = drivers_df[['name', 'total_earnings']].sort_values('total_earnings', ascending=False)
            st.bar_chart(earnings_chart_df.set_index('name'))
        else:
            st.info("No financial data available")
    
    elif report_type == "Complete Export":
        st.subheader("📤 Complete Data Export")
        
        if not drivers_df.empty:
            # Show all data
            st.dataframe(drivers_df, use_container_width=True)
            
            # Export options
            export_format = st.radio("Export Format", ["CSV", "Excel", "JSON"])
            
            if export_format == "CSV":
                csv = drivers_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"taxi_drivers_export_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            elif export_format == "Excel":
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    drivers_df.to_excel(writer, sheet_name='Drivers', index=False)
                st.download_button(
                    label="📥 Download Excel",
                    data=output.getvalue(),
                    file_name=f"taxi_drivers_export_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:  # JSON
                json_data = drivers_df.to_json(orient='records', indent=2)
                st.download_button(
                    label="📥 Download JSON",
                    data=json_data,
                    file_name=f"taxi_drivers_export_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
        else:
            st.info("No data to export")

# Settings Page
elif menu == "⚙️ Settings":
    st.title("⚙️ Settings")
    
    # Get current settings
    current_settings = get_settings()
    
    with st.form("settings_form"):
        st.subheader("Company Settings")
        
        col1, col2 = st.columns(2)
        with col1:
            company_name = st.text_input("Company Name", value=current_settings.get('company_name', ''))
            fare_per_km = st.number_input("Fare per KM (₹)", value=float(current_settings.get('fare_per_km', 50)))
        
        with col2:
            currency = st.text_input("Currency Symbol", value=current_settings.get('currency', '₹'))
            report_email = st.text_input("Report Email", value=current_settings.get('report_email', ''))
        
        st.subheader("Application Settings")
        auto_backup = st.checkbox("Enable Auto Backup", value=True)
        backup_interval = st.selectbox("Backup Interval", ["Daily", "Weekly", "Monthly"], index=0)
        
        st.divider()
        
        col1, col2 = st.columns(2)
        with col1:
            save = st.form_submit_button("💾 Save Settings", type="primary", use_container_width=True)
        with col2:
            reset = st.form_submit_button("🔄 Reset to Defaults", use_container_width=True)
        
        if save:
            new_settings = {
                'company_name': company_name,
                'fare_per_km': str(fare_per_km),
                'currency': currency,
                'report_email': report_email,
                'auto_backup': str(auto_backup),
                'backup_interval': backup_interval
            }
            update_settings(new_settings)
            st.success("✅ Settings saved successfully!")
            st.rerun()
        
        if reset:
            update_settings({
                'company_name': 'Taxi Manager Pro',
                'fare_per_km': '50',
                'currency': '₹',
                'report_email': 'admin@taximanager.com'
            })
            st.success("✅ Settings reset to defaults!")
            st.rerun()
    
    st.divider()
    
    # Database Management
    st.subheader("Database Management")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📤 Backup Database", use_container_width=True):
            # Create backup
            import shutil
            shutil.copy2('taxi_manager.db', f'taxi_manager_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
            st.success("Database backup created!")
    
    with col2:
        if st.button("🔄 Reset All Data", type="secondary", use_container_width=True):
            st.warning("⚠️ This will delete all data!")
            confirm = st.checkbox("I understand this cannot be undone")
            if confirm and st.button("🚨 Confirm Reset"):
                conn = get_db_connection()
                c = conn.cursor()
                c.execute('DELETE FROM drivers')
                conn.commit()
                conn.close()
                st.error("All data has been reset!")
                st.rerun()

# Footer
st.divider()
st.caption(f"© 2024 Taxi Manager Pro | Version 1.0 | Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
