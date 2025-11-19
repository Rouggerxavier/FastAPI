from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dependencies import get_db, verificar_token
from models import Pedido, STATUS_VALUES
from schemas import PedidoSchema

# todas as rotas aqui exigem token válido
order_router = APIRouter(
    prefix="/orders",
    tags=["orders"],
    dependencies=[Depends(verificar_token)],
)


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


@order_router.post("/pedido/cancelar/{id_pedido}")
async def cancelar_pedido(id_pedido: int, db: Session = Depends(get_db)):
    # aqui é Pedido.id, não pedido.id
    pedido = db.query(Pedido).filter(Pedido.id == id_pedido).first()

    if not pedido:
        raise HTTPException(status_code=404, dSSetail="Pedido não encontrado")

    # como suas choices são ("cancelado", "Cancelado"), use o valor "cancelado"
    pedido.status = "cancelado"
    db.commit()
    db.refresh(pedido)

    return {
        "mensagem": f"Pedido número {pedido.id} cancelado com sucesso",
        "pedido": {
            "id": pedido.id,
            "usuario_id": pedido.usuario_id,
            "preco": pedido.preco,
            "status": pedido.status.value if hasattr(pedido.status, "value") else pedido.status,
        },
    }
