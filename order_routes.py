from fastapi import APIRouter

order_router = APIRouter(prefix="/orders", tags=["orders"])

@order_router.get("/lista")
async def pedidos():
    return {"message": "você está na lista de pedidos"}
