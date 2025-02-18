from fastapi import FastAPI
from app.routers import linkedin

from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="LinkedIn Scraper API")

# Allow requests from your frontend (adjust allowed origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust to your frontend's URL
    allow_credentials=True,
    allow_methods=["*"],  # This will allow all methods including OPTIONS, POST, etc.
    allow_headers=["*"],
)


app.include_router(linkedin.router)


@app.get("/")
def home():
    return {"message": "Welcome to LinkedIn Scraper API"}
