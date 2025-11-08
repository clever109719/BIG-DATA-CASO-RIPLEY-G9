from pyspark.sql import functions as F
from pyspark.sql import DataFrame

# Frecuencia de palabras por fuente (tendencia temática)
def tendencia_palabras(df: DataFrame, fuente: str) -> DataFrame:
    # Divide los comentarios en palabras, cuenta frecuencia y agrega fuente
    df_palabras = (
        df.withColumn("palabra", F.explode(F.split(F.col("comment"), "\\s+")))
          .groupBy("palabra")
          .agg(F.count("*").alias("frecuencia"))
          .filter(F.length("palabra") > 2)
          .orderBy(F.desc("frecuencia"))
          .withColumn("fuente", F.lit(fuente))
    )
    return df_palabras


# Promedio de likes o score por fuente (participación general)
def participacion_promedio(df: DataFrame, fuente: str, col_metric: str) -> DataFrame:
    # Calcula el promedio de interacción por fuente
    df_avg = (
        df.groupBy()
          .agg(F.avg(F.col(col_metric)).alias("promedio_interaccion"))
          .withColumn("fuente", F.lit(fuente))
    )
    return df_avg


# Distribución de likes o score por rangos (participación estructurada)
def distribucion_rangos(df: DataFrame, fuente: str, col_metric: str) -> DataFrame:
    # Clasifica la cantidad de interacciones por rangos
    df_rangos = (
        df.withColumn(
            "rango_interaccion",
            F.when(F.col(col_metric) <= 1, "0-1")
             .when((F.col(col_metric) > 1) & (F.col(col_metric) <= 5), "2-5")
             .when((F.col(col_metric) > 5) & (F.col(col_metric) <= 10), "6-10")
             .otherwise("10+")
        )
        .groupBy("rango_interaccion")
        .agg(F.count("*").alias("cantidad"))
        .withColumn("fuente", F.lit(fuente))
        .orderBy(F.col("rango_interaccion"))
    )
    return df_rangos


# Promedio de likes por longitud del comentario (profundidad del engagement)
def engagement_por_longitud(df: DataFrame, fuente: str, col_metric: str) -> DataFrame:
    # Relaciona longitud del comentario con nivel promedio de interacción
    df_len = (
        df.withColumn("longitud", F.length(F.col("comment")))
          .withColumn(
              "rango_longitud",
              F.when(F.col("longitud") < 50, "Corto (<50)")
               .when((F.col("longitud") >= 50) & (F.col("longitud") < 150), "Medio (50-150)")
               .otherwise("Largo (>150)")
          )
          .groupBy("rango_longitud")
          .agg(F.avg(F.col(col_metric)).alias("promedio_interaccion"))
          .withColumn("fuente", F.lit(fuente))
          .orderBy(F.col("rango_longitud"))
    )
    return df_len