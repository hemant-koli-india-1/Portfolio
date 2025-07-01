from fastapi import FastAPI, HTTPException, Request, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, BaseSettings
from typing import List, Dict, Optional, Any
import json
import os
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import the Chain class
from chains import Chain

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
    title="Portfolio Website",
    description="Portfolio website with chatbot API",
    version="1.0.0",
    docs_url="/docs" if settings.environment == "development" else None,
    redoc_url="/redoc" if settings.environment == "development" else None,
    openapi_url="/openapi.json" if settings.environment == "development" else None
)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), '..', 'static')

# Ensure static directory exists and is readable
if not os.path.exists(static_dir):
    logger.error(f"Static directory does not exist: {static_dir}")
    raise RuntimeError(f"Static directory not found: {static_dir}")

# Serve static files from the static directory
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Also serve files from subdirectories of static
app.mount("/static/js", StaticFiles(directory=os.path.join(static_dir, 'js')), name="static_js")

# Serve index.html at root
@app.get("/")
async def root():
    return FileResponse(os.path.join(static_dir, "index.html"))

# Serve favicon
@app.get("/favicon.ico")
async def favicon():
    return FileResponse(os.path.join(static_dir, "favicon.ico"))

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

def get_chain() -> Chain:
    """
    Get an instance of the Chain class with the Groq API key.
    
    Returns:
        Chain: An instance of the Chain class
        
    Raises:
        HTTPException: If the GROQ_API_KEY environment variable is not set
    """
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        error_msg = "GROQ_API_KEY environment variable not set. Please set it to use the chatbot."
        logger.error(error_msg)
        raise HTTPException(
            status_code=500,
            detail=error_msg
        )
    try:
        return Chain(groq_api_key=groq_api_key)
    except Exception as e:
        error_msg = f"Failed to initialize Chain: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(
            status_code=500,
            detail="Failed to initialize the chatbot. Please try again later."
        )

# Knowledge Base
KNOWLEDGE_BASE = {
    "chatbot_info": "The chatbot on this website is developed by Hemant Koli using his custom LLaMA 4 Scout model.",
    "contact": [
        "Email: hemant.koli.india@gmail.com",
        "Phone: +91 8484833655",
        "Location: Pune, Maharashtra, India"
    ],
    "experience": [
        "Gen AI Intern at TATA MOTORS (June 2025 - Present) | Pune, Maharashtra | Led Gen AI initiatives for manufacturing operations, implementing practical use cases in plant environments such as Issue knowledge bots, automated reporting, and production planning. Assisted in developing low-code/no-code solutions to streamline workflows.",
        "Cloud API Migration Intern at TATA Consultancy Services (Feb 2025 - Apr 2025) | Pune, Maharashtra | Upskilled in AWS and Node.js to support a mini project simulating project infrastructure development. Gained hands-on experience in cloud computing and backend development while working on industry-relevant tasks.",
        "Business Analyst & Solution Architect Intern at AIQoD (Aug 2024 - Jan 2025) | Pune, Maharashtra | Designed and developed advanced machine learning models, specializing in large language models (LLMs) and vision-language models (VLMs). Delivered innovative, data-driven solutions and drove cutting-edge research in AI technologies. Developed strategic pitch materials and conducted in-depth market research to drive client acquisition. Delivered actionable insights and bi-weekly updates to senior stakeholders, enhancing decision-making.",
        "Data Analyst Sub Team Lead at Ozibook Tech Solution (Jun 2024 - Jul 2024) | Remote | Executed comprehensive web scraping and data analysis on 1000+ LinkedIn accounts to extract user engagement metrics. Generated insights that led to a 25% increase in targeted marketing effectiveness for client campaigns. Led and managed 4 teams in the Data Analyst department, coordinating tasks and ensuring efficient workflow."
    ],
    "education": [
        "B.Tech in Computer Science and Engineering | Vellore Institute of Technology - AP | 2021 - 2025 | CGPA: 8.54/10.0",
        "Specialization in Artificial Intelligence and Machine Learning",
        "Senior Secondary (12th) | Creative Public School | 2021 | Percentage: 85.0%",
        "Secondary (10th) | Vidya Niketan | 2019 | Percentage: 81.40%"
    ],
    "certifications": [
        {
            "name": "AWS Solutions Architect Associate",
            "issuer": "Amazon Web Services (AWS)",
            "year": 2024
        },
        {
            "name": "AWS Academy Cloud Practitioner",
            "issuer": "Amazon Web Services (AWS)",
            "year": 2023
        },
        {
            "name": "Python for Data Analysis",
            "issuer": "Great Learning Academy",
            "year": 2023
        },
        {
            "name": "Fundamentals of UI/UX",
            "issuer": "GrowthSchool.io",
            "year": 2023
        },
        {
            "name": "JavaScript Essentials",
            "issuer": "Cisco Networking Academy",
            "year": 2022
        },
        {
            "name": "PwC Switzerland Power BI Virtual Case Experience",
            "issuer": "Forage (formerly InsideSherpa)",
            "year": 2023
        }
    ],
    "skills": {
        "Programming": ["Python", "Java", "JavaScript", "SQL"],
        "AI/ML & Data Science": [
            "Machine Learning", "Deep Learning", "Large Language Models (LLMs)",
            "Computer Vision", "Natural Language Processing (NLP)", "Generative AI",
            "Data Analysis & Visualization"
        ],
        "Cloud & DevOps": [
            "AWS (SageMaker, Lambda, S3, Textract)", "Docker",
            "CI/CD Pipelines", "Serverless Architecture", "Cloud Architecture"
        ],
        "Databases": [
            "MongoDB", "MySQL", "Redis", "Neo4j", "Cassandra", "Hive"
        ],
        "Data Visualization": [
            "Tableau", "Power BI", "Amazon QuickSight",
            "Google Looker Studio", "QlikView", "Matplotlib/Seaborn"
        ],
        "Big Data & Analytics": [
            "Hadoop Ecosystem", "Apache Spark", "Google BigQuery",
            "Data Warehousing", "ETL Processes"
        ],
        "Web Development": [
            "HTML/CSS/JavaScript", "Streamlit", "FastAPI/Flask", "RESTful APIs"
        ],
        "Tools & Platforms": [
            "Git/GitHub", "Docker", "Jupyter Notebooks", "Google Colab",
            "VS Code", "JIRA", "Figma"
        ],
        "Professional Skills": [
            "Problem Solving", "Team Leadership", "Project Management",
            "Agile/Scrum", "Technical Documentation",
            "Client Communication", "Research & Development"
        ]
    },
    "projects": [
        {
            "name": "Machinery Maintenance System for Manufacturing Industry",
            "description": "Developed a maintenance optimization system using LangChain, Llama 3, and GroqCloud to generate tailored maintenance strategies, schedules, and worker assignments. Enhanced operational efficiency by providing AI-driven recommendations and system check summaries.",
            "technologies": ["LangChain", "Llama 3", "MongoDB", "Amazon S3", "Streamlit"]
        },
        {
            "name": "DataVise – Intelligent Data Analyst Assistant",
            "description": "Engineered a MongoDB and Streamlit-based query system with Groq Cloud API integration, enabling natural language data retrieval and processing. Delivered LLM-powered insights that convert data into actionable summaries, supporting faster business decisions.",
            "technologies": ["MongoDB", "Streamlit", "Groq Cloud API", "Python"]
        },
        {
            "name": "Cold Email Generator using Llama 3",
            "description": "Built a cold email generator using Groq, LangChain, and Streamlit to automate job listing extraction from company career pages. Integrated a vector database to personalize outreach emails with relevant portfolio links, enhancing targeted client acquisition.",
            "technologies": ["Llama 3", "LangChain", "Chroma DB", "Streamlit"]
        },
        {
            "name": "Intelligent Invoice Processing Automation",
            "description": "Designed a robust invoice automation platform integrating with ERP systems, enabling processing of 500+ vendor invoices weekly and reducing payment delays by 30%.",
            "technologies": ["AWS Textract", "Amazon SageMaker", "AWS Lambda", "Amazon QuickSight", "Python"]
        }
    ]
}

def format_knowledge_item(item, indent=0):
    """Recursively format knowledge base items into a string."""
    if isinstance(item, dict):
        return '\n'.join(
            f"{'  ' * indent}{key}: {format_knowledge_item(value, indent + 1)}"
            for key, value in item.items()
        )
    elif isinstance(item, list):
        return '\n'.join(
            f"{'  ' * indent}- {format_knowledge_item(i, indent + 1)}"
            for i in item
        )
    return str(item)

def generate_response(chain: Chain, user_message: str) -> str:
    """Generate a response based on the user's message using the Chain class."""
    # Format the knowledge base as a string
    knowledge_str = format_knowledge_item(KNOWLEDGE_BASE)
    
    # Create a prompt for the language model
    prompt = """You are Hemant Koli. Use only the information provided in the knowledge base below to respond as yourself.
    If the answer is not found in the knowledge base, respond politely that you don't have that information.
    Do not make up or infer any details beyond what is provided.

    Knowledge Base:
    {knowledge_str}

    User: {user_message}
    Hemant Koli:"""
    
    try:
        # Use the Chain instance to generate a response
        response = chain.ask(
            prompt=prompt,
            input_vars={"knowledge_str": knowledge_str, "user_message": user_message}
        )
        return response
    except Exception as e:
        logging.error(f"Error generating response: {str(e)}")
        return "I'm sorry, I encountered an error while processing your request. Please try again later."

# API Endpoints
@app.get("/api/health")
async def health():
    return {"status": "ok", "message": "Portfolio API is running"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(chat_request: ChatRequest, chain: Chain = Depends(get_chain)):
    """Handle chat messages and return responses using the Chain class."""
    if not chat_request.messages:
        raise HTTPException(status_code=400, detail="No messages provided")
    
    # Get the last user message
    last_message = next((msg for msg in reversed(chat_request.messages) if msg.role == "user"), None)
    if not last_message:
        raise HTTPException(status_code=400, detail="No user message found")
    
    try:
        # Generate response using the Chain instance
        response_text = generate_response(chain, last_message.content)
        
        return ChatResponse(
            response=response_text,
            sources=[{"type": "knowledge_base", "timestamp": datetime.utcnow().isoformat()}]
        )
    except Exception as e:
        logging.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your request: {str(e)}"
        )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# Health check endpoint with more details
@app.get("/healthz")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.environment,
        "groq_key_loaded": bool(os.getenv("GROQ_API_KEY"))
    }

# Test endpoint to verify environment variables
@app.get("/test-env")
async def test_env():
    return {
        "groq_key_loaded": bool(os.getenv("GROQ_API_KEY")),
        "groq_key_length": len(os.getenv("GROQ_API_KEY", ""))
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    
    # Validate required environment variables
    if not os.getenv("GROQ_API_KEY"):
        logging.warning("GROQ_API_KEY environment variable is not set. The chatbot will not function properly.")
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=port,
        reload=settings.environment == "development",
        log_level=settings.log_level,
        workers=1
    )
