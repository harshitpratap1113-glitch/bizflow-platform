import asyncio
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.core.config import settings
from app.db.database import init_db, get_db
from app.api.leadradar_routes import router as leadradar_router
from app.modules.leadradar.scanner import scanner
from app.modules.leadradar.notifier import ws_manager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("bizflow.main")

# Background Periodic Scanner Worker (Local / Daemon Mode)
async def background_scanner_loop():
    logger.info("[*] LeadRadar Background Scanner Worker Started.")
    await asyncio.sleep(5)
    while True:
        try:
            db = get_db()
            cursor = db.cursor()
            try:
                cursor.execute("SELECT value FROM settings WHERE key = 'scan_interval_seconds'")
                row = cursor.fetchone()
                interval = int(row["value"]) if row else settings.SCAN_INTERVAL
            except Exception:
                interval = settings.SCAN_INTERVAL
            db.close()

            logger.info("[*] Executing scheduled social intent scan...")
            await scanner.run_full_scan()
        except Exception as e:
            logger.error(f"[!] Background scanner error: {e}")
        
        # Sleep for configured interval
        await asyncio.sleep(max(30, interval))

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup:
    logger.info("[*] Initializing BizFlow AI Database...")
    try:
        init_db()
    except Exception as e:
        logger.error(f"DB Init error: {e}")
    
    scanner_task = None
    if not os.environ.get("VERCEL") and not os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        scanner_task = asyncio.create_task(background_scanner_loop())
    
    yield
    
    # Shutdown:
    if scanner_task:
        logger.info("[*] Shutting down background tasks...")
        scanner_task.cancel()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# Enable CORS for frontend flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount LeadRadar API routes for both direct /api/leadradar and versioned /api/v1
app.include_router(leadradar_router, prefix="/api/leadradar", tags=["LeadRadar"])
app.include_router(leadradar_router, prefix="/api/v1/leadradar", tags=["LeadRadar v1"])
app.include_router(leadradar_router, prefix=settings.API_V1_STR, tags=["API v1"])

# Real-time WebSocket Endpoint
@app.websocket("/ws/leads")
async def websocket_leads_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep-alive ping/pong
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)

# Static Files & Dashboard UI
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def root():
    candidates = [
        os.path.join(STATIC_DIR, "index.html"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "static", "index.html"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "index.html"),
        os.path.join(os.getcwd(), "backend", "static", "index.html"),
        os.path.join(os.getcwd(), "static", "index.html")
    ]
    for c in candidates:
        if os.path.exists(c):
            return FileResponse(c)
    return {"message": "BizFlow AI Backend is running!", "status": "online", "docs": "/docs"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "BizFlow AI LeadRadar"}
