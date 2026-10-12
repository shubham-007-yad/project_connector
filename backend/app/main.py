from fastapi import FastAPI
from .routes import router
from .database import Base, engine
from . import db_models

app = FastAPI()
Base.metadata.create_all(bind=engine)
app.include_router(router)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/")
def read_root():
    return {"message": "Welcome to the Nexus App!"}
