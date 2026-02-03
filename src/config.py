import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
FRONTEND_PATH = os.path.join(BASE_DIR, "src", "frontend")

DB_CONNECTION = "postgresql://postgres:86789787@localhost:5432/postgres" #NORMALMENTE O HOST É LOCALHOST, E A PORTA PADRÃO É 5432