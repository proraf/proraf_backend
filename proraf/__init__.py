# proraf/__init__.py
"""ProRAF - Sistema de Rastreabilidade Agrícola"""

__version__ = "0.1.0"
__author__ = "ProRAF Team"


# proraf/models/__init__.py
from proraf.models.user import User
from proraf.models.product import Product
from proraf.models.batch import Batch
from proraf.models.movement import Movement
from proraf.models.field_data import FieldData

__all__ = [
    "User",
    "Product",
    "Batch",
    "Movement",
    "FieldData",
]


# proraf/schemas/__init__.py
from proraf.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    Token,
    TokenData
)
from proraf.schemas.product import (
    ProductBase,
    ProductCreate,
    ProductUpdate,
    ProductResponse
)
from proraf.schemas.batch import (
    BatchBase,
    BatchCreate,
    BatchUpdate,
    BatchResponse
)

__all__ = [
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "Token",
    "TokenData",
    "ProductBase",
    "ProductCreate",
    "ProductUpdate",
    "ProductResponse",
    "BatchBase",
    "BatchCreate",
    "BatchUpdate",
    "BatchResponse",
]


# proraf/routers/__init__.py
from proraf.routers import auth, products, batches

__all__ = ["auth", "products", "batches"]


# proraf/services/__init__.py
from proraf.services.qrcode_service import generate_qrcode

__all__ = ["generate_qrcode"]


# tests/__init__.py
"""Testes para ProRAF API"""