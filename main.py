from fastapi import FastAPI
from routes.election_routes import router as election_router
import uvicorn

app = FastAPI(title="TruVox Voting API", version="1.0")

# Register routes
app.include_router(election_router)

@app.get("/")
def home():
    return {"message": "Welcome to TruVox Election API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
