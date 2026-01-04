import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Taxi Manager", layout="wide")
st.title("🚕 Taxi Management System")

menu = st.sidebar.selectbox("Menu", ["Dashboard", "Data Entry", "Car Management"])

if menu == "Dashboard":
    st.header("Dashboard")
    st.write("Welcome to Taxi Manager!")
    
elif menu == "Data Entry":
    st.header("Data Entry")
    st.write("Data entry form will go here")
    
elif menu == "Car Management":
    st.header("Car Management")
    st.write("Car management form will go here")

