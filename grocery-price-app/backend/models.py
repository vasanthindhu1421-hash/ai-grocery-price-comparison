"""
Database models for the Grocery Price Comparison app.
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt

db = SQLAlchemy()


class Category(db.Model):
    """Category model for organizing products."""
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    image_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    products = db.relationship('Product', backref='category_obj', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'image_url': self.image_url,
        }


class User(db.Model):
    """User model for authentication."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    search_history = db.relationship('SearchHistory', backref='user', lazy=True)
    
    def set_password(self, password):
        """Hash and set password using bcrypt."""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password):
        """Check if provided password matches hash."""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self):
        """Convert user to dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }


class Product(db.Model):
    """Product model to store product information."""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    normalized_name = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text)
    # Legacy string category (kept for backward compatibility)
    category = db.Column(db.String(100), index=True)
    # New normalized category system
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), index=True)
    image_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Remove unique constraint on name to allow same product from different searches
    
    # Relationships
    prices = db.relationship('Price', backref='product', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert product to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': (self.category_obj.name if self.category_obj else self.category),
            'category_id': self.category_id,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'prices': [price.to_dict() for price in self.prices]
        }


class Price(db.Model):
    """Price model to store price information from different stores."""
    __tablename__ = 'prices'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    store_name = db.Column(db.String(100), nullable=False, index=True)
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='INR')
    product_url = db.Column(db.String(500))
    in_stock = db.Column(db.Boolean, default=True)
    scraped_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Unique constraint to prevent duplicate prices for same product+store per day
    __table_args__ = (
        db.Index('idx_product_store_time', 'product_id', 'store_name', 'scraped_at'),
        db.Index('idx_product_store', 'product_id', 'store_name'),
    )
    
    def to_dict(self):
        """Convert price to dictionary."""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'store_name': self.store_name,
            'price': self.price,
            'currency': self.currency,
            'link': self.product_url,  # Backward compatibility
            'product_url': self.product_url,
            'in_stock': self.in_stock,
            'recorded_at': self.scraped_at.isoformat(),  # Backward compatibility
            'scraped_at': self.scraped_at.isoformat()
        }


class SearchHistory(db.Model):
    """Search history model to track user searches."""
    __tablename__ = 'search_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    query = db.Column(db.String(200), nullable=False, index=True)
    results_count = db.Column(db.Integer, default=0)
    searched_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        """Convert search history to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'query': self.query,
            'results_count': self.results_count,
            'searched_at': self.searched_at.isoformat()
        }

