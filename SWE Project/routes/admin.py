from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import mysql
from helpers import role_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@role_required('admin')
def dashboard():
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) as cnt FROM users WHERE role = 'buyer'")
    buyer_count = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) as cnt FROM farmers WHERE status = 'approved'")
    farmer_count = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) as cnt FROM farmers WHERE status = 'pending'")
    pending_count = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) as cnt FROM products WHERE is_active = 1")
    product_count = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) as cnt FROM orders")
    order_count = cur.fetchone()['cnt']
    cur.execute("SELECT COALESCE(SUM(total_amount), 0) as total FROM orders WHERE status = 'picked-up'")
    total_revenue = cur.fetchone()['total']
    # Recent orders
    cur.execute("""SELECT o.*, u.full_name as buyer_name FROM orders o
                  JOIN users u ON o.buyer_id = u.id ORDER BY o.created_at DESC LIMIT 10""")
    recent_orders = cur.fetchall()
    # Sales by category
    cur.execute("""SELECT p.category, SUM(oi.subtotal) as total, COUNT(DISTINCT oi.order_id) as order_count
                  FROM order_items oi JOIN products p ON oi.product_id = p.id
                  JOIN orders o ON oi.order_id = o.id WHERE o.status = 'picked-up'
                  GROUP BY p.category ORDER BY total DESC""")
    category_sales = cur.fetchall()
    cur.close()
    return render_template('admin/dashboard.html', buyer_count=buyer_count, farmer_count=farmer_count,
                         pending_count=pending_count, product_count=product_count, order_count=order_count,
                         total_revenue=total_revenue, recent_orders=recent_orders, category_sales=category_sales)

@admin_bp.route('/farmers')
@role_required('admin')
def farmers():
    status_filter = request.args.get('status', '')
    cur = mysql.connection.cursor()
    query = "SELECT f.*, u.full_name, u.email FROM farmers f JOIN users u ON f.user_id = u.id"
    params = []
    if status_filter:
        query += " WHERE f.status = %s"
        params.append(status_filter)
    query += " ORDER BY f.created_at DESC"
    cur.execute(query, params)
    farmers = cur.fetchall()
    cur.close()
    return render_template('admin/farmers.html', farmers=farmers, status_filter=status_filter)

@admin_bp.route('/farmers/approve/<int:fid>')
@role_required('admin')
def approve_farmer(fid):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE farmers SET status = 'approved' WHERE id = %s", (fid,))
    cur.execute("SELECT user_id FROM farmers WHERE id = %s", (fid,))
    farmer = cur.fetchone()
    if farmer:
        cur.execute("INSERT INTO notifications (user_id, title, message) VALUES (%s, %s, %s)",
                   (farmer['user_id'], 'Registration Approved!', 'Your farmer account has been approved. You can now list products.'))
    mysql.connection.commit()
    cur.close()
    flash('Farmer approved.', 'success')
    return redirect(url_for('admin.farmers'))

@admin_bp.route('/farmers/reject/<int:fid>')
@role_required('admin')
def reject_farmer(fid):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE farmers SET status = 'rejected' WHERE id = %s", (fid,))
    cur.execute("SELECT user_id FROM farmers WHERE id = %s", (fid,))
    farmer = cur.fetchone()
    if farmer:
        cur.execute("INSERT INTO notifications (user_id, title, message) VALUES (%s, %s, %s)",
                   (farmer['user_id'], 'Registration Rejected', 'Your farmer registration has been rejected. Please contact support.'))
    mysql.connection.commit()
    cur.close()
    flash('Farmer rejected.', 'info')
    return redirect(url_for('admin.farmers'))

@admin_bp.route('/products')
@role_required('admin')
def products():
    cur = mysql.connection.cursor()
    cur.execute("""SELECT p.*, f.farm_name,
                  (SELECT photo_path FROM product_photos WHERE product_id = p.id ORDER BY display_order LIMIT 1) as photo
                  FROM products p JOIN farmers f ON p.farmer_id = f.id ORDER BY p.created_at DESC""")
    products = cur.fetchall()
    cur.close()
    return render_template('admin/products.html', products=products)

@admin_bp.route('/products/remove/<int:pid>')
@role_required('admin')
def remove_product(pid):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE products SET is_active = 0 WHERE id = %s", (pid,))
    mysql.connection.commit()
    cur.close()
    flash('Product removed from listings.', 'success')
    return redirect(url_for('admin.products'))

@admin_bp.route('/products/restore/<int:pid>')
@role_required('admin')
def restore_product(pid):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE products SET is_active = 1 WHERE id = %s", (pid,))
    mysql.connection.commit()
    cur.close()
    flash('Product restored.', 'success')
    return redirect(url_for('admin.products'))

@admin_bp.route('/reports')
@role_required('admin')
def reports():
    cur = mysql.connection.cursor()
    # Monthly sales
    cur.execute("""SELECT DATE_FORMAT(o.created_at, '%%Y-%%m') as month, SUM(o.total_amount) as revenue,
                  COUNT(*) as order_count FROM orders o WHERE o.status = 'picked-up'
                  GROUP BY month ORDER BY month DESC LIMIT 12""")
    monthly = cur.fetchall()
    # Top farmers by revenue
    cur.execute("""SELECT f.farm_name, SUM(oi.subtotal) as revenue, COUNT(DISTINCT oi.order_id) as orders
                  FROM order_items oi JOIN farmers f ON oi.farmer_id = f.id
                  JOIN orders o ON oi.order_id = o.id WHERE o.status = 'picked-up'
                  GROUP BY f.id ORDER BY revenue DESC LIMIT 10""")
    top_farmers = cur.fetchall()
    # Top products
    cur.execute("""SELECT p.name, f.farm_name, SUM(oi.quantity) as sold, SUM(oi.subtotal) as revenue
                  FROM order_items oi JOIN products p ON oi.product_id = p.id
                  JOIN farmers f ON p.farmer_id = f.id JOIN orders o ON oi.order_id = o.id
                  WHERE o.status = 'picked-up'
                  GROUP BY p.id ORDER BY sold DESC LIMIT 10""")
    top_products = cur.fetchall()
    cur.close()
    return render_template('admin/reports.html', monthly=monthly, top_farmers=top_farmers, top_products=top_products)
