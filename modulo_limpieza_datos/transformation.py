
from modulo_limpieza_datos.cleaner import process_youtube, process_reddit
from modulo_limpieza_datos.config import RAW_YT_PATH, RAW_RD_PATH

def transformation(spark):
    """Transforma y limpia los datos crudos de YouTube y Reddit"""
    yt_clean = process_youtube(spark, RAW_YT_PATH)
    rd_clean = process_reddit(spark, RAW_RD_PATH)
    return yt_clean, rd_clean