from pyspark.sql import SparkSession
from modulo_tend.analysis_tend import (
    tendencia_palabras,
    participacion_promedio,
    distribucion_rangos,
    engagement_por_longitud
)
from modulo_carga.load_tend import load_tend
from modulo_carga.config import ANALYTICS_YT_PATH, ANALYTICS_RD_PATH

def process_tend(spark: SparkSession):
    """
    Ejecuta el análisis de tendencias y participación usando los datos
    con sentimiento (ya analizados por BETO), y guarda los resultados
    finales en HDFS dentro de /user/ripley/analytics.
    """
    print(">>> Cargando datos con sentimiento para análisis de tendencias y participación...")
    df_youtube = spark.read.parquet(ANALYTICS_YT_PATH)
    df_reddit = spark.read.parquet(ANALYTICS_RD_PATH)

    print(">>> Ejecutando análisis de tendencias y métricas de participación...")

    # Análisis para YouTube
    yt_palabras = tendencia_palabras(df_youtube, "YouTube")
    yt_rangos = distribucion_rangos(df_youtube, "YouTube", "likes")
    yt_eng = engagement_por_longitud(df_youtube, "YouTube", "likes")
    yt_avg = participacion_promedio(df_youtube, "YouTube", "likes")

    # Análisis para Reddit
    rd_palabras = tendencia_palabras(df_reddit, "Reddit")
    rd_rangos = distribucion_rangos(df_reddit, "Reddit", "score")
    rd_eng = engagement_por_longitud(df_reddit, "Reddit", "score")
    rd_avg = participacion_promedio(df_reddit, "Reddit", "score")

    # Guardado en HDFS
    print(">>> Guardando resultados analíticos en HDFS (/user/ripley/analytics)...")
    load_tend(
        yt_palabras, yt_rangos, yt_eng, yt_avg,
        rd_palabras, rd_rangos, rd_eng, rd_avg
    )
    print(">>> Análisis de tendencias y participación completado y guardado correctamente.")