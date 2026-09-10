import math


def trig_arcoseno(x: float, n_terminos: int) -> float:
    """Serie de Maclaurin para arcsin(x), válida en [-1, 1]."""
    if not -1 <= x <= 1:
        raise ValueError("arcoseno solo está definido para x en [-1, 1]")
    resultado = 0.0
    termino = x
    for k in range(n_terminos):
        resultado += termino
        termino *= ((2 * k + 1) ** 2) * (x * x) / ((2 * k + 2) * (2 * k + 3))
        if termino == 0.0:
            break
    return resultado


def trig_arcocoseno(x: float, n_terminos: int) -> float:
    return (math.pi / 2) - trig_arcoseno(x, n_terminos)


def trig_arcotangente(x: float, n_terminos: int) -> float:
    """Serie de Maclaurin para arctan(x), converge bien en [-1, 1]."""
    if not -1 <= x <= 1:
        raise ValueError("Esta serie converge de forma confiable solo en [-1, 1]")
    resultado = 0.0
    termino = x
    for k in range(n_terminos):
        resultado += termino
        termino *= -x * x * (2 * k + 1) / (2 * k + 3)
        if termino == 0.0:
            break
    return resultado