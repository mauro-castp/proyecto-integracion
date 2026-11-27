"""
colas.py — Teoría de colas M/M/1 y M/M/c (Erlang C) para la fila de pedidos de un microhub. Funciones puras, sin bases de datos.

Un microhub es una fila: los pedidos llegan al azar (Poisson, tasa λ por hora) y c operadores los preparan, cada uno a un ritmo μ por hora
con tiempos exponenciales. Con c = 1 es M/M/1; con c > 1, M/M/c. La fila solo es estable si ρ = λ / (c·μ) < 1; si no, crece sin límite.

  a  = λ / μ                       carga ofrecida (operadores ocupados en promedio)
  ρ  = a / c                       utilización de cada operador
  P0 = [ Σ_{n=0}^{c-1} aⁿ/n!  +  aᶜ / (c!·(1-ρ)) ]⁻¹        probabilidad de que no haya nadie
  C  = aᶜ / (c!·(1-ρ)) · P0        probabilidad de esperar (Erlang C); con c = 1, C = ρ
  Lq = C · ρ / (1-ρ)               pedidos esperando        Wq = Lq / λ      tiempo en la fila
  W  = Wq + 1/μ                    tiempo total             L  = λ · W       pedidos en el sistema (Little)

Con c = 1 las fórmulas dan las de M/M/1: P0 = 1-ρ, Lq = ρ²/(1-ρ), Wq = ρ/(μ-λ), W = 1/(μ-λ).
Los términos aⁿ/n! se calculan uno a partir del anterior (sin factoriales grandes), así que no se desborda con c = 50.
"""
import math

MAX_SERVIDORES = 50


def mmc(llegadas_hora, servicio_hora, servidores):
    """Indicadores de una fila M/M/c (M/M/1 si servidores = 1). Tiempos en minutos. Si la fila no es estable, las esperas son None."""
    if llegadas_hora <= 0 or servicio_hora <= 0:
        raise ValueError("Las tasas de llegada y de servicio deben ser mayores que cero.")
    if not 1 <= servidores <= MAX_SERVIDORES:
        raise ValueError(f"Los servidores deben estar entre 1 y {MAX_SERVIDORES}.")
    lam, mu, c = float(llegadas_hora), float(servicio_hora), int(servidores)
    a = lam / mu
    rho = a / c
    base = {"modelo": "M/M/1" if c == 1 else "M/M/c", "llegadas_hora": lam, "servicio_hora": mu, "servidores": c,
            "carga_ofrecida": round(a, 4), "utilizacion_pct": round(100 * rho, 2), "estable": rho < 1}
    if rho >= 1:
        return {**base, "p0": None, "prob_esperar": 1.0, "lq": None, "l": None, "wq_min": None, "w_min": None}
    termino, suma = 1.0, 1.0                       # n = 0
    for n in range(1, c):
        termino *= a / n                           # aⁿ/n!
        suma += termino
    ultimo = termino * a / c                       # aᶜ/c!
    cola = ultimo / (1 - rho)
    p0 = 1 / (suma + cola)
    prob = cola * p0
    lq = prob * rho / (1 - rho)
    wq = lq / lam
    w = wq + 1 / mu
    return {**base, "p0": round(p0, 6), "prob_esperar": round(prob, 6), "lq": round(lq, 4), "l": round(lam * w, 4),
            "wq_min": round(60 * wq, 3), "w_min": round(60 * w, 3)}


def servidores_minimos(llegadas_hora, servicio_hora, espera_objetivo_min):
    """El menor número de operadores con fila estable y espera promedio en fila (Wq) ≤ objetivo. None si ni con el máximo se logra."""
    inicio = max(1, math.floor(llegadas_hora / servicio_hora) + 1)       # el primero estable
    for c in range(inicio, MAX_SERVIDORES + 1):
        r = mmc(llegadas_hora, servicio_hora, c)
        if r["estable"] and r["wq_min"] <= espera_objetivo_min:
            return c
    return None


def tabla(llegadas_hora, servicio_hora, espera_objetivo_min, desde=None, filas=6):
    """Cómo cambian la espera y la utilización con más operadores, desde el primero estable (o `desde`)."""
    inicio = desde or max(1, math.floor(llegadas_hora / servicio_hora) + 1)
    out = []
    for c in range(inicio, min(inicio + filas, MAX_SERVIDORES + 1)):
        r = mmc(llegadas_hora, servicio_hora, c)
        out.append({"servidores": c, "utilizacion_pct": r["utilizacion_pct"], "prob_esperar": r["prob_esperar"], "lq": r["lq"],
                    "wq_min": r["wq_min"], "w_min": r["w_min"], "cumple": bool(r["estable"] and r["wq_min"] <= espera_objetivo_min)})
    return out
