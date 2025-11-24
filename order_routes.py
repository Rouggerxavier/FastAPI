from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dependencies import get_db, verificar_token
from models import Pedido, STATUS_VALUES, Usuario, ItemPedido
from schemas import (
    PedidoSchema,
    ItemPedidoSchema,
    RemoverItemSchema,
    PedidoCreateSchema,
)

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
            "status": pedido.status.value if hasattr(pedido.status, "value") else pedido.status,
        }
        for pedido in pedidos_cadastrados
    ]


@order_router.post("/pedido", status_code=201)
async def criar_pedido(
    pedido_schema: PedidoCreateSchema,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(verificar_token),
):
    # valida status
    if pedido_schema.status is not None and pedido_schema.status not in STATUS_VALUES:
        raise HTTPException(status_code=400, detail="Status inválido para o pedido")

    # regra de permissão: admin pode criar pra qualquer usuario_id,
    # usuário normal só cria pedido pra ele mesmo
    if not usuario.admin and usuario.id != pedido_schema.usuario_id:
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para criar pedido para outro usuário",
        )

    # calcula o preço total com base nos itens enviados
    preco_total = 0.0
    for item in pedido_schema.itens:
        preco_total += item.quantidade * item.preco_unitario

    # cria o pedido já com o preço calculado
    novo_pedido = Pedido(
        usuario_id=pedido_schema.usuario_id,
        preco=preco_total,
        status=pedido_schema.status,
    )
    db.add(novo_pedido)
    db.flush()  # garante que novo_pedido.id existe

    # cria os itens vinculados ao pedido
    for item in pedido_schema.itens:
        item_pedido = ItemPedido(
            pedido_id=novo_pedido.id,
            sabor=item.sabor,
            tamanho=item.tamanho,
            quantidade=item.quantidade,
            preco_unitario=item.preco_unitario,
        )
        db.add(item_pedido)

    db.commit()
    db.refresh(novo_pedido)

    return {
        "mensagem": f"Pedido criado com sucesso. Id do pedido: {novo_pedido.id}",
        "pedido": {
            "id": novo_pedido.id,
            "usuario_id": novo_pedido.usuario_id,
            "preco": novo_pedido.preco,
            "status": novo_pedido.status.value if hasattr(novo_pedido.status, "value") else novo_pedido.status,
        },
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
            "status": pedido.status.value if hasattr(pedido.status, "value") else pedido.status,
        },
    }


@order_router.get("/listar")
async def listar_pedidos(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(verificar_token),
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
    pedido = db.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    if not usuario.admin and usuario.id != pedido.usuario_id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para alterar esse pedido")

    item_pedido = ItemPedido(
        sabor=item_pedido_schema.sabor,
        tamanho=item_pedido_schema.tamanho,
        quantidade=item_pedido_schema.quantidade,
        preco_unitario=item_pedido_schema.preco_unitario,
        pedido=pedido,  # liga na relação
    )

    # soma no preço atual em vez de recalcular tudo
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
    # 1) Busca o pedido
    pedido = db.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    # 2) Verifica permissão (admin ou dono do pedido)
    if not usuario.admin and usuario.id != pedido.usuario_id:
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para alterar esse pedido",
        )

    # 3) Busca o item específico (pelo sabor + tamanho)
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

    # 4) Calcula quanto vai ser removido de fato
    if remover_item.quantidade >= item.quantidade:
        # remove tudo desse item
        quantidade_removida = item.quantidade
        valor_removido = item.quantidade * item.preco_unitario
        db.delete(item)
    else:
        # remove só uma parte
        quantidade_removida = remover_item.quantidade
        valor_removido = remover_item.quantidade * item.preco_unitario
        item.quantidade -= remover_item.quantidade

    # 5) Atualiza preço do pedido
    novo_preco = pedido.preco - valor_removido
    if novo_preco < 0:
        novo_preco = 0
    pedido.preco = novo_preco

    db.commit()
    db.refresh(pedido)

    # 6) Busca itens restantes do pedido
    itens_restantes = (
        db.query(ItemPedido)
        .filter(ItemPedido.pedido_id == id_pedido)
        .all()
    )

    itens_restantes_out = [
        {
            "id": it.id,
            "sabor": it.sabor,
            "tamanho": it.tamanho,
            "quantidade": it.quantidade,
            "preco_unitario": it.preco_unitario,
            "subtotal": it.quantidade * it.preco_unitario,
        }
        for it in itens_restantes
    ]

    # 7) Monta resposta com "o que saiu" e "como ficou"
    item_removido_out = {
        "sabor": remover_item.sabor,
        "tamanho": remover_item.tamanho,
        "quantidade_removida": quantidade_removida,
        "valor_removido": valor_removido,
    }

    return {
        "mensagem": "Item removido com sucesso",
        "item_removido": item_removido_out,
        "pedido_atualizado": {
            "id": pedido.id,
            "usuario_id": pedido.usuario_id,
            "preco": pedido.preco,
            "status": pedido.status.value if hasattr(pedido.status, "value") else pedido.status,
            "itens": itens_restantes_out,
        },
    }

