from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from proraf.database import get_db
from proraf.models.product import Product
from proraf.models.user import User, DEFAULT_USER_AVATAR


router = APIRouter(
    prefix="/public",
    tags=["Público - Catálogo"],
)


@router.get(
    "/products",
    summary="Listar todos os produtos (público)",
    description="Retorna todos os produtos com dados básicos e nome do produtor.",
)
async def list_public_products(
    db: Session = Depends(get_db),
):
    rows = (
        db.query(Product, User.nome)
        .join(User, User.id == Product.user_id)
        .order_by(Product.id.desc())
        .all()
    )

    return [
        {
            "id": product.id,
            "nome": product.name,
            "imagem": product.image,
            "descricao": product.description,
            "produtor_nome": producer_name,
        }
        for product, producer_name in rows
    ]


@router.get(
    "/producers",
    summary="Listar todos os produtores (público)",
    description="Retorna todos os produtores com id, nome e imagem.",
)
async def list_public_producers(
    db: Session = Depends(get_db),
):
    producers = (
        db.query(User.id, User.nome, User.avatar_url)
        .order_by(User.nome.asc())
        .all()
    )

    return [
        {
            "id": producer.id,
            "nome": producer.nome,
            "imagem": producer.avatar_url or DEFAULT_USER_AVATAR,
        }
        for producer in producers
    ]


@router.get(
    "/search",
    summary="Busca pública de produtos e produtores",
    description="Busca textual simultânea por nome de produto e nome de produtor.",
)
async def public_search(
    q: str = Query(..., min_length=1, description="Texto para busca"),
    db: Session = Depends(get_db),
):
    search_term = f"%{q.strip()}%"

    products = (
        db.query(Product)
        .filter(Product.name.ilike(search_term))
        .order_by(Product.name.asc())
        .all()
    )

    producers = (
        db.query(User.id, User.nome, User.avatar_url)
        .filter(User.nome.ilike(search_term))
        .order_by(User.nome.asc())
        .all()
    )

    return {
        "produtos": [
            {
                "id": product.id,
                "nome": product.name,
                "descricao": product.description,
                "imagem": product.image,
            }
            for product in products
        ],
        "produtores": [
            {
                "id": producer.id,
                "nome": producer.nome,
                "icone": producer.avatar_url or DEFAULT_USER_AVATAR,
            }
            for producer in producers
        ],
    }


@router.get(
    "/producers/{producer_id}/products",
    summary="Listar produtos por produtor (público)",
    description="Retorna todos os produtos de um produtor específico pelo id.",
)
async def list_public_products_by_producer(
    producer_id: int,
    db: Session = Depends(get_db),
):
    producer = db.query(User.id).filter(User.id == producer_id).first()
    if not producer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produtor não encontrado",
        )

    products = (
        db.query(Product)
        .filter(Product.user_id == producer_id)
        .order_by(Product.id.desc())
        .all()
    )

    return [
        {
            "id": product.id,
            "nome": product.name,
            "imagem": product.image,
            "descricao": product.description,
        }
        for product in products
    ]
