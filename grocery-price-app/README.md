# 🛒 AI-Powered Grocery Price Comparison App

A full-stack web application that compares grocery prices across multiple stores and uses AI to predict price trends.

## 📋 Features

- **Price Comparison**: Compare prices from multiple Indian stores (BigBasket, Zepto, Swiggy Instamart, JioMart, Amazon Fresh)
- **AI Price Prediction**: Get ML-powered predictions for future price trends
- **Product Search**: Search for any grocery item and get instant price comparisons
- **User Authentication**: Sign up and login functionality
- **Search History**: Track your search history (when logged in)

## 🏗️ Project Structure

```
grocery-price-app/
├── backend/
│   ├── scrapers/
│   │   ├── __init__.py
│   │   └── price_scraper.py      # Web scraping module
│   ├── ml/
│   │   ├── __init__.py
│   │   └── price_predictor.py    # ML price prediction module
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth_routes.py        # Authentication endpoints
│   │   ├── product_routes.py     # Product search endpoints
│   │   └── predict_routes.py     # Price prediction endpoints
│   ├── models.py                 # Database models
│   ├── app.py                    # Flask application
│   └── requirements.txt          # Python dependencies
│
└── frontend/
    ├── public/
    │   └── index.html
    ├── src/
    │   ├── components/
    │   │   ├── SearchBar.js
    │   │   ├── PriceComparisonList.js
    │   │   └── PricePredictionBadge.js
    │   ├── pages/
    │   │   ├── Home.js
    │   │   └── ProductDetails.js
    │   ├── services/
    │   │   └── api.js            # API service layer
    │   ├── App.js
    │   ├── index.js
    │   └── index.css
    └── package.json
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- npm or yarn

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd grocery-price-app/backend
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Flask application:**
   ```bash
   python app.py
   ```

   The backend API will be running at `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd grocery-price-app/frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```

   The frontend will be running at `http://localhost:3000`

## 📡 API Endpoints

### Authentication

- `POST /auth/signup` - User registration
  ```json
  {
    "username": "user123",
    "email": "user@example.com",
    "password": "password123"
  }
  ```

- `POST /auth/login` - User login
  ```json
  {
    "username": "user123",
    "password": "password123"
  }
  ```

### Products

- `POST /search` - Search for products and get prices
  ```json
  {
    "product_name": "milk",
    "user_id": 1  // optional
  }
  ```

- `GET /product/<id>` - Get product details by ID

### Predictions

- `POST /predict` - Get price prediction
  ```json
  {
    "product_id": 1,  // optional
    "product_name": "milk",  // optional
    "current_price": 4.99  // optional
  }
  ```

### Health Check

- `GET /health` - API health check

## 🗄️ Database

The application uses SQLite with SQLAlchemy ORM. The database file (`grocery_price.db`) will be automatically created when you first run the backend.

### Models

- **User**: User accounts for authentication
- **Product**: Product information
- **Price**: Price data from different stores
- **SearchHistory**: User search history

## 🤖 Machine Learning

The ML module uses scikit-learn's Linear Regression to predict price trends based on historical data. Currently uses dummy data, but can be extended to use real historical price data from the database.

## 🧪 Testing the Application

1. **Start the backend** (in one terminal):
   ```bash
   cd grocery-price-app/backend
   python app.py
   ```

2. **Start the frontend** (in another terminal):
   ```bash
   cd grocery-price-app/frontend
   npm start
   ```

3. **Open your browser** and navigate to `http://localhost:3000`

4. **Try searching** for products like:
   - "milk"
   - "bread"
   - "eggs"
   - "chicken"

5. **Click "Get Price Prediction"** to see AI-powered price forecasts

## 🔧 Configuration

### Backend

- Default port: `5000`
- Database: SQLite (`grocery_price.db`)
- CORS: Enabled for all origins (configure in `app.py` for production)

### Frontend

- Default port: `3000`
- API URL: Configured in `src/services/api.js`
- Proxy: Set in `package.json` to `http://localhost:5000`

## 📝 Notes

- **Web Scraping**: Currently returns dummy data. To implement real scraping, modify `backend/scrapers/price_scraper.py`
- **ML Predictions**: Uses dummy historical data. Connect to database for real predictions
- **Authentication**: Basic implementation. For production, implement JWT tokens
- **CORS**: Currently allows all origins. Restrict in production

## 🛠️ Tech Stack

### Backend
- **Flask**: Web framework
- **SQLAlchemy**: ORM for database operations
- **BeautifulSoup**: Web scraping
- **scikit-learn**: Machine learning
- **pandas**: Data manipulation

### Frontend
- **React**: UI framework
- **React Router**: Routing
- **Axios**: HTTP client
- **CSS3**: Styling

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues and questions, please open an issue on the repository.

---

**Happy Shopping! 🛒💰**

