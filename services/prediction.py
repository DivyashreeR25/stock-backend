from flask import Blueprint, jsonify
import requests
import os

prediction_bp = Blueprint("prediction", __name__)

API_KEY = os.getenv("d2fb3m9r01qj3egs36bgd2fb3m9r01qj3egs36c0")  # store your API key safely
FINNHUB_URL = "https://finnhub.io/api/v1/quote"

@prediction_bp.route("/predict/<symbol>", methods=["GET"])
def predict_price(symbol):
    """Real-time simple prediction based on live data."""
    try:
        # Get live stock data
        response = requests.get(FINNHUB_URL, params={"symbol": symbol.upper(), "token": API_KEY})
        data = response.json()

        current_price = data.get("c")  # current price
        prev_close = data.get("pc")    # previous close

        # Simple "prediction": assume tomorrow will move in same direction as today
        change = current_price - prev_close
        forecast = round(current_price + (0.5 * change), 2)

        return jsonify({
            "symbol": symbol.upper(),
            "current_price": current_price,
            "predicted_next_day_price": forecast
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
