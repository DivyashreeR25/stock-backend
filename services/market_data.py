from flask import Blueprint, request, jsonify
import requests
from config import Config
import random
import time

market_data_bp = Blueprint('market_data', __name__)
BASE_URL = "https://finnhub.io/api/v1"


# ----------------- LIVE DATA ROUTES -----------------

@market_data_bp.route('/quote/<symbol>', methods=['GET'])
def get_quote(symbol):
    """Get live quote for a single symbol."""
    try:
        url = f"{BASE_URL}/quote?symbol={symbol.upper()}&token={Config.FINNHUB_API_KEY}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()

        data = response.json()
        if not data.get("c"):
            return jsonify({"error": f"No valid data for symbol '{symbol.upper()}'"}), 404

        return jsonify({
            "symbol": symbol.upper(),
            "current_price": data.get("c"),
            "change": data.get("d"),
            "change_percent": data.get("dp"),
            "high": data.get("h"),
            "low": data.get("l"),
            "open": data.get("o"),
            "previous_close": data.get("pc"),
            "timestamp": data.get("t")
        })
    except requests.RequestException as e:
        return jsonify({"error": "Request failed", "details": str(e)}), 503


@market_data_bp.route('/quotes', methods=['POST'])
def get_multiple_quotes():
    """Get live quotes for multiple symbols."""
    data = request.get_json()
    symbols = data.get("symbols", [])

    if not symbols or len(symbols) > 100:
        return jsonify({"error": "Provide 1-100 symbols"}), 400

    quotes = {}
    for symbol in symbols:
        try:
            url = f"{BASE_URL}/quote?symbol={symbol.upper()}&token={Config.FINNHUB_API_KEY}"
            r = requests.get(url, timeout=5)
            r.raise_for_status()
            q = r.json()

            if q.get("c"):
                quotes[symbol.upper()] = {
                    "current_price": q.get("c"),
                    "change": q.get("d"),
                    "change_percent": q.get("dp"),
                    "high": q.get("h"),
                    "low": q.get("l"),
                    "open": q.get("o"),
                    "previous_close": q.get("pc")
                }
        except requests.RequestException:
            continue

    return jsonify({"quotes": quotes})


@market_data_bp.route('/company/<symbol>', methods=['GET'])
def get_company_profile(symbol):
    """Get company profile."""
    try:
        url = f"{BASE_URL}/stock/profile2?symbol={symbol.upper()}&token={Config.FINNHUB_API_KEY}"
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()

        if not data:
            return jsonify({"error": "Company not found"}), 404

        return jsonify({
            "symbol": symbol.upper(),
            "name": data.get("name"),
            "country": data.get("country"),
            "currency": data.get("currency"),
            "exchange": data.get("exchange"),
            "industry": data.get("finnhubIndustry"),
            "logo": data.get("logo"),
            "market_cap": data.get("marketCapitalization"),
            "phone": data.get("phone"),
            "share_outstanding": data.get("shareOutstanding"),
            "ticker": data.get("ticker"),
            "website": data.get("weburl")
        })
    except requests.RequestException:
        return jsonify({"error": "Company data service unavailable"}), 503


@market_data_bp.route('/candles/<symbol>', methods=['GET'])
def get_candles(symbol):
    """Get historical candle data."""
    resolution = request.args.get("resolution", "D")
    from_ts = request.args.get("from")
    to_ts = request.args.get("to")

    if not from_ts or not to_ts:
        return jsonify({"error": "from and to timestamps required"}), 400

    try:
        url = (f"{BASE_URL}/stock/candle?symbol={symbol.upper()}&resolution={resolution}"
               f"&from={from_ts}&to={to_ts}&token={Config.FINNHUB_API_KEY}")
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        data = r.json()

        if data.get("s") != "ok":
            return jsonify({"error": "No candle data available"}), 404

        return jsonify({
            "symbol": symbol.upper(),
            "resolution": resolution,
            "timestamps": data.get("t"),
            "open": data.get("o"),
            "high": data.get("h"),
            "low": data.get("l"),
            "close": data.get("c"),
            "volume": data.get("v")
        })
    except requests.RequestException as e:
     return jsonify({"error": "Candle data service unavailable", "details": str(e)}), 503



@market_data_bp.route('/news/<symbol>', methods=['GET'])
def get_company_news(symbol):
    """Get recent company news."""
    from_date = request.args.get("from")
    to_date = request.args.get("to")

    try:
        url = (f"{BASE_URL}/company-news?symbol={symbol.upper()}&from={from_date}&to={to_date}"
               f"&token={Config.FINNHUB_API_KEY}")
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        news = r.json()

        return jsonify({
            "symbol": symbol.upper(),
            "news": news[:20]  # limit to 20 items
        })
    except requests.RequestException:
        return jsonify({"error": "News service unavailable"}), 503

@market_data_bp.route('/stats/<symbol>', methods=['GET'])
def get_stats(symbol):
    """Get 52-week high/low and average volume."""
    try:
        url = f"{BASE_URL}/stock/metric?symbol={symbol.upper()}&metric=all&token={Config.FINNHUB_API_KEY}"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()

        metrics = data.get("metric", {})
        return jsonify({
            "symbol": symbol.upper(),
            "52WeekHigh": metrics.get("52WeekHigh"),
            "52WeekLow": metrics.get("52WeekLow"),
            "10DayAvgVolume": metrics.get("10DayAverageTradingVolume")
        })
    except requests.RequestException as e:
        return jsonify({"error": "Stats service unavailable", "details": str(e)}), 503
