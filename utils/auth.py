import hashlib
import secrets
from typing import Optional, Tuple
from fastapi import Request, Depends
from sqlalchemy.orm import Session

from database.db import get_db
from database.models import Usuario

COOKIE_SESSION_NAME = "session_token"


def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """
    Genera un hash seguro de la contraseña usando PBKDF2-HMAC-SHA256 y un salt criptográfico.
    Retorna (password_hash, salt).
    """
    if not salt:
        salt = secrets.token_hex(16)
    
    # 100,000 iteraciones con sha256
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    )
    return key.hex(), salt


def verify_password(password: str, password_hash: str, salt: str) -> bool:
    """Verifica si la contraseña ingresada coincide con el hash almacenado."""
    if not password_hash or not salt:
        return False
    computed_hash, _ = hash_password(password, salt)
    return secrets.compare_digest(computed_hash, password_hash)


def generar_session_token() -> str:
    """Genera un token de sesión seguro y único."""
    return secrets.token_urlsafe(32)


def obtener_usuario_actual(request: Request, db: Session = Depends(get_db)) -> Optional[Usuario]:
    """
    Extrae el usuario actual a partir de la cookie de sesión o header Authorization.
    """
    token = request.cookies.get(COOKIE_SESSION_NAME)
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            
    if not token:
        return None

    usuario = db.query(Usuario).filter_by(session_token=token).first()
    return usuario
