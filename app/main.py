from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.scheduler import start_scheduler, stop_scheduler
from app.database.db import Base, engine
from app.routers.post_routes import router as post_router
from fastapi.staticfiles import StaticFiles


app = FastAPI()

app.mount("/media", StaticFiles(directory="media"), name="media")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


Base.metadata.create_all(bind=engine)


@app.on_event("startup")
def startup_event():
    start_scheduler()


@app.on_event("shutdown")
def shutdown_event():
    stop_scheduler()


app.include_router(post_router)