"""
Main Flask application for Grocery Price Comparison API.
"""
from flask import Flask
from flask_cors import CORS
from models import db
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routes
from routes.auth_routes import auth_bp
from routes.product_routes import product_bp
from routes.predict_routes import predict_bp


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # CORS configuration
    cors_origins = os.getenv('CORS_ORIGINS', '*')
    if cors_origins != '*':
        cors_origins = [origin.strip() for origin in cors_origins.split(',')]
    
    CORS(
        app,
        resources={r"/*": {"origins": cors_origins}},
        supports_credentials=True
    )
    
    # Database configuration
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        basedir = os.path.abspath(os.path.dirname(__file__))
        database_url = f'sqlite:///{os.path.join(basedir, "grocery_price.db")}'
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(predict_bp)
    
    # Create database tables and handle schema updates
    with app.app_context():
        try:
            db.create_all()
            # Handle schema migration for normalized_name if needed
            from sqlalchemy import inspect, text
            from sqlalchemy.exc import OperationalError
            
            try:
                inspector = inspect(db.engine)
                columns = [col['name'] for col in inspector.get_columns('products')]
                
                if 'normalized_name' not in columns:
                    # Add normalized_name column if missing
                    try:
                        with db.engine.connect() as conn:
                            conn.execute(text('ALTER TABLE products ADD COLUMN normalized_name VARCHAR(200)'))
                            conn.commit()
                        # Populate normalized_name for existing products
                        from utils import normalize_product_name
                        from models import Product
                        products = Product.query.all()
                        for product in products:
                            if not product.normalized_name:
                                product.normalized_name = normalize_product_name(product.name)
                        db.session.commit()
                    except Exception as e:
                        print(f"Schema migration note: {str(e)}")
                
                # Handle Price table schema update (product_url, scraped_at)
                price_columns = [col['name'] for col in inspector.get_columns('prices')]
                
                if 'product_url' not in price_columns and 'link' in price_columns:
                    try:
                        with db.engine.connect() as conn:
                            conn.execute(text('ALTER TABLE prices ADD COLUMN product_url VARCHAR(500)'))
                            conn.execute(text('UPDATE prices SET product_url = link WHERE product_url IS NULL'))
                            conn.commit()
                    except Exception as e:
                        print(f"Price schema migration note: {str(e)}")
                
                if 'scraped_at' not in price_columns and 'recorded_at' in price_columns:
                    try:
                        with db.engine.connect() as conn:
                            conn.execute(text('ALTER TABLE prices ADD COLUMN scraped_at DATETIME'))
                            conn.execute(text('UPDATE prices SET scraped_at = recorded_at WHERE scraped_at IS NULL'))
                            conn.commit()
                    except Exception as e:
                        print(f"Price schema migration note: {str(e)}")
            except OperationalError:
                # Table doesn't exist yet, will be created by create_all
                pass
                    
        except Exception as e:
            print(f"Database initialization note: {str(e)}")
    
    # Health check endpoint (no auth required)
    @app.route('/health', methods=['GET'])
    def health():
        """Health check endpoint."""
        return {'status': 'healthy', 'message': 'Grocery Price API is running'}, 200
    
    return app


if __name__ == '__main__':
    app = create_app()
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    app.run(debug=debug, host=host, port=port)

