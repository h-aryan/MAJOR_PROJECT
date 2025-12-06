require("dotenv").config();
const mongoose = require("mongoose");
const Property = require("./models/Property");

const mongoURI = process.env.MONGODB_URI;

if (!mongoURI) {
  console.error("✗ Error: MONGODB_URI is not defined in .env file");
  process.exit(1);
}

console.log(
  "Connection string (masked):",
  mongoURI.replace(/:[^:@]+@/, ":***@")
);

(async () => {
  try {
    console.log("Attempting to connect to MongoDB...");
    await mongoose.connect(mongoURI, {});
    console.log("✓ MongoDB connected successfully!");

    await Property.deleteMany({});
    console.log("✓ Cleared existing properties");

    await Property.insertMany([
      {
        title: "Sunrise Residency 2BHK",
        sqFt: 1150,
        pricePerSqFt: 6200,
        ownerName: "Amit Sharma",
        brokerName: "Kavya Realtors",
        brokerPhone: "+91 98765 43210",
        address: "Sector 62, Noida",
        description: "Spacious 2BHK with park view.",
        coverImageUrl:
          "https://images.unsplash.com/photo-1560518883-ce09059eeffa?q=80&w=1200",
      },
      {
        title: "Lakeview Villa",
        sqFt: 3200,
        pricePerSqFt: 9500,
        ownerName: "Riya Mehta",
        brokerName: "Prime Estates",
        brokerPhone: "+91 99887 76655",
        address: "Whitefield, Bengaluru",
        description: "Premium villa near tech park.",
        coverImageUrl: "/public/lake.jpg",
      },
      {
        title: "Downtown Studio",
        sqFt: 620,
        pricePerSqFt: 12500,
        ownerName: "Karan Patel",
        brokerName: "Urban Brokers",
        brokerPhone: "+91 90909 80808",
        address: "BKC, Mumbai",
        description: "Compact studio with excellent connectivity.",
        coverImageUrl:
          "https://images.unsplash.com/photo-1494526585095-c41746248156?q=80&w=1200",
      },
    ]);
    console.log("✓ Seed complete - 3 properties inserted");
    process.exit(0);
  } catch (e) {
    console.error("✗ Error:", e.message);
    if (e.message.includes("authentication failed")) {
      console.error("\n=== TROUBLESHOOTING ===");
      console.error("1. Go to MongoDB Atlas → Database Access");
      console.error(
        '2. Verify user "haryan956" exists and password is "test12345678"'
      );
      console.error("3. If password is different, update .env file");
      console.error("4. Go to MongoDB Atlas → Network Access");
      console.error("5. Add your IP address (or 0.0.0.0/0 for testing)");
      console.error("6. Try creating a NEW user with a fresh password");
    }
    process.exit(1);
  }
})();
