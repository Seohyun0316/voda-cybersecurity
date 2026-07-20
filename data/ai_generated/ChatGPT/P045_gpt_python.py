import os
import requests


API_KEY = os.environ["STOCK_API_KEY"]

BASE_URL = "https://api.example.com/v1/stock/price"


def get_stock_price(symbol):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    params = {
        "symbol": symbol
    }

    response = requests.get(
        BASE_URL,
        headers=headers,
        params=params
    )

    response.raise_for_status()

    data = response.json()

    return {
        "symbol": symbol,
        "price": data["price"],
        "change": data.get("change")
    }


# Å×½ºÆ®
stock = get_stock_price("AAPL")

print(stock)