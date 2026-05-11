"""Seed the database with an admin user and sample data."""
import sys
sys.path.insert(0, '.')
from werkzeug.security import generate_password_hash

admin_hash = generate_password_hash('admin123')
print(f"UPDATE users SET password_hash = '{admin_hash}' WHERE email = 'admin@farmmarket.com';")
