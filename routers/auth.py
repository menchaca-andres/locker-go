from fastapi import APIRouter, Depends, HTTPException, Request, Response, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional

from database.db import get_db
from database.models import Usuario
from database.schemas import UsuarioRegistroRequest, UsuarioLoginRequest, UsuarioResponse
from utils.auth import hash_password, verify_password, generar_session_token, obtener_usuario_actual, COOKIE_SESSION_NAME

router = APIRouter()
templates = Jinja2Templates(directory="templates")


# ─── Vistas HTML ────────────────────────────────────────────────────────────

@router.get("/login", response_class=HTMLResponse)
def login_view(request: Request, db: Session = Depends(get_db)):
    usuario = obtener_usuario_actual(request, db)
    if usuario:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@router.get("/register", response_class=HTMLResponse)
def register_view(request: Request, db: Session = Depends(get_db)):
    usuario = obtener_usuario_actual(request, db)
    if usuario:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("register.html", {"request": request, "error": None})


# ─── Endpoints de Autenticación ──────────────────────────────────────────────

@router.post("/register")
def register_user(
    request: Request,
    nombre_usuario: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    nombre_usuario = nombre_usuario.strip()
    email = email.strip().lower()

    if len(nombre_usuario) < 3:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "El nombre de usuario debe tener al menos 3 caracteres"},
            status_code=400
        )
    if "@" not in email or "." not in email:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "El correo electrónico ingresado no es válido"},
            status_code=400
        )
    if len(password) < 6:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "La contraseña debe tener al menos 6 caracteres"},
            status_code=400
        )

    # Verificar si el usuario o correo ya existen
    if db.query(Usuario).filter_by(nombre_usuario=nombre_usuario).first():
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": f"El nombre de usuario '{nombre_usuario}' ya está en uso"},
            status_code=400
        )
    if db.query(Usuario).filter_by(email=email).first():
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": f"El correo '{email}' ya se encuentra registrado"},
            status_code=400
        )

    pwd_hash, salt = hash_password(password)
    session_token = generar_session_token()

    nuevo_usuario = Usuario(
        nombre_usuario=nombre_usuario,
        email=email,
        password_hash=pwd_hash,
        salt=salt,
        session_token=session_token
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key=COOKIE_SESSION_NAME,
        value=session_token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 7  # 7 días
    )
    return response


@router.post("/login")
def login_user(
    request: Request,
    email_o_usuario: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    email_o_usuario = email_o_usuario.strip()

    # Buscar usuario por email o nombre_usuario
    usuario = db.query(Usuario).filter(
        (Usuario.email == email_o_usuario.lower()) | (Usuario.nombre_usuario == email_o_usuario)
    ).first()

    if not usuario or not usuario.password_hash or not verify_password(password, usuario.password_hash, usuario.salt):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Correo/usuario o contraseña incorrectos"},
            status_code=400
        )

    session_token = generar_session_token()
    usuario.session_token = session_token
    db.commit()

    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key=COOKIE_SESSION_NAME,
        value=session_token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 7  # 7 días
    )
    return response


@router.get("/logout")
def logout_user(request: Request, db: Session = Depends(get_db)):
    usuario = obtener_usuario_actual(request, db)
    if usuario:
        usuario.session_token = None
        db.commit()

    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(COOKIE_SESSION_NAME)
    return response


# ─── JSON API Endpoints ──────────────────────────────────────────────────────

@router.post("/api/auth/register", response_model=UsuarioResponse)
def api_register(datos: UsuarioRegistroRequest, db: Session = Depends(get_db)):
    email = datos.email.strip().lower()
    if db.query(Usuario).filter_by(nombre_usuario=datos.nombre_usuario).first():
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está registrado")
    if db.query(Usuario).filter_by(email=email).first():
        raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado")

    pwd_hash, salt = hash_password(datos.password)
    session_token = generar_session_token()

    usuario = Usuario(
        nombre_usuario=datos.nombre_usuario,
        email=email,
        password_hash=pwd_hash,
        salt=salt,
        session_token=session_token
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.post("/api/auth/login")
def api_login(datos: UsuarioLoginRequest, response: Response, db: Session = Depends(get_db)):
    ident = datos.email_o_usuario.strip()
    usuario = db.query(Usuario).filter(
        (Usuario.email == ident.lower()) | (Usuario.nombre_usuario == ident)
    ).first()

    if not usuario or not usuario.password_hash or not verify_password(datos.password, usuario.password_hash, usuario.salt):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    session_token = generar_session_token()
    usuario.session_token = session_token
    db.commit()

    response.set_cookie(
        key=COOKIE_SESSION_NAME,
        value=session_token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 7
    )
    return {
        "status": "ok",
        "token": session_token,
        "usuario": {
            "id_usuario": usuario.id_usuario,
            "nombre_usuario": usuario.nombre_usuario,
            "email": usuario.email
        }
    }


@router.get("/api/auth/me", response_model=Optional[UsuarioResponse])
def api_me(request: Request, db: Session = Depends(get_db)):
    usuario = obtener_usuario_actual(request, db)
    return usuario
