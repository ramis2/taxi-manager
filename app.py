import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Taxi Manager",
    page_icon="🚕",
    layout="wide"
)

# Title
st.title("🚕 Taxi Manager")
st.success("✅ App deployed successfully!")

# SIMPLE NAVIGATION THAT WORKS
menu = st.sidebar.radio(
    "📋 Navigation",
    ["Dashboard", "Add Driver", "Driver Letters", "View Drivers", "Settings"]
)

# Initialize database
def init_db():
    conn = sqlite3.connect('taxi.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS drivers
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT, license TEXT, phone TEXT, 
                  status TEXT, date_added TEXT)''')
    conn.commit()
    conn.close()

init_db()

# DASHBOARD
if menu == "Dashboard":
    st.header("📊 Dashboard")
    
    conn = sqlite3.connect('taxi.db')
    df = pd.read_sql_query("SELECT * FROM drivers", conn)
    conn.close()
    
    if not df.empty:
        st.metric("Total Drivers", len(df))
        st.dataframe(df)
    else:
        st.info("No drivers yet. Add some in 'Add Driver' tab.")

# ADD DRIVER
elif menu == "Add Driver":
    st.header("👤 Add New Driver")
    
    with st.form("driver_form"):
        name = st.text_input("Full Name")
        license_no = st.text_input("License Number")
        phone = st.text_input("Phone Number")
        
        if st.form_submit_button("Save Driver"):
            if name and license_no:
                conn = sqlite3.connect('taxi.db')
                c = conn.cursor()
                c.execute("INSERT INTO drivers (name, license, phone, status, date_added) VALUES (?, ?, ?, ?, ?)",
                         (name, license_no, phone, 'active', datetime.now().strftime("%Y-%m-%d")))
                conn.commit()
                conn.close()
                st.success(f"Driver '{name}' added successfully!")
            else:
                st.error("Please fill in name and license")

# DRIVER LETTERS
elif menu == "Driver Letters":
    st.header("📄 Generate Driver Letter")
    
    conn = sqlite3.connect('taxi.db')
    df = pd.read_sql_query("SELECT * FROM drivers", conn)
    conn.close()
    
    if not df.empty:
        driver_names = df['name'].tolist()
        selected = st.selectbox("Select Driver", driver_names)
        
        if st.button("Generate Letter"):
            letter = f"""
            TO WHOM IT MAY CONCERN
            
            This certifies that {selected} is a registered taxi driver.
            
            Date: {datetime.now().strftime('%B %d, %Y')}
            
            Sincerely,
            Taxi Manager
            """
            
            st.text_area("Generated Letter", letter, height=200)
            
            st.download_button(
                "📥 Download Letter",
                letter,
                file_name=f"letter_{selected}.txt"
            )
    else:
        st.warning("No drivers found. Add drivers first.")

# VIEW DRIVERS
elif menu == "View Drivers":
    st.header("👥 All Drivers")
    
    conn = sqlite3.connect('taxi.db')
    df = pd.read_sql_query("SELECT * FROM drivers", conn)
    conn.close()
    
    if not df.empty:
        st.dataframe(df)
    else:
        st.info("No drivers in database")

# SETTINGS
elif menu == "Settings":
    st.header("⚙️ Settings")
    
    if st.button("Reset Database", type="secondary"):
        try:
            os.remove('taxi.db')
            st.success("Database reset. Refresh page.")
        except:
            st.error("No database to reset")

# Footer
st.sidebar.divider()
st.sidebar.caption("© 2024 Taxi Manager")
