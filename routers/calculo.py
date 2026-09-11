from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import math

from database.db import get_db
from database.models import Usuario, TipoSerie, RegistroCalculo, IteracionCalculo
from database.schemas import CalculoRequest, CalculoResponse, TipoSerieEnum
from series.taylor import taylor_seno, taylor_coseno
from series.trigonometricas import trig_seno, trig_coseno, trig_tangente
from series.trig_inversas import trig_arcoseno, trig_arcocoseno, trig_arcotangente

router = APIRouter()

FUNCIONES_SERIE = {
    TipoSerieEnum.taylor_seno: (taylor_seno, math.sin),
    TipoSerieEnum.taylor_coseno: (taylor_coseno, math.cos),
    TipoSerieEnum.trig_seno: (trig_seno, math.sin),
    TipoSerieEnum.trig_coseno: (trig_coseno, math.cos),
    TipoSerieEnum.trig_tangente: (trig_tangente, math.tan),
    TipoSerieEnum.trig_arcoseno: (trig_arcoseno, math.asin),
    TipoSerieEnum.trig_arcocoseno: (trig_arcocoseno, math.acos),
    TipoSerieEnum.trig_arcotangente: (trig_arcotangente, math.atan),
}


def obtener_o_crear_usuario(db: Session, nombre_usuario: str) -> Usuario:
    usuario = db.query(Usuario).filter_by(nombre_usuario=nombre_usuario).first()
    if not usuario:
        usuario = Usuario(nombre_usuario=nombre_usuario)
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
    return usuario



def obtener_tipo(db: Session, nombre_tipo: str) -> TipoSerie:
    tipo = db.query(TipoSerie).filter_by(nombre=nombre_tipo).first()
    if not tipo:
        raise HTTPException(
            status_code=500,
            detail=f"Tipo de serie '{nombre_tipo}' no encontrado en el catálogo",
        )
    return tipo


@router.post("/calcular", response_model=CalculoResponse)
def calcular_serie(datos: CalculoRequest, db: Session = Depends(get_db)):
    funcion_aprox, funcion_real = FUNCIONES_SERIE[datos.tipo_serie]

    try:
        valor_aproximado, iteraciones_raw = funcion_aprox(datos.valor_x, datos.n_terminos, detallado=True)
        valor_real = funcion_real(datos.valor_x)
    except (ValueError, OverflowError, ZeroDivisionError) as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error matemático en la serie con x={datos.valor_x} y n={datos.n_terminos}: {str(e)}"
        )

    error_absoluto = abs(valor_real - valor_aproximado)
    error_relativo = (error_absoluto / abs(valor_real)) if valor_real != 0 else None

    usuario = obtener_o_crear_usuario(db, datos.nombre_usuario)
    tipo_serie = obtener_tipo(db, datos.tipo_serie.value)

    registro = RegistroCalculo(
        id_usuario=usuario.id_usuario,
        id_tipo=tipo_serie.id_tipo,
        valor_x=datos.valor_x,
        n_terminos=datos.n_terminos,
        valor_aproximado=valor_aproximado,
        valor_real=valor_real,
        error_absoluto=error_absoluto,
        error_relativo=error_relativo,
    )
    db.add(registro)
    db.flush()

    # Guardar cada iteración calculada
    for it in iteraciones_raw:
        val_acum = it["valor_acumulado"]
        err_abs = abs(valor_real - val_acum) if math.isfinite(val_acum) else float('inf')
        err_rel = (err_abs / abs(valor_real)) if valor_real != 0 and math.isfinite(err_abs) else None

        iter_obj = IteracionCalculo(
            n_registro=registro.n_registro,
            n_iteracion=it["n_iteracion"],
            valor_termino=it["valor_termino"] if math.isfinite(it["valor_termino"]) else 0.0,
            valor_acumulado=val_acum if math.isfinite(val_acum) else 0.0,
            error_absoluto=err_abs if math.isfinite(err_abs) else 1e9,
            error_relativo=err_rel if err_rel is not None and math.isfinite(err_rel) else None,
        )
        db.add(iter_obj)

    db.commit()
    db.refresh(registro)

    return registro