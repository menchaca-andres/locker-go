from sqlalchemy.orm import Session
from database.models import TipoSerie

# Catálogo completo — fuente de verdad para los tipos de serie.
# categoria: "Taylor" | "Trigonometrica" | "Trig_inversa"
CATALOGO: list[dict] = [
    {"nombre": "taylor_seno",       "categoria": "Taylor"},
    {"nombre": "taylor_coseno",     "categoria": "Taylor"},
    {"nombre": "trig_seno",         "categoria": "Trigonometrica"},
    {"nombre": "trig_coseno",       "categoria": "Trigonometrica"},
    {"nombre": "trig_tangente",     "categoria": "Trigonometrica"},
    {"nombre": "trig_arcoseno",     "categoria": "Trig_inversa"},
    {"nombre": "trig_arcocoseno",   "categoria": "Trig_inversa"},
    {"nombre": "trig_arcotangente", "categoria": "Trig_inversa"},
]


def seed_tipos(db: Session) -> None:
    """Inserta los tipos de serie que aún no existen. Es idempotente."""
    nombres_existentes = {t.nombre for t in db.query(TipoSerie.nombre).all()}
    nuevos = [
        TipoSerie(nombre=entry["nombre"], categoria=entry["categoria"])
        for entry in CATALOGO
        if entry["nombre"] not in nombres_existentes
    ]
    if nuevos:
        db.add_all(nuevos)
        db.commit()
