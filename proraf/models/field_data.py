from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from proraf.database import Base


class FieldData(Base):
    __tablename__ = "field_data"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    latitude = Column(String(50), nullable=True)
    longitude = Column(String(50), nullable=True)
    mapa = Column(String(255), nullable=True)
    imagem_aerea = Column(String(255), nullable=True)
    imagem_perfil = Column(String(255), nullable=True)
    imagem_fundo = Column(String(255), nullable=True)
    observacoes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento
    user = relationship("User", backref="field_data")
    
    def __repr__(self):
        return f"<FieldData {self.id} - User {self.user_id}>"