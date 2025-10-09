import hashlib
from datetime import datetime


def generate_qrcode(data: str) -> str:
    """
    Gera um identificador único para o QR Code
    Na produção, isso seria substituído por uma biblioteca real de QR Code
    """
    timestamp = datetime.utcnow().isoformat()
    combined = f"{data}-{timestamp}"
    qrcode_hash = hashlib.sha256(combined.encode()).hexdigest()[:32]
    
    return f"QR-{qrcode_hash}"