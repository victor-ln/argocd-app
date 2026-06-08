import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings

app = FastAPI()

logging.basicConfig(
    stream=sys.stdout,
    level=settings.app_log_level.upper(),
    format="%(asctime)s - %(levelname)s - [%(name)s] - %(message)s",
)

logger = logging.getLogger(__name__)


app = FastAPI(
    title="argocd-app",
    description="API de demonstração (CRUD in-memory) do lab de GitOps com ArgoCD",
    version=settings.app_version,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.app_cors_origins,
    allow_credentials=settings.app_allow_credentials,
    allow_methods=settings.app_allow_methods,
    allow_headers=settings.app_allow_headers,
)

@app.get("/health")
async def health():
    """Liveness probe — responde 200 enquanto o processo está de pé.

    NÃO depende de Mongo/Temporal: um blip no Mongo não deve matar o pod
    (isso é papel do readiness). Usado pelo livenessProbe do K8s.
    """
    return {"status": "ok", "version": settings.app_version}
