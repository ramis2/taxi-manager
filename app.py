# app.py - Taxi Manager with Driver Letters Feature
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import io
import tempfile
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

# Set page configuration
st.set_page_config(
    page_title="Taxi Manager",
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
            total_earnings REAL DEFAULT 0,
            address TEXT,
            email TEXT
        )
    ''')
    
    # Letters/Notifications table
    c.execute('''
        CREATE TABLE IF NOT EXISTS letters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            driver_id TEXT,
            letter_type TEXT,
            subject TEXT,
            content TEXT,
            date_sent TEXT,
            status TEXT DEFAULT 'Draft',
            FOREIGN KEY (driver_id) REFERENCES drivers (id)
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
if 'current_letter_id' not in st.session_state:
    st.session_state.current_letter_id = None
if 'selected_drivers' not in st.session_state:
    st.session_state.selected_drivers = []

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
    c.execute('INSERT INTO drivers (id, name, phone, vehicle_number, license_number, join_date, address, email) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', driver_data)
    conn.commit()
    conn.close()

def update_driver(driver_id, update_data):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('UPDATE drivers SET name=?, phone=?, vehicle_number=?, license_number=?, address=?, email=? WHERE id=?', (*update_data, driver_id))
    conn.commit()
    conn.close()

def delete_driver(driver_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('DELETE FROM drivers WHERE id = ?', (driver_id,))
    conn.commit()
    conn.close()

def get_letters():
    conn = get_db_connection()
    df = pd.read_sql('SELECT * FROM letters ORDER BY date_sent DESC', conn)
    conn.close()
    return df

def get_letter_by_id(letter_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM letters WHERE id = ?', (letter_id,))
    letter_data = c.fetchone()
    conn.close()
    return letter_data

def save_letter(letter_data):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO letters (driver_id, letter_type, subject, content, date_sent, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', letter_data)
    conn.commit()
    conn.close()

def update_letter(letter_id, letter_data):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        UPDATE letters SET driver_id=?, letter_type=?, subject=?, content=?, date_sent=?, status=?
        WHERE id=?
    ''', (*letter_data, letter_id))
    conn.commit()
    conn.close()

def delete_letter(letter_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('DELETE FROM letters WHERE id = ?', (letter_id,))
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

# PDF Generation function
def generate_pdf_letter(driver_info, letter_type, subject, content, settings):
    buffer = io.BytesIO()
    
    # Create PDF
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom styles
    company_style = ParagraphStyle(
        'CompanyStyle',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=TA_CENTER,
        spaceAfter=30
    )
    
    driver_style = ParagraphStyle(
        'DriverStyle',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_LEFT,
        leftIndent=50
    )
    
    content_style = ParagraphStyle(
        'ContentStyle',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_LEFT,
        leading=14
    )
    
    # Build story (content)
    story = []
    
    # Company Header
    company_name = settings.get('company_name', 'Taxi Manager')
    company_address = settings.get('company_address', '123 Taxi Street, Mumbai')
    company_phone = settings.get('company_phone', '+91 22 12345678')
    
    story.append(Paragraph(company_name, company_style))
    story.append(Paragraph(company_address, styles['Normal']))
    story.append(Paragraph(f"Phone: {company_phone}", styles['Normal']))
    story.append(Spacer(1, 30))
    
    # Date
    story.append(Paragraph(f"Date: {datetime.now().strftime('%d %B, %Y')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Driver Address
    driver_name = driver_info[1] if driver_info else "Driver Name"
    driver_address = driver_info[8] if driver_info and len(driver_info) > 8 else "Driver Address"
    
    story.append(Paragraph(f"To,", styles['Normal']))
    story.append(Paragraph(f"{driver_name}", driver_style))
    if driver_address:
        story.append(Paragraph(f"{driver_address}", driver_style))
    story.append(Spacer(1, 30))
    
    # Subject
    story.append(Paragraph(f"<b>Subject: {subject}</b>", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Salutation
    story.append(Paragraph(f"Dear {driver_name},", styles['Normal']))
    story.append(Spacer(1, 10))
    
    # Content
    story.append(Paragraph(content, content_style))
    story.append(Spacer(1, 30))
    
    # Closing
    story.append(Paragraph("Yours sincerely,", styles['Normal']))
    story.append(Spacer(1, 40))
    story.append(Paragraph(settings.get('manager_name', 'Manager'), styles['Normal']))
    story.append(Paragraph(settings.get('company_name', 'Taxi Manager'), styles['Normal']))
    
    # Build PDF
    doc.build(story)
    
    buffer.seek(0)
    return buffer

# Sidebar Navigation
st.sidebar.title("TAXI MANAGER")
st.sidebar.divider()

menu = st.sidebar.radio(
    "NAVIGATION",
    ["DASHBOARD", "DRIVERS", "LETTERS", "REPORTS", "SETTINGS"]
)

# Dashboard Page
if menu == "DASHBOARD":
    st.title("DASHBOARD")
    
    drivers_df = get_drivers()
    letters_df = get_letters()
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        active_drivers = len(drivers_df[drivers_df['status'] == 'Active']) if not drivers_df.empty else 0
        st.metric(
            label="TOTAL DRIVERS",
            value=len(drivers_df),
            delta=f"+{active_drivers} Active"
        )
    
    with col2:
        total_trips = drivers_df['total_trips'].sum() if not drivers_df.empty else 0
        st.metric(
            label="TOTAL TRIPS",
            value=total_trips,
            delta="This Month"
        )
    
    with col3:
        total_letters = len(letters_df) if not letters_df.empty else 0
        st.metric(
            label="LETTERS SENT",
            value=total_letters,
            delta="This Month"
        )
    
    with col4:
        pending_letters = len(letters_df[letters_df['status'] == 'Draft']) if not letters_df.empty else 0
        st.metric(
            label="PENDING LETTERS",
            value=pending_letters,
            delta_color="inverse"
        )
    
    st.divider()
    
    # Quick Actions
    st.subheader("QUICK ACTIONS")
    qcol1, qcol2, qcol3, qcol4 = st.columns(4)
    
    with qcol1:
        if st.button("WRITE LETTER", use_container_width=True, type="primary"):
            st.session_state.current_letter_id = 'new'
            st.rerun()
    
    with qcol2:
        if st.button("VIEW DRIVERS", use_container_width=True):
            pass  # Already on drivers page
    
    with qcol3:
        if st.button("VIEW REPORTS", use_container_width=True):
            pass
    
    with qcol4:
        if st.button("ADD NEW DRIVER", use_container_width=True):
            st.session_state.edit_driver_id = 'new'
            st.rerun()

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
        if st.button("WRITE LETTER", use_container_width=True):
            st.session_state.current_letter_id = 'new'
            st.rerun()
    
    st.divider()
    
    drivers_df = get_drivers()
    
    if search_term:
        mask = drivers_df['name'].str.contains(search_term, case=False) | drivers_df['id'].str.contains(search_term, case=False)
        drivers_df = drivers_df[mask]
    
    if not drivers_df.empty:
        # Add checkbox for selecting drivers
        st.write("SELECT DRIVERS FOR LETTER:")
        
        for _, driver in drivers_df.iterrows():
            col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 2, 1])
            
            with col1:
                driver_id = driver['id']
                is_selected = driver_id in st.session_state.selected_drivers
                if st.checkbox("", key=f"select_{driver_id}", value=is_selected):
                    if driver_id not in st.session_state.selected_drivers:
                        st.session_state.selected_drivers.append(driver_id)
                else:
                    if driver_id in st.session_state.selected_drivers:
                        st.session_state.selected_drivers.remove(driver_id)
            
            with col2:
                st.write(f"**{driver['id']}**")
                st.write(driver['name'])
            
            with col3:
                st.write(driver['phone'])
                st.write(driver['vehicle_number'])
            
            with col4:
                status_text = f"[ACTIVE]" if driver['status'] == 'Active' else f"[INACTIVE]"
                st.write(status_text)
                if driver.get('email'):
                    st.write(driver['email'])
            
            with col5:
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("EDIT", key=f"edit_{driver['id']}", use_container_width=True):
                        st.session_state.edit_driver_id = driver['id']
                        st.rerun()
                with col_btn2:
                    if st.button("DELETE", key=f"del_{driver['id']}", use_container_width=True):
                        st.session_state.delete_confirm = driver['id']
                        st.rerun()
            
            st.divider()
        
        # Show selected drivers count
        if st.session_state.selected_drivers:
            selected_names = []
            for driver_id in st.session_state.selected_drivers:
                driver = get_driver_by_id(driver_id)
                if driver:
                    selected_names.append(driver[1])
            
            st.info(f"Selected {len(st.session_state.selected_drivers)} drivers: {', '.join(selected_names)}")
            
            if st.button("WRITE LETTER TO SELECTED DRIVERS", type="primary"):
                st.session_state.current_letter_id = 'new'
                st.rerun()
    else:
        st.info("No drivers found. Add your first driver!")
    
    # Add/Edit Driver Form
    if st.session_state.edit_driver_id:
        st.subheader("ADD NEW DRIVER" if st.session_state.edit_driver_id == 'new' else "EDIT DRIVER")
        
        with st.form(key="driver_form"):
            if st.session_state.edit_driver_id == 'new':
                driver_id = st.text_input("DRIVER ID*", placeholder="DRV001")
                name = st.text_input("FULL NAME*", placeholder="John Doe")
                phone = st.text_input("PHONE NUMBER*", placeholder="+91 9876543210")
                vehicle = st.text_input("VEHICLE NUMBER*", placeholder="MH01AB1234")
                license = st.text_input("LICENSE NUMBER", placeholder="DL123456789")
                address = st.text_area("ADDRESS", placeholder="Full postal address")
                email = st.text_input("EMAIL", placeholder="driver@email.com")
            else:
                driver_data = get_driver_by_id(st.session_state.edit_driver_id)
                driver_id = st.text_input("DRIVER ID*", value=driver_data[0], disabled=True)
                name = st.text_input("FULL NAME*", value=driver_data[1])
                phone = st.text_input("PHONE NUMBER*", value=driver_data[2])
                vehicle = st.text_input("VEHICLE NUMBER*", value=driver_data[3])
                license = st.text_input("LICENSE NUMBER", value=driver_data[4])
                address = st.text_area("ADDRESS", value=driver_data[8] if len(driver_data) > 8 else "")
                email = st.text_input("EMAIL", value=driver_data[9] if len(driver_data) > 9 else "")
            
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
                            add_driver((driver_id, name, phone, vehicle, license, datetime.now().strftime("%Y-%m-%d"), address, email))
                            st.success(f"Driver {name} added successfully!")
                        else:
                            update_driver(driver_id, (name, phone, vehicle, license, address, email))
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

# LETTERS PAGE - NEW FEATURE!
elif menu == "LETTERS":
    st.title("DRIVER LETTERS & NOTIFICATIONS")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_term = st.text_input("SEARCH LETTERS", placeholder="Search by subject or driver name...")
    
    with col2:
        if st.button("WRITE NEW LETTER", type="primary", use_container_width=True):
            st.session_state.current_letter_id = 'new'
            st.rerun()
    
    st.divider()
    
    # List existing letters
    letters_df = get_letters()
    
    if not letters_df.empty:
        st.subheader("PREVIOUS LETTERS")
        
        for _, letter in letters_df.iterrows():
            with st.expander(f"{letter['subject']} - {letter['date_sent']}"):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**To:** {letter['driver_id']}")
                    st.write(f"**Type:** {letter['letter_type']}")
                    st.write(f"**Status:** {letter['status']}")
                
                with col2:
                    if st.button("VIEW", key=f"view_{letter['id']}", use_container_width=True):
                        st.session_state.current_letter_id = letter['id']
                        st.rerun()
                
                with col3:
                    if st.button("DELETE", key=f"delete_letter_{letter['id']}", use_container_width=True):
                        delete_letter(letter['id'])
                        st.success("Letter deleted!")
                        st.rerun()
                
                st.write("---")
                st.write(letter['content'][:200] + "...")
    
    # Write New Letter / Edit Letter
    if st.session_state.current_letter_id:
        st.subheader("WRITE NEW LETTER" if st.session_state.current_letter_id == 'new' else "EDIT LETTER")
        
        drivers_df = get_drivers()
        settings = get_settings()
        
        with st.form(key="letter_form"):
            # Select driver(s)
            if st.session_state.current_letter_id == 'new':
                if st.session_state.selected_drivers:
                    st.info(f"Writing to {len(st.session_state.selected_drivers)} selected drivers")
                    driver_options = st.session_state.selected_drivers
                else:
                    driver_options = ["ALL DRIVERS"] + list(drivers_df['id'].unique())
                
                selected_driver = st.selectbox("SELECT DRIVER", driver_options)
                
                if selected_driver == "ALL DRIVERS":
                    selected_driver = "ALL"
            else:
                letter_data = get_letter_by_id(st.session_state.current_letter_id)
                selected_driver = st.text_input("DRIVER ID", value=letter_data[1] if letter_data else "")
            
            # Letter type
            letter_types = ["APPOINTMENT LETTER", "WARNING LETTER", "NOTICE", "PAYMENT REMINDER", "MEETING NOTICE", "GENERAL MESSAGE"]
            
            if st.session_state.current_letter_id == 'new':
                letter_type = st.selectbox("LETTER TYPE", letter_types)
                subject = st.text_input("SUBJECT", placeholder="Subject of the letter...")
            else:
                letter_type = st.selectbox("LETTER TYPE", letter_types, index=letter_types.index(letter_data[2]) if letter_data and letter_data[2] in letter_types else 0)
                subject = st.text_input("SUBJECT", value=letter_data[3] if letter_data else "")
            
            # Letter content templates
            st.write("QUICK TEMPLATES:")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("APPOINTMENT"):
                    st.session_state.letter_content = f"""We are pleased to appoint you as a driver with {settings.get('company_name', 'our company')}.

Your duties will include:
1. Safe transportation of passengers
2. Maintaining vehicle cleanliness
3. Following all traffic rules
4. Reporting daily earnings

Please report to the office on Monday at 9:00 AM for further instructions."""
            
            with col2:
                if st.button("WARNING"):
                    st.session_state.letter_content = f"""This is a formal warning regarding your recent conduct.

It has come to our attention that:
- [Specify issue]
- [Specify issue]

Please rectify these issues immediately. Failure to do so may result in further disciplinary action.

You are required to meet with the manager within 3 days to discuss this matter."""
            
            with col3:
                if st.button("MEETING"):
                    st.session_state.letter_content = f"""This is to inform you about an important meeting.

Date: [Enter Date]
Time: [Enter Time]
Venue: {settings.get('company_address', 'Office')}
Agenda: [Specify agenda]

Your attendance is mandatory. Please be punctual."""
            
            # Letter content
            if 'letter_content' not in st.session_state or st.session_state.current_letter_id != 'new':
                if st.session_state.current_letter_id == 'new':
                    default_content = f"""Dear Driver,



Yours sincerely,
{settings.get('manager_name', 'Manager')}
{settings.get('company_name', 'Taxi Manager')}"""
                else:
                    default_content = letter_data[4] if letter_data else ""
                st.session_state.letter_content = default_content
            
            content = st.text_area("LETTER CONTENT", value=st.session_state.letter_content, height=300)
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("SAVE & GENERATE PDF", type="primary", use_container_width=True)
            with col2:
                cancel = st.form_submit_button("CANCEL", use_container_width=True)
            
            if submit:
                if not all([selected_driver, letter_type, subject, content]):
                    st.error("Please fill all fields")
                else:
                    try:
                        if st.session_state.current_letter_id == 'new':
                            save_letter((selected_driver, letter_type, subject, content, datetime.now().strftime("%Y-%m-%d"), "Sent"))
                            st.success("Letter saved successfully!")
                        else:
                            update_letter(st.session_state.current_letter_id, (selected_driver, letter_type, subject, content, datetime.now().strftime("%Y-%m-%d"), "Sent"))
                            st.success("Letter updated successfully!")
                        
                        # Generate PDF
                        if selected_driver != "ALL":
                            driver_info = get_driver_by_id(selected_driver)
                            pdf_buffer = generate_pdf_letter(driver_info, letter_type, subject, content, settings)
                            
                            # Offer download
                            st.download_button(
                                label="DOWNLOAD PDF LETTER",
                                data=pdf_buffer,
                                file_name=f"Letter_{selected_driver}_{datetime.now().strftime('%Y%m%d')}.pdf",
                                mime="application/pdf"
                            )
                        
                        st.session_state.current_letter_id = None
                        st.session_state.selected_drivers = []
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            
            if cancel:
                st.session_state.current_letter_id = None
                st.rerun()

# Reports Page (simplified)
elif menu == "REPORTS":
    st.title("REPORTS")
    
    report_type = st.selectbox(
        "SELECT REPORT TYPE",
        ["DRIVER PERFORMANCE", "LETTERS HISTORY", "COMPLETE EXPORT"]
    )
    
    drivers_df = get_drivers()
    letters_df = get_letters()
    
    if report_type == "DRIVER PERFORMANCE":
        st.subheader("DRIVER PERFORMANCE REPORT")
        
        if not drivers_df.empty:
            st.dataframe(drivers_df, use_container_width=True)
            
            csv = drivers_df.to_csv(index=False)
            st.download_button(
                label="DOWNLOAD CSV",
                data=csv,
                file_name=f"driver_report_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No data available")
    
    elif report_type == "LETTERS HISTORY":
        st.subheader("LETTERS HISTORY")
        
        if not letters_df.empty:
            st.dataframe(letters_df, use_container_width=True)
            
            csv = letters_df.to_csv(index=False)
            st.download_button(
                label="DOWNLOAD CSV",
                data=csv,
                file_name=f"letters_history_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No letters sent yet")

# Settings Page (simplified)
elif menu == "SETTINGS":
    st.title("SETTINGS")
    
    current_settings = get_settings()
    
    with st.form("settings_form"):
        st.subheader("COMPANY SETTINGS")
        
        col1, col2 = st.columns(2)
        with col1:
            company_name = st.text_input("COMPANY NAME", value=current_settings.get('company_name', ''))
            fare_per_km = st.number_input("FARE PER KM", value=float(current_settings.get('fare_per_km', 50)))
            company_address = st.text_area("COMPANY ADDRESS", value=current_settings.get('company_address', ''))
        
        with col2:
            manager_name = st.text_input("MANAGER NAME", value=current_settings.get('manager_name', ''))
            company_phone = st.text_input("COMPANY PHONE", value=current_settings.get('company_phone', ''))
            report_email = st.text_input("REPORT EMAIL", value=current_settings.get('report_email', ''))
        
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
                'report_email': report_email
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
st.caption(f"Taxi Manager | Version 2.0 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
