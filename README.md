#  Automatización de Reportes Financieros & Dashboard USD/MXN (API Banxico)

![Python](https://img.shields.io/badge/Python-3.9+-yellow?style=flat&logo=python)
![Banxico API](https://img.shields.io/badge/Banxico_API-SIE-blue)
![Power BI](https://img.shields.io/badge/Power_BI-Dashboard-F2C811?style=flat&logo=powerbi)
![Pandas](https://img.shields.io/badge/Pandas-Data_Analysis-150458?style=flat&logo=pandas)
![License](https://img.shields.io/badge/License-MIT-green)

Pipeline de ingeniería de datos en Python que consume la API REST del **Sistema de Información Económica (SIE) de Banco de México**, procesa el tipo de cambio FIX (USD/MXN), calcula indicadores analíticos de volatilidad y tendencias, y genera reportes ejecutivos automatizados en **Excel**, **PDF** y un **Dashboard Interactivo en Power BI**.

---

##  Funcionalidades Clave

- **Ingesta Automatizada desde API REST**: Consulta controlada de la serie oficial `SF63528` (Tipo de cambio FIX) de Banxico.
- **Procesamiento & Validación en Pandas**: Limpieza, conversión nativa a `datetime`, ordenamiento cronológico y manejo defensivo de valores nulos.
- **Indicadores Financieros & Análisis Cuantitativo**:
  - Variación diaria (%) respecto a la jornada anterior.
  - Variación mensual comparada contra la observación equivalente del mes previo.
  - Promedios móviles de **30 días** (corto plazo) y **90 días** (mediano plazo).
  - Volatilidad acumulada de 30 días anualizada mediante el factor $\sqrt{252}$.
  - Resumen anual de KPIs (Tipo de Cambio actual, máximo, mínimo y promedio).
- **Reporte Corporativo en Excel (`openpyxl`)**: Libro `.xlsx` formateado con pestañas de *Resumen Ejecutivo* e *Histórico*, cuadrícula activa, formatos de moneda (`$#,##0.0000`) y ancho de columnas autoajustado.
- **Reporte Ejecutivo PDF (`ReportLab`)**: Documento estático de una página con diseño limpio, tarjetas de resumen, tabla de últimos registros y pie institucional.
- **Dashboard Interactivo en Power BI (`.pbix`)**: Pantalla ejecutiva única de alto impacto optimizada para la toma de decisiones.
- **Seguridad en Credenciales**: Uso de variables de entorno mediante `.env` sin exponer tokens privados en el código.

---

##  Dashboard Ejecutivo en Power BI (1 Página)

El proyecto incluye un dashboard interactivo estructurado en **una sola pantalla ejecutiva**, diseñado para responder preguntas estratégicas de negocio de un vistazo:

```
+-----------------------------------------------------------------------------------+
|   Dashboard Financiero: Tipo de Cambio USD/MXN (Banxico)                         |
+-----------------------------------------------------------------------------------+
| [TC Actual]  [Var Diaria %]  [Mínimo Periodo]  [Máximo Periodo]  [Volatilidad 30D]  |
+-------------------------------------------------+---------------------------------+
|                                                 |                                 |
|  1. Gráfico de Evolución y Promedios Móviles    |  2. Gráfico de Promedio Mensual |
|     (Serie FIX vs. MA 30D vs. MA 90D)           |     (Tendencia interanual)      |
|                                                 |                                 |
+-------------------------------------------------+---------------------------------+
|                                                 |                                 |
|  3. Tabla de Últimos Registros Observados       |  Filtros / Segmentadores:       |
|     (Fecha, TC, Var %, MA 30D)                  |  - Rango de Fechas              |
|                                                 |  - Selector de Año (2022-2026)  |
+-------------------------------------------------+---------------------------------+
```

### Componentes Visuales y Preguntas de Negocio

1. **Gráfico de Evolución del Tipo de Cambio (`linea-tendencia`)**:
   - Muestra el Tipo de Cambio diario junto con la Media Móvil de 30 días y la Media Móvil de 90 días.
   - *Responde*: ¿El peso está en tendencia de apreciación o depreciación? ¿Coincide el impulso de corto plazo con la tendencia de 90 días?
2. **Gráfico de Promedio Mensual (`promedio-mensual`)**:
   - Comportamiento mensual agregado (`YYYY-MM`) para identificar estacionalidad.
   - *Responde*: ¿Qué meses presentaron las mayores presiones cambiarias y cómo se compara entre distintos años?
3. **Tabla de Últimos Registros (`ultimos-registros`)**:
   - Detalle operativo descendente con Fecha, Tipo de Cambio, Variación Diaria y Promedio Móvil 30D.
   - *Responde*: ¿Cuál es la lectura de las últimas observaciones disponibles y el sesgo más reciente?
4. **Tarjetas KPI Ejecutivas**:
   - `kpi-tc-actual`: Tipo de cambio FIX más reciente.
   - `kpi-var-diaria`: Porcentaje de variación respecto al día anterior.
   - `kpi-minimo`: Valor mínimo del periodo seleccionado.
   - `kpi-maximo`: Valor máximo alcanzado en el rango filtrado.
   - `kpi-promedio`: Tipo de cambio promedio del periodo.
   - `kpi-volatilidad`: Nivel de riesgo e incertidumbre acumulado a 30 días.
5. **Segmentadores Dinámicos**:
   - `filtro-fecha`: Filtro interactivo por intervalo de fechas.
   - `filtro-año`: Selector multianual para análisis comparativo.

---

##  Estructura del Repositorio

```text
banxico-financial-reporter/
├── .env.example                     # Plantilla segura para variables de entorno
├── .gitignore                       # Reglas de exclusión (caché, .env, reportes)
├── README.md                        # Documentación ejecutiva del proyecto
├── requirements.txt                 # Lista de dependencias con versiones fijas
├── main.py                          # Orquestador principal del pipeline
├── data/
│   └── reporte_financiero.xlsx      # Salida formateada en Excel (openpyxl)
├── output/
│   ├── reporte_financiero.pdf       # Reporte ejecutivo en PDF (ReportLab)
│   └── dashboard_preview.png        # Captura de pantalla del Dashboard Power BI
├── dashboard/
│   └── Dashboard_Financiero.pbix    # Modelo y Dashboard interactivo en Power BI
├── src/
   ├── banxico_client.py            # Cliente HTTP para API SIE con reintentos y logging
   ├── data_processor.py            # Módulo de transformación y cálculo de métricas
   ├── excel_exporter.py            # Exportador formateado a Excel
   └── pdf_generator.py             # Generador y maquetador del PDF

```

---

##  Requisitos e Instalación

### Requisitos Previos
- Python 3.9 o superior.
- Token de acceso a la API SIE de Banco de México ([Solicitar token aquí](https://www.banxico.org.mx/SieAPIRest/service/v1/)).

### Instalación del Entorno Virtual

**En Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**En macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## ⚙️ Configuración

1. Copia la plantilla `.env.example` para crear tu archivo `.env` local:
   ```bash
   cp .env.example .env
   ```
2. Edita `.env` e ingresa tu token real de Banxico:
   ```env
   BANXICO_TOKEN=TU_TOKEN_REAL_AQUI
   BANXICO_SERIES_ID=SF63528
   BANXICO_FECHA_INICIO=2022-01-01
   ```

*Nota: El archivo `.env` está protegido en `.gitignore`. Nunca publiques credenciales reales en GitHub.*

---

##  Ejecución del Pipeline

```bash
python main.py
```

El script ejecutará secuencialmente:
1. Verificación automática de carpetas (`data/`, `output/`).
2. Extracción de datos vía API REST de Banxico.
3. Procesamiento de variaciones, medias móviles y volatilidad en Pandas.
4. Exportación del libro Excel en `data/reporte_financiero.xlsx`.
5. Maquetación del PDF ejecutivo en `output/reporte_financiero.pdf`.

---

##  Metodología e Indicadores Financieros

- **Variación Diaria %**: $\frac{TC_t - TC_{t-1}}{TC_{t-1}} \times 100$
- **Variación Mensual %**: Comparación de la observación $TC_t$ contra el registro disponible más cercano un mes atrás ($t - 30d$).
- **Promedios Móviles (30D / 90D)**: Media aritmética móvil calculada sobre ventanas de días calendario para suavizar el ruido bursátil.
- **Volatilidad Anualizada 30D**: Desviación estándar de los retornos diarios multiplicada por la raíz del número de días bursátiles al año ($\sqrt{252}$):
  $$\sigma_{anual} = \sigma_{30d} \times \sqrt{252}$$

---

##  Seguridad y Limpieza

Los archivos `.env`, los reportes binarios generados (`.xlsx`, `.pdf`), cachés de Python (`__pycache__`) y archivos temporales de Excel están excluidos en `.gitignore` para garantizar la privacidad y mantener un repositorio limpio.

---

##  Licencia y Autor

Este proyecto está bajo la Licencia **MIT**.

**Copado Crespo Jesus Adahir**
- **Perfil**: Economista y Científico de Datos especializado en Inteligencia de Negocios, Ingeniería de Datos y MLOps.
- **LinkedIn**: [Jesus Adahir Copado Crespo](https://www.linkedin.com/in/jesus-adahir-copado-crespo-251748294)
- **GitHub**: [jesus09001](https://github.com/jesus09001)
