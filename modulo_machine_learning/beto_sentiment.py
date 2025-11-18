from pyspark.sql import functions as F
from pyspark.sql.types import StringType
from transformers import pipeline
from modulo_carga.load_sentiment import load_sentiment

# Cargar modelo BETO
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="finiteautomata/beto-sentiment-analysis"
)

# Función para clasificar sentimiento
def analizar_sentimiento(texto):
    if not texto or texto.strip() == "":
        return "neutral"
    try:
        result = sentiment_pipeline(texto[:512])[0]
        label = result["label"].lower()   # BETO devuelve: POS, NEG, NEU
        if "neg" in label:
            return "negativo"
        elif "neu" in label:
            return "neutral"
        else:
            return "positivo"
    except Exception:
        return "neutral"

sentiment_udf = F.udf(analizar_sentimiento, StringType())

def ejecutar_sentimiento(df_youtube, df_reddit):
    print(">>> Aplicando modelo de sentimiento BETO (español)")
    
    yt_sent = df_youtube.withColumn("sentimiento", sentiment_udf(F.col("comment")))
    rd_sent = df_reddit.withColumn("sentimiento", sentiment_udf(F.col("comment")))
    
    # Guardar resultados
    load_sentiment(yt_sent, rd_sent)
    
    print("Análisis de sentimiento completado y guardado en HDFS.")
    return yt_sent, rd_sent