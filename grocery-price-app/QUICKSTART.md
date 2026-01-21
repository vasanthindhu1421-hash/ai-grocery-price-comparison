# Quick Start Guide

## 🚀 Quick Setup (5 minutes)

### Step 1: Backend Setup

```bash
cd grocery-price-app/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```

Backend will run on `http://localhost:5000`

### Step 2: Frontend Setup

Open a **new terminal**:

```bash
cd grocery-price-app/frontend

# Install dependencies
npm install

# Start the development server
npm start
```

Frontend will run on `http://localhost:3000`

### Step 3: Test the App

1. Open `http://localhost:3000` in your browser
2. Search for products like "milk", "bread", or "eggs"
3. Click "Get Price Prediction" to see AI predictions

## ✅ Verify Installation

### Backend Health Check
```bash
curl http://localhost:5000/health
```

Should return: `{"status": "healthy", "message": "Grocery Price API is running"}`

### Test Search API
```bash
curl -X POST http://localhost:5000/search \
  -H "Content-Type: application/json" \
  -d '{"product_name": "milk"}'
```

## 🐛 Troubleshooting

### Backend Issues
- **Port 5000 already in use**: Change port in `app.py` line 50
- **Module not found**: Make sure virtual environment is activated
- **Database errors**: Delete `grocery_price.db` and restart

### Frontend Issues
- **Port 3000 already in use**: React will prompt to use another port
- **npm install fails**: Try `npm install --legacy-peer-deps`
- **API connection errors**: Ensure backend is running on port 5000

## 📚 Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the API endpoints
- Customize the scraper with real store URLs
- Connect ML predictions to real historical data

