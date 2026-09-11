import math


def trig_arcoseno(x: float, n_terminos: int, detallado: bool = False):
    """Serie de Maclaurin para arcsin(x), válida en [-1, 1]."""
    if not -1 <= x <= 1:
        raise ValueError("arcoseno solo está definido para x en [-1, 1]")
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
        termino *= ((2 * k + 1) ** 2) * (x * x) / ((2 * k + 2) * (2 * k + 3))
        if termino == 0.0:
            break
    if detallado:
        return resultado, iteraciones
    return resultado


def trig_arcocoseno(x: float, n_terminos: int, detallado: bool = False):
    if detallado:
        res_asin, iters_asin = trig_arcoseno(x, n_terminos, detallado=True)
        resultado = (math.pi / 2) - res_asin
        iteraciones = []
        for it in iters_asin:
            k = it["n_iteracion"]
            val_acum = (math.pi / 2) - it["valor_acumulado"]
            val_term = ((math.pi / 2) - it["valor_termino"]) if k == 1 else -it["valor_termino"]
            iteraciones.append({
                "n_iteracion": k,
                "valor_termino": val_term,
                "valor_acumulado": val_acum,
            })
        return resultado, iteraciones
    return (math.pi / 2) - trig_arcoseno(x, n_terminos)


def trig_arcotangente(x: float, n_terminos: int, detallado: bool = False):
    """Serie de Maclaurin para arctan(x), converge bien en [-1, 1]."""
    if not -1 <= x <= 1:
        raise ValueError("Esta serie converge de forma confiable solo en [-1, 1]")
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
        termino *= -x * x * (2 * k + 1) / (2 * k + 3)
        if termino == 0.0:
            break
    if detallado:
        return resultado, iteraciones
    return resultado