from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import files

# Create the FastAPI app
app = FastAPI(title="Files Explorer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(files.router, prefix="/api/v1/files", tags=["files"])

@app.get("/server-status")
def server_status():
    return {"status": "online"}



