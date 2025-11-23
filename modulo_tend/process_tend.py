import logging
from pyspark.sql import SparkSession
from modulo_tend.analysis_tend import (
    tendencia_palabras,
    participacion_promedio,
    distribucion_rangos,
    engagement_por_longitud
)
from modulo_carga.load_tend import load_tend
from modulo_carga.config import ANALYTICS_YT_PATH, ANALYTICS_RD_PATH

# Importamos privacidad diferencial
from modulo_privacidad.dp import dp_protect

# Configuración del logger
logger = logging.getLogger(__name__)

def process_tend(spark: SparkSession):
    """
    Ejecuta el análisis de tendencias y participación usando los datos
    con sentimiento, aplica privacidad diferencial y guarda los resultados.
    """

    # ---------------------------------------------------------
    # Carga de datos
    # ---------------------------------------------------------
    logger.info(">>> Cargando datos con sentimiento para análisis de tendencias y participación...")
    df_youtube = spark.read.parquet(ANALYTICS_YT_PATH)
    df_reddit = spark.read.parquet(ANALYTICS_RD_PATH)

    # ---------------------------------------------------------
    # VERIFICACIÓN: Datos *antes* del ruido DP
    # ---------------------------------------------------------
    logger.info(">>> MUESTRA DE DATOS ORIGINALES (ANTES DEL RUIDO DP)")

    logger.info("YouTube - sentimiento (Muestra):")
    df_youtube.select("sentimiento").show(5)

    logger.info("Reddit - sentimiento (Muestra):")
    df_reddit.select("sentimiento").show(5)

    # ---------------------------------------------------------
    # Análisis de tendencias y participación
    # ---------------------------------------------------------
    logger.info(">>> Ejecutando análisis de tendencias y métricas de participación...")

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

    # ---------------------------------------------------------
    # APLICACIÓN DE PRIVACIDAD DIFERENCIAL
    # ---------------------------------------------------------
    logger.info(">>> Aplicando Privacidad Diferencial a los resultados...")

    # Frecuencia de palabras
    yt_palabras = dp_protect(yt_palabras, ["frecuencia"], epsilon=1.0)
    rd_palabras = dp_protect(rd_palabras, ["frecuencia"], epsilon=1.0)

    # Rangos
    yt_rangos = dp_protect(yt_rangos, ["cantidad"], epsilon=1.0)
    rd_rangos = dp_protect(rd_rangos, ["cantidad"], epsilon=1.0)

    # Engagement
    yt_eng = dp_protect(
        yt_eng,
        ["n_comentarios", "promedio_interaccion", "suma_interaccion"],
        epsilon=1.2
    )
    rd_eng = dp_protect(
        rd_eng,
        ["n_comentarios", "promedio_interaccion", "suma_interaccion"],
        epsilon=1.2
    )

    # Promedio total de participación
    yt_avg = dp_protect(
        yt_avg,
        ["n_total", "suma_interaccion", "promedio_interaccion"],
        epsilon=1.2
    )
    rd_avg = dp_protect(
        rd_avg,
        ["n_total", "suma_interaccion", "promedio_interaccion"],
        epsilon=1.2
    )

    logger.info(">>> Privacidad diferencial aplicada correctamente.")

    # ---------------------------------------------------------
    # VERIFICACIÓN: Datos *después* del ruido DP
    # ---------------------------------------------------------
    logger.info(">>> MUESTRA DE RESULTADOS DESPUÉS DEL RUIDO DP")

    logger.info("YouTube - Tendencia de palabras (con ruido):")
    yt_palabras.show(5)

    logger.info("YouTube - Distribución de rangos (con ruido):")
    yt_rangos.show(5)

    logger.info("Reddit - Tendencia de palabras (con ruido):")
    rd_palabras.show(5)

    logger.info("Reddit - Distribución de rangos (con ruido):")
    rd_rangos.show(5)

    # ---------------------------------------------------------
    # Guardado en HDFS
    # ---------------------------------------------------------
    logger.info(">>> Guardando resultados analíticos en HDFS (/user/ripley/analytics)...")
    load_tend(
        yt_palabras, yt_rangos, yt_eng, yt_avg,
        rd_palabras, rd_rangos, rd_eng, rd_avg
    )
    logger.info(">>> Análisis de tendencias y participación completado y guardado correctamente.")