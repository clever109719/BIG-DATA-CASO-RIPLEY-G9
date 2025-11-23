import logging
from pyspark.sql import SparkSession
from modulo_machine_learning.beto_sentiment import ejecutar_sentimiento 
from modulo_carga.config import PROCESSED_YT_PATH, PROCESSED_RD_PATH

# Configuración del logger
logger = logging.getLogger(__name__)

def sentiment_process(spark: SparkSession):
    logger.info(">>> Iniciando orquestación del Análisis de Sentimiento (BETO)")
    
    logger.info(f"Leyendo datos procesados desde: {PROCESSED_YT_PATH} y {PROCESSED_RD_PATH}")
    df_youtube = spark.read.parquet(PROCESSED_YT_PATH)
    df_reddit = spark.read.parquet(PROCESSED_RD_PATH)

    logger.info(">>> Ejecutando modelo BETO sobre comentarios (Batch Inference Pandas UDF)")
    ejecutar_sentimiento(df_youtube, df_reddit)

    logger.info(">>> Resultados de sentimiento almacenados correctamente en capa Analytics.")