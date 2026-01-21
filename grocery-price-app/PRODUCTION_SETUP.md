# Production Setup Guide

## Overview
This is a production-ready grocery price comparison application for Indian markets, supporting BigBasket, Zepto, Swiggy Instamart, JioMart, and Amazon Fresh.

## Features
- ✅ JWT Authentication (Login/Signup required)
- ✅ Real Indian grocery store price scraping
- ✅ AI-powered price predictions based on historical data
- ✅ INR currency support
- ✅ Protected routes (backend + frontend)
- ✅ Search history tracking
- ✅ Duplicate price prevention
- ✅ Proper database indexing

## Backend Setup

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Configuration
Create a `.env` file in the `backend` directory:
```env
JWT_SECRET=your-strong-secret-key-here-change-in-production
DATABASE_URL=sqlite:///grocery_price.db
FLASK_ENV=production
FLASK_DEBUG=False
API_HOST=0.0.0.0
API_PORT=5000
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

**IMPORTANT**: Change `JWT_SECRET` to a strong random string in production!

### 3. Initialize Database
The database will be created automatically on first run. To reset:
```bash
# Delete existing database
rm grocery_price.db

# Run app to recreate
python app.py
```

### 4. Run Backend
```bash
python app.py
```

Or with gunicorn for production:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:create_app()
```

## Frontend Setup

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Environment Configuration
Create a `.env` file in the `frontend` directory:
```env
REACT_APP_API_URL=http://localhost:5000
```

### 3. Run Frontend
```bash
npm start
```

For production build:
```bash
npm run build
```

## Store Scrapers

The application includes scrapers for:
- **BigBasket** (`scrapers/bigbasket_scraper.py`)
- **Zepto** (`scrapers/zepto_scraper.py`)
- **Swiggy Instamart** (`scrapers/instamart_scraper.py`)
- **JioMart** (`scrapers/jiomart_scraper.py`)
- **Amazon Fresh** (`scrapers/amazonfresh_scraper.py`)

### Scraper Behavior
- Scrapers use proper headers and respect rate limits
- Parallel execution for faster results
- Graceful error handling (continues if one store fails)
- Returns real product URLs that open actual store pages

### Note on Scraping
If live scraping is blocked by stores:
1. The system will gracefully handle failures
2. Consider implementing cached prices
3. Use periodic background updates
4. Implement manual refresh endpoints

## API Endpoints

### Authentication (No auth required)
- `POST /auth/signup` - User registration
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `GET /auth/verify` - Verify token

### Products (Auth required)
- `POST /search` - Search for products
- `GET /product/<id>` - Get product details
- `GET /search-history` - Get user's search history

### Predictions (Auth required)
- `POST /predict` - Get price prediction

### Health Check (No auth required)
- `GET /health` - API health check

## Database Schema

### Users
- id, username, email, password_hash, created_at

### Products
- id, name, normalized_name, description, category, image_url, created_at, updated_at

### Prices
- id, product_id, store_name, price, currency (INR), link, in_stock, recorded_at
- Indexed on: product_id, store_name, recorded_at
- Unique constraint prevents duplicate prices

### Search History
- id, user_id, query, results_count, searched_at
- Indexed on: user_id, query, searched_at

## Security Features

1. **JWT Authentication**: All protected routes require valid JWT
2. **Password Hashing**: Uses Werkzeug's secure password hashing
3. **Input Validation**: All inputs are validated
4. **SQL Injection Protection**: Uses SQLAlchemy ORM
5. **CORS Configuration**: Configurable CORS origins
6. **Environment Variables**: No hardcoded secrets

## Price Prediction

The AI prediction system:
- Uses real historical price data from database
- Requires minimum 3 price records
- Uses linear regression for trend analysis
- Provides confidence scores
- Explains price changes based on variance
- Shows recommendations

## Troubleshooting

### Scrapers not working
- Check internet connection
- Verify store websites are accessible
- Some stores may block automated requests
- Implement fallback to cached data

### Authentication issues
- Verify JWT_SECRET is set
- Check token expiration (24 hours default)
- Clear localStorage and login again

### Database issues
- Ensure write permissions on database file
- Check SQLite version compatibility
- Reset database if needed

## Production Deployment

1. Set `FLASK_ENV=production` and `FLASK_DEBUG=False`
2. Use strong `JWT_SECRET`
3. Configure proper CORS origins
4. Use production WSGI server (gunicorn, uwsgi)
5. Set up HTTPS
6. Configure proper database (PostgreSQL recommended for production)
7. Set up monitoring and logging
8. Implement rate limiting
9. Use environment-specific configurations

## License
See LICENSE file

