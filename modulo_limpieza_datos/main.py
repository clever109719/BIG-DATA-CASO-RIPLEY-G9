from spark_client import get_spark
from cleaner import clean_comments
import config
from pyspark.sql.functions import explode, col

def main():
    spark = get_spark()

    print("Leyendo datos crudos desde HDFS...")
    df_raw = spark.read.json(config.RAW_PATH, multiLine=True)

    # Expandir la lista de comentarios
    df = df_raw.withColumn("comment", explode(col("comments"))) \
               .select(
                   col("id").alias("video_id"),
                   col("title"),
                   col("comment")
               )

    print("Total de comentarios antes de limpieza:", df.count())

    print("Aplicando limpieza y normalización...")
    df_clean = clean_comments(df)

    print("Total de comentarios después de limpieza:", df_clean.count())

    print("Guardando datos procesados en HDFS...")
    df_clean.write.mode("overwrite").json(config.PROCESSED_PATH)

    print(f"Limpieza completada. Datos en: {config.PROCESSED_PATH}")

    spark.stop()

if __name__ == "__main__":
    main()
