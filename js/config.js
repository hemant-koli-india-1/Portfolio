// API Configuration
const API_CONFIG = {
    // Use the API URL from environment variable or fallback to localhost
    BASE_URL: process.env.API_BASE_URL || 'http://localhost:8000',
    
    // API endpoints
    ENDPOINTS: {
        CHAT: '/api/chat'
    },
    
    // Get full API URL for an endpoint
    getUrl: function(endpoint) {
        return `${this.BASE_URL}${this.ENDPOINTS[endpoint] || endpoint}`;
    }
};

// For development - you can override this in production
// by setting window.API_OVERRIDES before this script loads
if (typeof window.API_OVERRIDES === 'object') {
    Object.assign(API_CONFIG, window.API_OVERRIDES);
}

// Export for ES modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = API_CONFIG;
}
