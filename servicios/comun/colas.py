"""
colas.py — Teoría de colas M/M/1 y M/M/c (funciones puras, sin bases de datos).

Modelo: los pedidos llegan al azar (proceso de Poisson, tasa λ por hora), cada persona prepara un pedido en un tiempo exponencial de
media 1/μ horas, hay c personas en paralelo y una sola fila. Con c = 1 es M/M/1; con c > 1, M/M/c (fórmula de Erlang C).

    a  = λ / μ                       carga ofrecida (erlangs)
    ρ  = a / c                       utilización; la cola solo es estable si ρ < 1
    P0 = 1 / ( Σ_{n<c} aⁿ/n!  +  a^c / (c!·(1−ρ)) )     probabilidad de que no haya pedidos
    Pw = a^c / (c!·(1−ρ)) · P0       probabilidad de tener que esperar (Erlang C)
    Lq = Pw · ρ / (1−ρ)              pedidos en fila
    Wq = Lq / λ                      espera en fila
    W  = Wq + 1/μ                    tiempo total en el sistema
    L  = λ · W                       pedidos en el sistema (ley de Little)

Complejidad: O(c) por escenario; buscar las personas necesarias es O(c²) en el peor caso.
"""
MAX_SERVIDORES = 200


def mmc(llegadas_hora, atencion_hora, servidores):
    """Un escenario M/M/c. llegadas_hora = λ, atencion_hora = μ por persona. Si no es estable (ρ ≥ 1), la cola crece sin límite."""
    if llegadas_hora < 0 or atencion_hora <= 0 or servidores < 1:
        raise ValueError("λ ≥ 0, μ > 0 y al menos un servidor.")
    c = int(servidores)
    a = llegadas_hora / atencion_hora
    rho = a / c
    base = {"servidores": c, "modelo": "M/M/1" if c == 1 else "M/M/c", "estable": rho < 1, "utilizacion_pct": round(100 * rho, 1)}
    if rho >= 1:
        return {**base, "prob_vacio": None, "prob_espera": None, "en_cola": None, "en_sistema": None, "espera_cola_min": None,
                "tiempo_sistema_min": None}
    termino, suma = 1.0, 0.0                       # termino = aⁿ/n!, calculado sin factoriales grandes
    for n in range(c):
        suma += termino
        termino *= a / (n + 1)
    cola = termino / (1 - rho)                     # a^c / (c!·(1−ρ))
    p0 = 1 / (suma + cola)
    pw = cola * p0
    lq = pw * rho / (1 - rho)
    wq = lq / llegadas_hora if llegadas_hora else 0.0
    w = wq + 1 / atencion_hora
    return {**base, "prob_vacio": round(p0, 4), "prob_espera": round(pw, 4), "en_cola": round(lq, 3), "en_sistema": round(llegadas_hora * w, 3),
            "espera_cola_min": round(60 * wq, 2), "tiempo_sistema_min": round(60 * w, 2)}


def servidores_necesarios(llegadas_hora, atencion_hora, espera_max_min):
    """El menor número de personas con cola estable y espera media en fila ≤ espera_max_min. None si no basta ni con el máximo."""
    for c in range(1, MAX_SERVIDORES + 1):
        e = mmc(llegadas_hora, atencion_hora, c)
        if e["estable"] and e["espera_cola_min"] <= espera_max_min:
            return c
    return None


def comparar(llegadas_hora, atencion_hora, actual, necesarios, extra=2, tope=12):
    """Escenarios de 1 persona (M/M/1) hasta algunas más de las necesarias, para ver el efecto de sumar personal."""
    ultimo = min(max(actual, necesarios or actual) + extra, max(tope, actual, necesarios or 0))
    return [mmc(llegadas_hora, atencion_hora, c) for c in range(1, ultimo + 1)]


def lectura(actual, necesarios, espera_max_min):
    if not actual["estable"]:
        texto = (f"Con {actual['servidores']} persona(s) los pedidos llegan más rápido de lo que se preparan (utilización "
                 f"{actual['utilizacion_pct']:.0f} %): la fila crece sin límite.")
    else:
        texto = (f"Con {actual['servidores']} persona(s) la utilización es {actual['utilizacion_pct']:.0f} %, se espera en fila "
                 f"{actual['espera_cola_min']:.1f} min y la probabilidad de esperar es {100 * actual['prob_espera']:.0f} %.")
    if necesarios is None:
        return texto + " No se alcanza la meta de espera ni con el máximo de personas."
    return texto + f" Para esperar {espera_max_min:g} min o menos hacen falta {necesarios} persona(s)."
