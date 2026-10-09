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

# Serve Root Brand Icons, Favicons, and Manifest for Global Domain Logos
@app.get("/favicon.ico")
@app.get("/favicon.svg")
@app.get("/favicon.png")
@app.get("/favicon-32x32.png")
@app.get("/apple-touch-icon.png")
@app.get("/android-chrome-192x192.png")
@app.get("/android-chrome-512x512.png")
@app.get("/site.webmanifest")
@app.get("/og-image.png")
@app.get("/robots.txt")
@app.get("/sitemap.xml")
async def serve_root_asset(request: WebSocket): # using generic request path
    from fastapi import Request
    # We can handle via request path
    pass

@app.get("/favicon.ico")
async def favicon_ico():
    for base in [STATIC_DIR, os.path.dirname(os.path.dirname(__file__))]:
        p = os.path.join(base, "favicon.ico")
        if os.path.exists(p):
            return FileResponse(p, media_type="image/x-icon")
    return {"error": "not found"}

@app.get("/favicon.svg")
async def favicon_svg():
    for base in [STATIC_DIR, os.path.dirname(os.path.dirname(__file__))]:
        p = os.path.join(base, "favicon.svg")
        if os.path.exists(p):
            return FileResponse(p, media_type="image/svg+xml")
    return {"error": "not found"}

@app.get("/android-chrome-192x192.png")
async def icon_192():
    for base in [STATIC_DIR, os.path.dirname(os.path.dirname(__file__))]:
        p = os.path.join(base, "android-chrome-192x192.png")
        if os.path.exists(p):
            return FileResponse(p, media_type="image/png")
    return {"error": "not found"}

@app.get("/android-chrome-512x512.png")
async def icon_512():
    for base in [STATIC_DIR, os.path.dirname(os.path.dirname(__file__))]:
        p = os.path.join(base, "android-chrome-512x512.png")
        if os.path.exists(p):
            return FileResponse(p, media_type="image/png")
    return {"error": "not found"}

@app.get("/apple-touch-icon.png")
async def apple_icon():
    for base in [STATIC_DIR, os.path.dirname(os.path.dirname(__file__))]:
        p = os.path.join(base, "apple-touch-icon.png")
        if os.path.exists(p):
            return FileResponse(p, media_type="image/png")
    return {"error": "not found"}

@app.get("/site.webmanifest")
async def web_manifest():
    for base in [STATIC_DIR, os.path.dirname(os.path.dirname(__file__))]:
        p = os.path.join(base, "site.webmanifest")
        if os.path.exists(p):
            return FileResponse(p, media_type="application/manifest+json")
    return {"error": "not found"}

@app.get("/og-image.png")
async def og_img():
    for base in [STATIC_DIR, os.path.dirname(os.path.dirname(__file__))]:
        p = os.path.join(base, "og-image.png")
        if os.path.exists(p):
            return FileResponse(p, media_type="image/png")
    return {"error": "not found"}

@app.get("/robots.txt")
async def robots_txt():
    for base in [STATIC_DIR, os.path.dirname(os.path.dirname(__file__))]:
        p = os.path.join(base, "robots.txt")
        if os.path.exists(p):
            return FileResponse(p, media_type="text/plain")
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse("User-agent: *\nAllow: /\nSitemap: https://bizflow-platform.vercel.app/sitemap.xml\n")

@app.get("/sitemap.xml")
async def sitemap_xml():
    for base in [STATIC_DIR, os.path.dirname(os.path.dirname(__file__))]:
        p = os.path.join(base, "sitemap.xml")
        if os.path.exists(p):
            return FileResponse(p, media_type="application/xml")
    from fastapi.responses import Response
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://bizflow-platform.vercel.app/</loc>
    <lastmod>2026-10-09</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>"""
    return Response(content=xml_content, media_type="application/xml")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "BizFlow AI LeadRadar"}

