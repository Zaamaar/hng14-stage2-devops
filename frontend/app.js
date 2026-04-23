const express = require('express');
const axios = require('axios');
const path = require('path');
const app = express();

const API_URL = process.env.API_URL || "http://api:8000"

app.use(express.json());
app.use(express.static(path.join(__dirname, 'views')));

app.post('/api/submit', async (req, res) => {
  try {
    const response = await axios.post(`${API_URL}/api/jobs`);
    res.json(response.data);
  } catch (err) {
    console.error('Submit error:', err.message);
    res.status(500).json({ error: "something went wrong" });
  }
});

app.get('/api/status/:id', async (req, res) => {
  try {
    const response = await axios.get(`${API_URL}/api/jobs/${req.params.id}`);
    res.json(response.data);
  } catch (err) {
    if (err.response && err.response.status === 404) {
      res.status(404).json({ error: "not found" });
    } else {
      console.error('Status error:', err.message);
      res.status(500).json({ error: "something went wrong" });
    }
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Frontend running on port ${PORT}`);
});
