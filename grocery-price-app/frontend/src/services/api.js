/**
 * API service for communicating with the backend Flask API.
 */
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000';


const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Include cookies
});

// Add token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

/**
 * Search for products and get prices from multiple stores.
 * @param {string} productName - Name of the product to search
 * @returns {Promise} API response with product and prices
 */
export const searchProduct = async (productName) => {
  try {
    const response = await api.post('/search', {
      product_name: productName,
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error || 'Failed to search product');
  }
};

/**
 * Get product details by ID.
 * @param {number} productId - ID of the product
 * @returns {Promise} API response with product details
 */
export const getProduct = async (productId) => {
  try {
    const response = await api.get(`/product/${productId}`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error || 'Failed to get product');
  }
};

/**
 * Get price prediction for a product.
 * @param {Object} params - Prediction parameters
 * @param {number} params.productId - Optional product ID
 * @param {string} params.productName - Optional product name
 * @param {number} params.currentPrice - Optional current price
 * @returns {Promise} API response with price prediction
 */
export const getPricePrediction = async (params) => {
  try {
    const response = await api.post('/predict', params);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error || 'Failed to get prediction');
  }
};

/**
 * User signup.
 * @param {Object} userData - User registration data
 * @param {string} userData.username - Username
 * @param {string} userData.email - Email address
 * @param {string} userData.password - Password
 * @returns {Promise} API response with user data
 */
export const signup = async (userData) => {
  try {
    const response = await api.post('/auth/signup', userData);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error || 'Failed to sign up');
  }
};

/**
 * User login.
 * @param {Object} credentials - Login credentials
 * @param {string} credentials.email - Email
 * @param {string} credentials.password - Password
 * @returns {Promise} API response with user data and token
 */
export const login = async (credentials) => {
  try {
    const response = await api.post('/auth/login', credentials);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error || 'Failed to login');
  }
};

/**
 * Verify authentication token.
 * @returns {Promise} API response with validation status
 */
export const verifyAuth = async () => {
  try {
    const response = await api.get('/auth/verify');
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error || 'Authentication failed');
  }
};

/**
 * Logout user.
 * @returns {Promise} API response
 */
export const logout = async () => {
  try {
    const response = await api.post('/auth/logout');
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error || 'Logout failed');
  }
};

/**
 * Get product suggestions for autocomplete.
 * @param {string} query - Partial product name (min 2 characters)
 * @returns {Promise} API response with suggestions
 */
export const getProductSuggestions = async (query) => {
  try {
    const response = await api.get('/products/suggest', {
      params: { q: query },
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error || 'Failed to get suggestions');
  }
};

export default api;

