from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from proraf.database import Base


class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    comertial_name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    variedade_cultivar = Column(String(255), nullable=True)
    status = Column(Boolean, default=True)
    image = Column(String(255), nullable=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Product {self.name}>"