from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List

from database.db import get_db
from database.models import Usuario, RegistroCalculo, IteracionCalculo
from database.schemas import CalculoResponse, RegistroDetalle, IteracionDetalle

router = APIRouter()
templates = Jinja2Templates(directory="templates")


from utils.auth import obtener_usuario_actual


# ─── HTML routes ────────────────────────────────────────────────────────────

@router.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    usuario = obtener_usuario_actual(request, db)
    return templates.TemplateResponse("index.html", {"request": request, "usuario": usuario})


@router.get("/dashboard/{nombre_usuario}", response_class=HTMLResponse)
def dashboard_view(request: Request, nombre_usuario: str, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter_by(nombre_usuario=nombre_usuario).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "nombre_usuario": nombre_usuario},
    )


# ─── JSON API routes ─────────────────────────────────────────────────────────

@router.get("/historial/{nombre_usuario}", response_model=List[CalculoResponse])
def historial_usuario(nombre_usuario: str, db: Session = Depends(get_db)):
    """Devuelve el historial básico (sin tipo_serie). Mantiene compatibilidad."""
    usuario = db.query(Usuario).filter_by(nombre_usuario=nombre_usuario).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return (
        db.query(RegistroCalculo)
        .filter_by(id_usuario=usuario.id_usuario)
        .order_by(RegistroCalculo.n_registro)
        .all()
    )


@router.get("/api/historial/{nombre_usuario}", response_model=List[RegistroDetalle])
def historial_detalle(nombre_usuario: str, db: Session = Depends(get_db)):
    """Devuelve el historial enriquecido con tipo_serie y categoría para el dashboard."""
    usuario = db.query(Usuario).filter_by(nombre_usuario=nombre_usuario).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    registros = (
        db.query(RegistroCalculo)
        .filter_by(id_usuario=usuario.id_usuario)
        .order_by(RegistroCalculo.n_registro)
        .all()
    )

    return [
        RegistroDetalle(
            n_registro=r.n_registro,
            tipo_serie=r.tipo_serie.nombre,
            categoria=r.tipo_serie.categoria,
            valor_x=r.valor_x,
            n_terminos=r.n_terminos,
            valor_aproximado=r.valor_aproximado,
            valor_real=r.valor_real,
            error_absoluto=r.error_absoluto,
            error_relativo=r.error_relativo,
            fecha_calculo=r.fecha_calculo,
        )
        for r in registros
    ]


@router.get("/api/registro/{n_registro}/iteraciones", response_model=List[IteracionDetalle])
def obtener_iteraciones_registro(n_registro: int, db: Session = Depends(get_db)):
    """Devuelve la lista detallada de iteraciones/términos calculados para un registro."""
    registro = db.query(RegistroCalculo).filter_by(n_registro=n_registro).first()
    if not registro:
        raise HTTPException(status_code=404, detail="Registro de cálculo no encontrado")
    return registro.iteraciones