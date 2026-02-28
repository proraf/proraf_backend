from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from proraf.database import Base


DEFAULT_USER_AVATAR = "static/images/users/icone.png"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    senha = Column(String(255), nullable=True)  # Nullable para usuários OAuth
    tipo_pessoa = Column(String(10), nullable=False)
    cpf = Column(String(14), nullable=True, unique=True, index=True)
    cnpj = Column(String(18), nullable=True, unique=True, index=True)
    nit = Column(String(11), nullable=True, unique=True, index=True)  # NIT - Número de Inscrição do Trabalhador
    telefone = Column(String(20), nullable=True, unique=True, index=True)
    tipo_perfil = Column(String(20), default="user")
    google_id = Column(String(255), nullable=True, unique=True, index=True)
    avatar_url = Column(String(500), nullable=False, default=DEFAULT_USER_AVATAR)
    provider = Column(String(20), default="local")  # local, google
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    products = relationship("Product", back_populates="user")
    
    __table_args__ = (
        CheckConstraint("tipo_pessoa IN ('F', 'J', 'N')", name="check_tipo_pessoa"),
    )
    
    def __repr__(self):
        return f"<User {self.email}>"