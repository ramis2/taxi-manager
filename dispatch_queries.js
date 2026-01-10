// Dispatch system queries

// 1. Find nearest available driver
const findNearestDriver = (pickupLng, pickupLat) => `
  db.drivers.find({
    status: "available",
    location: {
      $near: {
        $geometry: {
          type: "Point",
          coordinates: [${pickupLng}, ${pickupLat}]
        },
        $maxDistance: 5000
      }
    }
  }).sort({rating: -1}).limit(1)
`;

// 2. Dispatch a driver
const dispatchDriver = (driverId, rideId) => `
  db.drivers.updateOne(
    {driver_id: "${driverId}"},
    {$set: {status: "on_trip", current_ride: "${rideId}"}}
  )
`;

module.exports = { findNearestDriver, dispatchDriver };
