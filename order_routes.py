from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dependencies import get_db, verificar_token
from models import Pedido, STATUS_VALUES, Usuario, ItemPedido
from schemas import PedidoSchema, ItemPedidoSchema


order_router = APIRouter(
    prefix="/orders",
    tags=["orders"],
)


@order_router.get("/lista")
async def pedidos(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(verificar_token)
):
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
async def criar_pedido(
    pedido_schema: PedidoSchema,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(verificar_token)
):
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
async def cancelar_pedido(
    id_pedido: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(verificar_token)
):
    pedido = db.query(Pedido).filter(Pedido.id == id_pedido).first()

    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    if not usuario.admin and usuario.id != pedido.usuario_id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para cancelar esse pedido")

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


@order_router.get("/listar")
async def listar_pedidos(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(verificar_token)
):
    if not usuario.admin:
        raise HTTPException(status_code=403, detail="Você não tem permissão para listar pedidos")

    pedidos = db.query(Pedido).all()

    return [
        {
            "id": p.id,
            "usuario_id": p.usuario_id,
            "preco": p.preco,
            "status": p.status.value if hasattr(p.status, "value") else p.status,
        }
        for p in pedidos
    ]


@order_router.post("/pedido/adicionar-item/{id_pedido}")
async def adicionar_item_pedido(
    id_pedido: int,
    item_pedido_schema: ItemPedidoSchema,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(verificar_token),
):
    # busca o pedido
    pedido = db.query(Pedido).filter(Pedido.id == id_pedido).first()

    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não existente")

    # só admin ou dono do pedido
    if not usuario.admin and usuario.id != pedido.usuario_id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para alterar este pedido")

    # cria o item
    item_pedido = ItemPedido(
        pedido_id=pedido.id,
        nome_item=item_pedido_schema.sabor,      # ou outro mapeamento que você preferir
        quantidade=item_pedido_schema.quantidade,
        # se você adicionar preco_unitario na model, coloque aqui também
        # preco_unitario=item_pedido_schema.preco_unitario,
    )

    db.add(item_pedido)

    # recalcula o preço do pedido (usa o método da classe Pedido)
    pedido.calcular_preco()

    db.commit()
    db.refresh(pedido)
    db.refresh(item_pedido)

    return {
        "mensagem": "Item criado com sucesso",
        "item_id": item_pedido.id,
        "preco_pedido": pedido.preco,
    }
