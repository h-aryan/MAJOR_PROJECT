const mongoose = require("mongoose");

const PropertySchema = new mongoose.Schema(
  {
    title: { type: String, required: true },
    sqFt: { type: Number, required: true },
    pricePerSqFt: { type: Number, required: true },
    ownerName: { type: String, required: true },
    brokerName: { type: String, required: true },
    brokerPhone: { type: String, required: true },
    address: { type: String, default: "" },
    description: { type: String, default: "" },
    coverImageUrl: { type: String, default: "" },
  },
  { timestamps: true }
);

PropertySchema.virtual("totalPrice").get(function () {
  return this.sqFt * this.pricePerSqFt;
});

module.exports = mongoose.model("Property", PropertySchema);
