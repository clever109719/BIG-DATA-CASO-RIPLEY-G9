from modulo_extraccion_datos.extraction import extraction
from modulo_limpieza_datos.transformation import transformation
from modulo_limpieza_datos.spark_client import get_spark
from modulo_machine_learning.sentiment_process import sentiment_process
from modulo_tend.process_tend import process_tend
from modulo_carga.load import load

def main():
    # --- Extracción ---
    #print(">>> INICIANDO EXTRACCIÓN")
    #extraction()

    # --- TRANSFORMACIÓN ---
    print(">>> INICIANDO TRANSFORMACIÓN")
    spark = get_spark()
    yt_clean, rd_clean = transformation(spark)

    # --- CARGA ---
    print(">>> INICIANDO CARGA")
    load(yt_clean, rd_clean)

    # --- MACHINE LEARNING (Análisis de Sentimiento) ---
    print(">>> INICIANDO ANÁLISIS DE SENTIMIENTO")
    sentiment_process(spark)

    # --- TENDENCIAS Y PARTICIPACIÓN ---
    print(">>> INICIANDO ANÁLISIS DE TENDENCIAS Y PARTICIPACIÓN")
    process_tend(spark)

    spark.stop()
    print(">>> PIPELINE COMPLETADO")

if __name__ == "__main__":
    main()
