from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from app import mysql

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm_password']
        role = request.form['role']

        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.register'))

        if role not in ('buyer', 'farmer'):
            flash('Invalid role.', 'danger')
            return redirect(url_for('auth.register'))

        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cur.fetchone():
            flash('Email already registered.', 'danger')
            cur.close()
            return redirect(url_for('auth.register'))

        pw_hash = generate_password_hash(password)
        cur.execute("INSERT INTO users (full_name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
                    (full_name, email, pw_hash, role))
        user_id = cur.lastrowid

        if role == 'farmer':
            farm_name = request.form.get('farm_name', full_name + "'s Farm")
            phone = request.form.get('phone', '')
            address = request.form.get('address', '')
            description = request.form.get('description', '')
            cur.execute("""INSERT INTO farmers (user_id, farm_name, phone, address, description)
                          VALUES (%s, %s, %s, %s, %s)""",
                       (user_id, farm_name, phone, address, description))

        mysql.connection.commit()
        cur.close()

        if role == 'farmer':
            flash('Registration submitted! Please wait for admin approval.', 'success')
        else:
            flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user['password_hash'], password):
            if user['role'] == 'farmer':
                cur = mysql.connection.cursor()
                cur.execute("SELECT status FROM farmers WHERE user_id = %s", (user['id'],))
                farmer = cur.fetchone()
                cur.close()
                if farmer and farmer['status'] != 'approved':
                    flash(f'Your farmer account is {farmer["status"]}. Please wait for admin approval.', 'warning')
                    return redirect(url_for('auth.login'))

            session['user_id'] = user['id']
            session['user_name'] = user['full_name']
            session['email'] = user['email']
            session['role'] = user['role']

            if user['role'] == 'farmer':
                return redirect(url_for('farmer.dashboard'))
            elif user['role'] == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('main.marketplace'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))
