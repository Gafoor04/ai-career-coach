from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.routers import interview, auth

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Career Coach API",
    description="Intelligent Interview Simulation Engine",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(interview.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "AI Career Coach API is running"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}