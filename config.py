import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///trading.db'
    FINNHUB_API_KEY = os.environ.get('FINNHUB_API_KEY', 'd2fb3m9r01qj3egs36bgd2fb3m9r01qj3egs36c0')
    