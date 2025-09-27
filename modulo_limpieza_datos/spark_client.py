from pyspark.sql import SparkSession

def get_spark(app_name="LimpiezaDatosRipley"):
    spark = SparkSession.builder \
        .appName(app_name) \
        .getOrCreate()
    return spark
