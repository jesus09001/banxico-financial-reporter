import numpy as np
import pandas as pd


class FinancialDataProcessor:
    """Calcula indicadores sobre series financieras diarias."""

    @staticmethod
    def _validate_processed_data(df: pd.DataFrame) -> None:
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df_usd debe ser un pandas.DataFrame")
        required = {"fecha", "tipo_cambio"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"Faltan columnas para KPIs: {', '.join(sorted(missing))}")
        if df.empty:
            raise ValueError("No hay datos para procesar")
        if not pd.api.types.is_datetime64_any_dtype(df["fecha"]):
            raise TypeError("La columna fecha debe tener tipo datetime")
        if not pd.api.types.is_numeric_dtype(df["tipo_cambio"]):
            raise TypeError("La columna tipo_cambio debe ser numerica")
        if df[["fecha", "tipo_cambio"]].isna().any().any():
            raise ValueError("fecha y tipo_cambio no pueden contener valores nulos")
        if not np.isfinite(df["tipo_cambio"].to_numpy(dtype=float)).all():
            raise ValueError("tipo_cambio contiene valores no finitos")
        if (df["tipo_cambio"] <= 0).any():
            raise ValueError("tipo_cambio debe contener valores mayores que cero")
        if not df["fecha"].is_monotonic_increasing:
            raise ValueError("Los datos deben estar ordenados por fecha")

    @staticmethod
    def process_usd_mxn(df_usd: pd.DataFrame) -> pd.DataFrame:
        """Limpia una serie USD/MXN y calcula indicadores de fecha calendario."""
        if not isinstance(df_usd, pd.DataFrame):
            raise TypeError("df_usd debe ser un pandas.DataFrame")
        required = {"fecha", "dato"}
        missing = required - set(df_usd.columns)
        if missing:
            raise ValueError(f"Faltan columnas requeridas: {', '.join(sorted(missing))}")
        if df_usd.empty:
            raise ValueError("No hay datos para procesar")

        df = df_usd[["fecha", "dato"]].copy()
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
        df["tipo_cambio"] = pd.to_numeric(df["dato"], errors="coerce")
        df = (
            df.dropna(subset=["fecha", "tipo_cambio"])
            .sort_values("fecha")
            .drop_duplicates(subset=["fecha"], keep="last")
            .reset_index(drop=True)
        )
        if df.empty:
            raise ValueError("No hay datos validos para procesar")
        if not np.isfinite(df["tipo_cambio"].to_numpy(dtype=float)).all():
            raise ValueError("La columna dato contiene valores no finitos")
        if (df["tipo_cambio"] <= 0).any():
            raise ValueError("La columna dato debe contener valores mayores que cero")

        df = df.drop(columns=["dato"])
        df["variacion_diaria_pct"] = df["tipo_cambio"].pct_change() * 100
        monthly_lookup = df[["fecha", "tipo_cambio"]].copy()
        monthly_lookup["fecha_referencia"] = monthly_lookup["fecha"] - pd.DateOffset(months=1)
        monthly_lookup = monthly_lookup.sort_values("fecha_referencia")
        historical_values = df[["fecha", "tipo_cambio"]].rename(
            columns={"fecha": "fecha_base", "tipo_cambio": "tipo_cambio_mes_anterior"}
        ).sort_values("fecha_base")
        monthly = pd.merge_asof(
            monthly_lookup,
            historical_values,
            left_on="fecha_referencia",
            right_on="fecha_base",
            direction="backward",
        )
        df["variacion_mensual_pct"] = (
            (df["tipo_cambio"].to_numpy() / monthly["tipo_cambio_mes_anterior"].to_numpy() - 1)
            * 100
        )

        indexed_values = df.set_index("fecha")["tipo_cambio"]
        indexed_returns = df.set_index("fecha")["variacion_diaria_pct"]
        df["ma_30d"] = indexed_values.rolling("30D", min_periods=1).mean().to_numpy()
        df["ma_90d"] = indexed_values.rolling("90D", min_periods=1).mean().to_numpy()
        df["volatilidad_30d"] = (
            indexed_returns.rolling("30D", min_periods=2).std() * np.sqrt(252)
        ).to_numpy()
        return df

    @staticmethod
    def summarize_kpis(df_usd: pd.DataFrame) -> dict:
        """Resume los KPIs del año correspondiente a la última observación."""
        FinancialDataProcessor._validate_processed_data(df_usd)
        if len(df_usd) < 2:
            raise ValueError("Se necesitan al menos dos registros para calcular los KPIs")

        latest = df_usd.iloc[-1]
        previous = df_usd.iloc[-2]
        year_data = df_usd[df_usd["fecha"].dt.year == latest["fecha"].year]
        if previous["tipo_cambio"] == 0:
            raise ValueError("No se puede calcular la variacion diaria con un valor anterior igual a cero")
        daily_variation = (
            (latest["tipo_cambio"] - previous["tipo_cambio"])
            / previous["tipo_cambio"]
            * 100
        )
        return {
            "fecha_corte": latest["fecha"].strftime("%Y-%m-%d"),
            "tc_actual": round(float(latest["tipo_cambio"]), 4),
            "var_diaria_pct": round(float(daily_variation), 4),
            "tc_max_anio": round(float(year_data["tipo_cambio"].max()), 4),
            "tc_min_anio": round(float(year_data["tipo_cambio"].min()), 4),
            "tc_prom_anio": round(float(year_data["tipo_cambio"].mean()), 4),
        }
