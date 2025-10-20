from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Aplicação
    app_name: str = "ProRAF API"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # Banco de dados
    database_url: str = "sqlite:///./proraf.db"
    
    # Segurança
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 horas
    
    allowed_origins: list[str] = ["http://localhost:3000"] 
    
    # API Key para comunicação frontend-backend
    api_key: str = "your-api-key-change-in-production"
    
    # Upload de arquivos
    upload_dir: str = "static/images/products"
    max_file_size: int = 5 * 1024 * 1024  # 5MB
    allowed_image_types: list[str] = [".jpg", ".jpeg", ".png", ".webp"]
    max_image_width: int = 1920
    max_image_height: int = 1080
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


settings = Settings()