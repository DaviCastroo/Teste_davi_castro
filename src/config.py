import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
FRONTEND_PATH = os.path.join(BASE_DIR, "src", "frontend")

DB_CONNECTION = "postgresql://usuario:senha_banco@host:porta/nome_banco" #NORMALMENTE O HOST É LOCALHOST, E A PORTA PADRÃO É 5432