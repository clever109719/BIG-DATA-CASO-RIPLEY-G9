from spark_client import get_spark
from cleaner import clean_comments
import config
from pyspark.sql.functions import explode, col, lit

def main():
    spark = get_spark()

    print("Leyendo datos crudos desde HDFS...")
    df_youtube = spark.read.json(config.RAW_YT_PATH, multiLine=True)
    df_reddit = spark.read.json(config.RAW_RD_PATH, multiLine=True)

    # ---- YouTube ----
    df_youtube = df_youtube.withColumn("comment", explode(col("comments"))) \
        .select(
            col("id").alias("content_id"),
            col("title"),
            col("comment")
        ) \
        .withColumn("source", lit("youtube"))

    # ---- Reddit ----
    df_reddit = df_reddit.withColumn("comment", explode(col("comments"))) \
        .select(
            col("id").alias("content_id"),
            col("title"),
            col("comment")
        ) \
        .withColumn("source", lit("reddit"))

    # ---- Unir ambos ----
    df_union = df_youtube.unionByName(df_reddit)

    print("Total de comentarios antes de limpieza:", df_union.count())

    print("Aplicando limpieza y normalización...")
    df_clean = clean_comments(df_union)

    print("Total de comentarios después de limpieza:", df_clean.count())

    print("Guardando datos procesados en HDFS...")
    df_clean.write.mode("overwrite").parquet(config.PROCESSED_PATH)

    print(f"Limpieza completada. Datos en: {config.PROCESSED_PATH}")

    spark.stop()


if __name__ == "__main__":
    main()
