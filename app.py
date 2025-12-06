import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Taxi Manager",
    page_icon="🚕",
    layout="centered"  # Changed from "wide" to "centered"
)

# Better Mobile CSS
st.markdown("""
<style>
    /* Mobile optimization */
    @media (max-width: 768px) {
        .stButton > button { 
            width: 100% !important; 
            height: 60px !important; 
            font-size: 18px !important;
            margin: 5px 0 !important;
        }
        .stTextInput > div > input, 
        .stNumberInput > div > input,
        .stSelectbox > div > div,
        .stDateInput > div > input { 
            font-size: 18px !important; 
            height: 55px !important; 
            padding: 10px !important;
        }
        h1 { 
            font-size: 28px !important; 
            text-align: center !important;
        }
        h2 { font-size: 24px !important; }
        h3 { font-size: 20px !important; }
        .stDataFrame { font-size: 16px !important; }
        .stMetric { font-size: 20px !important; }
        .stRadio > div { flex-direction: column !important; }
        .stRadio > div > label { margin: 10px 0 !important; }
        .stForm { padding: 15px !important; }
        .element-container { padding: 10px !important; }
    }
    
    /* Better spacing for all devices */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Better card design */
    .card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        margin: 15px 0;
    }
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

# App Header
st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🚕 TAXI MANAGER</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px; color: #666;'>Manage your taxi business from phone</p>", unsafe_allow_html=True)

# Navigation - Better for mobile
st.markdown("---")
st.markdown("### 📱 Navigation")

# Create navigation buttons in grid
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

with col1:
    if st.button("📊 Dashboard", use_container_width=True):
        st.session_state.page = "dashboard"
with col2:
    if st.button("💰 Add Payment", use_container_width=True):
        st.session_state.page = "add_payment"
with col3:
    if st.button("📋 View Payments", use_container_width=True):
        st.session_state.page = "view_payments"
with col4:
    if st.button("🚗 Cars", use_container_width=True):
        st.session_state.page = "cars"

st.markdown("---")

# Set default page
if 'page' not in st.session_state:
    st.session_state.page = "dashboard"

# Dashboard Page
if st.session_state.page == "dashboard":
    st.markdown("<h2 style='text-align: center;'>📊 Dashboard</h2>", unsafe_allow_html=True)
    
    # Quick stats in card
    with st.container():
        col1, col2, col3 = st.columns(3)
        
        with col1:
            today = datetime.now().strftime("%Y-%m-%d")
            today_trips = conn.execute("SELECT COUNT(*) FROM payments WHERE date=?", (today,)).fetchone()[0]
            st.markdown(f"""
            <div class='card'>
                <div style='font-size: 16px; color: #666;'>Today's Trips</div>
                <div style='font-size: 32px; font-weight: bold; color: #FF4B4B;'>{today_trips}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            today_earning = conn.execute("SELECT SUM(amount) FROM payments WHERE date=?", (today,)).fetchone()[0] or 0
            st.markdown(f"""
            <div class='card'>
                <div style='font-size: 16px; color: #666;'>Today's Earnings</div>
                <div style='font-size: 32px; font-weight: bold; color: #4CAF50;'>₹{today_earning:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            total_cars = conn.execute("SELECT COUNT(*) FROM cars").fetchone()[0]
            st.markdown(f"""
            <div class='card'>
                <div style='font-size: 16px; color: #666;'>Total Cars</div>
                <div style='font-size: 32px; font-weight: bold; color: #2196F3;'>{total_cars}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Recent trips with better mobile view
    st.markdown("### 🕒 Recent Trips")
    recent = pd.read_sql("SELECT date, car_number, driver_name, amount FROM payments ORDER BY id DESC LIMIT 10", conn)
    if not recent.empty:
        # Format for mobile
        recent_display = recent.copy()
        recent_display['date'] = pd.to_datetime(recent_display['date']).dt.strftime('%d/%m')
        recent_display['amount'] = '₹' + recent_display['amount'].astype(str)
        
        st.dataframe(recent_display, use_container_width=True, height=300)
    else:
        st.info("No trips yet. Add your first trip!")

# Add Payment Page
elif st.session_state.page == "add_payment":
    st.markdown("<h2 style='text-align: center;'>💰 Add New Payment</h2>", unsafe_allow_html=True)
    
    with st.form("payment_form", clear_on_submit=True):
        st.markdown("### Enter Payment Details")
        
        # Date and Car Number
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("📅 Date", datetime.now(), key="date_input")
        with col2:
            car_number = st.text_input("🚗 Car Number *", placeholder="KA01AB1234", key="car_input")
        
        # Driver and Amount
        col1, col2 = st.columns(2)
        with col1:
            driver_name = st.text_input("👤 Driver Name", placeholder="Driver's name", key="driver_input")
        with col2:
            amount = st.number_input("💰 Amount (₹) *", min_value=0.0, step=100.0, key="amount_input")
        
        # Payment method and notes
        payment_method = st.selectbox("💳 Payment Method", ["Cash", "UPI", "Card", "Wallet"], key="method_input")
        notes = st.text_area("📝 Notes", placeholder="Any additional information...", height=100, key="notes_input")
        
        # Submit button
        submitted = st.form_submit_button("💾 SAVE PAYMENT", type="primary", use_container_width=True)
        
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
                    st.session_state.page = "dashboard"
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {e}")
            else:
                st.error("⚠️ Please fill required fields (Car Number and Amount)")

# View Payments Page
elif st.session_state.page == "view_payments":
    st.markdown("<h2 style='text-align: center;'>📋 Payment History</h2>", unsafe_allow_html=True)
    
    # Simple search
    search = st.text_input("🔍 Search by Car Number", placeholder="Enter car number...")
    
    # Build query
    if search:
        df = pd.read_sql("SELECT * FROM payments WHERE car_number LIKE ? ORDER BY date DESC", 
                         conn, params=[f"%{search}%"])
    else:
        df = pd.read_sql("SELECT * FROM payments ORDER BY date DESC", conn)
    
    if not df.empty:
        # Format for display
        df_display = df.copy()
        df_display['date'] = pd.to_datetime(df_display['date']).dt.strftime('%d/%m/%Y')
        df_display['amount'] = '₹' + df_display['amount'].astype(str)
        
        # Show summary
        total = df['amount'].sum()
        count = len(df)
        st.info(f"**Found:** {count} payments | **Total:** ₹{total:,.0f}")
        
        # Display data
        st.dataframe(df_display[['date', 'car_number', 'driver_name', 'amount', 'payment_method']], 
                    use_container_width=True, 
                    height=400)
        
        # Export
        csv = df.to_csv(index=False)
        st.download_button(
            "📥 Download CSV",
            csv,
            "taxi_payments.csv",
            "text/csv",
            use_container_width=True
        )
    else:
        st.warning("No payments found")

# Cars Page
elif st.session_state.page == "cars":
    st.markdown("<h2 style='text-align: center;'>🚗 Car Management</h2>", unsafe_allow_html=True)
    
    # Simple form to add car
    with st.form("car_form"):
        st.markdown("### Add/Edit Car")
        
        car_number = st.text_input("Car Number *", placeholder="KA01AB1234", key="car_num")
        model = st.text_input("Car Model", placeholder="Toyota Innova", key="model")
        year = st.number_input("Year", min_value=2000, max_value=2024, value=2020, key="year")
        
        col1, col2 = st.columns(2)
        with col1:
            owner = st.text_input("Owner Name", key="owner")
        with col2:
            owner_phone = st.text_input("Owner Phone", key="phone")
        
        if st.form_submit_button("💾 SAVE CAR", use_container_width=True):
            if car_number:
                try:
                    conn.execute('''
                        INSERT OR REPLACE INTO cars 
                        (car_number, model, year, owner, owner_phone)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (car_number, model, year, owner, owner_phone))
                    conn.commit()
                    st.success("✅ Car saved!")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
    
    st.markdown("---")
    st.markdown("### All Cars")
    
    cars = pd.read_sql("SELECT * FROM cars ORDER BY car_number", conn)
    if not cars.empty:
        st.dataframe(cars, use_container_width=True)
    else:
        st.info("No cars added yet")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 20px; color: #888; font-size: 14px;'>
    <p>📱 <b>Taxi Management System</b> | Mobile Optimized</p>
    <p>Bookmark this page on your phone for quick access</p>
</div>
""", unsafe_allow_html=True)

