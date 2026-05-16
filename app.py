import os
from flask import Flask
from flask_mysqldb import MySQL
from config import Config

mysql = MySQL()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure upload directories exist
    uploads = app.config['UPLOAD_FOLDER']
    for sub in ['products', 'profiles']:
        os.makedirs(os.path.join(uploads, sub), exist_ok=True)

    # Init MySQL
    mysql.init_app(app)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.farmer import farmer_bp
    from routes.buyer import buyer_bp
    from routes.admin import admin_bp
    from routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(farmer_bp, url_prefix='/farmer')
    app.register_blueprint(buyer_bp, url_prefix='/buyer')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')

    # Add context processor for photo_url helper
    @app.context_processor
    def inject_photo_url():
        def photo_url(path):
            if not path:
                return '/static/images/placeholder.jpg'
            if path.startswith('http'):
                return path
            if not path.startswith('/'):
                path = '/' + path
            return f'/static/{path}'
        return dict(photo_url=photo_url)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
