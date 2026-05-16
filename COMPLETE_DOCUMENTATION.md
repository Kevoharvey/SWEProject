# Local Farmers Market Aggregator - Complete Documentation

**Version:** 1.0.0 | **Last Updated:** May 2026

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Database Schema](#database-schema)
5. [User Roles & Permissions](#user-roles--permissions)
6. [Quick Start Setup](#quick-start-setup)
7. [Detailed Setup Instructions](#detailed-setup-instructions)
8. [Routes & API Endpoints](#routes--api-endpoints)
9. [Code Architecture & Design Patterns](#code-architecture--design-patterns)
10. [Code Examples & Common Patterns](#code-examples--common-patterns)
11. [Testing Guidelines](#testing-guidelines)
12. [Development Guidelines](#development-guidelines)
13. [Troubleshooting](#troubleshooting)

---

# Project Overview

## About the Project

**Local Farmers Market Aggregator** is a web-based marketplace platform that connects local farmers with buyers. The platform enables farmers to list their products, manage orders, and connect with customers. Buyers can browse products, place orders for pickup at local farmers markets, and follow their favorite farmers.

### Key Features
- **Multi-role user system**: Buyers, Farmers, and Admins
- **Product marketplace** with advanced filtering and sorting
- **Shopping cart** functionality with persistent storage
- **Order management** with pickup scheduling at farmers markets
- **Farmer approval workflow** for quality control
- **Review & rating system** (1-5 stars)
- **Farmer subscriptions** (followers/subscribers)
- **Notifications system** for order updates
- **Admin dashboard** with analytics and management tools
- **GPS location tracking** for farmers and market locations
- **Weekly availability scheduling** for products
- **Image upload system** with validation

---

# Technology Stack

| Layer | Technologies |
|-------|---------------|
| **Backend** | Flask 3.1.1, Python 3.x |
| **Database** | MySQL 5.7+ |
| **Frontend** | HTML5/CSS3/JavaScript, Jinja2 Templates |
| **Database Driver** | flask-mysqldb 2.0.0 |
| **Security** | Werkzeug (password hashing, file security) |
| **Utilities** | python-dotenv (config), Pillow (image processing) |
| **Port** | 5000 (development) |

### Dependencies
```
Flask==3.1.1
flask-mysqldb==2.0.0
python-dotenv==1.1.0
Werkzeug==3.1.3
Pillow==11.1.0
```

---

# Project Structure

```
SWEProject/
├── app.py                      # Flask app factory and initialization
├── config.py                   # Configuration management (environment variables)
├── helpers.py                  # Utility functions (auth decorators, file upload)
├── database_models.md          # Database schema documentation with diagrams
├── schema.sql                  # Database initialization script
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (DO NOT COMMIT)
├── .env.example                # Example environment variables template
│
├── routes/                     # Flask blueprints for modular organization
│   ├── __init__.py            # Routes package initialization
│   ├── auth.py                # Authentication (login, register, password reset)
│   ├── main.py                # Public pages (home, marketplace, product details)
│   ├── farmer.py              # Farmer-specific features
│   ├── buyer.py               # Buyer-specific features
│   ├── admin.py               # Admin management and analytics
│   └── api.py                 # API endpoints (optional JSON API)
│
├── static/                    # Static files (CSS, JavaScript, images)
│   ├── css/
│   │   └── style.css          # Main stylesheet
│   ├── js/                    # JavaScript files
│   └── uploads/               # User-uploaded files (DYNAMICALLY CREATED)
│       ├── products/          # Product images
│       └── profiles/          # Farmer profile images
│
└── templates/                 # Jinja2 HTML templates
    ├── base.html              # Base template with navigation
    ├── 404.html               # 404 error page
    ├── index.html             # Homepage
    ├── marketplace.html       # Product marketplace with filters
    ├── map.html               # Market location map
    ├── product_detail.html    # Individual product page
    ├── farmer_public.html     # Public farmer profile
    │
    ├── auth/                  # Authentication pages
    │   ├── login.html
    │   ├── register.html
    │   └── forgot_password.html
    │
    ├── farmer/                # Farmer dashboard and management
    │   ├── dashboard.html
    │   ├── profile.html
    │   ├── products.html
    │   ├── add_product.html
    │   ├── edit_product.html
    │   ├── orders.html
    │   └── reviews.html
    │
    ├── buyer/                 # Buyer pages
    │   ├── dashboard.html
    │   ├── cart.html
    │   ├── orders.html
    │   ├── subscriptions.html
    │   ├── notifications.html
    │   └── review.html
    │
    └── admin/                 # Admin management pages
        ├── dashboard.html
        ├── farmers.html
        ├── products.html
        └── reports.html
```

---

# Database Schema

## Overview

The database uses MySQL with InnoDB engine for referential integrity. All tables support foreign key constraints and use proper indexing for performance.

## Core Tables

### `users` - All user accounts
Stores registration for buyers, farmers, and admins.

```sql
- id (INT, PRIMARY KEY, AUTO_INCREMENT)
- email (VARCHAR 255, UNIQUE, NOT NULL)
- password_hash (VARCHAR 255, NOT NULL)
- full_name (VARCHAR 150, NOT NULL)
- role (ENUM: 'buyer', 'farmer', 'admin') DEFAULT 'buyer'
- created_at (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
```

### `farmers` - Extended farmer profiles
One-to-one relationship with users table (optional for farmers).

```sql
- id (INT, PRIMARY KEY, AUTO_INCREMENT)
- user_id (INT, FOREIGN KEY→users, UNIQUE, NOT NULL)
- farm_name (VARCHAR 200, NOT NULL)
- description (TEXT)
- address (VARCHAR 500)
- location_lat (DECIMAL 10,8) - GPS latitude
- location_lng (DECIMAL 11,8) - GPS longitude
- phone (VARCHAR 30)
- profile_image (VARCHAR 500) - path to uploaded image
- status (ENUM: 'pending', 'approved', 'rejected') DEFAULT 'pending'
- created_at (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
```

### `products` - Farmer product listings
Stores all products offered by farmers.

```sql
- id (INT, PRIMARY KEY, AUTO_INCREMENT)
- farmer_id (INT, FOREIGN KEY→farmers, NOT NULL)
- name (VARCHAR 200, NOT NULL)
- category (ENUM: 'Vegetables','Fruits','Dairy','Meat','Eggs','Honey',
           'Baked Goods','Herbs','Flowers','Preserves','Beverages','Other')
- description (TEXT)
- price (DECIMAL 10,2, NOT NULL)
- quantity (INT NOT NULL DEFAULT 0)
- unit (ENUM: 'kg','bunch','item','dozen','liter','jar','bag') DEFAULT 'kg'
- harvest_date (DATE)
- stock_status (ENUM: 'in-stock','low-stock','sold-out') DEFAULT 'in-stock'
- is_active (BOOLEAN DEFAULT TRUE)
- created_at (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
- updated_at (TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)
```

### `orders` - Customer orders
Stores orders placed by buyers for specific market pickups.

```sql
- id (INT, PRIMARY KEY, AUTO_INCREMENT)
- buyer_id (INT, FOREIGN KEY→users, NOT NULL)
- market_location (VARCHAR 500)
- pickup_date (DATE, NOT NULL)
- pickup_time_slot (VARCHAR 50, NOT NULL)
- status (ENUM: 'pending','confirmed','ready','picked-up','cancelled') DEFAULT 'pending'
- total_amount (DECIMAL 10,2, NOT NULL)
- notes (TEXT)
- created_at (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
- updated_at (TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)
```

### `cart_items` - Shopping cart items
Stores items in each buyer's shopping cart.

```sql
- id (INT, PRIMARY KEY, AUTO_INCREMENT)
- buyer_id (INT, FOREIGN KEY→users, NOT NULL)
- product_id (INT, FOREIGN KEY→products, NOT NULL)
- quantity (INT NOT NULL DEFAULT 1)
- added_at (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
- UNIQUE KEY unique_cart_product (buyer_id, product_id)
```

### Additional Tables

**product_photos** - Up to 3 images per product
```sql
- id, product_id (FK), photo_path, display_order
```

**product_availability** - Weekly availability schedule
```sql
- id, product_id (FK), day_of_week (Mon-Sun), is_available
- UNIQUE(product_id, day_of_week)
```

**market_schedules** - Where/when farmers sell
```sql
- id, farmer_id (FK), market_name, market_address, market_lat/lng
- day_of_week, start_time, end_time
```

**order_items** - Line items within orders
```sql
- id, order_id (FK), product_id (FK), farmer_id (FK)
- quantity, unit_price, subtotal
```

**reviews** - Customer reviews and responses
```sql
- id, order_id (FK), buyer_id (FK), farmer_id (FK)
- rating (1-5), comment, farmer_response, created_at, responded_at
```

**subscriptions** - Buyers follow farmers
```sql
- id, buyer_id (FK), farmer_id (FK), created_at
- UNIQUE(buyer_id, farmer_id)
```

**notifications** - In-app notifications
```sql
- id, user_id (FK), title, message, link, is_read, created_at
```

## Database Relationships

```
User (1) ──→ (0..1) Farmer
Farmer (1) ──→ (0..*) Product
Product (1) ──→ (0..*) ProductPhoto
Product (1) ──→ (0..7) ProductAvailability
Farmer (1) ──→ (0..*) MarketSchedule
User (1) ──→ (0..*) CartItem
Product (1) ──→ (0..*) CartItem
User (1) ──→ (0..*) Order
Order (1) ──→ (0..*) OrderItem
Product (1) ──→ (0..*) OrderItem
Order (1) ──→ (0..*) Review
User (1) ──→ (0..*) Review (as buyer)
Farmer (1) ──→ (0..*) Review (as reviewed)
User (1) ──→ (0..*) Subscription (as buyer)
Farmer (1) ──→ (0..*) Subscription (as followed)
User (1) ──→ (0..*) Notification
```

---

# User Roles & Permissions

## Buyer
**Who**: Regular users purchasing fresh produce and farm products

**Permissions**:
- Browse marketplace with advanced filtering and search
- View detailed product information with photos
- Add/remove items from shopping cart
- Place orders for market pickup
- Receive order confirmations and updates
- Subscribe to (follow) favorite farmers
- Leave reviews and ratings on farmers
- Track order history and status
- View and manage notifications
- View all subscriptions

**Routes Prefix**: `/buyer/*`
**Default Redirects To**: Marketplace on login

## Farmer
**Who**: Agricultural producers selling their products (requires admin approval)

**Permissions**:
- Register with farm details (pending admin approval)
- Manage complete farm profile with images and GPS location
- Add/edit/delete products with up to 3 photos each
- Set weekly market attendance schedule
- Set product availability by day of week
- View pending orders for their products
- Manage order fulfillment and confirm ready for pickup
- View and respond to customer reviews
- Track subscriber count
- View sales analytics and revenue
- Receive notifications for new orders
- Upload profile images

**Routes Prefix**: `/farmer/*`
**Requirements**: Must be approved by admin before accessing dashboard
**Default Redirects To**: Farmer dashboard on login

## Admin
**Who**: System administrators managing platform operations and quality

**Permissions**:
- View system-wide dashboard with analytics
- Approve/reject farmer registrations
- View and manage all farmers
- View and remove inappropriate products
- Monitor all orders and users
- View sales reports by category
- Generate system reports
- Manage notifications
- Access user and activity monitoring
- Configure system settings (if extended)

**Routes Prefix**: `/admin/*`
**Default Redirects To**: Admin dashboard on login

### Default Admin Account
```
Email: admin@farmmarket.com
Password: admin123
```
⚠️ **IMPORTANT**: Change these credentials in production!

---

# Quick Start Setup

## Prerequisites
- Python 3.8+
- MySQL 5.7+
- Git
- 10 minutes

## Steps

1. **Clone and navigate**
   ```bash
   git clone <repository-url>
   cd SWEProject
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup database**
   ```bash
   mysql -u root -p < schema.sql
   ```

5. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your MySQL credentials
   ```

6. **Run application**
   ```bash
   python app.py
   ```

Visit `http://localhost:5000`

---

# Detailed Setup Instructions

## Step 1: Install Python

**macOS:**
```bash
brew install python3
python3 --version  # Verify: Python 3.x.x
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install python3 python3-venv python3-pip
python3 --version
```

**Windows:**
- Download from python.org
- Run installer
- **IMPORTANT**: Check "Add Python to PATH"
- Verify: `python --version`

## Step 2: Install MySQL

**macOS:**
```bash
brew install mysql
mysql --version
brew services start mysql
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install mysql-server
sudo mysql_secure_installation  # Follow prompts
sudo service mysql start
```

**Windows:**
- Download MySQL Community Server
- Run installer, follow setup wizard
- Configure as service
- Start MySQL Service from Services panel

## Step 3: Verify MySQL Connection

```bash
mysql -u root -p
# Enter password
# Should show: mysql>
exit  # Exit MySQL
```

## Step 4: Clone Repository

```bash
git clone <repository-url>
cd SWEProject
pwd  # Display current directory
ls   # Show files (should see app.py, config.py, etc.)
```

## Step 5: Create Virtual Environment

```bash
python3 -m venv venv

# Activate (choose based on your OS):
# macOS/Linux:
source venv/bin/activate

# Windows PowerShell:
venv\Scripts\Activate.ps1

# Windows Command Prompt:
venv\Scripts\activate.bat

# Verify activation (should show "venv" in terminal)
which python  # macOS/Linux
where python  # Windows
```

## Step 6: Install Python Packages

```bash
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# Verify (should list Flask, flask-mysqldb, etc.)
pip list
```

## Step 7: Create and Load Database

```bash
# Create the database
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS farmers_market;"

# Load the schema
mysql -u root -p farmers_market < schema.sql

# Verify (should show all tables created)
mysql -u root -p farmers_market -e "SHOW TABLES;"
```

## Step 8: Configure Environment Variables

Create `.env` file in project root:

```bash
cp .env.example .env
```

Edit `.env` with your settings:
```
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password_here
MYSQL_DB=farmers_market
MYSQL_CURSORCLASS=DictCursor
SECRET_KEY=your-super-secret-key-change-this
DEBUG=True
```

**Important Security Notes:**
- Never commit `.env` to git (already in `.gitignore`)
- Change `SECRET_KEY` for production
- Use strong passwords for MySQL
- Store sensitive data in environment variables only

## Step 9: Test Database Connection

```bash
python3 << 'EOF'
from config import Config
import mysql.connector

try:
    conn = mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB
    )
    print("✓ Database connection successful!")
    conn.close()
except Exception as e:
    print(f"✗ Connection failed: {e}")
EOF
```

## Step 10: Run Application

```bash
# Make sure venv is activated (should see "venv" in terminal)
python app.py
```

**Expected output:**
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

**Open in browser**: `http://localhost:5000`

---

# Routes & API Endpoints

## Public Routes (No Login Required)

### Homepage
```
GET /
```
Displays homepage with featured products and platform statistics.

### Marketplace
```
GET /marketplace
```
Displays all products with advanced filtering and sorting.

**Query Parameters**:
- `category` - Filter by product category
- `search` - Search product names, descriptions, farm names
- `price_min` - Minimum price filter
- `price_max` - Maximum price filter
- `market_day` - Filter by market day (Monday-Sunday)
- `farm` - Filter by farm name
- `sort` - Sort by `newest` (default), `price_low`, `price_high`

**Example**:
```
GET /marketplace?category=Vegetables&price_min=5&price_max=20&sort=price_low
```

### Product Detail
```
GET /product/<product_id>
```
Shows complete product details including photos, farmer info, reviews, and availability.

### Farmer Profile (Public)
```
GET /farmer_public/<farmer_id>
```
Public farmer profile with farm details and products.

### Market Map
```
GET /map
```
Map view of all market locations.

---

## Authentication Routes

### Register
```
GET  /register          # Show registration form
POST /register          # Submit registration
```

**Form Data**:
```
full_name (required)
email (required, must be unique)
password (required, min 6 chars)
confirm_password (required, must match)
role (required: 'buyer' or 'farmer')
farm_name (required if farmer)
phone (optional if farmer)
address (optional if farmer)
description (optional if farmer)
```

### Login
```
GET  /login             # Show login form
POST /login             # Submit login
```

**Form Data**:
```
email (required)
password (required)
```

### Password Reset
```
GET  /forgot_password           # Show reset form
POST /forgot_password           # Submit new password
```

### Logout
```
GET  /logout
```

---

## Farmer Routes (`/farmer/*`)

All routes require `@role_required('farmer')` decorator.

```
GET  /dashboard               # Dashboard with stats
GET  /profile                 # Edit farm profile
POST /profile                 # Update profile
POST /schedule/add            # Add market attendance
GET  /schedule/delete/<id>    # Remove market attendance
GET  /products                # List products
GET  /add_product             # Add product form
POST /add_product             # Create product
GET  /edit_product/<id>       # Edit product form
POST /edit_product/<id>       # Update product
GET  /delete_product/<id>     # Delete product
GET  /orders                  # View pending orders
POST /order/<id>/confirm      # Confirm ready for pickup
GET  /reviews                 # View reviews
POST /reviews/<id>/respond    # Respond to review
```

---

## Buyer Routes (`/buyer/*`)

All routes require `@login_required` decorator.

```
GET  /dashboard                      # Dashboard
GET  /cart                           # Shopping cart
POST /cart/add                       # Add to cart
POST /cart/update                    # Update cart item
GET  /cart/remove/<id>               # Remove from cart
POST /checkout                       # Create order
GET  /orders                         # Order history
GET  /orders/<id>                    # Order detail
GET  /subscriptions                  # Followed farmers
POST /subscribe/<farmer_id>          # Follow farmer
POST /unsubscribe/<farmer_id>        # Unfollow farmer
GET  /notifications                  # All notifications
POST /notifications/<id>/read        # Mark as read
GET  /review/<order_id>              # Review form
POST /review                         # Submit review
```

---

## Admin Routes (`/admin/*`)

All routes require `@role_required('admin')` decorator.

```
GET  /dashboard                      # Dashboard & analytics
GET  /farmers                        # List all farmers
GET  /farmers/approve/<id>           # Approve farmer
GET  /farmers/reject/<id>            # Reject farmer
GET  /products                       # All products
GET  /products/remove/<id>           # Deactivate product
GET  /reports                        # Reports & analytics
```

---

# Code Architecture & Design Patterns

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         Templates (Jinja2)                  │
│              HTML Views for Each User Role                   │
└─────────────────────────────────────────────────────────────┘
                            ↑
                    ┌────────┴─────────┐
                    │                  │
        ┌───────────▼────────┐    ┌───▼──────────────┐
        │  Route Handlers    │    │  Static Files    │
        │  (routes/*.py)     │    │  CSS/JS/Images   │
        └───────────┬────────┘    └──────────────────┘
                    │
        ┌───────────▼────────────────────┐
        │    Flask Application Core      │
        │  - app.py (App Factory)        │
        │  - config.py (Configuration)   │
        │  - helpers.py (Utilities)      │
        └───────────┬────────────────────┘
                    │
        ┌───────────▼────────────────────┐
        │    MySQL Database Layer        │
        │  - Schemas & Tables            │
        │  - Data Models                 │
        │  - Queries & Transactions      │
        └────────────────────────────────┘
```

## Design Patterns

### 1. Blueprint Pattern (Flask Blueprints)
Organizes routes into modular, maintainable components.

```python
# routes/auth.py
from flask import Blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    # Handle login logic
```

**Benefits**: Separation of concerns, reusability, testability, clear URL prefixes

### 2. Factory Pattern (App Factory)
Creates Flask app instances with different configurations.

```python
# app.py
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    mysql.init_app(app)
    # Register blueprints
    return app
```

**Benefits**: Different configs for dev/test/prod, easy testing, scalable

### 3. Decorator Pattern (Auth Decorators)
Wraps routes with authentication and authorization logic.

```python
@login_required
def protected_route():
    pass

@role_required('farmer')
def farmer_only():
    pass
```

**Benefits**: DRY principle, centralized security, reusability

### 4. MVC Pattern
Separation of Model-View-Controller concerns:
- **Model**: Database schemas (schema.sql)
- **View**: Templates (Jinja2 HTML)
- **Controller**: Route handlers (routes/*.py)

## Code Style Guidelines

### Python Naming
```python
def register_user():           # Functions: snake_case
class UserManager:             # Classes: PascalCase
MYSQL_HOST = "localhost"       # Constants: UPPERCASE
user_id = 1                    # Variables: snake_case
```

### Database Naming
```python
users                          # Tables: lowercase, plural
user_id                        # Columns: snake_case
farmer_id                      # Foreign keys: {table}_id
is_active                      # Booleans: is_* or has_*
created_at                     # Timestamps: *_at
```

### HTML/CSS Naming
```html
<div class="product-card">    <!-- Classes: kebab-case -->
<button id="btn-submit">      <!-- IDs: kebab-case -->
```

## Best Practices

### 1. DRY (Don't Repeat Yourself)
Use decorators and utilities to avoid repeating code.

### 2. SQL Injection Prevention
Always use parameterized queries:
```python
# GOOD
cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))

# BAD
cur.execute(f"SELECT * FROM users WHERE id = {user_id}")
```

### 3. Resource Management
Always close cursors:
```python
try:
    cur = mysql.connection.cursor()
    cur.execute(query, params)
finally:
    cur.close()
```

### 4. Transactions
Group related operations:
```python
cur.execute("INSERT INTO orders ...")
cur.execute("INSERT INTO order_items ...")
mysql.connection.commit()
```

### 5. Error Handling
Handle exceptions gracefully:
```python
try:
    # DB operation
except Exception as e:
    mysql.connection.rollback()
    flash('Error occurred', 'danger')
finally:
    cur.close()
```

---

# Code Examples & Common Patterns

## Authentication Examples

### Protecting Routes

```python
from helpers import login_required, role_required

# Require any login
@buyer_bp.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    return render_template('buyer/dashboard.html')

# Require specific role
@admin_bp.route('/dashboard')
@role_required('admin')
def admin_dashboard():
    return render_template('admin/dashboard.html')

# Require farmer role
@farmer_bp.route('/products')
@role_required('farmer')
def products():
    return render_template('farmer/products.html')
```

### Checking Session

```python
if 'user_id' not in session:
    flash('Please log in first', 'warning')
    return redirect(url_for('auth.login'))

if session.get('role') != 'farmer':
    flash('Access denied', 'danger')
    return redirect(url_for('main.index'))

user_id = session['user_id']
user_name = session['user_name']
role = session['role']
```

## Database Query Examples

### SELECT - Basic
```python
cur = mysql.connection.cursor()
cur.execute("""
    SELECT id, name, price FROM products
    WHERE id = %s AND is_active = 1
""", (product_id,))
product = cur.fetchone()
cur.close()
```

### SELECT - With JOIN
```python
cur.execute("""
    SELECT p.id, p.name, p.price, f.farm_name, f.address,
           AVG(r.rating) as avg_rating
    FROM products p
    JOIN farmers f ON p.farmer_id = f.id
    LEFT JOIN reviews r ON r.farmer_id = f.id
    WHERE f.status = 'approved' AND p.is_active = 1
    GROUP BY p.id
    ORDER BY p.created_at DESC
    LIMIT 20
""")
products = cur.fetchall()
```

### SELECT - With Filtering
```python
query = """
    SELECT p.*, f.farm_name FROM products p
    JOIN farmers f ON p.farmer_id = f.id
    WHERE f.status = 'approved' AND p.is_active = 1
"""
params = []

if category:
    query += " AND p.category = %s"
    params.append(category)

if price_min:
    query += " AND p.price >= %s"
    params.append(float(price_min))

query += " ORDER BY p.created_at DESC"
cur.execute(query, params)
products = cur.fetchall()
```

### INSERT - Single Record
```python
cur = mysql.connection.cursor()
try:
    pw_hash = generate_password_hash(password)
    cur.execute("""
        INSERT INTO users (full_name, email, password_hash, role)
        VALUES (%s, %s, %s, %s)
    """, (full_name, email, pw_hash, 'buyer'))
    user_id = cur.lastrowid
    mysql.connection.commit()
    flash('Registration successful!', 'success')
except Exception as e:
    mysql.connection.rollback()
    flash('Registration failed', 'danger')
finally:
    cur.close()
```

### INSERT - Multiple Related Records
```python
try:
    cur.execute("""
        INSERT INTO products (farmer_id, name, category, price, description)
        VALUES (%s, %s, %s, %s, %s)
    """, (farmer_id, name, category, price, description))
    product_id = cur.lastrowid
    
    # Insert photos
    for i, file in enumerate(request.files.getlist('photos')):
        if file and allowed_file(file.filename):
            photo_path = save_upload(file, 'products')
            cur.execute("""
                INSERT INTO product_photos (product_id, photo_path, display_order)
                VALUES (%s, %s, %s)
            """, (product_id, photo_path, i))
    
    # Insert availability
    for day in ['Monday', 'Tuesday', ...]:
        cur.execute("""
            INSERT INTO product_availability (product_id, day_of_week, is_available)
            VALUES (%s, %s, %s)
        """, (product_id, day, True))
    
    mysql.connection.commit()
finally:
    cur.close()
```

### UPDATE
```python
try:
    cur.execute("""
        UPDATE farmers
        SET farm_name = %s, phone = %s, address = %s
        WHERE user_id = %s
    """, (farm_name, phone, address, session['user_id']))
    mysql.connection.commit()
    flash('Profile updated!', 'success')
except Exception as e:
    mysql.connection.rollback()
    flash('Update failed', 'danger')
finally:
    cur.close()
```

### DELETE (Soft)
```python
try:
    cur.execute("UPDATE products SET is_active = 0 WHERE id = %s", (product_id,))
    mysql.connection.commit()
    flash('Product removed', 'success')
except:
    mysql.connection.rollback()
    flash('Failed to delete', 'danger')
finally:
    cur.close()
```

## File Upload Examples

```python
from helpers import allowed_file, save_upload

if 'profile_image' in request.files:
    file = request.files['profile_image']
    if file and allowed_file(file.filename):
        profile_image_path = save_upload(file, subfolder='profiles')
        # Use path in database
    else:
        flash('Invalid file type. Allowed: PNG, JPG, JPEG, GIF, WebP', 'warning')
```

## Form Validation Examples

```python
# Validate required fields
if not full_name or not email or not password:
    flash('Please fill all required fields', 'danger')
    return redirect(url_for('auth.register'))

# Validate length
if len(full_name) < 2 or len(full_name) > 150:
    flash('Full name must be 2-150 characters', 'danger')
    return redirect(url_for('auth.register'))

# Validate email format
if '@' not in email or '.' not in email:
    flash('Please enter a valid email address', 'danger')
    return redirect(url_for('auth.register'))

# Validate passwords match
if password != confirm_password:
    flash('Passwords do not match', 'danger')
    return redirect(url_for('auth.register'))

# Check email not registered
cur.execute("SELECT id FROM users WHERE email = %s", (email,))
if cur.fetchone():
    flash('Email already registered', 'danger')
    return redirect(url_for('auth.register'))
```

## Shopping Cart & Order Example

```python
@buyer_bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    market_location = request.form.get('market_location', '').strip()
    pickup_date = request.form.get('pickup_date')
    pickup_time_slot = request.form.get('pickup_time_slot', '').strip()
    
    if not market_location or not pickup_date or not pickup_time_slot:
        flash('Please fill all required fields', 'danger')
        return redirect(url_for('buyer.cart'))
    
    cur = mysql.connection.cursor()
    try:
        # Get cart items
        cur.execute("""
            SELECT ci.product_id, ci.quantity, p.price, p.farmer_id
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.id
            WHERE ci.buyer_id = %s
        """, (session['user_id'],))
        
        cart_items = cur.fetchall()
        if not cart_items:
            flash('Cart is empty', 'warning')
            return redirect(url_for('buyer.cart'))
        
        # Calculate total
        total = sum(item['quantity'] * item['price'] for item in cart_items)
        
        # Create order
        cur.execute("""
            INSERT INTO orders (buyer_id, market_location, pickup_date, pickup_time_slot, total_amount, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (session['user_id'], market_location, pickup_date, pickup_time_slot, total, 'pending'))
        
        order_id = cur.lastrowid
        
        # Create order items
        for item in cart_items:
            cur.execute("""
                INSERT INTO order_items (order_id, product_id, farmer_id, quantity, unit_price, subtotal)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (order_id, item['product_id'], item['farmer_id'], 
                  item['quantity'], item['price'], item['quantity'] * item['price']))
        
        # Clear cart
        cur.execute("DELETE FROM cart_items WHERE buyer_id = %s", (session['user_id'],))
        
        mysql.connection.commit()
        flash('Order created successfully!', 'success')
        return redirect(url_for('buyer.orders'))
    
    except Exception as e:
        mysql.connection.rollback()
        flash('Failed to create order', 'danger')
        return redirect(url_for('buyer.cart'))
    finally:
        cur.close()
```

---

# Testing Guidelines

## Manual Testing Checklist

### Authentication Flow
- [ ] Register as buyer - verify success message and redirect to login
- [ ] Register as farmer - verify approval message shown
- [ ] Login with valid credentials - verify redirect to dashboard
- [ ] Login with invalid credentials - verify error message
- [ ] Password reset - verify can login with new password
- [ ] Admin approves farmer - verify farmer can login and access dashboard
- [ ] Admin rejects farmer - verify farmer cannot access farmer dashboard

### Buyer Features
- [ ] Browse marketplace - verify products display
- [ ] Filter by category - verify only selected category shows
- [ ] Filter by price range - verify prices within range
- [ ] Search by name - verify results match
- [ ] Sort by newest - verify newest first
- [ ] Sort by price - verify ascending/descending order
- [ ] View product detail - verify all info displays
- [ ] Add to cart - verify item count increases
- [ ] View cart - verify items grouped by farmer
- [ ] Update cart quantity - verify updates
- [ ] Remove from cart - verify removed
- [ ] Checkout - verify order created, cart cleared
- [ ] View orders - verify all orders listed
- [ ] View order detail - verify complete info
- [ ] Subscribe to farmer - verify added to subscriptions
- [ ] Unsubscribe - verify removed from subscriptions
- [ ] Leave review - verify appears on farmer profile

### Farmer Features
- [ ] Complete farmer registration - verify pending approval
- [ ] Admin approves registration - verify can login
- [ ] Update farm profile - verify changes persist
- [ ] Add market schedule - verify appears in profile
- [ ] Remove market schedule - verify removed
- [ ] Add product - verify appears in products list
- [ ] Edit product - verify changes persist
- [ ] Delete product - verify removed from marketplace
- [ ] Upload product images - verify display correctly
- [ ] View pending orders - verify items from this farmer
- [ ] Confirm order ready - verify status changes
- [ ] View reviews - verify all reviews appear
- [ ] Respond to review - verify response appears

### Admin Features
- [ ] View dashboard - verify stats accurate
- [ ] Approve farmer - verify status changes, notification sent
- [ ] Reject farmer - verify status changes, notification sent
- [ ] View all products - verify complete list
- [ ] Remove product - verify deactivated from marketplace
- [ ] View all farmers - verify filters work

### Data Validation
- [ ] Empty required fields - verify error shown, not submitted
- [ ] Invalid email format - verify rejected
- [ ] Password mismatch - verify error
- [ ] Price as negative - verify error
- [ ] Duplicate email registration - verify rejected
- [ ] File upload wrong format - verify rejected
- [ ] File upload too large - verify rejected

---

# Development Guidelines

## Code Style
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to functions
- Keep functions focused and under 50 lines
- Use type hints where applicable

## File Uploads
- Max file size: 16MB (configured in `config.py`)
- Allowed formats: PNG, JPG, JPEG, GIF, WebP
- Filenames randomized using UUID for security
- Files stored in `static/uploads/products/` or `static/uploads/profiles/`

## Database Queries
- Always use parameterized queries (prevents SQL injection)
- Always close cursors after use
- Use transactions for multi-step operations
- Add indexes on frequently queried columns
- Limit result sets with LIMIT clause

## Password Security
- Passwords hashed using Werkzeug's `generate_password_hash()`
- Verified using `check_password_hash()`
- Never store plain-text passwords
- Never display passwords in templates or logs

## Session Management
- Session data: `user_id`, `user_name`, `email`, `role`
- Stored server-side in MySQL
- Configure timeout in Flask config for production

## Error Handling
- Use Flask's `flash()` for user-facing messages
- Return `404.html` for not found resources
- Validate all user input before database operations
- Log errors to application logger
- Show generic error messages to users (security)

## Adding New Features
1. Create route file in `routes/` directory
2. Create blueprint and register in `app.py`
3. Create corresponding templates in `templates/`
4. Add database tables/columns to `schema.sql`
5. Add navigation links in `base.html` if needed
6. Test thoroughly with all user roles

---

# Troubleshooting

## ModuleNotFoundError: No module named 'flask'

**Cause**: Virtual environment not activated or dependencies not installed

**Solution**:
```bash
# Verify venv is activated (should see "venv" in terminal)
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall requirements
pip install -r requirements.txt
```

## Access denied for user 'root'@'localhost'

**Cause**: Wrong MySQL password or credentials

**Solution**:
```bash
# Verify MySQL is running
mysql -u root -p

# Update .env with correct password
# Test connection again using Python
```

## Can't connect to MySQL server on 'localhost'

**Cause**: MySQL service not running

**Solution**:
```bash
# macOS
brew services start mysql

# Linux
sudo service mysql start

# Windows
net start MySQL80  # (or MySQL57 depending on version)
```

## Database 'farmers_market' doesn't exist

**Solution**:
```bash
mysql -u root -p
# mysql> CREATE DATABASE farmers_market;
# mysql> USE farmers_market;
# mysql> source schema.sql;
# mysql> exit;
```

## Port 5000 already in use

**Solution**:
```bash
# Option 1: Use different port
python app.py --port 5001

# Option 2: Kill process on port 5000
lsof -ti:5000 | xargs kill -9    # macOS/Linux
netstat -ano | findstr :5000     # Windows
```

## Permission denied on static/uploads folder

**Solution**:
```bash
chmod -R 755 static/uploads
# Windows: Right-click → Properties → Security → Edit
```

## Images not uploading

**Possible Causes**:
- Wrong file format (only PNG, JPG, JPEG, GIF, WebP allowed)
- File size exceeds 16MB limit
- Permissions issue on uploads directory
- Directory doesn't exist

**Solution**:
```bash
# Check directory exists
ls -la static/uploads/products/

# Create if missing
mkdir -p static/uploads/products/
mkdir -p static/uploads/profiles/

# Fix permissions
chmod -R 755 static/uploads/
```

## "Email already registered" but it's new

**Cause**: Case-sensitivity issue with email comparison

**Solution**: Emails are converted to lowercase in registration, but check login too:
```python
email = request.form.get('email', '').strip().lower()
```

## Orders not showing for farmer

**Possible Causes**:
- Farmer not approved yet
- No orders with items from this farmer
- Orders still in 'pending' status
- Query filtering wrong status

**Debugging**:
```python
# Check farmer approval status
SELECT * FROM farmers WHERE user_id = %s;

# Check orders for farmer
SELECT * FROM order_items WHERE farmer_id = %s;

# Check order status
SELECT * FROM orders WHERE status = 'pending';
```

## Reviews not appearing

**Possible Causes**:
- Review not submitted successfully
- Order not in 'picked-up' status
- Wrong farmer_id in review
- Review is soft-deleted

**Debugging**:
```python
# Check reviews exist
SELECT * FROM reviews WHERE farmer_id = %s;

# Check order status
SELECT status FROM orders WHERE id = %s;
```

---

## Support & Resources

- **Flask Documentation**: https://flask.palletsprojects.com
- **MySQL Documentation**: https://dev.mysql.com/doc
- **Python Documentation**: https://docs.python.org
- **Jinja2 Templates**: https://jinja.palletsprojects.com
- **Werkzeug Security**: https://werkzeug.palletsprojects.com/security/

---

## Next Steps for Team

1. Read this entire documentation (30 minutes)
2. Follow the Quick Start Setup (10 minutes)
3. Create test accounts (buyer, farmer, admin)
4. Test the complete user flows
5. Review the code architecture section
6. Examine existing route files for patterns
7. Review templates for HTML structure
8. Start building new features using examples as reference

---

**Created**: May 2026
**Version**: 1.0.0
**For**: SWE Project Team
