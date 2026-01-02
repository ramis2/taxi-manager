import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Taxi Manager", layout="wide")
st.title("🚕 Taxi Management System")
st.write("### Welcome to Taxi Manager")

menu = st.sidebar.selectbox("Navigation", ["Dashboard", "Car Management", "Driver Management"])

if menu == "Dashboard":
    st.header("Dashboard")
    st.write("Overview of your taxi fleet")
    
elif menu == "Car Management":
    st.header("Car Management")
    
    with st.form("add_car"):
        st.write("### Add New Car")
        car_model = st.text_input("Car Model")
        license_plate = st.text_input("License Plate")
        year = st.number_input("Year", min_value=2000, max_value=2026, value=2024)
        
        if st.form_submit_button("Add Car"):
            st.success(f"Car {car_model} added successfully!")
            
elif menu == "Driver Management":
    st.header("Driver Management")
    st.write("Manage your drivers here")
