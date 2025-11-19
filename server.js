require("dotenv").config();
const path = require("path");
const express = require("express");
const mongoose = require("mongoose");
const morgan = require("morgan");
const cors = require("cors");

const pagesRouter = require("./routes/pages");
const propertiesRouter = require("./routes/properties");

const app = express();

// Use connection string directly from .env (same as seed.js)
const mongoURI = process.env.MONGODB_URI;

if (!mongoURI) {
  console.error("✗ Error: MONGODB_URI is not defined in .env file");
  process.exit(1);
}

mongoose
  .connect(mongoURI, {})
  .then(() => console.log("MongoDB connected"))
  .catch((err) => {
    console.error("MongoDB connection error:", err.message);
    process.exit(1);
  });

app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "views"));

app.use(morgan("dev"));
app.use(cors());
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(express.static(path.join(__dirname, "public")));

app.use("/", pagesRouter);
app.use("/properties", propertiesRouter);

app.use((req, res) => {
  res.status(404).render("layout", {
    title: "Not Found",
    body: `<div class="container"><h2>404 - Not Found</h2></div>`,
  });
});

const port = process.env.PORT || 3000;
app.listen(port, () =>
  console.log(`Server running on http://localhost:${port}`)
);
