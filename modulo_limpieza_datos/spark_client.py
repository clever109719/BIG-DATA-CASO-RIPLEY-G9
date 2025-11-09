from pyspark.sql import SparkSession
import os

def get_spark(app_name="LimpiezaDatosRipley"):
    # -----------------------------
    # Configurar Python para Spark
    # -----------------------------
    python_path = "/home/fab/BIG-DATA-CASO-RIPLEY-G9/proyectoripley_env/bin/python"
    os.environ["PYSPARK_PYTHON"] = python_path        # Para los workers
    os.environ["PYSPARK_DRIVER_PYTHON"] = python_path # Para el driver

    # Crear SparkSession
    spark = SparkSession.builder \
        .appName(app_name) \
        .getOrCreate()
    
    return spark
