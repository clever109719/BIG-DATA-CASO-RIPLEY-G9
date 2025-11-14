from pyspark.sql import functions as F
from pyspark.sql.types import StringType
from transformers import pipeline
from modulo_carga.load_sentiment import load_sentiment

# Cargar modelo, BETO para los compas
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="nlptown/bert-base-multilingual-uncased-sentiment"
)

# Función para clasificar sentimiento
def analizar_sentimiento(texto):
    if not texto or texto.strip() == "":
        return "neutral"
    try:
        result = sentiment_pipeline(texto[:512])[0]
        label = result["label"]
        if "1" in label or "2" in label:
            return "negativo"
        elif "3" in label:
            return "neutral"
        else:
            return "positivo"
    except Exception:
        return "neutral"

# Registrar UDF para Spark
sentiment_udf = F.udf(analizar_sentimiento, StringType())

def ejecutar_sentimiento(df_youtube, df_reddit):

    print(">>> Aplicando modelo de sentimiento BETO (multilingüe)")
    yt_sent = df_youtube.withColumn("sentimiento", sentiment_udf(F.col("comment")))
    rd_sent = df_reddit.withColumn("sentimiento", sentiment_udf(F.col("comment")))

    # Guardar resultados
    load_sentiment(yt_sent, rd_sent)
    print("Análisis de sentimiento completado y guardado en HDFS.")

    return yt_sent, rd_sent
