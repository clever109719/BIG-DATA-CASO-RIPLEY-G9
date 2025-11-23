import logging
from modulo_carga.loader import save_parquet
from modulo_carga.config import PROCESSED_YT_PATH, PROCESSED_RD_PATH

# Configuración del logger
logger = logging.getLogger(__name__)

def load(yt_clean, rd_clean):
    """Carga los datos transformados a HDFS en formato parquet"""
    logger.info(">>> Iniciando carga de datos procesados a HDFS...")
    
    # Guardar YouTube
    save_parquet(yt_clean, PROCESSED_YT_PATH)
    logger.info(f"Datos de YouTube guardados en: {PROCESSED_YT_PATH}")
    
    # Guardar Reddit
    save_parquet(rd_clean, PROCESSED_RD_PATH)
    logger.info(f"Datos de Reddit guardados en: {PROCESSED_RD_PATH}")
    
    logger.info(">>> Carga a HDFS completada exitosamente.")