from modulo_extraccion_datos.extraction import extraction
from modulo_limpieza_datos.transformation import transformation
from modulo_limpieza_datos.spark_client import get_spark
from modulo_carga.load import load

def main():
    # --- Extracción ---
    print(">>> INICIANDO EXTRACCIÓN")
    extraction()

    # --- TRANSFORMACIÓN ---
    print(">>> INICIANDO TRANSFORMACIÓN")
    spark = get_spark()
    yt_clean, rd_clean = transformation(spark)

    # --- CARGA ---
    print(">>> INICIANDO CARGA")
    load(yt_clean, rd_clean)

    spark.stop()
    print(">>> PIPELINE COMPLETADO")

if __name__ == "__main__":
    main()
