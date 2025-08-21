from flask import Flask
from flask_cors import CORS
from services.instruments import instruments_bp
from services.market_data import market_data_bp
from services.user import user_bp
from services.prediction import prediction_bp
from database.db import init_db


app = Flask(__name__)

# Load configuration (includes FINNHUB_API_KEY from config.py)
app.config.from_object('config.Config')

# Enable CORS for all routes
CORS(app)

# Register blueprints
app.register_blueprint(instruments_bp, url_prefix='/api/instruments')
app.register_blueprint(market_data_bp, url_prefix='/api/market')
app.register_blueprint(user_bp, url_prefix='/api/user')
app.register_blueprint(prediction_bp, url_prefix="/api/market")

@app.route('/')
def health_check():
    """Basic health check endpoint."""
    return {
        'status': 'healthy',
        'service': 'stock-trading-api',
        'version': '1.0.0'
    }


if __name__ == '__main__':
    # Initialize database tables if not already present
    init_db()
    
    # Run the Flask app
    app.run(
        debug=True,
        host='0.0.0.0',  # Makes it accessible from other devices in the network
        port=5000
    )
