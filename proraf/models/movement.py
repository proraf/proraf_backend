from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from proraf.database import Base


class Movement(Base):
    __tablename__ = "movements"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tipo_movimentacao = Column(String(50), nullable=False)
    quantidade = Column(Numeric, default=0)
    batch_id = Column(Integer, ForeignKey("batch.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    batch = relationship("Batch", backref="movements")
    user = relationship("User", backref="movements")
    
    def __repr__(self):
        return f"<Movement {self.tipo_movimentacao} - {self.quantidade}>"