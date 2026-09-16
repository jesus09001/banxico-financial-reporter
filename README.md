# Automatización de Reportes Financieros Banxico

![Python](https://img.shields.io/badge/Python-3.9%2B-yellow?style=flat&logo=python)
![API](https://img.shields.io/badge/Banxico_API-SIE-blue?style=flat)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

Pipeline en Python para consultar el tipo de cambio USD/MXN desde la API del Sistema de Información Económica (SIE) de Banco de México, calcular indicadores financieros y generar reportes ejecutivos en Excel y PDF.

## Funcionalidades

- Consulta de series de Banxico mediante API REST.
- Limpieza y validación de fechas y valores numéricos.
- Variación diaria y mensual por fecha calendario.
- Promedios móviles de 30 y 90 días.
- Volatilidad anualizada de 30 días.
- KPIs anuales: actual, máximo, mínimo y promedio.
- Libro Excel con resumen ejecutivo, histórico y gráfica.
- PDF ejecutivo de una página con KPIs, lectura ejecutiva, tabla y tendencia.
- Configuración mediante variables de entorno sin guardar credenciales en el código.

## Vista previa

El pipeline genera dos entregables ejecutivos:

- [Reporte Excel](output/reporte_financiero.xlsx): resumen ejecutivo, histórico y gráfica.
- [Reporte PDF](output/reporte_financiero.pdf): dashboard de una página con KPIs, lectura ejecutiva y tendencia.

Los archivos de `output/` son generados localmente y están excluidos por `.gitignore` para evitar publicar reportes desactualizados o datos derivados.

## Requisitos

- Windows, macOS o Linux.
- Python 3.9 o posterior.
- Un token de acceso para la API SIE de Banxico.

## Instalación

Desde la carpeta del proyecto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

En macOS o Linux, activa el entorno con:

```bash
source .venv/bin/activate
```

## Configuración

1. Copia la plantilla:

```powershell
Copy-Item .env.example .env
```

2. Edita `.env` y coloca tu token real:

```env
BANXICO_TOKEN=TU_TOKEN_REAL
BANXICO_SERIES_ID=SF63528
BANXICO_FECHA_INICIO=2022-01-01
```

El archivo `.env` está excluido por `.gitignore`. Nunca publiques el token en el repositorio, código fuente, capturas o mensajes.

## Ejecución

```powershell
python main.py
```

El pipeline crea las carpetas necesarias y genera:

- `output/reporte_financiero.xlsx`
- `output/reporte_financiero.pdf`

La consola muestra la serie consultada, periodo, registros procesados, fecha de corte, rutas y duración.

## Estructura

```text
Automatizacion/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── main.py
├── data/
├── output/
├── src/
│   ├── banxico_client.py
│   ├── data_processor.py
│   ├── excel_exporter.py
│   └── pdf_generator.py
└── tests/                 # reservado para pruebas automatizadas
```

## Indicadores

- **Variación diaria:** cambio porcentual respecto a la observación anterior.
- **Variación mensual:** comparación contra la última observación disponible aproximadamente un mes antes. Los primeros registros quedan vacíos si no existe información histórica suficiente.
- **MA 30/90 días:** promedio móvil basado en ventanas de días calendario.
- **Volatilidad 30 días:** desviación estándar de variaciones diarias, anualizada con `sqrt(252)`.

## Seguridad y limpieza

Los archivos `.env`, reportes, cachés de Python y archivos temporales de Excel están excluidos mediante `.gitignore`. Si un token fue expuesto anteriormente, revócalo y genera uno nuevo en Banxico.
