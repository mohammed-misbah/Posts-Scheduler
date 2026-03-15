from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.scheduler import start_scheduler
from app.database.db import Base, engine
from app.routers.post_routes import router as post_router


app = FastAPI()


# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Create database tables
Base.metadata.create_all(bind=engine)


# Start scheduler when app starts
@app.on_event("startup")
def startup_event():
    start_scheduler()


# Include API routes
app.include_router(post_router)
