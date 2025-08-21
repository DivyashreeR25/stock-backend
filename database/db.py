import sqlite3
import json
from contextlib import contextmanager

DATABASE_PATH = 'trading.db'

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS instruments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol VARCHAR(20) UNIQUE NOT NULL,
                name VARCHAR(255) NOT NULL,
                exchange VARCHAR(50) NOT NULL,
                sector VARCHAR(100),
                market_cap REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                balance REAL DEFAULT 10000.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                symbol VARCHAR(20) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(user_id, symbol)
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                symbol VARCHAR(20) NOT NULL,
                quantity INTEGER NOT NULL,
                avg_price REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        sample_instruments = [
            ('AAPL', 'Apple Inc.', 'NASDAQ', 'Technology', 3000000000000),
            ('GOOGL', 'Alphabet Inc.', 'NASDAQ', 'Technology', 2000000000000),
            ('MSFT', 'Microsoft Corporation', 'NASDAQ', 'Technology', 2800000000000),
            ('TSLA', 'Tesla Inc.', 'NASDAQ', 'Automotive', 800000000000),
            ('AMZN', 'Amazon.com Inc.', 'NASDAQ', 'Consumer Discretionary', 1500000000000),
            ('NVDA', 'NVIDIA Corporation', 'NASDAQ', 'Technology', 1800000000000),
            ('META', 'Meta Platforms Inc.', 'NASDAQ', 'Technology', 900000000000),
            ('NFLX', 'Netflix Inc.', 'NASDAQ', 'Communication Services', 200000000000),
            ('AMD', 'Advanced Micro Devices', 'NASDAQ', 'Technology', 250000000000),
            ('INTC', 'Intel Corporation', 'NASDAQ', 'Technology', 180000000000)
        ]
        
        conn.executemany('''
            INSERT OR IGNORE INTO instruments (symbol, name, exchange, sector, market_cap)
            VALUES (?, ?, ?, ?, ?)
        ''', sample_instruments)
        
        conn.commit()