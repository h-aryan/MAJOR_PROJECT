const express = require("express");
const Property = require("../models/Property");
const router = express.Router();

router.get("/", async (req, res) => {
  const properties = await Property.find().sort({ createdAt: -1 }).lean();
  res.render("index", { title: "Home", properties });
});

router.get("/about", (req, res) => {
  res.render("about", { title: "About" });
});

router.get("/contact", (req, res) => {
  res.render("contact", { title: "Contact Us" });
});

module.exports = router;
