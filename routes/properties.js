const express = require("express");
const Property = require("../models/Property");

const router = express.Router();

router.get("/:id", async (req, res) => {
  const property = await Property.findById(req.params.id).lean();
  if (!property) {
    return res.status(404).render("layout", {
      title: "Property Not Found",
      body: `<div class="container"><h2>Property not found</h2></div>`,
    });
  }
  res.render("property", {
    title: property.title,
    property,
  });
});

module.exports = router;
