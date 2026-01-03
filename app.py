from flask import Flask, render_template_string, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'taxi-manager-secret-key-2024'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///taxi_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    license_number = db.Column(db.String(50), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    status = db.Column(db.String(20), default='available')
    join_date = db.Column(db.DateTime, default=datetime.utcnow)
    
class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plate_number = db.Column(db.String(20), unique=True, nullable=False)
    make = db.Column(db.String(50))
    model = db.Column(db.String(50))
    year = db.Column(db.Integer)
    color = db.Column(db.String(30))
    status = db.Column(db.String(20), default='available')
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'))
    
class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20))
    pickup_address = db.Column(db.String(200), nullable=False)
    dropoff_address = db.Column(db.String(200), nullable=False)
    fare = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='pending')
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'))
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

# HTML TEMPLATES (all in one file)
BASE_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Taxi Manager - {title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        nav {{ background: #333; padding: 10px; margin-bottom: 20px; }}
        nav a {{ color: white; margin: 0 15px; text-decoration: none; }}
        .success {{ color: green; }}
        .error {{ color: red; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        form {{ max-width: 500px; }}
        input, select {{ width: 100%; padding: 8px; margin: 5px 0; }}
        button {{ background: #4CAF50; color: white; padding: 10px; border: none; cursor: pointer; }}
    </style>
</head>
<body>
    <nav>
        <a href="/">Home</a>
        <a href="/dashboard">Dashboard</a>
        <a href="/drivers">Drivers</a>
        <a href="/vehicles">Vehicles</a>
        <a href="/trips">Trips</a>
        <a href="/reports">Reports</a>
    </nav>
    
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="{{ category }}">{{ message }}</div>
            {% endfor %}
        {% endif %}
    {% endwith %}
    
    {content}
</body>
</html>
'''

INDEX_TEMPLATE = '''
<h1>Welcome to Taxi Management System</h1>
<p>Manage your taxi fleet efficiently.</p>
<h3>Quick Stats:</h3>
<ul>
    <li><a href="/drivers">Manage Drivers</a></li>
    <li><a href="/vehicles">Manage Vehicles</a></li>
    <li><a href="/trips">View All Trips</a></li>
    <li><a href="/reports">View Reports</a></li>
</ul>
'''

DASHBOARD_TEMPLATE = '''
<h1>Dashboard</h1>
<div style="display: flex; gap: 20px;">
    <div style="border: 1px solid #ddd; padding: 20px; width: 200px;">
        <h3>Total Drivers</h3>
        <p style="font-size: 24px;">{{ total_drivers }}</p>
    </div>
    <div style="border: 1px solid #ddd; padding: 20px; width: 200px;">
        <h3>Total Vehicles</h3>
        <p style="font-size: 24px;">{{ total_vehicles }}</p>
    </div>
    <div style="border: 1px solid #ddd; padding: 20px; width: 200px;">
        <h3>Active Trips</h3>
        <p style="font-size: 24px;">{{ active_trips }}</p>
    </div>
    <div style="border: 1px solid #ddd; padding: 20px; width: 200px;">
        <h3>Completed Trips</h3>
        <p style="font-size: 24px;">{{ completed_trips }}</p>
    </div>
</div>
'''

DRIVERS_TEMPLATE = '''
<h1>Drivers Management</h1>
<a href="/add_driver"><button>+ Add New Driver</button></a>
<br><br>
<table>
    <tr>
        <th>ID</th>
        <th>Name</th>
        <th>License Number</th>
        <th>Phone</th>
        <th>Email</th>
        <th>Status</th>
        <th>Actions</th>
    </tr>
    {% for driver in drivers %}
    <tr>
        <td>{{ driver.id }}</td>
        <td>{{ driver.name }}</td>
        <td>{{ driver.license_number }}</td>
        <td>{{ driver.phone }}</td>
        <td>{{ driver.email }}</td>
        <td>{{ driver.status }}</td>
        <td>
            <a href="/edit_driver/{{ driver.id }}">Edit</a>
            <a href="/delete_driver/{{ driver.id }}" onclick="return confirm('Delete this driver?')">Delete</a>
        </td>
    </tr>
    {% endfor %}
</table>
'''

ADD_DRIVER_TEMPLATE = '''
<h1>Add New Driver</h1>
<form method="POST">
    <label>Name:</label>
    <input type="text" name="name" required>
    
    <label>License Number:</label>
    <input type="text" name="license_number" required>
    
    <label>Phone:</label>
    <input type="text" name="phone">
    
    <label>Email:</label>
    <input type="email" name="email">
    
    <label>Status:</label>
    <select name="status">
        <option value="available">Available</option>
        <option value="busy">Busy</option>
        <option value="offline">Offline</option>
    </select>
    
    <br><br>
    <button type="submit">Add Driver</button>
    <a href="/drivers"><button type="button">Cancel</button></a>
</form>
'''

EDIT_DRIVER_TEMPLATE = '''
<h1>Edit Driver</h1>
<form method="POST">
    <label>Name:</label>
    <input type="text" name="name" value="{{ driver.name }}" required>
    
    <label>License Number:</label>
    <input type="text" name="license_number" value="{{ driver.license_number }}" required>
    
    <label>Phone:</label>
    <input type="text" name="phone" value="{{ driver.phone }}">
    
    <label>Email:</label>
    <input type="email" name="email" value="{{ driver.email }}">
    
    <label>Status:</label>
    <select name="status">
        <option value="available" {% if driver.status == 'available' %}selected{% endif %}>Available</option>
        <option value="busy" {% if driver.status == 'busy' %}selected{% endif %}>Busy</option>
        <option value="offline" {% if driver.status == 'offline' %}selected{% endif %}>Offline</option>
    </select>
    
    <br><br>
    <button type="submit">Update Driver</button>
    <a href="/drivers"><button type="button">Cancel</button></a>
</form>
'''

VEHICLES_TEMPLATE = '''
<h1>Vehicles Management</h1>
<a href="/add_vehicle"><button>+ Add New Vehicle</button></a>
<br><br>
<table>
    <tr>
        <th>ID</th>
        <th>Plate Number</th>
        <th>Make/Model</th>
        <th>Year</th>
        <th>Color</th>
        <th>Status</th>
        <th>Driver</th>
    </tr>
    {% for vehicle in vehicles %}
    <tr>
        <td>{{ vehicle.id }}</td>
        <td>{{ vehicle.plate_number }}</td>
        <td>{{ vehicle.make }} {{ vehicle.model }}</td>
        <td>{{ vehicle.year }}</td>
        <td>{{ vehicle.color }}</td>
        <td>{{ vehicle.status }}</td>
        <td>
            {% for driver in drivers %}
                {% if driver.id == vehicle.driver_id %}
                    {{ driver.name }}
                {% endif %}
            {% endfor %}
        </td>
    </tr>
    {% endfor %}
</table>
'''

ADD_VEHICLE_TEMPLATE = '''
<h1>Add New Vehicle</h1>
<form method="POST">
    <label>Plate Number:</label>
    <input type="text" name="plate_number" required>
    
    <label>Make:</label>
    <input type="text" name="make" required>
    
    <label>Model:</label>
    <input type="text" name="model" required>
    
    <label>Year:</label>
    <input type="number" name="year" min="2000" max="2024" required>
    
    <label>Color:</label>
    <input type="text" name="color">
    
    <label>Assign Driver (Optional):</label>
    <select name="driver_id">
        <option value="">No Driver</option>
        {% for driver in drivers %}
        <option value="{{ driver.id }}">{{ driver.name }} ({{ driver.license_number }})</option>
        {% endfor %}
    </select>
    
    <br><br>
    <button type="submit">Add Vehicle</button>
    <a href="/vehicles"><button type="button">Cancel</button></a>
</form>
'''

TRIPS_TEMPLATE = '''
<h1>Trips Management</h1>
<a href="/add_trip"><button>+ Add New Trip</button></a>
<br><br>
<table>
    <tr>
        <th>ID</th>
        <th>Customer</th>
        <th>Pickup</th>
        <th>Dropoff</th>
        <th>Fare</th>
        <th>Status</th>
        <th>Driver</th>
        <th>Created</th>
        <th>Actions</th>
    </tr>
    {% for trip in trips %}
    <tr>
        <td>{{ trip.id }}</td>
        <td>{{ trip.customer_name }}<br>{{ trip.customer_phone }}</td>
        <td>{{ trip.pickup_address }}</td>
        <td>{{ trip.dropoff_address }}</td>
        <td>${{ trip.fare }}</td>
        <td>{{ trip.status }}</td>
        <td>
            {% for driver in drivers %}
                {% if driver.id == trip.driver_id %}
                    {{ driver.name }}
                {% endif %}
            {% endfor %}
        </td>
        <td>{{ trip.created_at.strftime('%Y-%m-%d %H:%M') }}</td>
        <td>
            {% if trip.status == 'pending' %}
                <a href="/update_trip_status/{{ trip.id }}/ongoing">Start</a>
                <a href="/update_trip_status/{{ trip.id }}/cancelled">Cancel</a>
            {% elif trip.status == 'ongoing' %}
                <a href="/update_trip_status/{{ trip.id }}/completed">Complete</a>
            {% endif %}
        </td>
    </tr>
    {% endfor %}
</table>
'''

ADD_TRIP_TEMPLATE = '''
<h1>Add New Trip</h1>
<form method="POST">
    <label>Customer Name:</label>
    <input type="text" name="customer_name" required>
    
    <label>Customer Phone:</label>
    <input type="text" name="customer_phone" required>
    
    <label>Pickup Address:</label>
    <input type="text" name="pickup_address" required>
    
    <label>Dropoff Address:</label>
    <input type="text" name="dropoff_address" required>
    
    <label>Fare ($):</label>
    <input type="number" name="fare" step="0.01" min="0">
    
    <label>Assign Driver:</label>
    <select name="driver_id">
        <option value="">Select Driver</option>
        {% for driver in drivers %}
        <option value="{{ driver.id }}">{{ driver.name }} ({{ driver.status }})</option>
        {% endfor %}
    </select>
    
    <label>Assign Vehicle:</label>
    <select name="vehicle_id">
        <option value="">Select Vehicle</option>
        {% for vehicle in vehicles %}
        <option value="{{ vehicle.id }}">{{ vehicle.plate_number }} ({{ vehicle.make }} {{ vehicle.model }})</option>
        {% endfor %}
    </select>
    
    <br><br>
    <button type="submit">Add Trip</button>
    <a href="/trips"><button type="button">Cancel</button></a>
</form>
'''

REPORTS_TEMPLATE = '''
<h1>Reports</h1>
<div style="display: flex; gap: 20px; margin-bottom: 30px;">
    <div style="border: 1px solid #ddd; padding: 20px; width: 250px;">
        <h3>Total Trips</h3>
        <p style="font-size: 28px; color: #333;">{{ total_trips }}</p>
    </div>
    <div style="border: 1px solid #ddd; padding: 20px; width: 250px;">
        <h3>Completed Trips</h3>
        <p style="font-size: 28px; color: green;">{{ completed_trips }}</p>
    </div>
    <div style="border: 1px solid #ddd; padding: 20px; width: 250px;">
        <h3>Total Revenue</h3>
        <p style="font-size: 28px; color: blue;">${{ total_revenue }}</p>
    </div>
</div>

<h3>Recent Trips</h3>
<table>
    <tr>
        <th>Trip ID</th>
        <th>Customer</th>
        <th>Pickup</th>
        <th>Dropoff</th>
        <th>Fare</th>
        <th>Status</th>
        <th>Date</th>
    </tr>
    {% for trip in recent_trips %}
    <tr>
        <td>{{ trip.id }}</td>
        <td>{{ trip.customer_name }}</td>
        <td>{{ trip.pickup_address[:30] }}...</td>
        <td>{{ trip.dropoff_address[:30] }}...</td>
        <td>${{ trip.fare }}</td>
        <td>{{ trip.status }}</td>
        <td>{{ trip.created_at.strftime('%Y-%m-%d') }}</td>
    </tr>
    {% endfor %}
</table>
'''

# ROUTES
@app.route('/')
def index():
    return render_template_string(BASE_TEMPLATE.format(title="Home", content=INDEX_TEMPLATE))

@app.route('/dashboard')
def dashboard():
    total_drivers = Driver.query.count()
    total_vehicles = Vehicle.query.count()
    active_trips = Trip.query.filter_by(status='ongoing').count()
    completed_trips = Trip.query.filter_by(status='completed').count()
    
    return render_template_string(
        BASE_TEMPLATE.format(title="Dashboard", content=DASHBOARD_TEMPLATE),
        total_drivers=total_drivers,
        total_vehicles=total_vehicles,
        active_trips=active_trips,
        completed_trips=completed_trips
    )

@app.route('/drivers')
def drivers():
    all_drivers = Driver.query.all()
    return render_template_string(
        BASE_TEMPLATE.format(title="Drivers", content=DRIVERS_TEMPLATE),
        drivers=all_drivers
    )

@app.route('/add_driver', methods=['GET', 'POST'])
def add_driver():
    if request.method == 'POST':
        name = request.form['name']
        license_number = request.form['license_number']
        phone = request.form['phone']
        email = request.form['email']
        status = request.form.get('status', 'available')
        
        new_driver = Driver(
            name=name,
            license_number=license_number,
            phone=phone,
            email=email,
            status=status
        )
        
        try:
            db.session.add(new_driver)
            db.session.commit()
            flash('Driver added successfully!', 'success')
            return redirect(url_for('drivers'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding driver: {str(e)}', 'error')
    
    return render_template_string(BASE_TEMPLATE.format(title="Add Driver", content=ADD_DRIVER_TEMPLATE))

@app.route('/edit_driver/<int:driver_id>', methods=['GET', 'POST'])
def edit_driver(driver_id):
    driver = Driver.query.get_or_404(driver_id)
    
    if request.method == 'POST':
        driver.name = request.form['name']
        driver.license_number = request.form['license_number']
        driver.phone = request.form['phone']
        driver.email = request.form['email']
        driver.status = request.form['status']
        
        try:
            db.session.commit()
            flash('Driver updated successfully!', 'success')
            return redirect(url_for('drivers'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating driver: {str(e)}', 'error')
    
    return render_template_string(
        BASE_TEMPLATE.format(title="Edit Driver", content=EDIT_DRIVER_TEMPLATE),
        driver=driver
    )

@app.route('/delete_driver/<int:driver_id>')
def delete_driver(driver_id):
    driver = Driver.query.get_or_404(driver_id)
    
    try:
        db.session.delete(driver)
        db.session.commit()
        flash('Driver deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting driver: {str(e)}', 'error')
    
    return redirect(url_for('drivers'))

@app.route('/vehicles')
def vehicles():
    all_vehicles = Vehicle.query.all()
    drivers = Driver.query.all()
    return render_template_string(
        BASE_TEMPLATE.format(title="Vehicles", content=VEHICLES_TEMPLATE),
        vehicles=all_vehicles,
        drivers=drivers
    )

@app.route('/add_vehicle', methods=['GET', 'POST'])
def add_vehicle():
    if request.method == 'POST':
        plate_number = request.form['plate_number']
        make = request.form['make']
        model = request.form['model']
        year = request.form['year']
        color = request.form['color']
        driver_id = request.form.get('driver_id') or None
        
        new_vehicle = Vehicle(
            plate_number=plate_number,
            make=make,
            model=model,
            year=year,
            color=color,
            driver_id=driver_id
        )
        
        try:
            db.session.add(new_vehicle)
            db.session.commit()
            flash('Vehicle added successfully!', 'success')
            return redirect(url_for('vehicles'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding vehicle: {str(e)}', 'error')
    
    drivers = Driver.query.all()
    return render_template_string(
        BASE_TEMPLATE.format(title="Add Vehicle", content=ADD_VEHICLE_TEMPLATE),
        drivers=drivers
    )

@app.route('/trips')
def trips():
    all_trips = Trip.query.order_by(Trip.created_at.desc()).all()
    drivers = Driver.query.all()
    vehicles = Vehicle.query.all()
    return render_template_string(
        BASE_TEMPLATE.format(title="Trips", content=TRIPS_TEMPLATE),
        trips=all_trips,
        drivers=drivers,
        vehicles=vehicles
    )

@app.route('/add_trip', methods=['GET', 'POST'])
def add_trip():
    if request.method == 'POST':
        customer_name = request.form['customer_name']
        customer_phone = request.form['customer_phone']
        pickup_address = request.form['pickup_address']
        dropoff_address = request.form['dropoff_address']
        fare = request.form.get('fare', 0.0)
        driver_id = request.form.get('driver_id')
        vehicle_id = request.form.get('vehicle_id')
        
        new_trip = Trip(
            customer_name=customer_name,
            customer_phone=customer_phone,
            pickup_address=pickup_address,
            dropoff_address=dropoff_address,
            fare=fare,
            driver_id=driver_id,
            vehicle_id=vehicle_id
        )
        
        try:
            db.session.add(new_trip)
            db.session.commit()
            flash('Trip added successfully!', 'success')
            return redirect(url_for('trips'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding trip: {str(e)}', 'error')
    
    drivers = Driver.query.filter_by(status='available').all()
    vehicles = Vehicle.query.filter_by(status='available').all()
    return render_template_string(
        BASE_TEMPLATE.format(title="Add Trip", content=ADD_TRIP_TEMPLATE),
        drivers=drivers,
        vehicles=vehicles
    )

@app.route('/update_trip_status/<int:trip_id>/<status>')
def update_trip_status(trip_id, status):
    trip = Trip.query.get_or_404(trip_id)
    trip.status = status
    
    if status == 'completed':
        trip.completed_at = datetime.utcnow()
        # Free up driver and vehicle
        if trip.driver_id:
            driver = Driver.query.get(trip.driver_id)
            driver.status = 'available'
        if trip.vehicle_id:
            vehicle = Vehicle.query.get(trip.vehicle_id)
            vehicle.status = 'available'
    elif status == 'ongoing':
        # Mark driver and vehicle as busy
        if trip.driver_id:
            driver = Driver.query.get(trip.driver_id)
            driver.status = 'busy'
        if trip.vehicle_id:
            vehicle = Vehicle.query.get(trip.vehicle_id)
            vehicle.status = 'in-service'
    
    try:
        db.session.commit()
        flash(f'Trip #{trip_id} status updated to {status}!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating trip: {str(e)}', 'error')
    
    return redirect(url_for('trips'))

@app.route('/reports')
def reports():
    total_trips = Trip.query.count()
    completed_trips = Trip.query.filter_by(status='completed').count()
    total_revenue = db.session.query(db.func.sum(Trip.fare)).filter_by(status='completed').scalar() or 0
    recent_trips = Trip.query.order_by(Trip.created_at.desc()).limit(10).all()
    
    return render_template_string(
        BASE_TEMPLATE.format(title="Reports", content=REPORTS_TEMPLATE),
        total_trips=total_trips,
        completed_trips=completed_trips,
        total_revenue=total_revenue,
        recent_trips=recent_trips
    )

# Initialize database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    # Create instance folder for database
    if not os.path.exists('instance'):
        os.makedirs('instance')
    
    print("Starting Taxi Manager...")
    print("Access the application at: http://localhost:5000")
    print("Press Ctrl+C to stop")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
