from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import mysql
from helpers import login_required

buyer_bp = Blueprint('buyer', __name__)

@buyer_bp.route('/dashboard')
@login_required
def dashboard():
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) as cnt FROM orders WHERE buyer_id = %s", (session['user_id'],))
    order_count = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) as cnt FROM subscriptions WHERE buyer_id = %s", (session['user_id'],))
    sub_count = cur.fetchone()['cnt']
    cur.execute("""SELECT n.* FROM notifications n WHERE n.user_id = %s ORDER BY n.created_at DESC LIMIT 10""", (session['user_id'],))
    notifications = cur.fetchall()
    cur.execute("SELECT COUNT(*) as cnt FROM notifications WHERE user_id = %s AND is_read = 0", (session['user_id'],))
    unread = cur.fetchone()['cnt']
    cur.close()
    return render_template('buyer/dashboard.html', order_count=order_count, sub_count=sub_count,
                         notifications=notifications, unread=unread)

@buyer_bp.route('/cart')
@login_required
def cart():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT ci.*, p.name, p.price, p.unit, p.stock_status, p.quantity as available_qty,
               f.farm_name, f.id as farmer_id,
               (SELECT photo_path FROM product_photos WHERE product_id = p.id ORDER BY display_order LIMIT 1) as photo
        FROM cart_items ci
        JOIN products p ON ci.product_id = p.id
        JOIN farmers f ON p.farmer_id = f.id
        WHERE ci.buyer_id = %s
        ORDER BY f.farm_name, p.name
    """, (session['user_id'],))
    items = cur.fetchall()

    # Group by farmer
    grouped = {}
    total = 0
    for item in items:
        fname = item['farm_name']
        if fname not in grouped:
            grouped[fname] = {'farmer_id': item['farmer_id'], 'items': [], 'subtotal': 0}
        item_total = float(item['price']) * item['quantity']
        item['item_total'] = item_total
        grouped[fname]['items'].append(item)
        grouped[fname]['subtotal'] += item_total
        total += item_total

    # Get available market schedules for pickup
    farmer_ids = [g['farmer_id'] for g in grouped.values()]
    schedules = []
    if farmer_ids:
        placeholders = ','.join(['%s'] * len(farmer_ids))
        cur.execute(f"""SELECT DISTINCT market_name, market_address, day_of_week, start_time, end_time
                       FROM market_schedules WHERE farmer_id IN ({placeholders})
                       ORDER BY FIELD(day_of_week, 'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday')""",
                   farmer_ids)
        schedules = cur.fetchall()
    cur.close()
    return render_template('buyer/cart.html', grouped=grouped, total=total, schedules=schedules)

@buyer_bp.route('/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    product_id = request.form['product_id']
    quantity = int(request.form.get('quantity', 1))
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM cart_items WHERE buyer_id = %s AND product_id = %s",
               (session['user_id'], product_id))
    existing = cur.fetchone()
    if existing:
        cur.execute("UPDATE cart_items SET quantity = quantity + %s WHERE id = %s", (quantity, existing['id']))
    else:
        cur.execute("INSERT INTO cart_items (buyer_id, product_id, quantity) VALUES (%s, %s, %s)",
                   (session['user_id'], product_id, quantity))
    mysql.connection.commit()
    cur.close()
    flash('Added to cart!', 'success')
    return redirect(request.referrer or url_for('main.marketplace'))

@buyer_bp.route('/cart/update', methods=['POST'])
@login_required
def update_cart():
    item_id = request.form['item_id']
    quantity = int(request.form['quantity'])
    cur = mysql.connection.cursor()
    if quantity <= 0:
        cur.execute("DELETE FROM cart_items WHERE id = %s AND buyer_id = %s", (item_id, session['user_id']))
    else:
        cur.execute("UPDATE cart_items SET quantity = %s WHERE id = %s AND buyer_id = %s",
                   (quantity, item_id, session['user_id']))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('buyer.cart'))

@buyer_bp.route('/cart/remove/<int:item_id>')
@login_required
def remove_from_cart(item_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM cart_items WHERE id = %s AND buyer_id = %s", (item_id, session['user_id']))
    mysql.connection.commit()
    cur.close()
    flash('Item removed.', 'info')
    return redirect(url_for('buyer.cart'))

@buyer_bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    market_location = request.form['market_location']
    pickup_date = request.form['pickup_date']
    pickup_time = request.form['pickup_time_slot']
    notes = request.form.get('notes', '')

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT ci.*, p.price, p.farmer_id, p.quantity as available_qty, p.stock_status
        FROM cart_items ci JOIN products p ON ci.product_id = p.id
        WHERE ci.buyer_id = %s
    """, (session['user_id'],))
    items = cur.fetchall()

    if not items:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('buyer.cart'))

    # Validate stock
    for item in items:
        if item['stock_status'] == 'sold-out':
            flash(f'Some items are sold out. Please update your cart.', 'danger')
            return redirect(url_for('buyer.cart'))

    total = sum(float(item['price']) * item['quantity'] for item in items)

    cur.execute("""INSERT INTO orders (buyer_id, market_location, pickup_date, pickup_time_slot, total_amount, notes, status)
                  VALUES (%s, %s, %s, %s, %s, %s, 'pending')""",
               (session['user_id'], market_location, pickup_date, pickup_time, total, notes))
    order_id = cur.lastrowid

    for item in items:
        subtotal = float(item['price']) * item['quantity']
        cur.execute("""INSERT INTO order_items (order_id, product_id, farmer_id, quantity, unit_price, subtotal)
                      VALUES (%s, %s, %s, %s, %s, %s)""",
                   (order_id, item['product_id'], item['farmer_id'], item['quantity'], item['price'], subtotal))
        # Update product quantity
        cur.execute("UPDATE products SET quantity = GREATEST(0, quantity - %s) WHERE id = %s",
                   (item['quantity'], item['product_id']))
        # Auto update stock status
        cur.execute("SELECT quantity FROM products WHERE id = %s", (item['product_id'],))
        prod = cur.fetchone()
        if prod['quantity'] == 0:
            cur.execute("UPDATE products SET stock_status = 'sold-out' WHERE id = %s", (item['product_id'],))
        elif prod['quantity'] <= 5:
            cur.execute("UPDATE products SET stock_status = 'low-stock' WHERE id = %s", (item['product_id'],))

        # Notify farmer
        cur.execute("""INSERT INTO notifications (user_id, title, message, link)
                      SELECT user_id, 'New Order Created', %s, '/farmer/orders'
                      FROM farmers WHERE id = %s""",
                   (f'New order #{order_id} received', item['farmer_id']))

    # Clear cart
    cur.execute("DELETE FROM cart_items WHERE buyer_id = %s", (session['user_id'],))
    mysql.connection.commit()
    cur.close()

    flash('Order placed successfully. Waiting for farmer confirmation.', 'success')
    return redirect(url_for('buyer.orders'))

@buyer_bp.route('/orders')
@login_required
def orders():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT o.*,
               GROUP_CONCAT(DISTINCT CONCAT(p.name, ' x', oi.quantity) SEPARATOR ', ') as items_summary,
               GROUP_CONCAT(DISTINCT f.farm_name SEPARATOR ', ') as farms
        FROM orders o
        JOIN order_items oi ON oi.order_id = o.id
        JOIN products p ON oi.product_id = p.id
        JOIN farmers f ON oi.farmer_id = f.id
        WHERE o.buyer_id = %s
        GROUP BY o.id ORDER BY o.created_at DESC
    """, (session['user_id'],))
    orders = cur.fetchall()

    # Check which orders have reviews
    for order in orders:
        cur.execute("SELECT id FROM reviews WHERE order_id = %s AND buyer_id = %s", (order['id'], session['user_id']))
        order['has_review'] = cur.fetchone() is not None

    cur.close()
    return render_template('buyer/orders.html', orders=orders)

@buyer_bp.route('/review/<int:order_id>', methods=['GET', 'POST'])
@login_required
def review(order_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM orders WHERE id = %s AND buyer_id = %s AND status = 'picked-up'",
               (order_id, session['user_id']))
    order = cur.fetchone()
    if not order:
        flash('Cannot review this order.', 'danger')
        return redirect(url_for('buyer.orders'))

    if request.method == 'POST':
        farmer_id = request.form['farmer_id']
        rating = int(request.form['rating'])
        comment = request.form.get('comment', '')
        cur.execute("""INSERT INTO reviews (order_id, buyer_id, farmer_id, rating, comment)
                      VALUES (%s, %s, %s, %s, %s)""",
                   (order_id, session['user_id'], farmer_id, rating, comment))
        mysql.connection.commit()
        flash('Review submitted!', 'success')
        return redirect(url_for('buyer.orders'))

    # Get farmers in this order
    cur.execute("""SELECT DISTINCT f.id, f.farm_name FROM order_items oi
                  JOIN farmers f ON oi.farmer_id = f.id WHERE oi.order_id = %s""", (order_id,))
    farmers = cur.fetchall()
    cur.close()
    return render_template('buyer/review.html', order=order, farmers=farmers)

@buyer_bp.route('/subscribe/<int:farmer_id>')
@login_required
def subscribe(farmer_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM subscriptions WHERE buyer_id = %s AND farmer_id = %s",
               (session['user_id'], farmer_id))
    if cur.fetchone():
        cur.execute("DELETE FROM subscriptions WHERE buyer_id = %s AND farmer_id = %s",
                   (session['user_id'], farmer_id))
        flash('Unsubscribed.', 'info')
    else:
        cur.execute("INSERT INTO subscriptions (buyer_id, farmer_id) VALUES (%s, %s)",
                   (session['user_id'], farmer_id))
        flash('Subscribed! You will receive notifications.', 'success')
    mysql.connection.commit()
    cur.close()
    return redirect(request.referrer or url_for('main.marketplace'))

@buyer_bp.route('/subscriptions')
@login_required
def subscriptions():
    cur = mysql.connection.cursor()
    cur.execute("""SELECT f.*, u.full_name FROM subscriptions s
                  JOIN farmers f ON s.farmer_id = f.id
                  JOIN users u ON f.user_id = u.id
                  WHERE s.buyer_id = %s""", (session['user_id'],))
    subs = cur.fetchall()
    cur.close()
    return render_template('buyer/subscriptions.html', subscriptions=subs)

@buyer_bp.route('/notifications')
@login_required
def notifications():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM notifications WHERE user_id = %s ORDER BY created_at DESC", (session['user_id'],))
    notifs = cur.fetchall()
    cur.execute("UPDATE notifications SET is_read = 1 WHERE user_id = %s AND is_read = 0", (session['user_id'],))
    mysql.connection.commit()
    cur.close()
    return render_template('buyer/notifications.html', notifications=notifs)
