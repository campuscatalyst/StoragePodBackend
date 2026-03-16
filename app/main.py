from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import files, auth, system, media, tus_server
from contextlib import asynccontextmanager
from app.db.main import init_db, get_session
from app.core.auth import Auth
from starlette.middleware.trustedhost import TrustedHostMiddleware
from app.logger import logger
from app.utils import is_first_boot, scan_and_insert, mark_first_boot_done, create_tmp_uploads_folder
from app.config import STORAGE_DIR, settings
from app.core.utils.auth_utils import verify_token
from fastapi import Depends
import os
from sqlalchemy import text

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up: initializing database...")
    logger.info("Starting up the SQL DB")
    
    init_db()
    success = Auth.create_initial_user()

    if not success:
        raise RuntimeError("Failed to create initial user. Aborting startup.")

    if not STORAGE_DIR or not os.path.isdir(STORAGE_DIR):
        raise RuntimeError(
            "Storage directory not configured/mounted. "
            "Set STORAGE_DIR or ensure /srv/dev-disk-*/Folder1 exists."
        )
    
    if is_first_boot():
        create_tmp_uploads_folder()
        scan_and_insert(root_path=STORAGE_DIR)
        mark_first_boot_done()
    
    yield

    print("Shutting down: closing database engine...")  # SQLite doesn’t need manual close

# Create the FastAPI app
app = FastAPI(title="Files Explorer API", lifespan=lifespan)

# if the requested host isn't from this list then it will return error - 400
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*.campuscatalyst.info", "*.local", "localhost", "127.0.0.1"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_origin_regex=settings.CORS_ALLOW_ORIGIN_REGEX,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[
        "Location",
        "Tus-Resumable",
        "Tus-Version",
        "Tus-Extension",
        "Tus-Max-Size",
        "Upload-Offset",
        "Upload-Length",
        "Upload-Expires",
    ],
)

app.include_router(files.router, prefix="/api/v1/files", tags=["files"])
app.include_router(tus_server.router, tags=["tus"], dependencies=[Depends(verify_token)])
app.include_router(system.router, prefix="/api/v1/system", tags=["system"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(media.router, prefix="/api/v1/media", tags=["media"])

@app.get("/api/v1/server-status")
def server_status():
    return {"status": "online"}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/readyz")
def readyz():
    # Storage must be mounted/configured
    if not STORAGE_DIR or not os.path.isdir(STORAGE_DIR):
        raise HTTPException(status_code=503, detail="Storage directory not ready")

    # DB must be reachable
    try:
        with get_session() as session:
            session.exec(text("SELECT 1"))
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database not ready: {e}")

    return {"status": "ready"}
