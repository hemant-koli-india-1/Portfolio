# Portfolio Chatbot Backend

This is the backend service for the portfolio website's chatbot. It provides API endpoints to handle chat interactions.

## Features

- RESTful API for chat interactions
- Knowledge base for responding to common questions
- CORS enabled for frontend integration
- Health check endpoint
- Structured response format

## Setup

1. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the server**:
   ```bash
   uvicorn main:app --reload
   ```
   The server will start at `http://localhost:8000`

## API Endpoints

### Chat Endpoint
- **POST** `/api/chat` - Process chat messages
  ```json
  {
    "messages": [
      {"role": "user", "content": "Tell me about your experience"}
    ]
  }
  ```
  
  Example response:
  ```json
  {
    "response": "Hemant has the following professional experience...",
    "sources": [{"type": "knowledge_base", "timestamp": "2023-01-01T12:00:00"}]
  }
  ```

### Health Check
- **GET** `/health` - Check if the API is running
  ```json
  {
    "status": "healthy",
    "timestamp": "2023-01-01T12:00:00"
  }
  ```

## Extending the Knowledge Base

Edit the `KNOWLEDGE_BASE` dictionary in `main.py` to add or modify responses. The structure is:

```python
KNOWLEDGE_BASE = {
    "experience": ["Job 1", "Job 2"],
    "education": ["Degree 1"],
    "skills": ["Skill 1", "Skill 2"],
    "projects": ["Project 1", "Project 2"],
    "contact": ["Email: example@email.com"]
}
```

## Development

- The server uses hot-reload when run with `--reload`
- Add new response patterns in the `generate_response` function
- For production, consider adding authentication and rate limiting

## Deployment

### 1. Local Development

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. Update the `.env` file with your settings
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the development server:
   ```bash
   uvicorn main:app --reload
   ```

### 2. Production Deployment

#### Option 1: Render (Recommended)
1. Push your code to a GitHub repository
2. Sign up at [render.com](https://render.com) with GitHub
3. Click "New" > "Web Service" and connect your repo
4. Configure:
   - **Name**: your-app-name
   - **Region**: Choose the closest to your users
   - **Branch**: main (or your preferred branch)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables from your `.env` file
6. Click "Create Web Service"

#### Option 2: Railway
1. Install Railway CLI: `npm i -g @railway/cli`
2. Run `railway login` and `railway up`
3. Set environment variables: `railway env push .env`

#### Option 3: PythonAnywhere
1. Create an account at [pythonanywhere.com](https://www.pythonanywhere.com)
2. Upload your code
3. Configure a web app with FastAPI
4. Set up environment variables in the web app configuration

### Environment Variables

Update these in your hosting provider's dashboard:

```env
# Server Configuration
HOST=0.0.0.0
PORT=8000

# CORS (comma-separated origins, or * for all)
CORS_ORIGINS=https://your-portfolio.com,https://www.your-portfolio.com

# Environment (development, production)
ENVIRONMENT=production

# Logging Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO
```

### Production Command

If you need to run it manually in production:

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT --timeout 120
```

### Updating Frontend API URL

After deploying your backend, update the frontend configuration in `index.html`:

```html
<script>
    window.API_OVERRIDES = {
        BASE_URL: 'https://your-deployed-api.railway.app'  // Your deployed URL
    };
</script>
```
