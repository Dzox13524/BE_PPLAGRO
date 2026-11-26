"""FastAPI entrypoint:
- `/`        : Custom "Botanical Precision" Developer Portal (3-column Mintlify/Stripe layout, live telemetry, 1-click RBAC switcher)
- `/docs`    : Custom Swagger UI with Botanical Precision CSS & role switcher bar
- `/scalar`  : Scalar API Reference with matching dark botanical theme
- `/redoc`   : Built-in ReDoc
- `/health`  : Live telemetry endpoint (DB + AI Diagnosis CV mode)
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.common.exceptions import register_exception_handlers
from app.common.portal_ui import render_portal_html, render_scalar_html, render_swagger_html
from app.common.responses import success_response
from app.core.config import settings
from app.core.database import init_db
from app.modules.auth.router import router as auth_router
from app.modules.diagnosis.cv_detector import lettuce_detector
from app.modules.diagnosis.router import router as diagnosis_router
from app.modules.employees.router import router as employees_router
from app.modules.plants.router import router as plants_router
from app.modules.stocks.router import router as stocks_router
from app.utils.seeder import run_seeder

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s")
logger = logging.getLogger("lettuce-api")

# Folder harus ada sebelum StaticFiles di-mount
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.ML_MODELS_DIR.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Starting %s v%s (%s)", settings.APP_NAME, settings.APP_VERSION, settings.APP_ENV)
    init_db()
    run_seeder()
    lettuce_detector.load(settings.ML_MODELS_DIR)
    logger.info("AI Diagnosis mode: %s", lettuce_detector.mode)
    yield
    logger.info("Shutting down %s", settings.APP_NAME)


DESCRIPTION = f"""
REST API **Sistem Diagnosis Kesehatan Selada Hidroponik** (mengikuti ERD `hidroponik_selada`).

### Akun Demo (Tabel `users`)
- **owner**    → `{settings.SEED_OWNER_USERNAME}` / `{settings.SEED_OWNER_PASSWORD}`
- **karyawan** → `{settings.SEED_KARYAWAN_USERNAME}` / `{settings.SEED_KARYAWAN_PASSWORD}`

### Tabel Database (ERD `hidroponik_selada`)
`users`, `plants`, `growth_records`, `diagnosis_records`,
`disease_infos`, `nutrition_conditions`, `inventory_items`, `stock_movements`.
"""

TAGS_METADATA = [
    {"name": "A. Authentication", "description": "Login, logout, profil (`owner` & `karyawan`)"},
    {"name": "B. Manajemen Karyawan (OWNER)", "description": "Kelola tabel `users` - **owner only**"},
    {"name": "C. Manajemen Stok Bibit & Nutrisi (OWNER)",
     "description": "Kelola `inventory_items` & `stock_movements` - **owner only**"},
    {"name": "D. Manajemen Tanaman & Grafik Pertumbuhan (KARYAWAN & OWNER)",
     "description": "CRUD `plants`, `growth_records`, dan JSON grafik pertumbuhan"},
    {"name": "E. AI Diagnosis Kesehatan Selada (KARYAWAN)",
     "description": "Diagnosis citra daun selada (YOLO + Temperature Scaling) -> `diagnosis_records`, `disease_infos`, `nutrition_conditions`"},
    {"name": "System", "description": "Health check & telemetry"},
]

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=DESCRIPTION,
    openapi_tags=TAGS_METADATA,
    lifespan=lifespan,
    docs_url=None,   # disajikan secara kustom di bawah dengan injeksi CSS Botanical Precision
    redoc_url="/redoc",
)

_origins = settings.cors_origins_list
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=_origins != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.mount("/uploads", StaticFiles(directory=str(settings.UPLOAD_DIR)), name="uploads")

for r in (auth_router, employees_router, stocks_router, plants_router, diagnosis_router):
    app.include_router(r, prefix=settings.API_V1_PREFIX)


@app.get("/", include_in_schema=False)
def developer_portal(request: Request):
    """Serve the 3-column 'Botanical Precision' Developer Portal UI for browsers, or JSON info if explicitly requested."""
    accept = (request.headers.get("accept") or "").lower()
    if "application/json" in accept and "text/html" not in accept:
        return JSONResponse(
            success_response(
                {
                    "name": settings.APP_NAME,
                    "version": settings.APP_VERSION,
                    "portal": "/",
                    "docs": "/docs",
                    "scalar": "/scalar",
                    "redoc": "/redoc",
                },
                "Lettuce Management API berjalan",
            )
        )
    return HTMLResponse(render_portal_html())


@app.get("/docs", include_in_schema=False)
def custom_swagger_ui():
    """Swagger UI dengan injeksi CSS Botanical Precision + 1-click Role Switcher bar."""
    return HTMLResponse(render_swagger_html(app.openapi_url or "/openapi.json", settings.APP_NAME))


@app.get("/scalar", include_in_schema=False)
def custom_scalar_ui():
    """Scalar API Reference dengan tema Botanical Precision."""
    return HTMLResponse(render_scalar_html(app.openapi_url or "/openapi.json", settings.APP_NAME))


@app.get("/health", tags=["System"], summary="Live Telemetry & Health Check")
def health():
    return success_response(
        {
            "database": "ok",
            "ai_diagnosis": lettuce_detector.mode,
        },
        "Healthy",
    )
