from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    col, length, trim, explode, to_date, lower, regexp_replace, explode_outer
)

# -----------------------
# Patrón de limpieza
# -----------------------
pattern = r"^(http|www|\s*)$"

# -----------------------
# Normalización de columna
# -----------------------
def normalize_column(df: DataFrame, colname: str) -> DataFrame:
    return (
        df.withColumn(
            colname,
            lower(trim(regexp_replace(col(colname), r"[^a-zA-Z0-9áéíóúñ\s]", "")))
        )
    )

# -----------------------
# Limpieza
# -----------------------
def clean_comments_youtube(df: DataFrame) -> DataFrame:
    df = normalize_column(df, "comment")
    df = df.filter(length(trim(col("comment"))) > 2)
    df = df.filter(~col("comment").rlike(pattern))
    df = df.dropDuplicates(["content_id", "comment"])
    return df.select("content_id", "comment", "published_date", "likes")


def clean_comments_reddit(df: DataFrame) -> DataFrame:
    df = normalize_column(df, "comment")
    df = df.filter(length(trim(col("comment"))) > 2)
    df = df.filter(~col("comment").rlike(pattern))
    df = df.dropDuplicates(["content_id", "comment"])
    return df.select("content_id", "comment", "published_date", "score")

# -----------------------
# Procesamiento YouTube
# -----------------------
def process_youtube(spark, raw_path: str) -> DataFrame:
    df = spark.read.json(raw_path, multiLine=True)

    df = df.withColumn("comment", explode_outer(col("comments"))) \
        .select(
            col("video_id").alias("content_id"),
            col("comment.text").alias("comment"),
            col("comment.publishedAt").alias("published_date"),
            col("comment.likes").alias("likes")
        )

    df = df.withColumn("published_date", to_date(col("published_date")))

    print("Total comentarios YouTube antes de limpieza:", df.count())
    df_clean = clean_comments_youtube(df)
    print("Total comentarios YouTube después de limpieza:", df_clean.count())

    return df_clean

# -----------------------
# Procesamiento Reddit
# -----------------------
def process_reddit(spark, raw_path: str) -> DataFrame:
    df = spark.read.json(raw_path, multiLine=True)

    df = df.select(
        col("id").alias("content_id"),
        explode_outer(col("comments")).alias("comment")
    ).select(
        col("content_id"),
        col("comment.id").alias("comment_id"),
        col("comment.text").alias("comment"),
        col("comment.publishedAt").alias("published_date"),
        col("comment.score").alias("score"),
        col("comment.replies").alias("replies")
    )

    df_replies = df.filter(col("replies").isNotNull()) \
        .select(
            col("content_id"),
            explode(col("replies")).alias("reply")
        ).select(
            col("content_id"),
            col("reply.id").alias("comment_id"),
            col("reply.text").alias("comment"),
            col("reply.publishedAt").alias("published_date"),
            col("reply.score").alias("score")
        )

    df_all = df.select("content_id", "comment_id", "comment", "published_date", "score") \
               .unionByName(df_replies)

    df_all = df_all.withColumn("published_date", to_date(col("published_date")))

    print("Total comentarios Reddit antes de limpieza:", df_all.count())
    df_clean = clean_comments_reddit(df_all)
    print("Total comentarios Reddit después de limpieza:", df_clean.count())

    return df_clean

def load_json(spark, path: str) -> DataFrame:
    return spark.read.json(path, multiLine=True)