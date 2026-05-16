# Local Farmers Market Aggregator

A web-based marketplace platform connecting local farmers with buyers for fresh produce and farm products.

## Quick Start

1. **Read the documentation first**: Open `COMPLETE_DOCUMENTATION.md` for comprehensive setup and project information
2. **Setup (5 minutes)**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   mysql -u root -p < schema.sql
   cp .env.example .env
   # Edit .env with your MySQL credentials
   python app.py
   ```
3. **Visit**: `http://localhost:5000`

## Key Files

- **`COMPLETE_DOCUMENTATION.md`** - Full project documentation (start here!)
- **`database_models.md`** - Database schema with UML diagrams
- **`schema.sql`** - Database initialization script
- **`app.py`** - Flask application entry point
- **`config.py`** - Configuration management
- **`helpers.py`** - Utility functions and decorators
- **`routes/`** - Feature blueprints (auth, farmer, buyer, admin)
- **`templates/`** - HTML templates
- **`static/`** - CSS, JavaScript, and uploads

## Default Login Credentials

**Admin Account**:
- Email: `admin@farmmarket.com`
- Password: `admin123`

⚠️ Change these in production!

## Documentation Structure

The `COMPLETE_DOCUMENTATION.md` contains:
1. Project overview
2. Technology stack
3. Project structure
4. Complete database schema
5. User roles and permissions
6. Quick start setup (5 minutes)
7. Detailed setup instructions
8. All routes and API endpoints
9. Code architecture and design patterns
10. Code examples and common patterns
11. Testing guidelines
12. Development guidelines
13. Troubleshooting guide

## Technology Stack

- **Backend**: Flask 3.1.1 (Python)
- **Database**: MySQL 5.7+
- **Frontend**: HTML/CSS/JavaScript with Jinja2 templates
- **Port**: 5000 (development)

## Features

- Multi-role user system (buyer, farmer, admin)
- Product marketplace with advanced filtering
- Shopping cart and order management
- Farmer approval workflow
- Review and rating system
- Notifications system
- Admin dashboard with analytics

## Getting Help

1. Check `COMPLETE_DOCUMENTATION.md` for answers
2. Look at existing code in `routes/` for patterns
3. Review database queries in route files
4. Check the Troubleshooting section

## Team Onboarding Steps

1. Read `COMPLETE_DOCUMENTATION.md` (30 min)
2. Follow Quick Start Setup (10 min)
3. Create test accounts (buyer, farmer, admin)
4. Test complete user flows (20 min)
5. Review code architecture section (15 min)
6. Examine existing routes for patterns (20 min)
7. Review templates for structure (15 min)
8. Ready to start developing!

## Important Files to Know

| File | Purpose |
|------|---------|
| `app.py` | Flask app factory and initialization |
| `config.py` | Environment variables and configuration |
| `helpers.py` | Authentication decorators, file uploads |
| `routes/auth.py` | Login, register, password reset |
| `routes/buyer.py` | Shopping cart, orders, reviews |
| `routes/farmer.py` | Products, market schedules, orders |
| `routes/admin.py` | Dashboard, farmer approval, products |
| `schema.sql` | Complete database schema |
| `requirements.txt` | Python dependencies |
| `.env.example` | Environment variable template |

## Database Quick Reference

**Key Tables**:
- `users` - All user accounts
- `farmers` - Farmer extended profiles
- `products` - Farm products
- `orders` - Customer orders
- `cart_items` - Shopping cart
- `reviews` - Customer reviews
- `subscriptions` - Farmer followers
- `notifications` - User notifications

See `database_models.md` for UML diagrams and complete schema.

## Development Tips

- Always use parameterized queries to prevent SQL injection
- Use `@login_required` and `@role_required()` decorators for protection
- Validate all user input before database operations
- Use try/except/finally blocks for database connections
- Close cursors after every query
- Check the CODE_EXAMPLES section in documentation for patterns

## Project Status

✓ Complete backend implementation  
✓ Database schema finalized  
✓ Authentication system  
✓ Multi-role user system  
✓ Product marketplace  
✓ Order management  
✓ Review system  
✓ Admin dashboard  

## Next Steps

1. Review `COMPLETE_DOCUMENTATION.md` thoroughly
2. Set up your local development environment
3. Test all user flows
4. Familiarize yourself with the codebase
5. Start developing new features or improvements

---

**Questions?** Check `COMPLETE_DOCUMENTATION.md` - it has comprehensive answers!

Good luck! 🚀
