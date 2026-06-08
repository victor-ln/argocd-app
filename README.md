# argocd-app

API **FastAPI** de demonstração para o laboratório de **GitOps com ArgoCD**
([`k8s-manifests`](https://github.com/victor-ln/k8s-manifests)). É um CRUD bobo
in-memory cuja função real é **provar o ciclo de CD**: cada release gera uma imagem nova
que reporta a própria versão na rota `/version`.

> A imagem é publicada em **Docker Hub: `vlimanu/argocd-app`**. Os manifestos K8s que o
> ArgoCD observa vivem no repo **`gitops-manifests`** (não aqui) — este repo é só o
> **source** (código + Dockerfile + CI).

## Rotas

| Método | Rota          | O que faz                                            |
| ------ | ------------- | ---------------------------------------------------- |
| GET    | `/version`    | versão do build (vinda da tag via `--build-arg`)     |
| GET    | `/health`     | liveness probe (`{status, version}`)                 |
| GET    | `/items`      | lista os itens                                       |
| POST   | `/items`      | cria um item (`{name, description?}`) → 201          |
| GET    | `/items/{id}` | busca um item (404 se não existe)                    |
| PUT    | `/items/{id}` | substitui um item (404 se não existe)                |
| DELETE | `/items/{id}` | remove um item → 204 (404 se não existe)             |

O store é em memória — **some no restart do Pod** (proposital; o foco é o pipeline).

## Rodar local

```sh
uv sync --frozen
APP_VERSION=1.2.3 uv run fastapi run app/main.py   # http://localhost:8000
curl localhost:8000/version                          # {"version":"1.2.3"}
```

Sem `APP_VERSION`, a versão cai no `.env` local (`dev`/`1.0.0`). Docs interativas em
`/docs`.

## Build da imagem

```sh
docker build -t argocd-app --build-arg APP_VERSION=1.2.3 .
docker run -p 8000:8000 argocd-app
curl localhost:8000/version                          # {"version":"1.2.3"}
```

### Como a versão flui

`--build-arg APP_VERSION` → `ARG`/`ENV APP_VERSION` (Dockerfile) → `pydantic-settings`
(`app/config/settings.py`, campo `app_version`) → rota `/version`. Variável de ambiente
**sobrepõe** o `.env`, e o `.env` **não** entra na imagem (está no `.dockerignore`) — então
a versão da imagem vem 100% do build-arg (default `dev` se omitido).

## Pipeline de release & CD (`.github/workflows/deploy.yml`)

Um único workflow disparado por **push na `main`**, com 3 jobs encadeados por `needs`:

1. **release** — [semantic-release](https://semantic-release.gitbook.io/) lê os commits
   convencionais e, se houver release, cria a tag `vX.Y.Z` + GitHub Release. Usa o
   `GITHUB_TOKEN` padrão (não precisa de PAT, pois o build é o próximo *job* no mesmo run,
   não um workflow separado). Regras de bump em `.releaserc.json`.
2. **build** — builda e dá push de `vlimanu/argocd-app:X.Y.Z` (+ `:latest`) no Docker Hub,
   injetando `APP_VERSION=X.Y.Z`.
3. **bump** — `kustomize edit set image` no overlay `argocd-app/` do repo
   `gitops-manifests`, commitando a nova tag. O **ArgoCD** observa esse repo e sincroniza
   o cluster.

### Bump por tipo de commit (convencional)

| Tipo                                   | Release  |
| -------------------------------------- | -------- |
| `feat:`                                | minor    |
| `fix:` / `perf:` / `refactor:`         | patch    |
| `feat!:` / `BREAKING CHANGE:`          | major    |
| `chore:` `docs:` `test:` `ci:` `build:`| nenhum   |

### Secrets/vars necessários (no GitHub deste repo)

- **Secrets:** `REGISTRY_USER` (= `vlimanu`), `REGISTRY_PASSWORD` (access token do Docker
  Hub), `MANIFEST_REPO_TOKEN` (PAT com push no `gitops-manifests`).
- **Vars:** `GITOPS_MANIFEST_REPO` (= `victor-ln/gitops-manifests`),
  `GITOPS_MANIFEST_BRANCH` (= `main`), `GITOPS_BUMP_ENABLED` (= `true`).

O passo a passo completo do GitOps (instalar ArgoCD, Connect Repo, criar Applications,
rollback) está em
[`k8s-manifests/docs/gitops-argocd.md`](https://github.com/victor-ln/k8s-manifests/blob/main/docs/gitops-argocd.md).
