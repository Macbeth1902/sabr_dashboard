# 📈 Valuación SABR — TIIE de Fondeo

Dashboard interactivo en Streamlit para la valuación de swaptions europeos sobre la
TIIE de Fondeo mediante el modelo de volatilidad estocástica SABR.

**Proyecto Final — Seminario Avanzado de Derivados · Facultad de Ciencias, UNAM · 2026**

---

## Estructura del proyecto

```
sabr_dashboard/
│
├── app.py                        ← Portada (página de inicio)
│
├── pages/
│   ├── 1_Introduccion.py         ← Marco teórico y fundamentos
│   ├── 2_Modelo_SABR.py          ← Dinámica, parámetros y fórmula de Hagan
│   ├── 3_Curva_OIS.py            ← Bootstrapping directo (390 nodos MexDer)
│   ├── 4_Calibracion_SABR.py     ← Calibración SABR + superficie 3D
│   └── 5_Valuacion_Swaption.py   ← Calculadora interactiva
│   └── 6_Conclusiones.py         ← Conclusiones e interpretaciones
│
├── core/
│   ├── __init__.py
│   ├── data.py                   ← Datos de mercado (390 nodos + VCUB)
│   ├── bootstrap.py              ← Bootstrapping OIS directo
│   ├── sabr.py                   ← Fórmula Hagan et al. + calibración anclada
│   ├── valuation.py              ← Black-76 + valuación de swaptions
│   ├── charts.py                 ← Todas las gráficas Plotly
│   └── state.py                  ← Cálculos cacheados con st.cache_data
│
├── assets/
│   └── style.css                 ← CSS personalizado (dark theme)
│
├── .streamlit/
│   └── config.toml               ← Tema Streamlit (dark, teal accent)
│
├── requirements.txt
└── README.md
```

---

## Instalación y ejecución

### 1. Clonar o copiar el directorio

```bash
# Si descargaste el zip, extráelo. Luego:
cd sabr_dashboard
```

### 2. Crear un entorno virtual (recomendado)

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar el dashboard

```bash
streamlit run app.py
```

El navegador se abrirá automáticamente en `http://localhost:8501`.

---

## Navegación

| Página | Contenido |
|--------|-----------|
| **Portada** | Título, integrantes, resumen ejecutivo |
| **Introducción** | TIIE de Fondeo, swaptions, Black-76, smile |
| **Modelo SABR** | Dinámica estocástica, parámetros, fórmula, calibración |
| **Curva OIS** | Bootstrapping directo, gráficas, tabla de nodos |
| **Calibración SABR** | Heatmap VCUB, parámetros por tenor, superficie 3D, sensibilidad |
| **Valuación Swaption** | Calculadora interactiva (tenor + strike libres) |
| **Conclusiones** | Hallazgos, limitaciones, extensiones, referencias |

---

## Fuentes de datos

| Dato | Fuente |
|------|--------|
| 390 precios de liquidación (curva OIS) | Boletín MexDer/Asigna, 20-may-2026 |
| Volatilidades implícitas (VCUB) | Bloomberg: *MXN TIIE-F RFR BVOL Cube*, 20-may-2026 |

---

## Dependencias

| Paquete | Uso |
|---------|-----|
| `streamlit` | Framework del dashboard |
| `numpy` | Cálculo matricial y numérico |
| `scipy` | Optimización (`brentq`, `least_squares`) |
| `pandas` | Tablas y dataframes |
| `plotly` | Gráficas interactivas (2D y 3D) |

---

## Notas técnicas

- **Caching:** La curva OIS y la calibración SABR se cachean con `@st.cache_data`.
  La primera carga puede tardar ~10 s; las siguientes son instantáneas.
- **β = 1 (log-normal):** Fijo para todos los tenores, coherente con el régimen
  de tasas mexicanas positivas y elevadas.
- **Interpolación:** Los parámetros SABR se interpolan linealmente en el eje de
  tenores para valores intermedios (e.g., 7.5A entre 7Yr y 8Yr).
- **tex = 1 año:** El vencimiento de la opción está fijo, igual que en la vista
  de la matriz VCUB utilizada.
