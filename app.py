import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Taxi Manager",
    page_icon="🚕",
    layout="wide"
)

# Mobile CSS
st.markdown("""
<style>
    @media (max-width: 768px) {
        .stButton > button { width: 100% !important; height: 50px; font-size: 16px; }
        .stTextInput > div > input, 
        .stNumberInput > div > input,
        .stSelectbox > div > div,
        .stDateInput > div > input { 
            font-size: 16px !important; 
            height: 45px !important; 
        }
        h1 { font-size: 24px !important; }
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize database
@st.cache_resource
def init_db():
    conn = sqlite3.connect('taxi.db', check_same_thread=False)
    
    # Create payments table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            car_number TEXT NOT NULL,
            driver_name TEXT,
            amount REAL NOT NULL,
            payment_method TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create cars table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS cars (
            car_number TEXT PRIMARY KEY,
            model TEXT,
            year INTEGER,
            owner TEXT,
            owner_phone TEXT,
            insurance_expiry TEXT
        )
    ''')
    
    conn.commit()
    return conn

# Connect to database
conn = init_db()

# Navigation
st.sidebar.title("🚕 Navigation")
page = st.sidebar.radio("Go to:", 
    ["Dashboard", "Add Payment", "View Payments", "Car Management"])

# Dashboard Page
if page == "Dashboard":
    st.title("📊 Dashboard")
    
    # Quick stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        today = datetime.now().strftime("%Y-%m-%d")
        today_trips = conn.execute("SELECT COUNT(*) FROM payments WHERE date=?", (today,)).fetchone()[0]
        st.metric("Today's Trips", today_trips)
    
    with col2:
        today_earning = conn.execute("SELECT SUM(amount) FROM payments WHERE date=?", (today,)).fetchone()[0] or 0
        st.metric("Today's Earnings", f"₹{today_earning:,.0f}")
    
    with col3:
        total_cars = conn.execute("SELECT COUNT(*) FROM cars").fetchone()[0]
        st.metric("Total Cars", total_cars)
    
    # Recent trips
    st.subheader("Recent Trips")
    recent = pd.read_sql("SELECT date, car_number, driver_name, amount FROM payments ORDER BY id DESC LIMIT 10", conn)
    if not recent.empty:
        st.dataframe(recent, use_container_width=True)
    else:
        st.info("No trips yet. Add your first trip!")

# Add Payment Page
elif page == "Add Payment":
    st.title("💰 Add New Payment")
    
    with st.form("payment_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            date = st.date_input("Date", datetime.now())
            car_number = st.text_input("Car Number *", placeholder="KA01AB1234")
        
        with col2:
            driver_name = st.text_input("Driver Name")
            amount = st.number_input("Amount (₹) *", min_value=0.0, step=100.0)
        
        payment_method = st.selectbox("Payment Method", ["Cash", "UPI", "Card", "Wallet"])
        notes = st.text_area("Notes", placeholder="Any additional information...")
        
        submitted = st.form_submit_button("💾 SAVE PAYMENT", type="primary")
        
        if submitted:
            if car_number and amount > 0:
                try:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO payments (date, car_number, driver_name, amount, payment_method, notes)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (date.strftime("%Y-%m-%d"), car_number, driver_name, amount, payment_method, notes))
                    conn.commit()
                    st.success("✅ Payment saved successfully!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.error("Please fill required fields (Car Number and Amount)")

# View Payments Page
elif page == "View Payments":
    st.title("📋 Payment History")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        search_car = st.text_input("Search Car Number")
    with col2:
        filter_date = st.date_input("Filter by Date")
    
    # Build query
    query = "SELECT * FROM payments WHERE 1=1"
    params = []
    
    if search_car:
        query += " AND car_number LIKE ?"
        params.append(f"%{search_car}%")
    if filter_date:
        query += " AND date = ?"
        params.append(filter_date.strftime("%Y-%m-%d"))
    
    query += " ORDER BY date DESC"
    
    # Load data
    df = pd.read_sql_query(query, conn, params=params)
    
    if not df.empty:
        st.dataframe(df, use_container_width=True, height=400)
        
        # Summary
        total_amount = df['amount'].sum()
        total_trips = len(df)
        st.info(f"**Total:** {total_trips} payments | **Amount:** ₹{total_amount:,.0f}")
        
        # Export
        csv = df.to_csv(index=False)
        st.download_button(
            "📥 Download CSV",
            csv,
            "taxi_payments.csv",
            "text/csv"
        )
    else:
        st.warning("No payments found")

# Car Management Page
elif page == "Car Management":
    st.title("🚗 Car Management")
    
    tab1, tab2 = st.tabs(["Add/Edit Car", "View Cars"])
    
    with tab1:
        st.subheader("Add/Edit Car Details")
        
        with st.form("car_form"):
            car_number = st.text_input("Car Number *", placeholder="KA01AB1234")
            model = st.text_input("Car Model", placeholder="Toyota Innova")
            year = st.number_input("Year", min_value=2000, max_value=2024, value=2020)
            owner = st.text_input("Owner Name")
            owner_phone = st.text_input("Owner Phone")
            insurance = st.date_input("Insurance Expiry", datetime.now())
            
            submitted = st.form_submit_button("💾 SAVE CAR")
            
            if submitted and car_number:
                try:
                    conn.execute('''
                        INSERT OR REPLACE INTO cars 
                        (car_number, model, year, owner, owner_phone, insurance_expiry)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (car_number, model, year, owner, owner_phone, insurance.strftime("%Y-%m-%d")))
                    conn.commit()
                    st.success("✅ Car details saved!")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    with tab2:
        st.subheader("All Cars")
        cars = pd.read_sql("SELECT * FROM cars ORDER BY car_number", conn)
        if not cars.empty:
            st.dataframe(cars, use_container_width=True)
        else:
            st.info("No cars registered yet")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    📱 <b>Taxi Management System</b> | Deployed by ramis2
</div>
""", unsafe_allow_html=True)

