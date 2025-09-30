from spark_client import get_spark
from cleaner import clean_comments_youtube, clean_comments_reddit
import config
from pyspark.sql.functions import explode, col, lit, to_date

def main():
    spark = get_spark()

    print("Leyendo datos crudos desde HDFS...")

    # Cargar datos de YouTube
    df_youtube = spark.read.json(config.RAW_YT_PATH, multiLine=True)
    # Expandir comentarios
    df_youtube = df_youtube.withColumn("comment", explode(col("comments"))) \
        .select(
            col("video_id").alias("content_id"),
            col("comment.text").alias("comment"),
            col("comment.publishedAt").alias("published_date"),
            col("comment.likes").alias("likes")
        )
    # Convertir fecha a YYYY-MM-DD
    df_youtube = df_youtube.withColumn("published_date", to_date(col("published_date")))
    print("Total comentarios YouTube antes de limpieza:", df_youtube.count())
    df_youtube_clean = clean_comments_youtube(df_youtube)
    print("Total comentarios YouTube después de limpieza:", df_youtube_clean.count())
    # Guardar Parquet
    df_youtube_clean.write.mode("overwrite").parquet(config.PROCESSED_YT_PATH)
    print(f"YouTube limpio guardado en: {config.PROCESSED_YT_PATH}")



    # Cargar datos de Reddit
    df_reddit = spark.read.json(config.RAW_RD_PATH, multiLine=True)
    # Expandir comentarios y replies
    df_reddit = df_reddit.select(
        col("id").alias("content_id"),
        explode(col("comments")).alias("comment")
    ).select(
        col("content_id"),
        col("comment.id").alias("comment_id"),
        col("comment.text").alias("comment"),
        col("comment.publishedAt").alias("published_date"),
        col("comment.score").alias("score"),
        col("comment.replies").alias("replies")
    )

    # Expandir replies como comentarios independientes
    df_replies = df_reddit.select(
        col("content_id"),
        explode(col("replies")).alias("reply")
    ).select(
        col("content_id"),
        col("reply.id").alias("comment_id"),
        col("reply.text").alias("comment"),
        col("reply.publishedAt").alias("published_date"),
        col("reply.score").alias("score")
    )

    # Unir comentarios y replies
    df_reddit_all = df_reddit.select("content_id","comment_id","comment","published_date","score").unionByName(df_replies)
    # Convertir fecha a YYYY-MM-DD
    df_reddit_all = df_reddit_all.withColumn("published_date", to_date(col("published_date")))

    print("Total comentarios Reddit antes de limpieza:", df_reddit_all.count())
    df_reddit_clean = clean_comments_reddit(df_reddit_all)
    print("Total comentarios Reddit después de limpieza:", df_reddit_clean.count())
    # Guardar Parquet
    df_reddit_clean.write.mode("overwrite").parquet(config.PROCESSED_RD_PATH)
    print(f"Reddit limpio guardado en: {config.PROCESSED_RD_PATH}")

    spark.stop()

if __name__ == "__main__":
    main()
