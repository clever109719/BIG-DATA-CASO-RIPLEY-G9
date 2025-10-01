from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    col, length, trim, explode, to_date, lower, regexp_replace, explode_outer
)
from pyspark.sql import functions as F

# -----------------------
# Patrón de limpieza general (URLs, espacios vacíos)
# -----------------------
pattern = r"^(http|www|\s*)$"

# -----------------------
# Palabras clave de spam (ajustables)
# -----------------------
SPAM_KEYWORDS = [
    "suscríbete", "subscribe", "sígueme", "follow me",
    "dale like", "me gusta", "comparte", "haz clic", "click here",
    "link en bio", "enlace", "promo", "gratis", "free", "giveaway",
    "visita mi canal", "canal", "youtube.com", "instagram", "tiktok",
    "dinero fácil", "trabaja desde casa", "oferta", "descuento",
    "100%", "garantizado", "spam", "http", "www", "👇", "👆",
    "únete", "registrate", "hazlo ahora", "descarga", "download",
    "ganar dinero", "no te pierdas", "nuevo video", "nuevo vídeo", "ahahahahhahahahaha"
]

# -----------------------
# Normalización de columna
# -----------------------
def normalize_column(df: DataFrame, colname: str) -> DataFrame:
    """
    Convierte el texto a minúsculas, quita espacios, símbolos y caracteres especiales.
    """
    return (
        df.withColumn(
            colname,
            lower(trim(regexp_replace(col(colname), r"[^a-zA-Z0-9áéíóúñ\s]", "")))
        )
    )

# -----------------------
# Filtro de spam textual
# -----------------------
def filter_spam(df: DataFrame, colname: str = "comment") -> DataFrame:
    """
    Elimina comentarios que contengan palabras o frases típicas de spam.
    """
    spam_pattern = "|".join([f"(?i){word}" for word in SPAM_KEYWORDS])
    return df.filter(~col(colname).rlike(spam_pattern))

# -----------------------
# Limpieza para YouTube
# -----------------------
def clean_comments_youtube(df: DataFrame) -> DataFrame:
    df = normalize_column(df, "comment")
    df = df.filter(length(trim(col("comment"))) > 2)
    df = df.filter(~col("comment").rlike(pattern))
    df = filter_spam(df, "comment")  # Filtro de spam agregado
    df = df.dropDuplicates(["content_id", "comment"])
    return df.select("content_id", "comment", "published_date", "likes")

# -----------------------
# Limpieza para Reddit
# -----------------------
def clean_comments_reddit(df: DataFrame) -> DataFrame:
    df = normalize_column(df, "comment")
    df = df.filter(length(trim(col("comment"))) > 2)
    df = df.filter(~col("comment").rlike(pattern))
    df = filter_spam(df, "comment")  # Filtro de spam agregado
    df = df.dropDuplicates(["content_id", "comment"])
    return df.select("content_id", "comment", "published_date", "score")

# -----------------------
# Procesamiento YouTube
# -----------------------
def process_youtube(spark, raw_path: str) -> DataFrame:
    """
    Lee datos crudos de YouTube desde HDFS, los transforma y limpia.
    """
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
    """
    Lee datos crudos de Reddit desde HDFS, los transforma y limpia.
    """
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

    # Desanidar replies
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

    # Combinar comentarios y respuestas
    df_all = df.select("content_id", "comment_id", "comment", "published_date", "score") \
               .unionByName(df_replies)

    df_all = df_all.withColumn("published_date", to_date(col("published_date")))

    print("Total comentarios Reddit antes de limpieza:", df_all.count())
    df_clean = clean_comments_reddit(df_all)
    print("Total comentarios Reddit después de limpieza:", df_clean.count())

    return df_clean

# -----------------------
# Utilidad para leer JSON
# -----------------------
def load_json(spark, path: str) -> DataFrame:
    return spark.read.json(path, multiLine=True)
