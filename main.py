from modulo_extraccion_datos import extraction
from modulo_limpieza_datos import transformation
from modulo_limpieza_datos.spark_client import get_spark
from modulo_carga import load

def main():
    # --- Extracción ---
    print(">>> INICIANDO EXTRACCIÓN")
    extraction()

    # --- TRANSFORMACIÓN ---
    print(">>> INICIANDO TRANSFORMACIÓN")
    spark = get_spark()
    transformation(spark)

    # --- CARGA ---
    print(">>> INICIANDO CARGA")
    load()

    spark.stop()
    print(">>> PIPELINE COMPLETADO")

    if __name__ == "_main_":
        main()