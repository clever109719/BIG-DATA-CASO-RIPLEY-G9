from pyspark.sql import SparkSession
from modulo_machine_learning.beto_sentiment import ejecutar_sentimiento
from modulo_carga.config import PROCESSED_YT_PATH, PROCESSED_RD_PATH

def sentiment_process(spark: SparkSession):
    """
    Carga los datos limpios desde HDFS, ejecuta el modelo BETO
    y guarda los resultados en la carpeta /analytics.
    """
    print(">>> Cargando datos limpios para análisis de sentimiento")
    df_youtube = spark.read.parquet(PROCESSED_YT_PATH)
    df_reddit = spark.read.parquet(PROCESSED_RD_PATH)

    print(">>> Ejecutando modelo BETO sobre comentarios")
    ejecutar_sentimiento(df_youtube, df_reddit)

    print(">>> Resultados de sentimiento almacenados correctamente.")
