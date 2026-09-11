# SeriesCalc — Calculadora de Series Matemáticas & Dashboard

Aplicación **Cliente-Servidor** para el cálculo numérico, aproximación y análisis de error de series matemáticas (Taylor, Trigonométricas directas e inversas), con persistencia relacional, visualización en tiempo real con **Chart.js**, renderizado de fórmulas con **KaTeX** y cliente CLI interactivo.

---

## Inicio Rápido

### 1. Requisitos Previos
- Python 3.9+
- Entorno virtual configurado

### 2. Instalación y Puesta en Marcha

```bash
# 1. Clonar el repositorio y entrar al directorio
git clone https://github.com/tu-usuario/locker-go.git
cd locker-go

# 2. Crear y activar entorno virtual
python3 -m venv venv
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Iniciar el servidor
uvicorn main:app --reload --port 8000
```

Accedé a la aplicación en:
- **Interfaz Web**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Documentación Swagger API**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Arquitectura del Sistema

```mermaid
graph TD
    subgraph Clientes
        WEB["Frontend Web (HTML / CSS / JS / KaTeX)"]
        CLI["Cliente Terminal (cliente.py)"]
    end

    subgraph Servidor FastAPI
        API["API REST Router (/api/calcular)"]
        DASH_ROUTER["Dashboard Router (/dashboard/:user)"]
        ENGINE["Motor de Series Numéricas"]
    end

    subgraph Persistencia
        DB[("Base de Datos (SQLite / Supabase)")]
    end

    WEB -->|HTTP / JSON| API
    WEB -->|HTTP GET| DASH_ROUTER
    CLI -->|HTTP / JSON| API
    API --> ENGINE
    API --> DB
    DASH_ROUTER --> DB
```

---

## Catálogo de Series Matemáticas

El sistema soporta 3 categorías de series matemáticas según el diseño del modelo:

| Categoría | Serie | Ecuación Matemática (Sumatoria) | Dominio / Restricción |
|---|---|---|---|
| **Taylor** | `taylor_seno` | $\sum_{k=0}^{n-1} \frac{(-1)^k x^{2k+1}}{(2k+1)!} = x - \frac{x^3}{3!} + \frac{x^5}{5!} - \dots$ | $x \in \mathbb{R}$ |
| **Taylor** | `taylor_coseno` | $\sum_{k=0}^{n-1} \frac{(-1)^k x^{2k}}{(2k)!} = 1 - \frac{x^2}{2!} + \frac{x^4}{4!} - \dots$ | $x \in \mathbb{R}$ |
| **Trigonométrica** | `trig_seno` | $\sum_{k=0}^{n-1} \frac{(-1)^k x^{2k+1}}{(2k+1)!}$ (Directa Maclaurin) | $x \in [-\pi, \pi]$ |
| **Trigonométrica** | `trig_coseno` | $\sum_{k=0}^{n-1} \frac{(-1)^k x^{2k}}{(2k)!}$ (Directa Maclaurin) | $x \in [-\pi, \pi]$ |
| **Trigonométrica** | `trig_tangente` | $\frac{\text{seno\_aprox}(x)}{\text{coseno\_aprox}(x)}$ (Cociente de series) | $x \neq \frac{\pi}{2} + k\pi$ |
| **Trig. Inversa** | `trig_arcoseno` | $\sum_{k=0}^{n-1} \frac{(2k)!}{4^k (k!)^2 (2k+1)} x^{2k+1} = x + \frac{1}{6}x^3 + \frac{3}{40}x^5 + \dots$ | $x \in [-1, 1]$ |
| **Trig. Inversa** | `trig_arcocoseno` | $\frac{\pi}{2} - \text{arcoseno\_aprox}(x)$ (Identidad complementaria) | $x \in [-1, 1]$ |
| **Trig. Inversa** | `trig_arcotangente` | $\sum_{k=0}^{n-1} \frac{(-1)^k x^{2k+1}}{2k+1} = x - \frac{x^3}{3} + \frac{x^5}{5} - \dots$ | $x \in [-1, 1]$ |

---

## Modelo de Base de Datos

La persistencia relacional está implementada con **SQLAlchemy ORM** (compatible con SQLite local y PostgreSQL / Supabase en la nube):

```
┌──────────────────┐       ┌──────────────────────┐       ┌──────────────────┐
│     usuarios     │       │  registros_calculo   │       │   tipos_serie    │
├──────────────────┤       ├──────────────────────┤       ├──────────────────┤
│ id_usuario (PK)  │───<   │ n_registro (PK)      │   >───│ id_tipo (PK)     │
│ nombre_usuario   │       │ id_usuario (FK)      │       │ nombre           │
│ fecha_registro   │       │ id_tipo (FK)         │       │ categoria        │
└──────────────────┘       │ valor_x              │       └──────────────────┘
                           │ n_terminos           │
                           │ valor_aproximado     │
                           │ valor_real           │
                           │ error_absoluto       │
                           │ error_relativo       │
                           │ fecha_calculo        │
                           └──────────────────────┘
```

---

## Funcionalidades Principales

### 1. Calculadora Interactiva Web
- Renderizado dinámico de fórmulas matemáticas con **KaTeX**.
- Selector de presets para ángulos clave ($\pi/6, \pi/4, \pi/3, \pi/2$).
- Cálculo instantáneo con visualización de error absoluto y relativo.

### 2. Dashboard Analítico en Tiempo Real (Doble Nivel de Detalle)

El dashboard resuelve tanto el **análisis granular registro por registro** como la **visión ejecutiva resumida**:

#### A. Nivel Granular — Análisis por Cálculo Individual
- **Gráfico de Líneas (Aproximado vs. Real)**: El eje horizontal mapea cada cálculo individual (`#1, #2, ... #N`), permitiendo comparar la precisión y convergencia obtenida en cada operación matemática específica.
- **Gráfico de Barras Logarítmico (Error Absoluto por Registro)**: Representa el error individual de cada cálculo en escala logarítmica ($10^0$ a $10^{-16}$). Esto evita que errores microscópicos se aplanen visualmente a cero y permite auditar la estabilidad numérica de cada ejecución.
- **Tabla Histórica Paginada (20 por página)**: Inspección registro a registro con parámetros de entrada ($x$, términos $n$), valor aproximado (8 decimales), valor real, error absoluto y error relativo porcentual.

#### B. Nivel Ejecutivo — Resumen y Métricas Agregadas
- **Tarjetas KPI**: Resumen superior instantáneo con *Total de cálculos*, *Error promedio acumulado*, *Serie más utilizada* y *Timestamp del último cálculo*.
- **Gráfico de Dona**: Distribución porcentual y volumen de uso agrupado por tipo de serie (Taylor, trigonométricas, inversas).
- **Sondeo en Tiempo Real**: Actualización automática cada 2 segundos vía polling asíncrono sin recarga de página.

### 3. Cliente CLI por Terminal
Incluye un cliente de consola interactivo en Python:

```bash
python cliente/cliente.py
```

---

## Endpoints de la API REST

| Método | Endpoint | Descripción |
|---|---|---|
| `POST` | `/api/calcular` | Registra y calcula una aproximación matemática |
| `GET` | `/api/historial/{usuario}` | Obtiene todos los cálculos asociados a un usuario |
| `GET` | `/api/tipos` | Lista el catálogo de series disponibles |
| `GET` | `/dashboard/{usuario}` | Vista HTML del dashboard para el usuario indicado |

---

## Pruebas Automatizadas

El proyecto cuenta con una suite completa de pruebas unitarias y de integración con **pytest**:

```bash
# Ejecutar todas las pruebas
pytest
```