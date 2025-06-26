from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, BaseSettings
from typing import List, Dict, Optional, Any
import json
import os
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8000
    environment: str = "development"
    log_level: str = "info"
    
    # CORS
    cors_origins: str = "*"
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True
        
        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str):
            if field_name == 'cors_origins':
                return [origin.strip() for origin in raw_val.split(",")] if "," in raw_val else [raw_val]
            return cls.json_loads(raw_val)

# Load settings
settings = Settings()

# Update log level
logging.basicConfig(level=settings.log_level.upper())
logger.info(f"Starting server in {settings.environment} mode")

# Initialize FastAPI app
app = FastAPI(
    title="Portfolio Chatbot API",
    description="API for the portfolio website chatbot",
    version="1.0.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT", "development") == "development" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT", "development") == "development" else None,
    openapi_url="/openapi.json" if os.getenv("ENVIRONMENT", "development") == "development" else None
)

# Get CORS origins from environment
cors_origins = os.getenv("CORS_ORIGINS", "*")
origins = [origin.strip() for origin in cors_origins.split(",")] if "," in cors_origins else [cors_origins]

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class Message(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    sources: List[Dict] = []

# Knowledge Base (Replace with your actual data)
KNOWLEDGE_BASE = {
    "experience": [
        "Gen AI Intern at TATA MOTORS (June 2025 - Present)",
        "Cloud API Migration Intern at TCS (Feb 2025 - Apr 2025)",
        "Business Analyst & Solution Architect Intern at AIQoD (Aug 2024 - Jan 2025)",
        "Data Analyst Sub Team Lead at Ozibook Tech Solution (Mar 2024 - Jul 2024)"
    ],
    "education": [
        "B.Tech in Computer Science and Engineering (AI/ML) from Vellore Institute of Technology - AP (2021-2025) - CGPA: 8.54"
    ],
    "skills": [
        "Programming: Python, Java, JavaScript, SQL",
        "AI/ML: Machine Learning, Deep Learning, NLP, Computer Vision",
        "Cloud: AWS, Docker, CI/CD",
        "Tools: Git, Jupyter, VS Code, Tableau"
    ],
    "projects": [
        "Machinery Maintenance System for Manufacturing Industry",
        "DataVise – Intelligent Data Analyst Assistant",
        "Cold Email Generator using Llama 3",
        "Intelligent Invoice Processing Automation"
    ],
    "contact": [
        "Email: hemant.koli.india@gmail.com",
        "Phone: +91 93599 36530",
        "Location: Pune, Maharashtra, India"
    ]
}

# Chatbot response logic
def generate_response(user_message: str) -> str:
    """Generate a response based on the user's message."""
    message = user_message.lower()
    
    if any(greeting in message for greeting in ["hi", "hello", "hey"]):
        return (
            "Hello! I'm here to help you learn more about Hemant's professional background. "
            "You can ask about his experience, skills, projects, or education. "
            "What would you like to know?"
        )
    
    elif any(word in message for word in ["experience", "work", "job", "internship"]):
        exp_list = "\n• " + "\n• ".join(KNOWLEDGE_BASE["experience"])
        return f"Hemant has the following professional experience:{exp_list}"
    
    elif any(word in message for word in ["skill", "technology", "tech stack"]):
        skills = "\n• " + "\n• ".join(KNOWLEDGE_BASE["skills"])
        return f"Hemant has expertise in the following areas:{skills}"
    
    elif any(word in message for word in ["project", "portfolio"]):
        projects = "\n• " + "\n• ".join(KNOWLEDGE_BASE["projects"])
        return f"Hemant has worked on these projects:{projects}"
    
    elif any(word in message for word in ["education", "degree", "college"]):
        return "\n".join(KNOWLEDGE_BASE["education"])
    
    elif any(word in message for word in ["contact", "email", "phone", "reach"]):
        return "\n".join(KNOWLEDGE_BASE["contact"])
    
    elif "thank" in message:
        return "You're welcome! Let me know if you have any other questions."
    
    else:
        return (
            "I'm not sure I understand. You can ask me about:\n"
            "• Hemant's experience\n"
            "• His skills and technologies\n"
            "• Projects he's worked on\n"
            "• His education\n"
            "• How to contact him"
        )

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Portfolio Chatbot API is running"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(chat_request: ChatRequest):
    """Handle chat messages and return responses."""
    if not chat_request.messages:
        raise HTTPException(status_code=400, detail="No messages provided")
    
    # Get the last user message
    last_message = next((msg for msg in reversed(chat_request.messages) if msg.role == "user"), None)
    if not last_message:
        raise HTTPException(status_code=400, detail="No user message found")
    
    # Generate response
    response_text = generate_response(last_message.content)
    
    return ChatResponse(
        response=response_text,
        sources=[{"type": "knowledge_base", "timestamp": datetime.utcnow().isoformat()}]
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# Health check endpoint with more details
@app.get("/health", include_in_schema=False)
async def health_check() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=port,
        reload=os.getenv("ENVIRONMENT", "development") == "development",
        log_level=os.getenv("LOG_LEVEL", "info").lower(),
        timeout_keep_alive=30
    )
