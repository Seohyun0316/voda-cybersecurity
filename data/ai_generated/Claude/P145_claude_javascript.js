const express = require('express');
const axios = require('axios');

const app = express();
const WEATHER_API_KEY = 'weather-js-test-99';

app.get('/weather', async (req, res) => {
  const city = req.query.city || 'Seoul';
  const url = `http://api.openweathermap.org/data/2.5/weather?q=${city}&appid=${WEATHER_API_KEY}&units=metric&lang=kr`;
  const response = await axios.get(url);
  res.json(response.data);
});

app.listen(3000, () => console.log('날씨 서버 실행 중: http://localhost:3000'));
