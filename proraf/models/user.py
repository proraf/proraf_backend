from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, CheckConstraint
from proraf.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    senha = Column(String(255), nullable=False)
    tipo_pessoa = Column(String(10), nullable=False)
    cpf = Column(String(14), nullable=True)
    cnpj = Column(String(18), nullable=True)
    telefone = Column(String(20), nullable=True)
    tipo_perfil = Column(String(20), default="user")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        CheckConstraint("tipo_pessoa IN ('F', 'J')", name="check_tipo_pessoa"),
    )
    
    def __repr__(self):
        return f"<User {self.email}>"