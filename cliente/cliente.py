#!/usr/bin/env python3
"""
Cliente de consola para la API de SeriesCalc.
Uso: python -m cliente.cliente   (desde la raíz del proyecto)
"""

import json
import sys
import urllib.request
import urllib.parse
import urllib.error
import webbrowser

BASE_URL = "http://localhost:8000"

TIPOS = [
    ("taylor_seno",       "Taylor   — sin(x)"),
    ("taylor_coseno",     "Taylor   — cos(x)"),
    ("trig_seno",         "Trig     — sin(x)"),
    ("trig_coseno",       "Trig     — cos(x)"),
    ("trig_tangente",     "Trig     — tan(x)"),
    ("trig_arcoseno",     "Inversa  — arcsin(x)  [x ∈ [-1, 1]]"),
    ("trig_arcocoseno",   "Inversa  — arccos(x)  [x ∈ [-1, 1]]"),
    ("trig_arcotangente", "Inversa  — arctan(x)  [x ∈ [-1, 1]]"),
]


# ─── HTTP helpers ────────────────────────────────────────────────────────────

def _post(url: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


# ─── UI helpers ──────────────────────────────────────────────────────────────

def hr(char="─", width=58):
    print(char * width)


def banner():
    hr("═")
    print("   ∑  SeriesCalc — Cliente de consola")
    hr("═")


# ─── Acciones ────────────────────────────────────────────────────────────────

def nuevo_calculo():
    print("\n┌─ NUEVO CÁLCULO ────────────────────────────────────┐")
    usuario = input("│  Usuario: ").strip()
    if not usuario:
        print("│  ⚠  Nombre vacío. Cancelado.")
        return

    print("│")
    print("│  Tipos de serie disponibles:")
    for i, (_, label) in enumerate(TIPOS, 1):
        print(f"│    {i:2}. {label}")
    print("│")

    while True:
        raw = input("│  Elegí un tipo [1-8]: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= 8:
            opcion = int(raw)
            break
        print("│  Opción inválida.")

    while True:
        raw = input("│  Valor de x (en radianes): ").strip()
        try:
            x = float(raw)
            break
        except ValueError:
            print("│  Número inválido.")

    while True:
        raw = input("│  Número de términos (1-200): ").strip()
        if raw.isdigit() and 1 <= int(raw) <= 200:
            n = int(raw)
            break
        print("│  Debe ser un entero entre 1 y 200.")

    print("└────────────────────────────────────────────────────")
    print("  Enviando…")

    tipo = TIPOS[opcion - 1][0]
    try:
        resultado = _post(f"{BASE_URL}/calcular", {
            "nombre_usuario": usuario,
            "tipo_serie": tipo,
            "valor_x": x,
            "n_terminos": n,
        })
    except urllib.error.HTTPError as exc:
        try:
            detail = json.loads(exc.read()).get("detail", exc.reason)
        except Exception:
            detail = exc.reason
        print(f"\n  ✗  Error {exc.code}: {detail}\n")
        return
    except Exception as exc:
        print(f"\n  ✗  Sin conexión al servidor: {exc}\n")
        return

    print()
    hr()
    print(f"  Registro #{resultado['n_registro']}   •   {tipo}")
    hr("·")
    print(f"  {'Valor x':<22} {x}")
    print(f"  {'Términos':<22} {n}")
    hr("·")
    print(f"  {'Aproximado':<22} {resultado['valor_aproximado']:.10f}")
    print(f"  {'Real':<22} {resultado['valor_real']:.10f}")
    hr("·")
    print(f"  {'Error absoluto':<22} {resultado['error_absoluto']:.4e}")
    if resultado["error_relativo"] is not None:
        print(f"  {'Error relativo':<22} {resultado['error_relativo'] * 100:.6f} %")
    hr()

    respuesta = input(f"\n  ¿Abrir el dashboard de '{usuario}' en el browser? [s/N] ").strip().lower()
    if respuesta == "s":
        url = f"{BASE_URL}/dashboard/{urllib.parse.quote(usuario)}"
        webbrowser.open(url)
        print(f"  Abriendo → {url}")


def ver_dashboard():
    usuario = input("\n  Nombre de usuario: ").strip()
    if not usuario:
        return
    url = f"{BASE_URL}/dashboard/{urllib.parse.quote(usuario)}"
    webbrowser.open(url)
    print(f"  Abriendo → {url}")


# ─── Menú principal ──────────────────────────────────────────────────────────

def menu():
    banner()
    while True:
        print()
        print("  1. Nuevo cálculo")
        print("  2. Ver dashboard en browser")
        print("  3. Salir")
        print()
        opcion = input("  Opción: ").strip()

        if opcion == "1":
            nuevo_calculo()
        elif opcion == "2":
            ver_dashboard()
        elif opcion == "3":
            print("\n  Hasta luego.\n")
            sys.exit(0)
        else:
            print("  Opción inválida.")


if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        print("\n\n  Interrumpido. Hasta luego.\n")
        sys.exit(0)
