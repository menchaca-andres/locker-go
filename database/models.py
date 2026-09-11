from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, timezone

Base = declarative_base()


class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    nombre_usuario = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=True, index=True)
    password_hash = Column(String, nullable=True)
    salt = Column(String, nullable=True)
    session_token = Column(String, nullable=True, index=True)
    fecha_registro = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    registros = relationship("RegistroCalculo", back_populates="usuario")


class TipoSerie(Base):
    __tablename__ = "tipos_serie"

    id_tipo = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)       # 'Taylor seno', 'Trig tangente', etc.
    categoria = Column(String, nullable=False)    # 'Taylor' | 'Trigonometrica' | 'Trig_inversa'

    registros = relationship("RegistroCalculo", back_populates="tipo_serie")


class RegistroCalculo(Base):
    __tablename__ = "registros_calculo"

    n_registro = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    id_tipo = Column(Integer, ForeignKey("tipos_serie.id_tipo"), nullable=False)

    valor_x = Column(Float, nullable=False)
    n_terminos = Column(Integer, nullable=False)
    valor_aproximado = Column(Float, nullable=False)
    valor_real = Column(Float, nullable=False)
    error_absoluto = Column(Float, nullable=False)
    error_relativo = Column(Float, nullable=True)
    fecha_calculo = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    usuario = relationship("Usuario", back_populates="registros")
    tipo_serie = relationship("TipoSerie", back_populates="registros")
    iteraciones = relationship("IteracionCalculo", back_populates="registro", cascade="all, delete-orphan", order_by="IteracionCalculo.n_iteracion")


class IteracionCalculo(Base):
    __tablename__ = "iteraciones_calculo"

    id_iteracion = Column(Integer, primary_key=True, autoincrement=True)
    n_registro = Column(Integer, ForeignKey("registros_calculo.n_registro"), nullable=False)
    n_iteracion = Column(Integer, nullable=False)
    valor_termino = Column(Float, nullable=False)
    valor_acumulado = Column(Float, nullable=False)
    error_absoluto = Column(Float, nullable=False)
    error_relativo = Column(Float, nullable=True)

    registro = relationship("RegistroCalculo", back_populates="iteraciones")