from pyspark.sql import functions as F, Window
from pyspark.sql import DataFrame

# Palabras vacías o stopwords comunes en español (artículos, pronombres, verbos, etc.)
# Se ampliaron con términos que no aportan al contexto de tendencias y participación
STOPWORDS_ES = set("""
a al algo algunas algunos ante antes aquel aquella aquellas aquellos aqui ahí asi aun aunque bajo bien cada casi como con contra cual cuales cualquier cuando de del desde donde dos el ella ellas ellos en entre era erais eramos eran eres es esa esas ese eso esos esta estaba estabais estabamos estaban estais estamos estan estar este estos fue fueron fui fuimos ha habeis haber habia habiais habiamos habian habra habran habre habreis habremos habria habriais habriamos habrian hago hasta hay la las le les lo los mas más me mi mia mias mientras mio mios mis mucha muchas mucho muchos muy nada ni no nos nosotras nosotros nuestra nuestras nuestro nuestros nunca o os otra otras otro otros para pero poco por porque que qué quien quienes se sea sean segun ser si siempre sino sobre soy su sus tal tambien también tampoco tan tanta tantas tanto tantos te tener tengo ti tu tus tuya tuyas tuyo tuyos un una uno unos vosotras vosotros ya y yo ahora solo sola solos solas hola porfavor porfa oye oigan bueno buenas ok vale tengo tienes tiene tenemos tienen puedo puedes puede pueden podria podrias podria podrian hacer hace hacen hice hicieron haremos haran comprar compro compre nada mismo mas menos puede pueden son the está estoy estas estamos están decir dice dicen dicho dicho esto eso alguien alguno alguna algunas algunos aquel aquella aquellas aquellos etc mismo entonces ese esa eso esta esto estaba estaban estaba este estos así ahí aquí allí bueno parece parece parece pues era eres eres estaba estaba estoy dice decir diciendo decirá dicen dijeron dicho diciendo durante dentro hacia hasta hasta mientras donde allí ahí además así aunque sino según también sin embargo entonces incluso luego etc algo alguna alguno algunas algunos etc veces tipo cada todos todas todo toda aún muy tanto tan otro otra otros otras alguien algo algún alguno algunos ninguna ningún ni nada nunca jamás ninguno ninguna además tampoco pues pues ahí eso esta está estos estas este este esta esto estaban estaban estaría sería serían será será eres soy estamos están estuvo estuvo estuvo están estábamos estaban estoy estaba está estábamos etc
""".split())

# Palabras importantes del dominio que deben mantenerse aunque estén en stopwords
DOMINIO_KEEP = {
    "ripley", "tarjeta", "banco", "credito", "interes", "intereses", "app", "aplicacion", "web", "pagina",
    "producto", "productos", "servicio", "servicios", "atencion", "postventa", "garantia",
    "precio", "precios", "oferta", "ofertas", "promocion", "promociones", "descuento", "descuentos",
    "entrega", "envio", "despacho", "tienda", "tiendas", "cambio", "devolucion", "reembolso",
    "stock", "pago", "pagos", "compra", "compras", "pedido", "pedidos", "sucursal", "delivery"
}


# Frecuencia de palabras por fuente (tendencia temática)
def tendencia_palabras(df: DataFrame, fuente: str) -> DataFrame:
    # Separa los comentarios palabra por palabra y limpia los caracteres no alfabéticos
    palabras = (
        df.withColumn("palabra", F.explode(F.split(F.lower(F.col("comment")), r"\s+")))
          .withColumn("palabra", F.regexp_replace("palabra", r"[^a-záéíóúñ]", ""))
          .filter(F.length("palabra") > 2)
    )

    # Función auxiliar para descartar palabras irrelevantes o verbos en infinitivo
    def es_valida(p):
        if not p:
            return False
        if p in DOMINIO_KEEP:
            return True
        if p in STOPWORDS_ES:
            return False
        if p.endswith(("ar", "er", "ir")):
            return False
        return True

    es_valida_udf = F.udf(es_valida, "boolean")
    palabras_filtradas = palabras.filter(es_valida_udf(F.col("palabra")))

    # Calcula la frecuencia de cada palabra
    freq = palabras_filtradas.groupBy("palabra").agg(F.count("*").alias("frecuencia"))

    # Determina el sentimiento predominante por palabra
    sent_por_pal = (
        palabras_filtradas.groupBy("palabra", "sentimiento")
        .agg(F.count("*").alias("c"))
        .withColumn("rnk", F.row_number().over(
            Window.partitionBy("palabra").orderBy(F.desc("c"))
        ))
        .filter(F.col("rnk") == 1)
        .select("palabra", F.col("sentimiento").alias("sentimiento_pred"))
    )

    # Obtiene las fechas en las que se mencionó cada palabra
    fechas = (
        palabras_filtradas.groupBy("palabra")
        .agg(
            F.min("published_date").alias("fecha_inicio"),
            F.max("published_date").alias("fecha_fin")
        )
        .withColumn(
            "rango_fecha",
            F.concat_ws(" - ",
                F.col("fecha_inicio").cast("string"),
                F.col("fecha_fin").cast("string"))
        )
    )

    # Une toda la información en un único DataFrame
    out = (
        freq.join(sent_por_pal, "palabra", "left")
            .join(fechas, "palabra", "left")
            .withColumnRenamed("sentimiento_pred", "sentimiento")
            .withColumn("fuente", F.lit(fuente))
            .orderBy(F.desc("frecuencia"))
    )
    return out


# Promedio de likes o score por fuente (participación general)
def participacion_promedio(df: DataFrame, fuente: str, col_metric: str) -> DataFrame:
    # Calcula el promedio general de interacción por fuente
    df_avg = (
        df.groupBy()
          .agg(F.avg(F.col(col_metric)).alias("promedio_interaccion"))
          .withColumn("promedio_interaccion", F.round(F.col("promedio_interaccion"), 0).cast("int"))
          .withColumn("fuente", F.lit(fuente))
    )
    return df_avg


# Distribución de likes o score por rangos (participación estructurada)
def distribucion_rangos(df: DataFrame, fuente: str, col_metric: str) -> DataFrame:
    # Clasifica los comentarios en rangos según su nivel de interacción
    df_rangos = (
        df.withColumn(
            "rango_interaccion",
            F.when(F.col(col_metric) <= 1, "0-1")
             .when((F.col(col_metric) >= 2) & (F.col(col_metric) <= 5), "2-5")
             .when((F.col(col_metric) >= 6) & (F.col(col_metric) <= 10), "6-10")
             .otherwise("10+")
        )
        .groupBy("rango_interaccion")
        .agg(F.count("*").alias("cantidad"))
        .withColumn("fuente", F.lit(fuente))
        .orderBy("rango_interaccion")
    )
    return df_rangos


# Promedio de likes/score por longitud del comentario (engagement)
def engagement_por_longitud(df: DataFrame, fuente: str, col_metric: str) -> DataFrame:
    # Calcula el nivel promedio de interacción según la longitud del comentario
    df_len = (
        df.withColumn("longitud", F.length(F.col("comment")))
          .withColumn(
              "rango_longitud",
              F.when(F.col("longitud") < 50, "Corto (<50)")
               .when((F.col("longitud") >= 50) & (F.col("longitud") <= 150), "Medio (50-150)")
               .otherwise("Largo (>150)")
          )
          .groupBy("rango_longitud")
          .agg(F.round(F.avg(F.col(col_metric)), 2).alias("promedio_interaccion"))
          .withColumn("fuente", F.lit(fuente))
          .orderBy("rango_longitud")
    )
    return df_len