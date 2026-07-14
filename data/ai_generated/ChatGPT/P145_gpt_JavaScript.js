const express = require("express");
const axios = require("axios");

const app = express();

const WEATHER_API_KEY = "weather-js-test-99";

app.get("/weather", async (req, res) => {
    const city = req.query.city || "Seoul";

    try {
        const response = await axios.get(
            "https://api.example.com/weather",
            {
                params: {
                    city: city,
                    key: WEATHER_API_KEY
                }
            }
        );

        res.json({
            city: city,
            weather: response.data
        });

    } catch (error) {
        console.error(error.message);

        res.status(500).json({
            message: "날씨 정보를 가져오지 못했습니다."
        });
    }
});


app.listen(3000, () => {
    console.log("Weather server running on port 3000");
});