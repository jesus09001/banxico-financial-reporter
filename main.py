import os
import time
from pathlib import Path

from dotenv import load_dotenv

from src.banxico_client import BanxicoClient
from src.data_processor import FinancialDataProcessor
from src.excel_exporter import ExcelExporter
from src.pdf_generator import PdfExecutiveReport


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"
DEFAULT_SERIES_ID = "SF63528"
DEFAULT_START_DATE = "2022-01-01"
load_dotenv(PROJECT_ROOT / ".env")


def _get_config() -> tuple[str, str]:
    series_id = os.getenv("BANXICO_SERIES_ID", DEFAULT_SERIES_ID).strip()
    start_date = os.getenv("BANXICO_FECHA_INICIO", DEFAULT_START_DATE).strip()
    if not series_id:
        raise ValueError("BANXICO_SERIES_ID no puede estar vacia")
    if not start_date:
        raise ValueError("BANXICO_FECHA_INICIO no puede estar vacia")
    return series_id, start_date


def _validate_output(path: str) -> Path:
    output = Path(path)
    if not output.is_file() or output.stat().st_size == 0:
        raise RuntimeError(f"No se genero correctamente el archivo: {output}")
    return output


def run_pipeline() -> tuple[str, str]:
    """Extrae datos, calcula indicadores y genera los reportes finales."""
    started_at = time.perf_counter()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    series_id, start_date = _get_config()
    client = BanxicoClient()
    raw_data = client.fetch_series(series_id, fecha_inicio=start_date)
    processed_data = FinancialDataProcessor.process_usd_mxn(raw_data)
    kpis = FinancialDataProcessor.summarize_kpis(processed_data)
    excel_output = ExcelExporter.export_to_excel(
        processed_data,
        kpis,
        str(OUTPUT_DIR / "reporte_financiero.xlsx"),
    )
    pdf_output = PdfExecutiveReport.generate(
        processed_data,
        kpis,
        str(OUTPUT_DIR / "reporte_financiero.pdf"),
    )
    excel_path = _validate_output(excel_output)
    pdf_path = _validate_output(pdf_output)
    elapsed = time.perf_counter() - started_at
    print("[OK] Pipeline completado")
    print(f"  Serie: {series_id}")
    print(f"  Periodo: {processed_data['fecha'].min():%Y-%m-%d} a {processed_data['fecha'].max():%Y-%m-%d}")
    print(f"  Registros procesados: {len(processed_data)}")
    print(f"  Fecha de corte: {kpis['fecha_corte']}")
    print(f"  Tipo de cambio actual: ${kpis['tc_actual']:,.4f}")
    print(f"  Excel: {excel_path}")
    print(f"  PDF: {pdf_path}")
    print(f"  Duracion: {elapsed:.2f} s")
    return str(excel_path), str(pdf_path)


if __name__ == "__main__":
    try:
        run_pipeline()
    except Exception as error:
        print(f"[ERROR] Pipeline no completado: {error}")
        raise SystemExit(1) from error
