from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Date, Boolean, Numeric, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from proraf.database import Base


class Batch(Base):
    __tablename__ = "batch"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(100), nullable=False, unique=True, index=True)
    dt_plantio = Column(Date, nullable=True)
    dt_colheita = Column(Date, nullable=True)
    dt_expedition = Column(Date, nullable=True)
    status = Column(Boolean, default=True)
    talhao = Column(String(100), nullable=True)
    registro_talhao = Column(Boolean, default=False)
    producao = Column(Numeric, default=0)
    unidadeMedida = Column(String(50), nullable=True)
    qrcode = Column(String(255), nullable=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Campos editáveis - cópia histórica do produto no momento da criação do lote
    product_name = Column(String(255), nullable=True)
    product_type = Column(String(255), nullable=True)
    
    # Campos blockchain - imutáveis após preenchimento
    blockchain_address_who = Column(String(255), nullable=True)
    blockchain_address_to = Column(String(255), nullable=True)
    blockchain_product_name = Column(String(255), nullable=True)
    blockchain_product_expedition_date = Column(String(100), nullable=True)
    blockchain_product_type = Column(String(255), nullable=True)
    blockchain_batch_id = Column(String(255), nullable=True)
    blockchain_unit_of_measure = Column(String(100), nullable=True)
    blockchain_batch_quantity = Column(Float, nullable=True)
    blockchain_token_id = Column(Integer, nullable=True)
    
    # Relacionamentos
    product = relationship("Product", backref="batches")
    user = relationship("User", backref="batches")
    
    def __repr__(self):
        return f"<Batch {self.code}>"