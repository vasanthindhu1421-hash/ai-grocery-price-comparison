import React, { useState } from 'react';
import SearchBar from '../components/SearchBar';
import PriceComparisonList from '../components/PriceComparisonList';
import PricePredictionBadge from '../components/PricePredictionBadge';
import { searchProduct, getPricePrediction } from '../services/api';
import './Home.css';

/**
 * Home page component with search functionality.
 */
const Home = () => {
  const [searchResults, setSearchResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [prediction, setPrediction] = useState(null);
  const [error, setError] = useState(null);

  const handleSearch = async (productName) => {
    setLoading(true);
    setError(null);
    setSearchResults(null);
    setPrediction(null);

    try {
      const results = await searchProduct(productName);
      setSearchResults(results);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handlePredictionClick = async () => {
    if (!searchResults || !searchResults.product) return;

    setLoading(true);
    try {
      const predData = await getPricePrediction({
        product_id: searchResults.product.id,
        product_name: searchResults.product.name,
      });
      setPrediction(predData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="home-page">
      <SearchBar onSearch={handleSearch} loading={loading} />

      {error && (
        <div className="error-message">
          <p>❌ {error}</p>
        </div>
      )}

      {searchResults && (
        <>
          {searchResults.warning && (
            <div className="warning-message">
              <p>⚠️ {searchResults.warning}</p>
            </div>
          )}
          <PriceComparisonList
            prices={searchResults.prices}
            productName={searchResults.product.name}
            productId={searchResults.product.id}
            onPredictionClick={handlePredictionClick}
          />
        </>
      )}

      {prediction && (
        <PricePredictionBadge
          prediction={prediction}
          onClose={() => setPrediction(null)}
        />
      )}

      {!searchResults && !loading && (
        <div className="welcome-message">
          <h2>Welcome to Grocery Price Comparison</h2>
          <p>Search for any grocery item to compare prices across Indian stores</p>
          <div className="features">
            <div className="feature-card">
              <span className="feature-icon">🔍</span>
              <h3>Price Comparison</h3>
              <p>Compare prices from BigBasket, Zepto, Swiggy Instamart, JioMart & Amazon Fresh</p>
            </div>
            <div className="feature-card">
              <span className="feature-icon">🤖</span>
              <h3>AI Predictions</h3>
              <p>Get AI-powered price trend predictions based on real historical data</p>
            </div>
            <div className="feature-card">
              <span className="feature-icon">💰</span>
              <h3>Best Deals</h3>
              <p>Find the best prices in INR and save money on your groceries</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Home;

