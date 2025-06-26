// API Configuration
const API_CONFIG = {
    // Use relative path for API calls (will be relative to the current domain)
    BASE_URL: '',
    
    // API endpoints
    ENDPOINTS: {
        CHAT: '/api/chat',
        HEALTH: '/api/health'
    },
    
    // Get full API URL for an endpoint
    getUrl: function(endpoint) {
        // Use relative URL for production, or full URL for development
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            return `http://localhost:8000${this.ENDPOINTS[endpoint] || endpoint}`;
        }
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
