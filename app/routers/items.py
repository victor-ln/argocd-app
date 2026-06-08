"""CRUD bobo in-memory — proposital: o estado some no restart do Pod.

Serve só de cobaia para o ciclo de GitOps/CD (build → tag → ArgoCD → cluster).
Quem expõe a versão do build é a rota /version (em app/main.py).
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/items", tags=["items"])


class ItemIn(BaseModel):
    name: str
    description: str | None = None


class Item(ItemIn):
    id: int


# Armazenamento em memória — sem persistência (some quando o processo morre).
_items: dict[int, Item] = {}
_next_id = 1


@router.get("")
def list_items() -> list[Item]:
    return list(_items.values())


@router.post("", status_code=201)
def create_item(payload: ItemIn) -> Item:
    global _next_id
    item = Item(id=_next_id, **payload.model_dump())
    _items[item.id] = item
    _next_id += 1
    return item


@router.get("/{item_id}")
def get_item(item_id: int) -> Item:
    item = _items.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    return item


@router.put("/{item_id}")
def update_item(item_id: int, payload: ItemIn) -> Item:
    if item_id not in _items:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    item = Item(id=item_id, **payload.model_dump())
    _items[item_id] = item
    return item


@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int) -> None:
    if _items.pop(item_id, None) is None:
        raise HTTPException(status_code=404, detail="Item não encontrado")
