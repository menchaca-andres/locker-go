"""
Unit tests for the series/ math modules.
These tests are pure — no DB, no HTTP, no FastAPI.
"""

import math
import pytest

from series.taylor import taylor_seno, taylor_coseno
from series.trigonometricas import trig_seno, trig_coseno, trig_tangente
from series.trig_inversas import trig_arcoseno, trig_arcocoseno, trig_arcotangente

TOLERANCIA = 1e-6
TOLERANCIA_BORDE = 1e-3  # las series de arcsin/arctan convergen lento cerca de |x|=1
N = 15       # términos para valores centrales del dominio
N_BORDE = 50 # términos para valores cerca de |x|=0.9


# ---------------------------------------------------------------------------
# Taylor — seno
# ---------------------------------------------------------------------------
class TestTaylorSeno:
    @pytest.mark.parametrize("x", [0, math.pi / 6, math.pi / 4, math.pi / 2, math.pi])
    def test_aproximacion(self, x: float):
        assert abs(taylor_seno(x, N) - math.sin(x)) < TOLERANCIA

    def test_un_termino_es_x(self):
        # Con 1 término la serie de sin es simplemente x
        assert taylor_seno(1.0, 1) == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# Taylor — coseno
# ---------------------------------------------------------------------------
class TestTaylorCoseno:
    @pytest.mark.parametrize("x", [0, math.pi / 6, math.pi / 4, math.pi / 2, math.pi])
    def test_aproximacion(self, x: float):
        assert abs(taylor_coseno(x, N) - math.cos(x)) < TOLERANCIA

    def test_un_termino_es_uno(self):
        # Con 1 término la serie de cos es 1
        assert taylor_coseno(0.5, 1) == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# Trigonométricas (wrappers)
# ---------------------------------------------------------------------------
class TestTrigonometricas:
    def test_seno_delega_en_taylor(self):
        x = 0.7
        assert trig_seno(x, N) == pytest.approx(taylor_seno(x, N))

    def test_coseno_delega_en_taylor(self):
        x = 0.7
        assert trig_coseno(x, N) == pytest.approx(taylor_coseno(x, N))

    @pytest.mark.parametrize("x", [0, 0.5, 1.0])
    def test_tangente(self, x: float):
        assert abs(trig_tangente(x, N) - math.tan(x)) < TOLERANCIA

    def test_tangente_indefinida_lanza_error(self):
        # Cerca de pi/2 la serie es numéricamente inestable.
        # Con pocos términos el coseno aproximado cae bajo el epsilon → ValueError.
        # Con muchos términos hay overflow antes → también falla de forma controlada.
        with pytest.raises((ValueError, OverflowError)):
            trig_tangente(math.pi / 2, 30)


# ---------------------------------------------------------------------------
# Inversas
# ---------------------------------------------------------------------------
class TestTrigInversas:
    @pytest.mark.parametrize("x,n,tol", [
        (-0.9, N_BORDE, TOLERANCIA_BORDE),
        (-0.5, N, TOLERANCIA),
        (0,    N, TOLERANCIA),
        (0.5,  N, TOLERANCIA),
        (0.9,  N_BORDE, TOLERANCIA_BORDE),
    ])
    def test_arcoseno(self, x: float, n: int, tol: float):
        assert abs(trig_arcoseno(x, n) - math.asin(x)) < tol

    def test_arcoseno_fuera_dominio(self):
        with pytest.raises(ValueError):
            trig_arcoseno(1.5, N)

    @pytest.mark.parametrize("x,n,tol", [
        (-0.9, N_BORDE, TOLERANCIA_BORDE),
        (-0.5, N, TOLERANCIA),
        (0,    N, TOLERANCIA),
        (0.5,  N, TOLERANCIA),
        (0.9,  N_BORDE, TOLERANCIA_BORDE),
    ])
    def test_arcocoseno(self, x: float, n: int, tol: float):
        assert abs(trig_arcocoseno(x, n) - math.acos(x)) < tol

    @pytest.mark.parametrize("x,n,tol", [
        (-0.9, N_BORDE, TOLERANCIA_BORDE),
        (-0.5, N, TOLERANCIA),
        (0,    N, TOLERANCIA),
        (0.5,  N, TOLERANCIA),
        (0.9,  N_BORDE, TOLERANCIA_BORDE),
    ])
    def test_arcotangente(self, x: float, n: int, tol: float):
        assert abs(trig_arcotangente(x, n) - math.atan(x)) < tol

    def test_arcotangente_fuera_dominio(self):
        with pytest.raises(ValueError):
            trig_arcotangente(1.5, N)
