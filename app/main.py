from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import files, auth, system
from contextlib import asynccontextmanager
from app.db.main import init_db
from app.core.auth import Auth
from starlette.middleware.trustedhost import TrustedHostMiddleware
from app.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up: initializing database...")
    logger.info("Starting up the SQL DB")
    
    init_db()
    success = Auth.create_initial_user()

    if not success:
        raise RuntimeError("Failed to create initial user. Aborting startup.")
    
    yield

    print("Shutting down: closing database engine...")  # SQLite doesn’t need manual close
    
# Create the FastAPI app
app = FastAPI(title="Files Explorer API", lifespan=lifespan)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*.campuscatalyst.info", "*.local", "localhost", "127.0.0.1"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(files.router, prefix="/api/v1/files", tags=["files"])
app.include_router(system.router, prefix="/api/v1/system", tags=["system"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])

@app.get("/api/v1/server-status")
def server_status():
    return {"status": "online"}
