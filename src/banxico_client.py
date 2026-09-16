#%%
import os
from typing import List, Optional

import pandas as pd
import requests


class BanxicoClient:
    """Cliente para extraer series economicas desde la API SIE de Banxico."""

    BASE_URL = "https://www.banxico.org.mx/SieAPIRest/service/v1/series"

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("BANXICO_TOKEN")
        if not self.token:
            raise ValueError(
                "No se encontró un token de Banxico. Define la variable de entorno "
                "BANXICO_TOKEN o pásalo explícitamente: BanxicoClient(token='...')"
            )
        self.headers = {"Bmx-Token": self.token, "Accept": "application/json"}

    def fetch_series(
        self,
        series_id: str,
        fecha_inicio: str = "2020-01-01",
        fecha_fin: Optional[str] = None,
    ) -> pd.DataFrame:
        """Obtiene una serie y la devuelve ordenada como fecha/dato."""
        if not series_id or not series_id.strip():
            raise ValueError("series_id no puede estar vacio")

        start = pd.to_datetime(fecha_inicio, errors="raise").strftime("%Y-%m-%d")
        end_date = pd.Timestamp.today().normalize() if fecha_fin is None else pd.to_datetime(fecha_fin, errors="raise")
        end = min(end_date, pd.Timestamp.today().normalize()).strftime("%Y-%m-%d")
        if start > end:
            raise ValueError("fecha_inicio no puede ser posterior a fecha_fin")

        url = f"{self.BASE_URL}/{series_id.strip()}/datos/{start}/{end}"
        try:
            response = requests.get(url, headers=self.headers, timeout=20)
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as error:
            detail = ""
            if error.response is not None:
                detail = f" | Respuesta: {error.response.text}"
            raise RuntimeError(f"Error al consultar Banxico: {error}{detail}") from error
        except ValueError as error:
            raise RuntimeError("Banxico devolvio una respuesta JSON invalida") from error

        series = payload.get("bmx", {}).get("series", [])
        if isinstance(series, dict):
            series = [series]
        if not series:
            raise ValueError(f"No se encontraron datos para la serie {series_id}")

        records = series[0].get("datos", [])
        df = pd.DataFrame(records, columns=["fecha", "dato"])
        if df.empty:
            return pd.DataFrame(columns=["fecha", "dato"])

        df["fecha"] = pd.to_datetime(df["fecha"], format="%d/%m/%Y", errors="coerce")
        df["dato"] = pd.to_numeric(
            df["dato"].astype("string").str.replace(",", "", regex=False),
            errors="coerce",
        )
        return (
            df.dropna(subset=["fecha", "dato"])
            .sort_values("fecha")
            .drop_duplicates(subset=["fecha"], keep="last")
            .reset_index(drop=True)
        )

    def fetch_multiple_series(
        self,
        series_ids: List[str],
        fecha_inicio: str = "2020-01-01",
        fecha_fin: Optional[str] = None,
    ) -> pd.DataFrame:
        """Obtiene varias series y las combina por fecha."""
        if not series_ids:
            raise ValueError("series_ids no puede estar vacio")

        normalized_ids = [series_id.strip() for series_id in series_ids]
        if any(not series_id for series_id in normalized_ids):
            raise ValueError("series_ids no puede contener identificadores vacios")

        start = pd.to_datetime(fecha_inicio, errors="raise").strftime("%Y-%m-%d")
        end_date = (
            pd.Timestamp.today().normalize()
            if fecha_fin is None
            else pd.to_datetime(fecha_fin, errors="raise")
        )
        end = min(end_date, pd.Timestamp.today().normalize()).strftime("%Y-%m-%d")
        if start > end:
            raise ValueError("fecha_inicio no puede ser posterior a fecha_fin")

        url = f"{self.BASE_URL}/{','.join(normalized_ids)}/datos/{start}/{end}"
        try:
            response = requests.get(url, headers=self.headers, timeout=20)
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as error:
            detail = ""
            if error.response is not None:
                detail = f" | Respuesta: {error.response.text}"
            raise RuntimeError(f"Error al consultar Banxico: {error}{detail}") from error
        except ValueError as error:
            raise RuntimeError("Banxico devolvio una respuesta JSON invalida") from error

        series = payload.get("bmx", {}).get("series", [])
        if isinstance(series, dict):
            series = [series]
        if not series:
            raise ValueError("No se encontraron datos para las series solicitadas")

        frames = []
        for item in series:
            series_id = item.get("idSerie")
            if not series_id:
                continue
            data = pd.DataFrame(item.get("datos", []), columns=["fecha", "dato"])
            if data.empty:
                continue
            data["fecha"] = pd.to_datetime(
                data["fecha"], format="%d/%m/%Y", errors="coerce"
            )
            data[series_id] = pd.to_numeric(
                data["dato"].astype("string").str.replace(",", "", regex=False),
                errors="coerce",
            )
            data = (
                data.dropna(subset=["fecha", series_id])
                .sort_values("fecha")
                .drop_duplicates(subset=["fecha"], keep="last")
            )
            frames.append(data[["fecha", series_id]])

        if not frames:
            return pd.DataFrame(columns=["fecha"] + normalized_ids)

        result = frames[0]
        for frame in frames[1:]:
            result = pd.merge(result, frame, on="fecha", how="outer")
        return result.sort_values("fecha").reset_index(drop=True)

#%%