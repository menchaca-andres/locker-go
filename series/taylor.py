import math


def taylor_seno(x: float, n_terminos: int) -> float:
    """Aproxima sin(x) con la serie de Maclaurin mediante acumulación iterativa."""
    resultado = 0.0
    termino = x
    for k in range(n_terminos):
        resultado += termino
        termino *= -x * x / ((2 * k + 2) * (2 * k + 3))
        if termino == 0.0:
            break
    return resultado


def taylor_coseno(x: float, n_terminos: int) -> float:
    """Aproxima cos(x) con la serie de Maclaurin mediante acumulación iterativa."""
    resultado = 0.0
    termino = 1.0
    for k in range(n_terminos):
        resultado += termino
        termino *= -x * x / ((2 * k + 1) * (2 * k + 2))
        if termino == 0.0:
            break
    return resultado