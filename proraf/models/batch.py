from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Date, Boolean, Numeric, DateTime, ForeignKey
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
    qrcode = Column(String(255), nullable=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    product = relationship("Product", backref="batches")
    user = relationship("User", backref="batches")
    
    def __repr__(self):
        return f"<Batch {self.code}>"