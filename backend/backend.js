const express = require("express");
const multer = require("multer");
const axios = require("axios");
const FormData = require("form-data");
const fs = require("fs");
const cors = require("cors");
const app = express();

app.use(cors());
const upload = multer({ dest: "uploads/" });

app.post("/upload", upload.single("pdf"), async (req, res) => {
  try {
    const filePath = req.file.path;
    const formData = new FormData();
    formData.append("pdf", fs.createReadStream(filePath));

    const response = await axios.post("http://127.0.0.1:8000/parse", formData, {
      headers: formData.getHeaders(),
      responseType: "arraybuffer",
    });

    fs.unlinkSync(filePath);
    res.setHeader("Content-Type", "application/pdf");
    res.setHeader("Content-Disposition", "attachment; filename=summary.pdf");
    res.send(response.data);
  } catch (error) {
    console.error("❌ Error:", error.message);
    res.status(500).send("Server error");
  }
});

app.listen(5000, () => console.log("🚀 Node server running on port 5000"));
