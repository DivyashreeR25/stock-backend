from flask import Blueprint, request, jsonify
import hashlib
import sqlite3
from database.db import get_db_connection

user_bp = Blueprint('user', __name__)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@user_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    required_fields = ['username', 'email', 'password']
    
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    with get_db_connection() as conn:
        try:
            conn.execute('''
                INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
            ''', (
                data['username'],
                data['email'],
                hash_password(data['password'])
            ))
            conn.commit()
            return jsonify({'message': 'User registered successfully'}), 201
        except sqlite3.IntegrityError:
            return jsonify({'error': 'Username or email already exists'}), 409

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password required'}), 400
    
    with get_db_connection() as conn:
        user = conn.execute('''
            SELECT id, username, email, balance FROM users 
            WHERE username = ? AND password_hash = ? AND is_active = 1
        ''', (data['username'], hash_password(data['password']))).fetchone()
        
        if user:
            return jsonify({
                'message': 'Login successful',
                'user': dict(user)
            })
        else:
            return jsonify({'error': 'Invalid credentials'}), 401

@user_bp.route('/<int:user_id>/watchlist', methods=['GET'])
def get_watchlist(user_id):
    with get_db_connection() as conn:
        watchlist = conn.execute('''
            SELECT w.symbol, i.name, w.created_at
            FROM watchlist w
            JOIN instruments i ON w.symbol = i.symbol
            WHERE w.user_id = ?
            ORDER BY w.created_at DESC
        ''', (user_id,)).fetchall()
        
        return jsonify([dict(item) for item in watchlist])

@user_bp.route('/<int:user_id>/watchlist', methods=['POST'])
def add_to_watchlist(user_id):
    data = request.get_json()
    symbol = data.get('symbol')
    
    if not symbol:
        return jsonify({'error': 'Symbol required'}), 400
    
    with get_db_connection() as conn:
        instrument = conn.execute(
            'SELECT symbol FROM instruments WHERE symbol = ? AND is_active = 1',
            (symbol.upper(),)
        ).fetchone()
        
        if not instrument:
            return jsonify({'error': 'Invalid symbol'}), 404
        
        try:
            conn.execute('''
                INSERT INTO watchlist (user_id, symbol)
                VALUES (?, ?)
            ''', (user_id, symbol.upper()))
            conn.commit()
            return jsonify({'message': 'Added to watchlist'}), 201
        except sqlite3.IntegrityError:
            return jsonify({'error': 'Symbol already in watchlist'}), 409

@user_bp.route('/<int:user_id>/watchlist/<symbol>', methods=['DELETE'])
def remove_from_watchlist(user_id, symbol):
    with get_db_connection() as conn:
        result = conn.execute(
            'DELETE FROM watchlist WHERE user_id = ? AND symbol = ?',
            (user_id, symbol.upper())
        )
        
        if result.rowcount == 0:
            return jsonify({'error': 'Symbol not found in watchlist'}), 404
            
        conn.commit()
        return jsonify({'message': 'Removed from watchlist'})

@user_bp.route('/<int:user_id>/portfolio', methods=['GET'])
def get_portfolio(user_id):
    with get_db_connection() as conn:
        portfolio = conn.execute('''
            SELECT p.symbol, i.name, p.quantity, p.avg_price, 
                   p.quantity * p.avg_price as invested_amount,
                   p.created_at, p.updated_at
            FROM portfolio p
            JOIN instruments i ON p.symbol = i.symbol
            WHERE p.user_id = ?
            ORDER BY p.updated_at DESC
        ''', (user_id,)).fetchall()
        
        return jsonify([dict(item) for item in portfolio])

@user_bp.route('/<int:user_id>/balance', methods=['GET'])
def get_balance(user_id):
    with get_db_connection() as conn:
        user = conn.execute(
            'SELECT balance FROM users WHERE id = ? AND is_active = 1',
            (user_id,)
        ).fetchone()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        return jsonify({'balance': user['balance']})
