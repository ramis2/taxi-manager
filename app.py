# app.py - Taxi Manager with CARS Page
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import io

# Set page configuration
st.set_page_config(
    page_title="Taxi Manager",
    layout="wide"
)

# Initialize database
def init_db():
    conn = sqlite3.connect('taxi_manager.db')
    c = conn.cursor()
    
    # Cars/Vehicles table (separate from drivers)
    c.execute('''
        CREATE TABLE IF NOT EXISTS cars (
            id TEXT PRIMARY KEY,
            vehicle_number TEXT UNIQUE NOT NULL,
            vehicle_type TEXT,
            model TEXT,
            year INTEGER,
            color TEXT,
            fuel_type TEXT,
            purchase_date TEXT,
            purchase_price REAL,
            insurance_number TEXT,
            insurance_expiry TEXT,
            status TEXT DEFAULT 'Active',
            assigned_driver TEXT,
            last_service TEXT,
            next_service TEXT,
            total_kms REAL DEFAULT 0,
            notes TEXT
        )
    ''')
    
    # Drivers table (simplified - references car by vehicle_number)
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
            email TEXT,
            salary REAL DEFAULT 0,
            commission_rate REAL DEFAULT 0.15,
            FOREIGN KEY (vehicle_number) REFERENCES cars (vehicle_number)
        )
    ''')
    
    # Payments table
    c.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            driver_id TEXT,
            payment_date TEXT,
            amount REAL,
            payment_type TEXT,
            description TEXT,
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY (driver_id) REFERENCES drivers (id)
        )
    ''')
    
    # Car maintenance table
    c.execute('''
        CREATE TABLE IF NOT EXISTS maintenance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_number TEXT,
            maintenance_date TEXT,
            service_type TEXT,
            cost REAL,
            description TEXT,
            next_service TEXT,
            status TEXT DEFAULT 'Completed',
            FOREIGN KEY (vehicle_number) REFERENCES cars (vehicle_number)
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
        ('company_phone
