from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime
import os

from proraf.database import get_db
from proraf.models.batch import Batch
from proraf.models.product import Product
from proraf.models.user import User
from proraf.security import get_current_user
from proraf.services.print_service import ProductLabelPrinter
from pydantic import BaseModel


router = APIRouter(prefix="/print", tags=["Print"])


class PrintLabelRequest(BaseModel):
    batch_code: str
    printer_name: Optional[str] = "ZDesigner ZT230-200dpi ZPL"
    peso: Optional[str] = None
    endereco: Optional[str] = None
    telefone: Optional[str] = None
    validade_dias: Optional[int] = 30  # Dias a partir da data atual


class PrintLabelResponse(BaseModel):
    success: bool
    message: str
    batch_info: Optional[Dict[str, Any]] = None


@router.post("/batch-label", response_model=PrintLabelResponse)
async def print_batch_label(
    request: PrintLabelRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Imprime uma etiqueta para um lote específico
    """
    try:
        # Buscar o lote no banco de dados
        batch = db.query(Batch).filter(
            Batch.code == request.batch_code,
            Batch.user_id == current_user.id  # Só pode imprimir lotes próprios
        ).first()
        
        if not batch:
            raise HTTPException(
                status_code=404, 
                detail=f"Lote '{request.batch_code}' não encontrado ou não pertence ao usuário atual"
            )
        
        # Verificar se o produto existe
        if not batch.product:
            raise HTTPException(
                status_code=400,
                detail="Lote não possui produto associado"
            )
        
        # Preparar informações para a etiqueta
        produto_info = prepare_label_info(batch, current_user, request)
        
        # Criar instância do printer
        printer = ProductLabelPrinter(printer_name=request.printer_name)
        
        # Imprimir etiqueta
        success = printer.print_product_label(produto_info)
        
        if success:
            return PrintLabelResponse(
                success=True,
                message=f"Etiqueta do lote '{batch.code}' impressa com sucesso!",
                batch_info={
                    "batch_code": batch.code,
                    "product_name": batch.product.name,
                    "production": float(batch.producao) if batch.producao else 0,
                    "unit": batch.unidadeMedida,
                    "planting_date": batch.dt_plantio.isoformat() if batch.dt_plantio else None,
                    "harvest_date": batch.dt_colheita.isoformat() if batch.dt_colheita else None
                }
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Falha ao imprimir etiqueta. Verifique se a impressora está conectada e configurada corretamente."
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno do servidor: {str(e)}"
        )


@router.get("/batch-info/{batch_code}")
async def get_batch_info(
    batch_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retorna informações de um lote para preview da etiqueta
    """
    batch = db.query(Batch).filter(
        Batch.code == batch_code,
        Batch.user_id == current_user.id
    ).first()
    
    if not batch:
        raise HTTPException(
            status_code=404,
            detail=f"Lote '{batch_code}' não encontrado"
        )
    
    return {
        "batch_code": batch.code,
        "product_name": batch.product.name if batch.product else "N/A",
        "production": float(batch.producao) if batch.producao else 0,
        "unit": batch.unidadeMedida,
        "planting_date": batch.dt_plantio.isoformat() if batch.dt_plantio else None,
        "harvest_date": batch.dt_colheita.isoformat() if batch.dt_colheita else None,
        "expedition_date": batch.dt_expedition.isoformat() if batch.dt_expedition else None,
        "talhao": batch.talhao,
        "user_name": current_user.nome,
        "user_email": current_user.email,
        "user_phone": current_user.telefone,
        "user_cpf": current_user.cpf,
        "user_cnpj": current_user.cnpj
    }


@router.post("/test-label")
async def print_test_label(
    printer_name: Optional[str] = Query("ZDesigner ZT230-200dpi ZPL", description="Nome da impressora"),
    current_user: User = Depends(get_current_user)
):
    """
    Imprime uma etiqueta de teste com dados fictícios
    """
    try:
        # Dados de teste
        produto_info = {
            'produto_nome': 'Produto',
            'peso': '500g',
            'empresa': 'Empresa Teste',
            'endereco': 'Rua Teste, 123',
            'cpf': '123.456.789-00',
            'telefone': '(00) 1234-5678',
            'validade': datetime.now().strftime('%d/%m/%Y'),
            'codigo_produto': 'PRD-TESTE',
            'codigo_lote': 'LOT-TESTE',
            'url_rastreio': 'http://proraf.unihacker.club:8000/rastreio?search=LOT-TESTE'
        }
        
        printer = ProductLabelPrinter(printer_name=printer_name)
        success = printer.print_product_label(produto_info)
        
        if success:
            return {"success": True, "message": "Etiqueta de teste impressa com sucesso!"}
        else:
            raise HTTPException(
                status_code=500,
                detail="Falha ao imprimir etiqueta de teste"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao imprimir etiqueta de teste: {str(e)}"
        )


def prepare_label_info(batch: Batch, user: User, request: PrintLabelRequest) -> Dict[str, str]:
    """
    Prepara as informações do lote para impressão da etiqueta
    """
    from datetime import datetime, timedelta
    
    # Peso personalizado ou da produção do lote
    peso = request.peso
    if not peso and batch.producao and batch.unidadeMedida:
        peso = f"{batch.producao}{batch.unidadeMedida}"
    elif not peso:
        peso = "500g"  # Padrão
    
    # Endereço personalizado ou padrão
    endereco = request.endereco or "Endereço não informado"
    
    # Telefone personalizado ou do usuário
    telefone = request.telefone or user.telefone or "(00) 0000-0000"
    
    # Data de validade baseada na data de colheita ou expedição
    validade_date = None
    if batch.dt_expedition:
        validade_date = batch.dt_expedition
    elif batch.dt_colheita:
        validade_date = batch.dt_colheita
    else:
        validade_date = datetime.now().date()
    
    # Adicionar dias de validade
    validade_final = validade_date + timedelta(days=request.validade_dias)
    validade = validade_final.strftime('%d/%m/%Y')
    
    # CPF/CNPJ
    documento = user.cpf or user.cnpj or "000.000.000-00"
    
    return {
        'produto_nome': batch.product.name if batch.product else 'Produto',
        'peso': peso,
        'empresa': user.nome,
        'endereco': endereco,
        'cpf': documento,
        'telefone': telefone,
        'validade': validade,
        'codigo_produto': f"PRD-{batch.product.id}" if batch.product else "PRD-00000",
        'codigo_lote': batch.code,
        'url_rastreio': f'http://proraf.unihacker.club:8000/rastreio?search={batch.code}'
    }