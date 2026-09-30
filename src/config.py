import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def _get(name, default=""):
    v = os.getenv(name)
    if v:
        return v
    try:  # Streamlit Cloud secrets
        import streamlit as st
        return str(st.secrets.get(name, default))
    except Exception:
        return default

API_KEY = _get("CWA_API_KEY")
URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"
DB_PATH = Path(_get("DB_PATH", "data/weather.db"))
CACHE_MINUTES = int(_get("CACHE_MINUTES", "30"))  # 假設值，可調整
RETENTION_DAYS = 7                                  # 假設值，可調整
TIMEOUT = 10
DEFAULT_LOCATION = "臺中市"
