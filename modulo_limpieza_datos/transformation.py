import logging
from modulo_limpieza_datos.cleaner import process_youtube, process_reddit
from modulo_limpieza_datos.config import RAW_YT_PATH, RAW_RD_PATH

# Configuración del logger
logger = logging.getLogger(__name__)

def transformation(spark):
    """Transforma y limpia los datos crudos de YouTube y Reddit"""
    logger.info(">>> Iniciando proceso de limpieza y transformación de datos...")
    
    # Procesar YouTube
    logger.info(f"Procesando datos de YouTube desde: {RAW_YT_PATH}")
    yt_clean = process_youtube(spark, RAW_YT_PATH)
    
    # Procesar Reddit
    logger.info(f"Procesando datos de Reddit desde: {RAW_RD_PATH}")
    rd_clean = process_reddit(spark, RAW_RD_PATH)
    
    logger.info(">>> Limpieza finalizada. DataFrames listos para carga.")
    return yt_clean, rd_clean