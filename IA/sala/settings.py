import os
import torch
from dotenv import load_dotenv
from .paths import DATA_DIR, INPUTS_DIR, SEPARATED_DIR, REPORTS_DIR, LOGS_DIR, MODELS_DIR

load_dotenv() 

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_KEY") or ""
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash") 
HF_TOKEN = os.getenv("HF_TOKEN") or ""