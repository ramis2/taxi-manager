// MongoDB setup for Atlanta Taxi Dispatch
use attaxidata;

// Create collections
db.createCollection("drivers");
db.createCollection("trips");
db.createCollection("rides");

// Insert Atlanta taxi drivers
db.drivers.insertMany([
  {
    driver_id: "ATL-001",
    name: "Michael Johnson",
    phone: "404-555-1234",
    status: "available",
    location: {
      type: "Point",
      coordinates: [-84.3879, 33.7488]
    },
    vehicle: "Toyota Camry",
    rating: 4.8
  },
  {
    driver_id: "ATL-002",
    name: "Sarah Williams", 
    phone: "404-555-5678",
    status: "on_trip",
    location: {
      type: "Point",
      coordinates: [-84.3963, 33.7756]
    },
    vehicle: "Honda Accord",
    rating: 4.9
  }
]);

// Create geospatial index
db.drivers.createIndex({ location: "2dsphere" });
