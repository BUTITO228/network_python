import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

ITEMS: dict[int, dict] = {}
NEXT_ID = 1


class ItemCreate(BaseModel):
    name: str


class ItemUpdate(BaseModel):
    name: str = ""


@app.get("/items")
def list_items():
    return {"items": list(ITEMS.values())}


@app.get("/items/{item_id}/counter")
def get_counter(item_id: int):
    if item_id not in ITEMS:
        raise HTTPException(status_code=404, detail="Item not found")
    ITEMS[item_id]["counter"] = ITEMS[item_id].get("counter", 0) + 1
    return {"counter": ITEMS[item_id]["counter"]}


@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id not in ITEMS:
        raise HTTPException(status_code=404, detail="Item not found")
    return ITEMS[item_id]


@app.post("/items", status_code=201)
def create_item(item: ItemCreate):
    global NEXT_ID
    new_item = {"id": NEXT_ID, "name": item.name}
    ITEMS[NEXT_ID] = new_item
    NEXT_ID += 1
    return {"id": new_item["id"]}


@app.put("/items/{item_id}")
def update_item(item_id: int, update: ItemUpdate):
    if item_id not in ITEMS:
        raise HTTPException(status_code=404, detail="Item not found")
    ITEMS[item_id] = {"id": item_id, "name": update.name}
    return ITEMS[item_id]


@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int):
    if item_id not in ITEMS:
        raise HTTPException(status_code=404, detail="Item not found")
    del ITEMS[item_id]


@app.get("/divide")
def divide(a: int, b: int):
    if b == 0:
        raise HTTPException(status_code=400, detail="Division by zero")
    return {"result": a / b}


@app.get("/slow-sync")
async def slow_sync():
    await asyncio.sleep(0.5)
    return {"status": "done"}