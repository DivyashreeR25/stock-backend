from flask import Blueprint, request, jsonify
from database.db import get_db_connection
import sqlite3
instruments_bp = Blueprint('instruments', __name__)

@instruments_bp.route('/', methods=['GET'])
def get_all_instruments():
    search = request.args.get('search', '')
    sector = request.args.get('sector', '')
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 50))
    offset = (page - 1) * limit
    
    with get_db_connection() as conn:
        query = '''
            SELECT * FROM instruments 
            WHERE is_active = 1
        '''
        params = []
        
        if search:
            query += ' AND (symbol LIKE ? OR name LIKE ?)'
            search_term = f'%{search}%'
            params.extend([search_term, search_term])
            
        if sector:
            query += ' AND sector LIKE ?'
            params.append(f'%{sector}%')
            
        query += ' ORDER BY market_cap DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        instruments = conn.execute(query, params).fetchall()
        
        total_query = 'SELECT COUNT(*) as count FROM instruments WHERE is_active = 1'
        total_params = []
        
        if search:
            total_query += ' AND (symbol LIKE ? OR name LIKE ?)'
            search_term = f'%{search}%'
            total_params.extend([search_term, search_term])
            
        if sector:
            total_query += ' AND sector LIKE ?'
            total_params.append(f'%{sector}%')
            
        total = conn.execute(total_query, total_params).fetchone()['count']
        
        return jsonify({
            'instruments': [dict(row) for row in instruments],
            'total': total,
            'page': page,
            'limit': limit,
            'has_next': offset + limit < total
        })

@instruments_bp.route('/<symbol>', methods=['GET'])
def get_instrument(symbol):
    with get_db_connection() as conn:
        instrument = conn.execute(
            'SELECT * FROM instruments WHERE symbol = ? AND is_active = 1',
            (symbol.upper(),)
        ).fetchone()
        
        if not instrument:
            return jsonify({'error': 'Instrument not found'}), 404
            
        return jsonify(dict(instrument))

@instruments_bp.route('/', methods=['POST'])
def add_instrument():
    data = request.get_json()
    required_fields = ['symbol', 'name', 'exchange']
    
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    with get_db_connection() as conn:
        try:
            conn.execute('''
                INSERT INTO instruments (symbol, name, exchange, sector, market_cap)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                data['symbol'].upper(),
                data['name'],
                data['exchange'],
                data.get('sector'),
                data.get('market_cap')
            ))
            conn.commit()
            return jsonify({'message': 'Instrument added successfully'}), 201
        except sqlite3.IntegrityError:
            return jsonify({'error': 'Instrument already exists'}), 409

@instruments_bp.route('/<symbol>', methods=['PUT'])
def update_instrument(symbol):
    data = request.get_json()
    
    with get_db_connection() as conn:
        result = conn.execute('''
            UPDATE instruments 
            SET name = ?, exchange = ?, sector = ?, market_cap = ?
            WHERE symbol = ? AND is_active = 1
        ''', (
            data.get('name'),
            data.get('exchange'),
            data.get('sector'),
            data.get('market_cap'),
            symbol.upper()
        ))
        
        if result.rowcount == 0:
            return jsonify({'error': 'Instrument not found'}), 404
            
        conn.commit()
        return jsonify({'message': 'Instrument updated successfully'})

@instruments_bp.route('/<symbol>', methods=['DELETE'])
def delete_instrument(symbol):
    with get_db_connection() as conn:
        result = conn.execute(
            'UPDATE instruments SET is_active = 0 WHERE symbol = ?',
            (symbol.upper(),)
        )
        
        if result.rowcount == 0:
            return jsonify({'error': 'Instrument not found'}), 404
            
        conn.commit()
        return jsonify({'message': 'Instrument deleted successfully'})
