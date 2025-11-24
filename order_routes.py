from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dependencies import get_db, verificar_token
from models import Pedido, STATUS_VALUES, Usuario, ItemPedido
from schemas import (
    PedidoCreateSchema,
    PedidoSchema,
    ItemPedidoCreateSchema,
    RemoverItemSchema,
)

TABELA_PRECOS_PIZZA = {
    ("calabresa", "pequeno"): 30.0,
    ("calabresa", "medio"): 40.0,
    ("calabresa", "grande"): 50.0,

    ("marguerita", "pequeno"): 32.0,
    ("marguerita", "medio"): 42.0,
    ("marguerita", "grande"): 52.0,

    ("frango catupiry", "pequeno"): 35.0,
    ("frango catupiry", "medio"): 45.0,
    ("frango catupiry", "grande"): 55.0,
}


def _status_to_str(status):
    if hasattr(status, "value"):
        return status.value
    return status


def calcular_preco_unitario(sabor: str, tamanho: str) -> float:
    sabor_key = sabor.strip().lower()
    tamanho_key = tamanho.strip().lower()

    preco = TABELA_PRECOS_PIZZA.get((sabor_key, tamanho_key))
    if preco is None:
        raise HTTPException(
            status_code=400,
            detail="Combinação de sabor e tamanho não encontrada na tabela de preços",
        )
    return preco


order_router = APIRouter(
    prefix="/orders",
    tags=["orders"],
)

@order_router.get("/lista")
async def pedidos(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(verificar_token),
):
    pedidos_cadastrados = db.query(Pedido).all()

    return [
        {
            "id": pedido.id,
            "usuario_id": pedido.usuario_id,
            "preco": pedido.preco,
            "status": _status_to_str(pedido.status),
        }
        for pedido in pedidos_cadastrados
    ]

@order_router.post("/pedido", status_code=201)
async def criar_pedido(
    pedido_schema: PedidoCreateSchema,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(verificar_token),
):
    
    if pedido_schema.status is not None and pedido_schema.status not in STATUS_VALUES:
        raise HTTPException(status_code=400, detail="Status inválido para o pedido")

    if pedido_schema.quantidade <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantidade deve ser maior que zero",
        )

    preco_unitario = calcular_preco_unitario(
        pedido_schema.sabor,
        pedido_schema.tamanho,
    )
    subtotal = preco_unitario * pedido_schema.quantidade

    novo_pedido = Pedido(
        usuario_id=pedido_schema.usuario_id,
        preco=subtotal,
        status=pedido_schema.status,
    )
    db.add(novo_pedido)
    db.flush()

    item = ItemPedido(
        pedido_id=novo_pedido.id,
        sabor=pedido_schema.sabor,
        tamanho=pedido_schema.tamanho,
        quantidade=pedido_schema.quantidade,
        preco_unitario=preco_unitario,
    )
    db.add(item)
    db.flush()

    db.commit()
    db.refresh(novo_pedido)
    db.refresh(item)

    return {
        "id": novo_pedido.id,
        "usuario_id": novo_pedido.usuario_id,
        "preco_total": novo_pedido.preco,
        "status": _status_to_str(novo_pedido.status),
        "itens": [
            {
                "id": item.id,
                "sabor": item.sabor,
                "tamanho": item.tamanho,
                "quantidade": item.quantidade,
                "preco_unitario": item.preco_unitario,
                "subtotal": subtotal,
            }
        ],
    }

@order_router.post("/pedido/cancelar/{id_pedido}")
async def cancelar_pedido(
    id_pedido: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(verificar_token),
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
            "status": _status_to_str(pedido.status),
        },
    }

@order_router.get("/listar")
async def listar_pedidos(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(verificar_token),
):
    
    if not usuario.admin:
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para listar pedidos"
        )

    pedidos = db.query(Pedido).all()

    resposta = []
    for p in pedidos:
        itens_formatados = []
        for item in p.itens:
            subtotal = item.quantidade * item.preco_unitario
            itens_formatados.append(
                {
                    "id": item.id,
                    "sabor": item.sabor,
                    "tamanho": item.tamanho,
                    "quantidade": item.quantidade,
                    "preco_unitario": item.preco_unitario,
                    "subtotal": subtotal,
                }
            )

        resposta.append(
            {
                "id": p.id,
                "usuario_id": p.usuario_id,
                "preco_total": p.preco,
                "status": _status_to_str(p.status),
                "itens": itens_formatados,
            }
        )

    return resposta

@order_router.post("/pedido/adicionar-item/{id_pedido}")
async def adicionar_item_pedido(
    id_pedido: int,
    item_pedido_schema: ItemPedidoCreateSchema,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(verificar_token),
):
    pedido = db.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    if not usuario.admin and usuario.id != pedido.usuario_id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para alterar esse pedido")
    
    if item_pedido_schema.quantidade <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantidade deve ser maior que zero",
        )

    preco_unitario = calcular_preco_unitario(
        item_pedido_schema.sabor,
        item_pedido_schema.tamanho,
    )

    item_pedido = ItemPedido(
        sabor=item_pedido_schema.sabor,
        tamanho=item_pedido_schema.tamanho,
        quantidade=item_pedido_schema.quantidade,
        preco_unitario=preco_unitario,
        pedido=pedido,
    )

    valor_novo_item = item_pedido.quantidade * item_pedido.preco_unitario
    pedido.preco += valor_novo_item

    db.add(item_pedido)
    db.commit()
    db.refresh(pedido)
    db.refresh(item_pedido)

    return {
        "mensagem": "Item adicionado com sucesso",
        "item": {
            "id": item_pedido.id,
            "pedido_id": item_pedido.pedido_id,
            "sabor": item_pedido.sabor,
            "tamanho": item_pedido.tamanho,
            "quantidade": item_pedido.quantidade,
            "preco_unitario": item_pedido.preco_unitario,
            "subtotal": valor_novo_item,
        },
        "preco_pedido": pedido.preco,
    }


@order_router.post("/pedido/remover-item/{id_pedido}")
async def remover_item_pedido(
    id_pedido: int,
    remover_item: RemoverItemSchema,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(verificar_token),
):
    pedido = db.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    if not usuario.admin and usuario.id != pedido.usuario_id:
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para alterar esse pedido",
        )

    item = (
        db.query(ItemPedido)
        .filter(
            ItemPedido.pedido_id == id_pedido,
            ItemPedido.sabor == remover_item.sabor,
            ItemPedido.tamanho == remover_item.tamanho,
        )
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Item não encontrado nesse pedido",
        )

    if remover_item.quantidade >= item.quantidade:
        valor_removido = item.quantidade * item.preco_unitario
        quantidade_removida = item.quantidade
        quantidade_restante = 0
        db.delete(item)
    else:
        valor_removido = remover_item.quantidade * item.preco_unitario
        item.quantidade -= remover_item.quantidade
        quantidade_removida = remover_item.quantidade
        quantidade_restante = item.quantidade

    novo_preco = pedido.preco - valor_removido
    if novo_preco < 0:
        novo_preco = 0.0
    pedido.preco = novo_preco

    db.commit()
    db.refresh(pedido)

    return {
        "mensagem": "Item removido com sucesso",
        "item_removido": {
            "sabor": remover_item.sabor,
            "tamanho": remover_item.tamanho,
            "quantidade_removida": quantidade_removida,
            "valor_removido": valor_removido,
        },
        "pedido_atualizado": {
            "id": pedido.id,
            "usuario_id": pedido.usuario_id,
            "preco": pedido.preco,
            "status": _status_to_str(pedido.status),
            "item_restante": {
                "sabor": remover_item.sabor,
                "tamanho": remover_item.tamanho,
                "quantidade_restante": quantidade_restante,
            },
        },
    }


@order_router.post("/pedido/finalizar/{id_pedido}")
async def finalizar_pedido(
    id_pedido: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(verificar_token),
):
    if not usuario.admin:
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para finalizar pedidos",
        )

    pedido = db.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    status_atual = _status_to_str(pedido.status).lower()

    if status_atual in ("fechado", "cancelado"):
        raise HTTPException(
            status_code=400,
            detail=f"Não é possível finalizar um pedido com status '{status_atual}'",
        )
    
    pedido.status = "fechado"
    db.commit()
    db.refresh(pedido)

    itens_formatados = []
    for item in pedido.itens:
        subtotal = item.quantidade * item.preco_unitario
        itens_formatados.append(
            {
                "id": item.id,
                "sabor": item.sabor,
                "tamanho": item.tamanho,
                "quantidade": item.quantidade,
                "preco_unitario": item.preco_unitario,
                "subtotal": subtotal,
            }
        )

    return {
        "mensagem": f"Pedido {pedido.id} finalizado com sucesso",
        "pedido": {
            "id": pedido.id,
            "usuario_id": pedido.usuario_id,
            "preco_total": pedido.preco,
            "status": _status_to_str(pedido.status),
            "itens": itens_formatados,
        },
    }

@order_router.get("/pedido/{id_pedido}")
async def obter_pedido(
    id_pedido: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(verificar_token),
):
    pedido = db.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    if not usuario.admin and usuario.id != pedido.usuario_id:
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para visualizar esse pedido",
        )

    itens_formatados = []
    for item in pedido.itens:
        subtotal = item.quantidade * item.preco_unitario
        itens_formatados.append(
            {
                "id": item.id,
                "sabor": item.sabor,
                "tamanho": item.tamanho,
                "quantidade": item.quantidade,
                "preco_unitario": item.preco_unitario,
                "subtotal": subtotal,
            }
        )

    return {
        "id": pedido.id,
        "usuario_id": pedido.usuario_id,
        "preco_total": pedido.preco,
        "status": _status_to_str(pedido.status),
        "itens": itens_formatados,
    }
