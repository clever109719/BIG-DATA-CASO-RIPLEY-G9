from pyspark.sql import SparkSession
from modulo_machine_learning.beto_sentiment import ejecutar_sentimiento 
from modulo_carga.config import PROCESSED_YT_PATH, PROCESSED_RD_PATH
import logging

logger = logging.getLogger(__name__)

def sentiment_process(spark: SparkSession):
    logger.info(">>> Cargando datos limpios para análisis de sentimiento")
    
    df_youtube = spark.read.parquet(PROCESSED_YT_PATH)
    df_reddit = spark.read.parquet(PROCESSED_RD_PATH)

    logger.info(">>> Ejecutando modelo BETO sobre comentarios (Batch Inference)")
    ejecutar_sentimiento(df_youtube, df_reddit)

    logger.info(">>> Resultados de sentimiento almacenados correctamente.")