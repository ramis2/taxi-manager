import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- SIMPLE PAGE CONFIG ---
st.set_page_config(
    page_title="Taxi Manager",
    page_icon="🚕",
    layout="wide"
)

# --- SIMPLE DATA ---
if 'drivers' not in st.session_state:
    st.session_state.drivers = pd.DataFrame({
        'ID': ["DRV-001", "DRV-002", "DRV-003"],
        'Name': ["John Smith", "Maria Garcia", "Robert Johnson"],
        'Phone': ["555-0101", "555-0102", "555-0103"],
        'CPNC': ["CPNC-1001", "CPNC-1002", "CPNC-1003"],
        'Status': ["Available", "On Trip", "Available"],
        'Latitude': [33.7550, 33.7860, 33.8460],
        'Longitude': [-84.3900, -84.3870, -84.3680]
    })

# --- SIMPLE APP ---
st.title("🚕 Atlanta Taxi Manager")

# Navigation
page = st.sidebar.selectbox(
    "Navigation",
    ["Dashboard", "Driver Map", "Add Driver"]
)

if page == "Dashboard":
    st.header("Dashboard")
    st.write(f"Total Drivers: {len(st.session_state.drivers)}")
    
    # Show drivers table
    st.dataframe(st.session_state.drivers)

elif page == "Driver Map":
    st.header("📍 Atlanta Driver Map")
    
    # Show map
    if not st.session_state.drivers.empty:
        st.map(st.session_state.drivers.rename(
            columns={'Latitude': 'lat', 'Longitude': 'lon'}
        ))

elif page == "Add Driver":
    st.header("Add New Driver")
    
    with st.form("add_form"):
        name = st.text_input("Driver Name")
        phone = st.text_input("Phone")
        cpnc = st.text_input("CPNC Number", placeholder="CPNC-0000")
        
        if st.form_submit_button("Add Driver"):
            if name and phone:
                # Generate ID
                new_id = f"DRV-{len(st.session_state.drivers) + 1:03d}"
                
                # Add to dataframe
                new_driver = pd.DataFrame([{
                    'ID': new_id,
                    'Name': name,
                    'Phone': phone,
                    'CPNC': cpnc if cpnc else f"CPNC-{1000 + len(st.session_state.drivers) + 1}",
                    'Status': 'Available',
                    'Latitude': 33.7490 + np.random.uniform(-0.05, 0.05),
                    'Longitude': -84.3880 + np.random.uniform(-0.05, 0.05)
                }])
                
                st.session_state.drivers = pd.concat([st.session_state.drivers, new_driver], ignore_index=True)
                st.success(f"Added {name}!")
                st.rerun()
