import pandas as pd
from typing import Iterator
from pyspark.sql.functions import pandas_udf
from pyspark.sql.types import StringType
from modulo_carga.load_sentiment import load_sentiment
from transformers import pipeline
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pandas_udf(StringType())
def analizar_sentimiento_beto(iterator: Iterator[pd.Series]) -> Iterator[pd.Series]:
    model_name = "finiteautomata/beto-sentiment-analysis"
    
    sentiment_pipeline = pipeline(
        "sentiment-analysis", 
        model=model_name, 
        tokenizer=model_name,
        truncation=True, 
        max_length=512
    )

    for batch in iterator:
        texts = batch.fillna("").tolist()
        predictions = []
        try:
            results = sentiment_pipeline(texts)
            for res in results:
                label = res['label'].lower() 
                if "neg" in label:
                    predictions.append("negativo")
                elif "neu" in label:
                    predictions.append("neutral")
                else:
                    predictions.append("positivo")
        except Exception as e:
            logger.error(f"Error en inferencia batch: {e}")
            predictions = ["neutral"] * len(texts)

        yield pd.Series(predictions)

def ejecutar_sentimiento(df_youtube, df_reddit):
    logger.info(">>> Aplicando modelo de sentimiento BETO, Optimizado Pandas UDF")
    
    yt_sent = df_youtube.withColumn("sentimiento", analizar_sentimiento_beto("comment"))
    rd_sent = df_reddit.withColumn("sentimiento", analizar_sentimiento_beto("comment"))
    
    load_sentiment(yt_sent, rd_sent)
    
    logger.info(">>> Análisis de sentimiento completado y guardado en HDFS.")
    return yt_sent, rd_sent