const express = require('express');
const axios = require('axios');

const app = express();
const PORT = 3000;

// 요청받은 API 키 설정
const API_KEY = 'weather-js-test-99';

// 날씨 조회 API 엔드포인트 (예: http://localhost:3000/weather?city=Seoul)
app.get('/weather', async (req, res) => {
    const city = req.query.city;

    if (!city) {
        return res.status(400).json({ error: '도시 이름(city)을 쿼리 스트링으로 입력해주세요. 예: ?city=Seoul' });
    }

    try {
        // 1. 도시 이름을 좌표(위도, 경도)로 변환 (Geocoding API)
        const geoUrl = `http://api.openweathermap.org/geo/1.0/direct?q=${encodeURIComponent(city)}&limit=1&appid=${API_KEY}`;
        const geoResponse = await axios.get(geoUrl);

        if (geoResponse.data.length === 0) {
            return res.status(404).json({ error: '해당 도시를 찾을 수 없습니다.' });
        }

        const { lat, lon, name } = geoResponse.data[0];

        // 2. 좌표를 바탕으로 현재 날씨 가져오기 (Current Weather API)
        const weatherUrl = `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&appid=${API_KEY}&units=metric&lang=kr`;
        const weatherResponse = await axios.get(weatherUrl);

        // 3. 필요한 데이터만 정제해서 클라이언트에 반환
        const weatherData = weatherResponse.data;
        res.json({
            city: name,
            weather: weatherData.weather[0].description,
            temp: `${weatherData.main.temp}°C`,
            feels_like: `${weatherData.main.feels_like}°C`,
            humidity: `${weatherData.main.humidity}%`,
            wind_speed: `${weatherData.wind.speed} m/s`
        });

    } catch (error) {
        console.error(error);
        res.status(500).json({ error: '날씨 정보를 가져오는 중 오류가 발생했습니다.' });
    }
});

app.listen(PORT, () => {
    console.log(`서버가 http://localhost:${PORT} 에서 원활히 실행 중입니다.`);
});