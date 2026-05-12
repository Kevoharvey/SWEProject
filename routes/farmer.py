from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import mysql
from helpers import role_required, save_upload

farmer_bp = Blueprint('farmer', __name__)

@farmer_bp.route('/dashboard')
@role_required('farmer')
def dashboard():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM farmers WHERE user_id = %s", (session['user_id'],))
    farmer = cur.fetchone()
    if not farmer:
        flash('Farmer profile not found.', 'danger')
        return redirect(url_for('main.index'))

    fid = farmer['id']
    cur.execute("SELECT COUNT(*) as cnt FROM products WHERE farmer_id = %s AND is_active = 1", (fid,))
    product_count = cur.fetchone()['cnt']
    cur.execute("""SELECT COUNT(*) as cnt FROM order_items oi
                   JOIN orders o ON oi.order_id = o.id
                   WHERE oi.farmer_id = %s AND o.status = 'pending'""", (fid,))
    pending_orders = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) as cnt FROM subscriptions WHERE farmer_id = %s", (fid,))
    subscriber_count = cur.fetchone()['cnt']
    cur.execute("SELECT AVG(rating) as avg_r, COUNT(*) as cnt FROM reviews WHERE farmer_id = %s", (fid,))
    review_stats = cur.fetchone()
    cur.execute("""SELECT COALESCE(SUM(oi.subtotal), 0) as total FROM order_items oi
                   JOIN orders o ON oi.order_id = o.id
                   WHERE oi.farmer_id = %s AND o.status = 'picked-up'""", (fid,))
    total_sales = cur.fetchone()['total']
    cur.close()
    return render_template('farmer/dashboard.html', farmer=farmer, product_count=product_count,
                         pending_orders=pending_orders, subscriber_count=subscriber_count,
                         review_stats=review_stats, total_sales=total_sales)

@farmer_bp.route('/profile', methods=['GET', 'POST'])
@role_required('farmer')
def profile():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM farmers WHERE user_id = %s", (session['user_id'],))
    farmer = cur.fetchone()

    if request.method == 'POST':
        farm_name = request.form['farm_name']
        phone = request.form['phone']
        address = request.form['address']
        description = request.form['description']
        lat = request.form.get('location_lat') or None
        lng = request.form.get('location_lng') or None

        profile_img = farmer['profile_image']
        if 'profile_image' in request.files and request.files['profile_image'].filename:
            saved = save_upload(request.files['profile_image'], 'profiles')
            if saved:
                profile_img = saved

        cur.execute("""UPDATE farmers SET farm_name=%s, phone=%s, address=%s, description=%s,
                      location_lat=%s, location_lng=%s, profile_image=%s WHERE user_id=%s""",
                   (farm_name, phone, address, description, lat, lng, profile_img, session['user_id']))
        mysql.connection.commit()
        flash('Profile updated!', 'success')
        return redirect(url_for('farmer.profile'))

    cur.execute("SELECT * FROM market_schedules WHERE farmer_id = %s", (farmer['id'],))
    schedules = cur.fetchall()
    cur.close()
    return render_template('farmer/profile.html', farmer=farmer, schedules=schedules)

@farmer_bp.route('/schedule/add', methods=['POST'])
@role_required('farmer')
def add_schedule():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM farmers WHERE user_id = %s", (session['user_id'],))
    farmer = cur.fetchone()
    cur.execute("""INSERT INTO market_schedules (farmer_id, market_name, market_address, market_lat, market_lng, day_of_week, start_time, end_time)
                  VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
               (farmer['id'], request.form['market_name'], request.form.get('market_address', ''),
                request.form.get('market_lat') or None, request.form.get('market_lng') or None,
                request.form['day_of_week'], request.form['start_time'], request.form['end_time']))
    mysql.connection.commit()
    cur.close()
    flash('Market schedule added!', 'success')
    return redirect(url_for('farmer.profile'))

@farmer_bp.route('/schedule/delete/<int:sid>')
@role_required('farmer')
def delete_schedule(sid):
    cur = mysql.connection.cursor()
    cur.execute("SELECT f.id FROM farmers f JOIN market_schedules ms ON ms.farmer_id = f.id WHERE ms.id = %s AND f.user_id = %s", (sid, session['user_id']))
    if cur.fetchone():
        cur.execute("DELETE FROM market_schedules WHERE id = %s", (sid,))
        mysql.connection.commit()
        flash('Schedule removed.', 'success')
    cur.close()
    return redirect(url_for('farmer.profile'))

@farmer_bp.route('/products')
@role_required('farmer')
def products():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM farmers WHERE user_id = %s", (session['user_id'],))
    farmer = cur.fetchone()
    cur.execute("""SELECT p.*, (SELECT photo_path FROM product_photos WHERE product_id = p.id ORDER BY display_order LIMIT 1) as photo
                  FROM products p WHERE p.farmer_id = %s ORDER BY p.created_at DESC""", (farmer['id'],))
    products = cur.fetchall()
    cur.close()
    return render_template('farmer/products.html', products=products)

@farmer_bp.route('/products/add', methods=['GET', 'POST'])
@role_required('farmer')
def add_product():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM farmers WHERE user_id = %s", (session['user_id'],))
        farmer = cur.fetchone()

        cur.execute("""INSERT INTO products (farmer_id, name, category, description, price, quantity, unit, harvest_date, stock_status)
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                   (farmer['id'], request.form['name'], request.form['category'],
                    request.form.get('description', ''), request.form['price'],
                    request.form['quantity'], request.form['unit'],
                    request.form.get('harvest_date') or None, request.form.get('stock_status', 'in-stock')))
        product_id = cur.lastrowid

        # Handle photos (up to 3)
        for i in range(3):
            key = f'photo_{i}'
            if key in request.files and request.files[key].filename:
                path = save_upload(request.files[key], 'products')
                if path:
                    cur.execute("INSERT INTO product_photos (product_id, photo_path, display_order) VALUES (%s, %s, %s)",
                               (product_id, path, i))

        # Handle availability
        days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        for day in days:
            is_avail = 1 if request.form.get(f'avail_{day}') else 0
            cur.execute("INSERT INTO product_availability (product_id, day_of_week, is_available) VALUES (%s, %s, %s)",
                       (product_id, day, is_avail))

        # Notify subscribers
        cur.execute("SELECT buyer_id FROM subscriptions WHERE farmer_id = %s", (farmer['id'],))
        subscribers = cur.fetchall()
        for sub in subscribers:
            cur.execute("""INSERT INTO notifications (user_id, title, message, link)
                          VALUES (%s, %s, %s, %s)""",
                       (sub['buyer_id'], 'New Product Available!',
                        f'{request.form["name"]} is now available from {session["user_name"]}',
                        f'/product/{product_id}'))

        mysql.connection.commit()
        cur.close()
        flash('Product added successfully!', 'success')
        return redirect(url_for('farmer.products'))

    categories = ['Vegetables','Fruits','Dairy','Meat','Eggs','Honey','Baked Goods','Herbs','Flowers','Preserves','Beverages','Other']
    units = ['kg','bunch','item','dozen','liter','jar','bag']
    return render_template('farmer/add_product.html', categories=categories, units=units)

@farmer_bp.route('/products/edit/<int:pid>', methods=['GET', 'POST'])
@role_required('farmer')
def edit_product(pid):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM farmers WHERE user_id = %s", (session['user_id'],))
    farmer = cur.fetchone()
    cur.execute("SELECT * FROM products WHERE id = %s AND farmer_id = %s", (pid, farmer['id']))
    product = cur.fetchone()
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('farmer.products'))

    if request.method == 'POST':
        old_status = product['stock_status']
        new_status = request.form.get('stock_status', 'in-stock')

        cur.execute("""UPDATE products SET name=%s, category=%s, description=%s, price=%s,
                      quantity=%s, unit=%s, harvest_date=%s, stock_status=%s, is_active=%s WHERE id=%s""",
                   (request.form['name'], request.form['category'], request.form.get('description', ''),
                    request.form['price'], request.form['quantity'], request.form['unit'],
                    request.form.get('harvest_date') or None, new_status,
                    1 if request.form.get('is_active') else 0, pid))

        # Update availability
        days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        cur.execute("DELETE FROM product_availability WHERE product_id = %s", (pid,))
        for day in days:
            is_avail = 1 if request.form.get(f'avail_{day}') else 0
            cur.execute("INSERT INTO product_availability (product_id, day_of_week, is_available) VALUES (%s, %s, %s)",
                       (pid, day, is_avail))

        # New photos
        for i in range(3):
            key = f'photo_{i}'
            if key in request.files and request.files[key].filename:
                path = save_upload(request.files[key], 'products')
                if path:
                    cur.execute("INSERT INTO product_photos (product_id, photo_path, display_order) VALUES (%s, %s, %s)",
                               (pid, path, i))

        # Notify subscribers on stock change
        if old_status != new_status:
            cur.execute("SELECT buyer_id FROM subscriptions WHERE farmer_id = %s", (farmer['id'],))
            for sub in cur.fetchall():
                cur.execute("""INSERT INTO notifications (user_id, title, message, link)
                              VALUES (%s, %s, %s, %s)""",
                           (sub['buyer_id'], 'Product Update',
                            f'{request.form["name"]} is now {new_status}',
                            f'/product/{pid}'))

        mysql.connection.commit()
        flash('Product updated!', 'success')
        return redirect(url_for('farmer.products'))

    cur.execute("SELECT * FROM product_photos WHERE product_id = %s ORDER BY display_order", (pid,))
    photos = cur.fetchall()
    cur.execute("SELECT * FROM product_availability WHERE product_id = %s", (pid,))
    availability = {a['day_of_week']: a['is_available'] for a in cur.fetchall()}
    cur.close()
    categories = ['Vegetables','Fruits','Dairy','Meat','Eggs','Honey','Baked Goods','Herbs','Flowers','Preserves','Beverages','Other']
    units = ['kg','bunch','item','dozen','liter','jar','bag']
    return render_template('farmer/edit_product.html', product=product, photos=photos,
                         availability=availability, categories=categories, units=units)

@farmer_bp.route('/products/delete/<int:pid>')
@role_required('farmer')
def delete_product(pid):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM farmers WHERE user_id = %s", (session['user_id'],))
    farmer = cur.fetchone()
    cur.execute("DELETE FROM products WHERE id = %s AND farmer_id = %s", (pid, farmer['id']))
    mysql.connection.commit()
    cur.close()
    flash('Product deleted.', 'success')
    return redirect(url_for('farmer.products'))

@farmer_bp.route('/orders')
@role_required('farmer')
def orders():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM farmers WHERE user_id = %s", (session['user_id'],))
    farmer = cur.fetchone()
    cur.execute("""
        SELECT o.*, u.full_name as buyer_name, u.email as buyer_email,
               GROUP_CONCAT(CONCAT(p.name, ' x', oi.quantity) SEPARATOR ', ') as items_summary,
               SUM(oi.subtotal) as farmer_total
        FROM orders o
        JOIN order_items oi ON oi.order_id = o.id
        JOIN products p ON oi.product_id = p.id
        JOIN users u ON o.buyer_id = u.id
        WHERE oi.farmer_id = %s
        GROUP BY o.id ORDER BY o.created_at DESC
    """, (farmer['id'],))
    orders = cur.fetchall()
    cur.close()
    return render_template('farmer/orders.html', orders=orders)

@farmer_bp.route('/orders/update/<int:oid>', methods=['POST'])
@role_required('farmer')
def update_order_status(oid):
    status = request.form['status']
    cur = mysql.connection.cursor()
    cur.execute("UPDATE orders SET status = %s WHERE id = %s", (status, oid))
    # Notify buyer
    cur.execute("SELECT buyer_id FROM orders WHERE id = %s", (oid,))
    order = cur.fetchone()
    if order:
        title = 'Order Confirmed!' if status == 'confirmed' else 'Order Update'
        cur.execute("INSERT INTO notifications (user_id, title, message, link) VALUES (%s, %s, %s, %s)",
                   (order['buyer_id'], title, f'Your order #{oid} is now {status}', f'/buyer/orders'))
    mysql.connection.commit()
    cur.close()
    flash(f'Order updated to {status}.', 'success')
    return redirect(url_for('farmer.orders'))

@farmer_bp.route('/reviews')
@role_required('farmer')
def reviews():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM farmers WHERE user_id = %s", (session['user_id'],))
    farmer = cur.fetchone()
    cur.execute("""SELECT r.*, u.full_name as buyer_name FROM reviews r
                  JOIN users u ON r.buyer_id = u.id WHERE r.farmer_id = %s ORDER BY r.created_at DESC""", (farmer['id'],))
    reviews = cur.fetchall()
    cur.close()
    return render_template('farmer/reviews.html', reviews=reviews)

@farmer_bp.route('/reviews/respond/<int:rid>', methods=['POST'])
@role_required('farmer')
def respond_review(rid):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM farmers WHERE user_id = %s", (session['user_id'],))
    farmer = cur.fetchone()
    cur.execute("UPDATE reviews SET farmer_response = %s, responded_at = NOW() WHERE id = %s AND farmer_id = %s",
               (request.form['response'], rid, farmer['id']))
    mysql.connection.commit()
    cur.close()
    flash('Response posted!', 'success')
    return redirect(url_for('farmer.reviews'))
