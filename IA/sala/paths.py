from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
INPUTS_DIR = DATA_DIR / "inputs"
SEPARATED_DIR = DATA_DIR / "separated"
TRANSCRIPTIONS_DIR = DATA_DIR / "transcriptions"
REPORTS_DIR = DATA_DIR / "reports"
LOGS_DIR = DATA_DIR / "logs"
MODELS_DIR = BASE_DIR / "models_cache"

for d in [DATA_DIR, INPUTS_DIR, SEPARATED_DIR, TRANSCRIPTIONS_DIR, REPORTS_DIR, LOGS_DIR, MODELS_DIR]:
    d.mkdir(parents=True, exist_ok=True)