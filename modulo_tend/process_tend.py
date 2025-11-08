from pyspark.sql import SparkSession
from modulo_tend.analysis_tend import (
    tendencia_palabras,
    participacion_promedio,
    distribucion_rangos,
    engagement_por_longitud
)
from modulo_carga.load_tend import load_tend
from modulo_carga.config import PROCESSED_YT_PATH, PROCESSED_RD_PATH

def process_tend(spark: SparkSession):
    # Carga los datos limpios desde HDFS
    print(">>> Cargando datos limpios para análisis de tendencias y participación...")
    df_youtube = spark.read.parquet(PROCESSED_YT_PATH)
    df_reddit = spark.read.parquet(PROCESSED_RD_PATH)

    print(">>> Ejecutando análisis de tendencias y métricas de participación...")

    # YouTube
    yt_palabras = tendencia_palabras(df_youtube, "YouTube")
    yt_avg = participacion_promedio(df_youtube, "YouTube", "likes")
    yt_rangos = distribucion_rangos(df_youtube, "YouTube", "likes")
    yt_eng = engagement_por_longitud(df_youtube, "YouTube", "likes")

    # Reddit
    rd_palabras = tendencia_palabras(df_reddit, "Reddit")
    rd_avg = participacion_promedio(df_reddit, "Reddit", "score")
    rd_rangos = distribucion_rangos(df_reddit, "Reddit", "score")
    rd_eng = engagement_por_longitud(df_reddit, "Reddit", "score")

    # Guarda los resultados finales
    print(">>> Guardando resultados en HDFS...")
    load_tend(yt_palabras, yt_avg, yt_rangos, yt_eng, rd_palabras, rd_avg, rd_rangos, rd_eng)

    print(">>> Análisis de tendencias completado y guardado en HDFS.")