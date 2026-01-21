from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db
from app.api import auth, customers, visits, sync

# Initialize FastAPI app
app = FastAPI(
    title="Sales Route Tracker API",
    description="API for tracking Kimball Midwest sales routes",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(customers.router)
app.include_router(visits.router)
app.include_router(sync.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()


@app.get("/")
async def root():
    return {
        "message": "Sales Route Tracker API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
