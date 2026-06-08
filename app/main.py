import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.routers import items

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

app.include_router(items.router)


@app.get("/version", tags=["meta"])
async def version():
    """Expõe a versão do build — vinda da tag via --build-arg APP_VERSION.

    É a rota que prova o ciclo de CD: a cada release, a imagem nova reporta a
    versão nova aqui.
    """
    return {"version": settings.app_version}


@app.get("/health", tags=["meta"])
async def health():
    """Liveness probe — responde 200 enquanto o processo está de pé.

    NÃO depende de dependências externas: usado pelo livenessProbe do K8s.
    """
    return {"status": "ok", "version": settings.app_version}
