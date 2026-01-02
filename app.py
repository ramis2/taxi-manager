i# 1
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json

# --- DATA PERSISTENCE FUNCTIONS ---
def save_data():
    """Save all data to CSV files"""
    try:
        if 'drivers_db' in st.session_state:
            st.session_state.drivers_db.to_csv('drivers.csv')  # Fixed filename
        if 'cars_db' in st.session_state:
            st.session_state.cars_db.to_csv('cars.csv')
        if 'rides_db' in st.session_state:
            st.session_state.rides_db.to_csv('rides.csv')
        return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False

# The rest of your app continues...
