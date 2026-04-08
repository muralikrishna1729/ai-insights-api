"""
This is Entry point of execution
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.database import engine,Base
from app.routers.upload import router as upload_router



## Create an async context manager called lifespan,Inside it → call Base.metadata.create_all(bind=engine) Then yield
## creates their tables in the DB if they don't exist yet. every time app restarts, this runs automatically. New models get their tables created without you doing anything
@asynccontextmanager
async def lifespan(app:FastAPI):
    Base.metadata.create_all(bind = engine)
    yield
    engine.dispose()



app = FastAPI(
    title="AutoInsight API",
    description="Upload CSV → Get ML-powered insights",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(upload_router)

@app.get("/")
def root():
    return {"message": "AutoInsight API is running"}

