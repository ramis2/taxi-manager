
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Taxi Manager", layout="wide")
st.title("🚕 Taxi Management System")

# Your app code continues here...
menu = st.sidebar.selectbox("Menu", ["Dashboard", "Data Entry", "Car Management"])

if menu == "Dashboard":
    st.header("Dashboard")
    st.write("Welcome to Taxi Manager!")
    
elif menu == "Data Entry":
    st.header("Data Entry")
    # Add your data entry forms
    
elif menu == "Car Management":
    st.header("Car Management")
    # Add your car management forms

