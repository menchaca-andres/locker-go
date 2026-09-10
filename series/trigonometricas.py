from series.taylor import taylor_seno, taylor_coseno


def trig_seno(x: float, n_terminos: int) -> float:
    return taylor_seno(x, n_terminos)


def trig_coseno(x: float, n_terminos: int) -> float:
    return taylor_coseno(x, n_terminos)


def trig_tangente(x: float, n_terminos: int) -> float:
    """Aproxima tan(x) como el cociente sin(x)/cos(x), cada uno vía su serie."""
    seno_aprox = taylor_seno(x, n_terminos)
    coseno_aprox = taylor_coseno(x, n_terminos)
    if abs(coseno_aprox) < 1e-10:
        raise ValueError("La aproximación de coseno es cercana a 0; tangente indefinida aquí")
    return seno_aprox / coseno_aprox