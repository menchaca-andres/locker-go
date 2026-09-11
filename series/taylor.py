import math


def taylor_seno(x: float, n_terminos: int, detallado: bool = False):
    """Aproxima sin(x) con la serie de Maclaurin mediante acumulación iterativa."""
    resultado = 0.0
    termino = x
    iteraciones = []
    for k in range(n_terminos):
        resultado += termino
        iteraciones.append({
            "n_iteracion": k + 1,
            "valor_termino": termino,
            "valor_acumulado": resultado,
        })
        termino *= -x * x / ((2 * k + 2) * (2 * k + 3))
        if termino == 0.0:
            break
    if detallado:
        return resultado, iteraciones
    return resultado


def taylor_coseno(x: float, n_terminos: int, detallado: bool = False):
    """Aproxima cos(x) con la serie de Maclaurin mediante acumulación iterativa."""
    resultado = 0.0
    termino = 1.0
    iteraciones = []
    for k in range(n_terminos):
        resultado += termino
        iteraciones.append({
            "n_iteracion": k + 1,
            "valor_termino": termino,
            "valor_acumulado": resultado,
        })
        termino *= -x * x / ((2 * k + 1) * (2 * k + 2))
        if termino == 0.0:
            break
    if detallado:
        return resultado, iteraciones
    return resultado