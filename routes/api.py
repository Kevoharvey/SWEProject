from flask import Blueprint, jsonify, session
from app import mysql

api_bp = Blueprint('api', __name__)

@api_bp.route('/markets')
def get_markets():
    """Return market data as JSON for the map."""
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT ms.*, f.farm_name, f.id as farmer_id,
               (SELECT GROUP_CONCAT(DISTINCT p.category) FROM products p WHERE p.farmer_id = f.id AND p.is_active = 1) as categories,
               (SELECT COUNT(*) FROM products p WHERE p.farmer_id = f.id AND p.is_active = 1) as product_count
        FROM market_schedules ms
        JOIN farmers f ON ms.farmer_id = f.id
        WHERE f.status = 'approved' AND ms.market_lat IS NOT NULL AND ms.market_lng IS NOT NULL
    """)
    markets = cur.fetchall()
    cur.close()

    result = []
    for m in markets:
        result.append({
            'id': m['id'],
            'farmer_id': m['farmer_id'],
            'farm_name': m['farm_name'],
            'market_name': m['market_name'],
            'market_address': m['market_address'],
            'lat': float(m['market_lat']) if m['market_lat'] else None,
            'lng': float(m['market_lng']) if m['market_lng'] else None,
            'day_of_week': m['day_of_week'],
            'start_time': str(m['start_time']),
            'end_time': str(m['end_time']),
            'categories': m['categories'] or '',
            'product_count': m['product_count']
        })
    return jsonify(result)

@api_bp.route('/cart/count')
def cart_count():
    if 'user_id' not in session:
        return jsonify({'count': 0})
    cur = mysql.connection.cursor()
    cur.execute("SELECT COALESCE(SUM(quantity), 0) as cnt FROM cart_items WHERE buyer_id = %s", (session['user_id'],))
    count = cur.fetchone()['cnt']
    cur.close()
    return jsonify({'count': int(count)})

@api_bp.route('/notifications/count')
def notification_count():
    if 'user_id' not in session:
        return jsonify({'count': 0})
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) as cnt FROM notifications WHERE user_id = %s AND is_read = 0", (session['user_id'],))
    count = cur.fetchone()['cnt']
    cur.close()
    return jsonify({'count': count})
