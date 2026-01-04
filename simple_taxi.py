# Simple Taxi Manager - No Dependencies Needed
import sqlite3
import os
from datetime import datetime

class TaxiManager:
    def __init__(self):
        self.db_name = "taxi_simple.db"
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        # Create drivers table
        c.execute('''
            CREATE TABLE IF NOT EXISTS drivers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                license TEXT UNIQUE NOT NULL,
                phone TEXT,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        # Create cars table
        c.execute('''
            CREATE TABLE IF NOT EXISTS cars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model TEXT NOT NULL,
                cpnc TEXT UNIQUE NOT NULL,
                plate TEXT UNIQUE NOT NULL,
                status TEXT DEFAULT 'available'
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def execute_query(self, query, params=(), fetch=False):
        """Execute SQL query"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute(query, params)
        
        if fetch:
            result = c.fetchall()
            conn.close()
            return result
        
        conn.commit()
        conn.close()
        return c.lastrowid
    
    def add_driver(self, name, license, phone):
        """Add a new driver"""
        try:
            self.execute_query(
                "INSERT INTO drivers (name, license, phone) VALUES (?, ?, ?)",
                (name, license, phone)
            )
            return True
        except:
            return False
    
    def add_car(self, model, cpnc, plate):
        """Add a new car"""
        try:
            self.execute_query(
                "INSERT INTO cars (model, cpnc, plate) VALUES (?, ?, ?)",
                (model, cpnc, plate)
            )
            return True
        except:
            return False
    
    def get_drivers(self):
        """Get all drivers"""
        return self.execute_query("SELECT * FROM drivers ORDER BY id", fetch=True)
    
    def get_cars(self):
        """Get all cars"""
        return self.execute_query("SELECT * FROM cars ORDER BY id", fetch=True)

def main():
    """Main function with simple text menu"""
    manager = TaxiManager()
    
    while True:
        print("\n" + "="*50)
        print("TAXI MANAGER SYSTEM")
        print("="*50)
        print("1. View Dashboard")
        print("2. Add Driver")
        print("3. Add Car")
        print("4. View All Drivers")
        print("5. View All Cars")
        print("6. Exit")
        print("="*50)
        
        choice = input("Enter your choice (1-6): ")
        
        if choice == "1":
            # Dashboard
            drivers = manager.get_drivers()
            cars = manager.get_cars()
            
            print("\n" + "="*50)
            print("DASHBOARD")
            print("="*50)
            print(f"Total Drivers: {len(drivers)}")
            print(f"Total Cars: {len(cars)}")
            print("-"*50)
            
            print("\nRecent Drivers:")
            if drivers:
                for driver in drivers[-5:]:  # Last 5 drivers
                    print(f"  - {driver[1]} (License: {driver[2]}, Phone: {driver[3]})")
            else:
                print("  No drivers found")
            
            print("\nRecent Cars:")
            if cars:
                for car in cars[-5:]:  # Last 5 cars
                    print(f"  - {car[1]} (CPNC: {car[2]}, Plate: {car[3]})")
            else:
                print("  No cars found")
        
        elif choice == "2":
            # Add Driver
            print("\n" + "="*50)
            print("ADD NEW DRIVER")
            print("="*50)
            name = input("Driver Name: ")
            license = input("License Number: ")
            phone = input("Phone Number: ")
            
            if manager.add_driver(name, license, phone):
                print(f"\n✓ Driver '{name}' added successfully!")
            else:
                print(f"\n✗ Error adding driver. License might already exist.")
        
        elif choice == "3":
            # Add Car
            print("\n" + "="*50)
            print("ADD NEW CAR")
            print("="*50)
            model = input("Car Model (e.g., Ford): ")
            cpnc = input("CPNC Number: ")
            plate = input("Plate Number: ")
            
            if manager.add_car(model, cpnc, plate):
                print(f"\n✓ Car '{plate}' added successfully!")
            else:
                print(f"\n✗ Error adding car. CPNC or Plate might already exist.")
        
        elif choice == "4":
            # View Drivers
            drivers = manager.get_drivers()
            
            print("\n" + "="*50)
            print("ALL DRIVERS")
            print("="*50)
            
            if drivers:
                print("\nID | Name | License | Phone | Status")
                print("-"*50)
                for driver in drivers:
                    print(f"{driver[0]} | {driver[1]} | {driver[2]} | {driver[3]} | {driver[4]}")
            else:
                print("\nNo drivers found. Add some drivers first.")
        
        elif choice == "5":
            # View Cars
            cars = manager.get_cars()
            
            print("\n" + "="*50)
            print("ALL CARS")
            print("="*50)
            
            if cars:
                print("\nID | Model | CPNC | Plate | Status")
                print("-"*50)
                for car in cars:
                    print(f"{car[0]} | {car[1]} | {car[2]} | {car[3]} | {car[4]}")
            else:
                print("\nNo cars found. Add some cars first.")
        
        elif choice == "6":
            print("\nThank you for using Taxi Manager!")
            break
        
        else:
            print("\nInvalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
