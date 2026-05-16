from flask import Blueprint, render_template, request, session
from app import mysql

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    cur = mysql.connection.cursor()
    # Get featured products from approved farmers
    cur.execute("""
        SELECT p.*, f.farm_name, f.address as farm_address,
               (SELECT photo_path FROM product_photos WHERE product_id = p.id ORDER BY display_order LIMIT 1) as photo
        FROM products p
        JOIN farmers f ON p.farmer_id = f.id
        WHERE f.status = 'approved' AND p.is_active = 1 AND p.stock_status != 'sold-out'
        ORDER BY p.created_at DESC LIMIT 8
    """)
    featured = cur.fetchall()
    cur.execute("SELECT COUNT(*) as cnt FROM farmers WHERE status = 'approved'")
    farmer_count = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) as cnt FROM products WHERE is_active = 1")
    product_count = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) as cnt FROM market_days")
    market_count = cur.fetchone()['cnt'] if cur.rowcount > 0 else 0
    cur.close()
    return render_template('index.html', featured=featured, farmer_count=farmer_count, product_count=product_count, market_count=market_count)

@main_bp.route('/marketplace')
def marketplace():
    cur = mysql.connection.cursor()
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    price_min = request.args.get('price_min', '')
    price_max = request.args.get('price_max', '')
    market_day = request.args.get('market_day', '')
    farm = request.args.get('farm', '')
    sort = request.args.get('sort', 'newest')

    query = """
        SELECT p.*, f.farm_name, f.address as farm_address, f.id as fid,
               (SELECT photo_path FROM product_photos WHERE product_id = p.id ORDER BY display_order LIMIT 1) as photo
        FROM products p
        JOIN farmers f ON p.farmer_id = f.id
        WHERE f.status = 'approved' AND p.is_active = 1
    """
    params = []

    if category:
        query += " AND p.category = %s"
        params.append(category)
    if search:
        query += " AND (p.name LIKE %s OR p.description LIKE %s OR f.farm_name LIKE %s)"
        params.extend([f'%{search}%'] * 3)
    if price_min:
        query += " AND p.price >= %s"
        params.append(float(price_min))
    if price_max:
        query += " AND p.price <= %s"
        params.append(float(price_max))
    if farm:
        query += " AND f.farm_name LIKE %s"
        params.append(f'%{farm}%')
    if market_day:
        query += " AND p.id IN (SELECT product_id FROM product_availability WHERE day_of_week = %s AND is_available = 1)"
        params.append(market_day)

    if sort == 'price_low':
        query += " ORDER BY p.price ASC"
    elif sort == 'price_high':
        query += " ORDER BY p.price DESC"
    else:
        query += " ORDER BY p.created_at DESC"

    cur.execute(query, params)
    products = cur.fetchall()

    # Get categories for filter
    categories = ['Vegetables','Fruits','Dairy','Meat','Eggs','Honey','Baked Goods','Herbs','Flowers','Preserves','Beverages','Other']
    days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

    cur.close()
    return render_template('marketplace.html', products=products, categories=categories, days=days,
                         filters={'category': category, 'search': search, 'price_min': price_min,
                                  'price_max': price_max, 'market_day': market_day, 'farm': farm, 'sort': sort})

@main_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT p.*, f.farm_name, f.address as farm_address, f.description as farm_desc,
               f.phone as farm_phone, f.id as fid, f.profile_image as farm_image, f.user_id as farmer_user_id
        FROM products p JOIN farmers f ON p.farmer_id = f.id
        WHERE p.id = %s AND f.status = 'approved'
    """, (product_id,))
    product = cur.fetchone()
    if not product:
        return render_template('404.html'), 404

    cur.execute("SELECT * FROM product_photos WHERE product_id = %s ORDER BY display_order", (product_id,))
    photos = cur.fetchall()

    cur.execute("SELECT * FROM product_availability WHERE product_id = %s", (product_id,))
    availability = cur.fetchall()

    # Get related products from same farmer
    cur.execute("""
        SELECT p.*, (SELECT photo_path FROM product_photos WHERE product_id = p.id ORDER BY display_order LIMIT 1) as photo
        FROM products p WHERE p.farmer_id = %s AND p.id != %s AND p.is_active = 1 LIMIT 4
    """, (product['farmer_id'], product_id))
    related = cur.fetchall()

    # Check subscription
    is_subscribed = False
    if session.get('user_id') and session.get('role') == 'buyer':
        cur.execute("SELECT id FROM subscriptions WHERE buyer_id = %s AND farmer_id = %s",
                   (session['user_id'], product['fid']))
        is_subscribed = cur.fetchone() is not None

    cur.close()
    return render_template('product_detail.html', product=product, photos=photos,
                         availability=availability, related=related, is_subscribed=is_subscribed)

@main_bp.route('/farmer/<int:farmer_id>')
def farmer_profile(farmer_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT f.*, u.full_name, u.email FROM farmers f
        JOIN users u ON f.user_id = u.id WHERE f.id = %s AND f.status = 'approved'
    """, (farmer_id,))
    farmer = cur.fetchone()
    if not farmer:
        return render_template('404.html'), 404

    cur.execute("""
        SELECT p.*, (SELECT photo_path FROM product_photos WHERE product_id = p.id ORDER BY display_order LIMIT 1) as photo
        FROM products p WHERE p.farmer_id = %s AND p.is_active = 1 ORDER BY p.created_at DESC
    """, (farmer_id,))
    products = cur.fetchall()

    cur.execute("SELECT * FROM market_schedules WHERE farmer_id = %s ORDER BY FIELD(day_of_week, 'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday')", (farmer_id,))
    schedules = cur.fetchall()

    cur.execute("""
        SELECT r.*, u.full_name as buyer_name FROM reviews r
        JOIN users u ON r.buyer_id = u.id WHERE r.farmer_id = %s ORDER BY r.created_at DESC
    """, (farmer_id,))
    reviews = cur.fetchall()

    cur.execute("SELECT AVG(rating) as avg_rating, COUNT(*) as review_count FROM reviews WHERE farmer_id = %s", (farmer_id,))
    stats = cur.fetchone()

    is_subscribed = False
    if session.get('user_id') and session.get('role') == 'buyer':
        cur.execute("SELECT id FROM subscriptions WHERE buyer_id = %s AND farmer_id = %s",
                   (session['user_id'], farmer_id))
        is_subscribed = cur.fetchone() is not None

    cur.close()
    return render_template('farmer_public.html', farmer=farmer, products=products,
                         schedules=schedules, reviews=reviews, stats=stats, is_subscribed=is_subscribed)

@main_bp.route('/map')
def market_map():
    cur = mysql.connection.cursor()
    day_filter = request.args.get('day', '')
    query = """
        SELECT ms.*, f.farm_name, f.id as farmer_id,
               (SELECT GROUP_CONCAT(DISTINCT p.category) FROM products p WHERE p.farmer_id = f.id AND p.is_active = 1) as categories
        FROM market_schedules ms
        JOIN farmers f ON ms.farmer_id = f.id
        WHERE f.status = 'approved'
    """
    params = []
    if day_filter:
        query += " AND ms.day_of_week = %s"
        params.append(day_filter)
    cur.execute(query, params)
    markets = cur.fetchall()
    days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    cur.close()
    return render_template('map.html', markets=markets, days=days, selected_day=day_filter)
