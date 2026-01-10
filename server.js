const express = require('express');
const { MongoClient } = require('mongodb');
const cors = require('cors');
const app = express();

app.use(cors());
app.use(express.json());

const PORT = 5000;
const MONGODB_URI = "mongodb://localhost:27017";

// Connect to Atlanta Taxi database
async function connectDB() {
  const client = new MongoClient(MONGODB_URI);
  await client.connect();
  console.log("✅ Connected to Atlanta Taxi Dispatch database");
  return client.db("attaxidata");
}

// API Routes
app.get('/api/health', (req, res) => {
  res.json({ status: '🚕 Atlanta Taxi Dispatch API is running!' });
});

app.get('/api/drivers', async (req, res) => {
  try {
    const db = await connectDB();
    const drivers = await db.collection('drivers').find().toArray();
    res.json(drivers);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/drivers/available', async (req, res) => {
  try {
    const db = await connectDB();
    const drivers = await db.collection('drivers')
      .find({ status: "available" })
      .toArray();
    res.json(drivers);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Dispatch a driver
app.post('/api/dispatch', async (req, res) => {
  const { pickup } = req.body; // { lng: -84.3879, lat: 33.7488 }
  
  try {
    const db = await connectDB();
    
    // Find nearest available driver (within 10km)
    const nearestDriver = await db.collection('drivers').findOne({
      status: "available",
      location: {
        $near: {
          $geometry: {
            type: "Point",
            coordinates: [pickup.lng, pickup.lat]
          },
          $maxDistance: 10000 // 10km
        }
      }
    });
    
    if (nearestDriver) {
      // Update driver status
      await db.collection('drivers').updateOne(
        { driver_id: nearestDriver.driver_id },
        { $set: { status: "on_trip", last_dispatch: new Date() } }
      );
      
      // Create trip record
      await db.collection('trips').insertOne({
        trip_id: `TRIP-${Date.now()}`,
        driver_id: nearestDriver.driver_id,
        pickup_location: [pickup.lng, pickup.lat],
        status: "dispatched",
        timestamp: new Date()
      });
      
      res.json({ 
        success: true, 
        message: "Driver dispatched!",
        driver: nearestDriver 
      });
    } else {
      res.status(404).json({ 
        success: false, 
        message: "No available drivers nearby" 
      });
    }
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`🚕 Atlanta Taxi Dispatch API running at http://localhost:${PORT}`);
});
