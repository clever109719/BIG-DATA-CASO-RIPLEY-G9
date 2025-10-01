from loader import save_parquet
from config import PROCESSED_YT_PATH, PROCESSED_RD_PATH

def load(yt_clean, rd_clean):
    """Carga los datos transformados a HDFS en formato parquet"""
    save_parquet(yt_clean, PROCESSED_YT_PATH)
    save_parquet(rd_clean, PROCESSED_RD_PATH)