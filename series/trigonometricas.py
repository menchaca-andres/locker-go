from series.taylor import taylor_seno, taylor_coseno


def trig_seno(x: float, n_terminos: int, detallado: bool = False):
    return taylor_seno(x, n_terminos, detallado=detallado)


def trig_coseno(x: float, n_terminos: int, detallado: bool = False):
    return taylor_coseno(x, n_terminos, detallado=detallado)


def trig_tangente(x: float, n_terminos: int, detallado: bool = False):
    """Aproxima tan(x) como el cociente sin(x)/cos(x), cada uno vía su serie."""
    if detallado:
        seno_aprox, seno_iters = taylor_seno(x, n_terminos, detallado=True)
        coseno_aprox, coseno_iters = taylor_coseno(x, n_terminos, detallado=True)
        if abs(coseno_aprox) < 1e-10:
            raise ValueError("La aproximación de coseno es cercana a 0; tangente indefinida aquí")
        
        iteraciones = []
        n_iters = min(len(seno_iters), len(coseno_iters))
        prev_tan = 0.0
        for i in range(n_iters):
            c_val = coseno_iters[i]["valor_acumulado"]
            s_val = seno_iters[i]["valor_acumulado"]
            if abs(c_val) < 1e-12:
                tan_val = float('inf') if s_val >= 0 else float('-inf')
            else:
                tan_val = s_val / c_val
            
            val_term = tan_val - prev_tan if i > 0 else tan_val
            prev_tan = tan_val
            iteraciones.append({
                "n_iteracion": i + 1,
                "valor_termino": val_term,
                "valor_acumulado": tan_val,
            })
        resultado = seno_aprox / coseno_aprox
        return resultado, iteraciones

    seno_aprox = taylor_seno(x, n_terminos)
    coseno_aprox = taylor_coseno(x, n_terminos)
    if abs(coseno_aprox) < 1e-10:
        raise ValueError("La aproximación de coseno es cercana a 0; tangente indefinida aquí")
    return seno_aprox / coseno_aprox