from numbers import Real
from pathlib import Path
from typing import Mapping

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


class PdfExecutiveReport:
    """Genera un reporte financiero ejecutivo de una pagina."""

    REQUIRED_COLUMNS = {"fecha", "tipo_cambio"}
    TABLE_COLUMNS = {"variacion_diaria_pct", "ma_30d", "ma_90d"}
    REQUIRED_KPIS = {
        "fecha_corte",
        "tc_actual",
        "var_diaria_pct",
        "tc_max_anio",
        "tc_min_anio",
        "tc_prom_anio",
    }

    @classmethod
    def generate(
        cls,
        df_usd: pd.DataFrame,
        kpis: Mapping[str, object],
        output_path: str = "data/reporte_financiero.pdf",
    ) -> str:
        """Genera un PDF de una pagina con KPIs, resumen, tabla y tendencia."""
        cls._validate_inputs(df_usd, kpis)
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        font = cls._register_font()
        pdf = canvas.Canvas(str(output), pagesize=landscape(letter))
        pdf.setTitle("Reporte Financiero Ejecutivo Banxico")
        pdf.setAuthor("Automatizacion Financiera")
        pdf.setSubject("Analisis ejecutivo del tipo de cambio USD/MXN")
        width, height = landscape(letter)
        margin = 36
        y = height - margin
        start_date = df_usd["fecha"].min().strftime("%Y-%m-%d")
        end_date = df_usd["fecha"].max().strftime("%Y-%m-%d")

        cls._draw_header(pdf, font, width, margin, y, str(kpis["fecha_corte"]), start_date, end_date)
        y -= 68
        y = cls._draw_kpi_cards(pdf, font, kpis, df_usd, margin, width, y) - 18
        y = cls._draw_summary(pdf, font, kpis, margin, width, y) - 18
        table_width = (width - 2 * margin) * 0.58
        cls._draw_recent_table(pdf, font, df_usd, margin, table_width, y)
        cls._draw_trend_chart(pdf, font, df_usd, margin + table_width + 18, y, width - margin - table_width - 18)
        cls._draw_footer(pdf, font, width, margin)
        pdf.save()
        return str(output)

    @staticmethod
    def _register_font() -> str:
        candidates = [
            ("Arial", r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\arialbd.ttf"),
            ("DejaVuSans", r"C:\Windows\Fonts\DejaVuSans.ttf", r"C:\Windows\Fonts\DejaVuSans-Bold.ttf"),
        ]
        for name, regular, bold in candidates:
            if Path(regular).exists() and Path(bold).exists():
                pdfmetrics.registerFont(TTFont(name, regular))
                pdfmetrics.registerFont(TTFont(f"{name}-Bold", bold))
                pdfmetrics.registerFontFamily(name, normal=name, bold=f"{name}-Bold", italic=name)
                return name
        return "Helvetica"

    @classmethod
    def _validate_inputs(cls, df_usd: pd.DataFrame, kpis: Mapping[str, object]) -> None:
        if not isinstance(df_usd, pd.DataFrame) or df_usd.empty:
            raise ValueError("df_usd debe ser un DataFrame no vacio")
        missing_columns = cls.REQUIRED_COLUMNS - set(df_usd.columns)
        if missing_columns:
            raise ValueError(f"Faltan columnas requeridas: {', '.join(sorted(missing_columns))}")
        missing_table_columns = cls.TABLE_COLUMNS - set(df_usd.columns)
        if missing_table_columns:
            raise ValueError(
                f"Faltan columnas de indicadores: {', '.join(sorted(missing_table_columns))}"
            )
        missing_kpis = cls.REQUIRED_KPIS - set(kpis)
        if missing_kpis:
            raise ValueError(f"Faltan KPIs requeridos: {', '.join(sorted(missing_kpis))}")
        if not pd.api.types.is_datetime64_any_dtype(df_usd["fecha"]):
            raise TypeError("La columna fecha debe tener tipo datetime")
        if not pd.api.types.is_numeric_dtype(df_usd["tipo_cambio"]):
            raise TypeError("La columna tipo_cambio debe ser numerica")
        if df_usd[["fecha", "tipo_cambio"]].isna().any().any():
            raise ValueError("fecha y tipo_cambio no pueden contener valores nulos")
        if not (df_usd["tipo_cambio"] > 0).all():
            raise ValueError("tipo_cambio debe contener valores mayores que cero")
        for name in cls.REQUIRED_KPIS - {"fecha_corte"}:
            if not isinstance(kpis[name], Real):
                raise TypeError(f"El KPI {name} debe ser numerico")

    @staticmethod
    def _draw_header(
        pdf: canvas.Canvas,
        font: str,
        width: float,
        margin: float,
        y: float,
        fecha: str,
        start_date: str,
        end_date: str,
    ) -> None:
        pdf.setFillColor(colors.HexColor("#1F4E79"))
        pdf.setFont(f"{font}-Bold", 20)
        pdf.drawString(margin, y, "REPORTE FINANCIERO EJECUTIVO")
        pdf.setFillColor(colors.HexColor("#555555"))
        pdf.setFont(font, 9)
        pdf.drawString(margin, y - 20, "Tipo de cambio USD/MXN - Banco de México")
        pdf.drawRightString(width - margin, y - 20, f"Fecha de corte: {fecha}")
        pdf.setFont(font, 8)
        pdf.drawString(margin, y - 33, f"Periodo analizado: {start_date} a {end_date}")
        pdf.setStrokeColor(colors.HexColor("#D9E2F3"))
        pdf.line(margin, y - 42, width - margin, y - 42)

    @classmethod
    def _draw_kpi_cards(
        cls,
        pdf: canvas.Canvas,
        font: str,
        kpis: Mapping[str, object],
        df: pd.DataFrame,
        margin: float,
        width: float,
        y: float,
    ) -> float:
        volatility = None
        if "volatilidad_30d" in df and df["volatilidad_30d"].notna().any():
            volatility = float(df["volatilidad_30d"].dropna().iloc[-1])
        variation = float(kpis["var_diaria_pct"])
        variation_color = "#2E7D32" if variation > 0 else "#C62828" if variation < 0 else "#607D8B"
        cards = [
            ("TIPO DE CAMBIO", f"${float(kpis['tc_actual']):,.4f}", "#1F4E79"),
            ("VARIACIÓN DIARIA", f"{variation:,.2f}%", variation_color),
            ("PROMEDIO DEL AÑO", f"${float(kpis['tc_prom_anio']):,.4f}", "#1565C0"),
            ("MÁXIMO DEL AÑO", f"${float(kpis['tc_max_anio']):,.4f}", "#6A1B9A"),
            ("MÍNIMO DEL AÑO", f"${float(kpis['tc_min_anio']):,.4f}", "#C62828"),
        ]
        gap = 8
        card_width = (width - 2 * margin - 4 * gap) / 5
        card_height = 56
        for index, (label, value, color) in enumerate(cards):
            x = margin + index * (card_width + gap)
            cls._draw_card(pdf, font, x, y, card_width, card_height, label, value, color)
        volatility_y = y - card_height - 8
        volatility_value = "-" if volatility is None else f"{volatility:,.2f}% anualizada"
        cls._draw_card(pdf, font, margin, volatility_y, card_width, 38, "VOLATILIDAD 30 DÍAS", volatility_value, "#EF6C00", compact=True)
        return volatility_y - 38

    @staticmethod
    def _draw_card(
        pdf: canvas.Canvas,
        font: str,
        x: float,
        y: float,
        width: float,
        height: float,
        label: str,
        value: str,
        color: str,
        compact: bool = False,
    ) -> None:
        pdf.setFillColor(colors.HexColor("#F3F6F9"))
        pdf.roundRect(x, y - height, width, height, 6, fill=1, stroke=0)
        pdf.setFillColor(colors.HexColor(color))
        pdf.rect(x, y - height, 4, height, fill=1, stroke=0)
        pdf.setFont(f"{font}-Bold", 7 if compact else 8)
        pdf.drawString(x + 10, y - 16, label)
        pdf.setFont(f"{font}-Bold", 12 if not compact else 10)
        pdf.drawString(x + 10, y - (34 if not compact else 30), value)

    @staticmethod
    def _draw_summary(
        pdf: canvas.Canvas,
        font: str,
        kpis: Mapping[str, object],
        margin: float,
        width: float,
        y: float,
    ) -> float:
        variation = float(kpis["var_diaria_pct"])
        direction = "al alza" if variation > 0 else "a la baja" if variation < 0 else "estable"
        title = "LECTURA EJECUTIVA"
        text = (
            f"El tipo de cambio cerró en ${float(kpis['tc_actual']):,.4f}, con una variación diaria "
            f"{direction} de {variation:,.2f}%. El promedio acumulado del año fue "
            f"${float(kpis['tc_prom_anio']):,.4f}."
        )
        box_width = width - 2 * margin
        pdf.setFillColor(colors.HexColor("#EAF2F8"))
        pdf.roundRect(margin, y - 39, box_width, 39, 5, fill=1, stroke=0)
        pdf.setFillColor(colors.HexColor("#1F4E79"))
        pdf.setFont(f"{font}-Bold", 8)
        pdf.drawString(margin + 10, y - 14, title)
        pdf.setFont(font, 8)
        pdf.drawString(margin + 10, y - 28, text)
        return y - 39

    @staticmethod
    def _draw_recent_table(
        pdf: canvas.Canvas, font: str, df: pd.DataFrame, margin: float, width: float, y: float
    ) -> None:
        pdf.setFillColor(colors.HexColor("#1F4E79"))
        pdf.setFont(f"{font}-Bold", 12)
        pdf.drawString(margin, y, "Registros recientes")
        y -= 18
        headers = ["Fecha", "Tipo de cambio", "Var. diaria", "Prom. 30 días", "Prom. 90 días"]
        widths = [76, 91, 78, 91, 91]
        row_height = 18
        total_width = sum(widths)
        pdf.setFillColor(colors.HexColor("#1F4E79"))
        pdf.rect(margin, y - row_height + 4, total_width, row_height, fill=1, stroke=0)
        pdf.setFillColor(colors.white)
        pdf.setFont(f"{font}-Bold", 8)
        x = margin
        for header, column_width in zip(headers, widths):
            pdf.drawCentredString(x + column_width / 2, y - 7, header)
            x += column_width
        y -= row_height
        pdf.setFont(font, 8)
        for row_number, row in enumerate(df.tail(8).iloc[::-1].itertuples(index=False)):
            values = [
                row.fecha.strftime("%Y-%m-%d"),
                f"${row.tipo_cambio:,.4f}",
                PdfExecutiveReport._format_percent(getattr(row, "variacion_diaria_pct", None)),
                PdfExecutiveReport._format_currency(getattr(row, "ma_30d", None)),
                PdfExecutiveReport._format_currency(getattr(row, "ma_90d", None)),
            ]
            pdf.setFillColor(colors.HexColor("#F3F6F9") if row_number % 2 == 0 else colors.white)
            pdf.rect(margin, y - row_height + 4, total_width, row_height, fill=1, stroke=0)
            pdf.setFillColor(colors.HexColor("#333333"))
            x = margin
            for index, (value, column_width) in enumerate(zip(values, widths)):
                if index == 0:
                    pdf.drawString(x + 5, y - 7, value)
                else:
                    pdf.drawRightString(x + column_width - 5, y - 7, value)
                x += column_width
            y -= row_height

    @staticmethod
    def _draw_trend_chart(
        pdf: canvas.Canvas, font: str, df: pd.DataFrame, x: float, y: float, width: float
    ) -> None:
        pdf.setFillColor(colors.HexColor("#1F4E79"))
        pdf.setFont(f"{font}-Bold", 12)
        pdf.drawString(x, y, "Tendencia reciente")
        chart_y = y - 170
        chart_width = width
        chart_height = 150
        recent = df.tail(30).reset_index(drop=True)
        series = [
            ("tipo_cambio", "#1F4E79"),
            ("ma_30d", "#2E7D32"),
            ("ma_90d", "#EF6C00"),
        ]
        available = [(column, color) for column, color in series if column in recent]
        numeric_values = pd.concat([recent[column] for column, _ in available]).dropna()
        lower = float(numeric_values.min()) - 0.05
        upper = float(numeric_values.max()) + 0.05
        pdf.setStrokeColor(colors.HexColor("#D9E2F3"))
        pdf.rect(x, chart_y, chart_width, chart_height, fill=0, stroke=1)
        for grid in range(1, 4):
            grid_y = chart_y + grid * chart_height / 4
            pdf.line(x, grid_y, x + chart_width, grid_y)
        for column, color in available:
            values = recent[column].interpolate().ffill().bfill().astype(float).tolist()
            points = []
            for index, value in enumerate(values):
                px = x + index * chart_width / max(len(values) - 1, 1)
                py = chart_y + (value - lower) / max(upper - lower, 0.001) * chart_height
                points.append((px, py))
            pdf.setStrokeColor(colors.HexColor(color))
            pdf.setLineWidth(2 if column == "tipo_cambio" else 1.2)
            for first, second in zip(points, points[1:]):
                pdf.line(first[0], first[1], second[0], second[1])
        pdf.setFillColor(colors.HexColor("#555555"))
        pdf.setFont(font, 7)
        pdf.drawString(x + 5, chart_y - 12, recent["fecha"].iloc[0].strftime("%Y-%m-%d"))
        pdf.drawRightString(x + chart_width - 5, chart_y - 12, recent["fecha"].iloc[-1].strftime("%Y-%m-%d"))
        pdf.drawString(x + 5, chart_y + chart_height + 5, f"${upper:,.2f}")
        pdf.drawString(x + 5, chart_y - 1, f"${lower:,.2f}")
        legend_y = chart_y - 27
        legend_x = x
        for label, color in [("Tipo de cambio", "#1F4E79"), ("MA 30 días", "#2E7D32"), ("MA 90 días", "#EF6C00")]:
            pdf.setStrokeColor(colors.HexColor(color))
            pdf.setLineWidth(2)
            pdf.line(legend_x, legend_y, legend_x + 12, legend_y)
            pdf.setFillColor(colors.HexColor("#444444"))
            pdf.setFont(font, 7)
            pdf.drawString(legend_x + 16, legend_y - 3, label)
            legend_x += 78

    @staticmethod
    def _draw_footer(pdf: canvas.Canvas, font: str, width: float, margin: float) -> None:
        pdf.setFont(font, 8)
        pdf.setFillColor(colors.HexColor("#666666"))
        pdf.drawString(margin, 20, "Fuente: Banco de México - Sistema de Información Económica")
        pdf.drawRightString(width - margin, 20, "Reporte automatizado")
        pdf.setFillColor(colors.HexColor("#1F4E79"))
        pdf.rect(0, 0, width, 7, fill=1, stroke=0)

    @staticmethod
    def _format_currency(value: object) -> str:
        return "-" if pd.isna(value) else f"${float(value):,.4f}"

    @staticmethod
    def _format_percent(value: object) -> str:
        return "-" if pd.isna(value) else f"{float(value):,.2f}%"
