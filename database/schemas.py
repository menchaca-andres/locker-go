from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class TipoSerieEnum(str, Enum):
    taylor_seno = "taylor_seno"
    taylor_coseno = "taylor_coseno"
    trig_seno = "trig_seno"
    trig_coseno = "trig_coseno"
    trig_tangente = "trig_tangente"
    trig_arcoseno = "trig_arcoseno"
    trig_arcocoseno = "trig_arcocoseno"
    trig_arcotangente = "trig_arcotangente"


class CalculoRequest(BaseModel):
    nombre_usuario: str
    tipo_serie: TipoSerieEnum
    valor_x: float
    n_terminos: int = Field(gt=0, le=200)  # evita que pidan 0 o miles de términos


class CalculoResponse(BaseModel):
    n_registro: int
    valor_aproximado: float
    valor_real: float
    error_absoluto: float
    error_relativo: Optional[float]
    fecha_calculo: datetime

    class Config:
        from_attributes = True  # permite crear el schema directo desde el modelo SQLAlchemy


class RegistroDetalle(BaseModel):
    """Schema enriquecido para el dashboard — incluye tipo_serie y categoría (flat)."""

    n_registro: int
    tipo_serie: str
    categoria: str
    valor_x: float
    n_terminos: int
    valor_aproximado: float
    valor_real: float
    error_absoluto: float
    error_relativo: Optional[float]
    fecha_calculo: datetime