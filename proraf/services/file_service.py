import os
import uuid
from typing import Optional
from fastapi import UploadFile, HTTPException, status
from PIL import Image
import aiofiles
from pathlib import Path


class FileService:
    """Serviço para gerenciamento de arquivos"""
    
    UPLOAD_DIR = "static/images/products"
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
    MAX_IMAGE_SIZE = (1920, 1080)  # Resolução máxima
    
    @classmethod
    def _get_upload_path(cls) -> Path:
        """Retorna o caminho do diretório de upload"""
        path = Path(cls.UPLOAD_DIR)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @classmethod
    def _validate_file(cls, file: UploadFile) -> None:
        """Valida o arquivo de upload"""
        # Verifica tamanho do arquivo
        if file.size and file.size > cls.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size is {cls.MAX_FILE_SIZE / (1024*1024):.1f}MB"
            )
        
        # Verifica extensão do arquivo
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in cls.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed types: {', '.join(cls.ALLOWED_EXTENSIONS)}"
            )
    
    @classmethod
    def _generate_filename(cls, original_filename: str) -> str:
        """Gera um nome único para o arquivo"""
        file_extension = Path(original_filename).suffix.lower()
        unique_id = str(uuid.uuid4())
        return f"{unique_id}{file_extension}"
    
    @classmethod
    async def save_product_image(cls, file: UploadFile) -> str:
        """
        Salva imagem de produto e retorna o caminho relativo
        
        Args:
            file: Arquivo de imagem para upload
            
        Returns:
            str: Caminho relativo da imagem salva
            
        Raises:
            HTTPException: Se houver erro na validação ou salvamento
        """
        # Validar arquivo
        cls._validate_file(file)
        
        # Gerar nome único
        filename = cls._generate_filename(file.filename)
        file_path = cls._get_upload_path() / filename
        
        try:
            # Salvar arquivo
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            # Processar imagem (redimensionar se necessário)
            await cls._process_image(file_path)
            
            # Retornar caminho relativo
            return f"{cls.UPLOAD_DIR}/{filename}"
            
        except Exception as e:
            # Remover arquivo se houver erro
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error saving file: {str(e)}"
            )
    
    @classmethod
    async def _process_image(cls, file_path: Path) -> None:
        """Processa a imagem (redimensiona se necessário)"""
        try:
            with Image.open(file_path) as img:
                # Verificar se precisa redimensionar
                if img.size[0] > cls.MAX_IMAGE_SIZE[0] or img.size[1] > cls.MAX_IMAGE_SIZE[1]:
                    img.thumbnail(cls.MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
                    
                    # Converter para RGB se necessário (para JPEG)
                    if img.mode in ('RGBA', 'LA', 'P'):
                        rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                        rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = rgb_img
                    
                    # Salvar imagem processada
                    img.save(file_path, optimize=True, quality=85)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid image file: {str(e)}"
            )
    
    @classmethod
    def delete_image(cls, image_path: str) -> None:
        """Remove uma imagem do sistema de arquivos"""
        if not image_path or not image_path.startswith(cls.UPLOAD_DIR):
            return
        
        try:
            file_path = Path(image_path)
            if file_path.exists():
                file_path.unlink()
        except Exception:
            # Ignorar erros ao deletar arquivo
            pass
    
    @classmethod
    def get_image_url(cls, image_path: Optional[str], base_url: str = "") -> Optional[str]:
        """
        Retorna a URL completa da imagem
        
        Args:
            image_path: Caminho relativo da imagem
            base_url: URL base da aplicação
            
        Returns:
            str: URL completa da imagem ou None
        """
        if not image_path:
            return None
        
        # Se já for uma URL completa, retornar como está
        if image_path.startswith(('http://', 'https://', 'data:')):
            return image_path
        
        # Construir URL completa
        return f"{base_url.rstrip('/')}/{image_path}"