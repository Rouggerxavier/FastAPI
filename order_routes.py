from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dependencies import get_db
from models import Pedido, STATUS_VALUES
from schemas import PedidoSchema

order_router = APIRouter(prefix="/orders", tags=["orders"])


@order_router.get("/lista")
async def pedidos(db: Session = Depends(get_db)):
    pedidos_cadastrados = db.query(Pedido).all()
    return [
        {
            "id": pedido.id,
            "usuario_id": pedido.usuario_id,
            "preco": pedido.preco,
            "status": pedido.status.value if hasattr(pedido.status, "value") else pedido.status,
        }
        for pedido in pedidos_cadastrados
    ]


@order_router.post("/pedido", status_code=201)
async def criar_pedido(pedido_schema: PedidoSchema, db: Session = Depends(get_db)):
    if pedido_schema.status is not None and pedido_schema.status not in STATUS_VALUES:
        raise HTTPException(status_code=400, detail="Status inválido para o pedido")

    novo_pedido = Pedido(
        usuario_id=pedido_schema.usuario_id,
        preco=pedido_schema.preco,
        status=pedido_schema.status,
    )
    db.add(novo_pedido)
    db.commit()
    db.refresh(novo_pedido)

    return {"mensagem": f"Pedido criado com sucesso. Id do pedido: {novo_pedido.id}"}
