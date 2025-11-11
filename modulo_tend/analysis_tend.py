from pyspark.sql import functions as F, Window
from pyspark.sql import DataFrame

# STOPWORDS
STOPWORDS_EN = set("""
actually alien aliens amigo and anos anything app año años about alguien all also are así
being before bianca but campeonato championship could day de dice did días día está estas
estoy esto for from hace had has have hacen his how into its just like luego mas más more
most not only out para por puedo puedes she sin some son still that the their them then him
they this tienen tiene todos todo two was were what when who with would you back bad balor
best big braun bunny can cant caso casa characters charlotte contenders corre than any very
creo dan damian debo deja después dijieron didnt doesnt dont dunne error es even every etc
extendida favor female fiel fiend film finn first forma getting get gente good going great
hoy igual kevin kai know lana last look looks lot love mal make makes matt mejor mes meses
mil mismo movie movies much mujer naomi nadie night now nuevo nxt omos one paso pasa peor
person poseidon pregunta primero priesto puede pues quiero queen real really replay rhea
riddle right sabe sale saludos say see sernac shes show sigo space strowman strong styles
take tag tengo theres thats think title usar van vez video videos voy wasnt way well will
win women womens wwe youre time because your since different something too same there off
there been work why down come without enough probably should always main story team male
away wins which priest edge ripleys
""".split())

STOPWORDS_ES = set("""
a al algo algunas algunos ante antes aquel aquella aquellas aquellos aqui ahí asi aun
aunque bajo bien cada casi como con contra cual cuales cualquier cuando de del desde
donde dos el ella ellas ellos en entre era erais eramos eran eres es esa esas ese eso
esos esta estaba estabais estabamos estaban estais estamos estan estar este estos fue
fueron fui fuimos ha habeis haber habia habiais habiamos habian habra habran habre habreis
habremos habria habriais habriamos habrian hago hasta hay la las le les lo los mas más
me mi mia mias mientras mio mios mis mucha muchas mucho muchos muy nada ni no nos nosotras
nosotros nuestra nuestras nuestro nuestros nunca o os otra otras otro otros para pero poco
por porque que qué quien quienes se sea sean segun ser si siempre sino sobre soy su sus tal
tambien también tampoco tan tanta tantas tanto tantos te tener tengo ti tu tus tuya tuyas
tuyo tuyos un una uno unos vosotras vosotros ya y yo ahora solo sola solos solas hola gracias
porfavor porfa oye oigan bueno buenas buenos ok vale
""".split())

STOPWORDS_ALL = STOPWORDS_ES.union(STOPWORDS_EN)

DOMINIO_KEEP = {
    "ripley", "tarjeta", "tienda", "banco", "credito", "servicio",
    "producto", "precio", "compra", "oferta", "promocion", "descuento",
    "garantia", "entrega", "envio", "devolucion", "reembolso", "delivery"
}

# TENDENCIA DE PALABRA
def tendencia_palabras(df: DataFrame, fuente: str) -> DataFrame:
    palabras = (
        df.withColumn("palabra", F.explode(F.split(F.lower(F.col("comment")), r"\s+")))
          .withColumn("palabra", F.regexp_replace("palabra", r"[^a-záéíóúñ]", ""))
          .filter(F.length("palabra") > 2)
    )

    def es_valida(p):
        if not p:
            return False
        if p in DOMINIO_KEEP:
            return True
        if p in STOPWORDS_ALL:
            return False
        if p.endswith(("ar", "er", "ir")):
            return False
        return True

    es_valida_udf = F.udf(es_valida, "boolean")
    palabras_filtradas = palabras.filter(es_valida_udf(F.col("palabra")))

    freq = palabras_filtradas.groupBy("palabra").agg(F.count("*").alias("frecuencia"))

    sent_por_pal = (
        palabras_filtradas.groupBy("palabra", "sentimiento")
        .agg(F.count("*").alias("c"))
        .withColumn("rnk", F.row_number().over(
            Window.partitionBy("palabra").orderBy(F.desc("c"))
        ))
        .filter(F.col("rnk") == 1)
        .select("palabra", F.col("sentimiento").alias("sentimiento_pred"))
    )

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

    out = (
        freq.join(sent_por_pal, "palabra", "left")
            .join(fechas, "palabra", "left")
            .withColumnRenamed("sentimiento_pred", "sentimiento")
            .withColumn("fuente", F.lit(fuente))
            .orderBy(F.desc("frecuencia"))
    )
    return out

# DISTRIBUCIÓN POR RANGOS
def distribucion_rangos(df: DataFrame, fuente: str, col_metric: str) -> DataFrame:
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

#ENGAGEMENT POR LONGITUD
def engagement_por_longitud(df: DataFrame, fuente: str, col_metric: str) -> DataFrame:
    df_len = (
        df.withColumn("longitud", F.length(F.col("comment")))
          .withColumn(
              "rango_longitud",
              F.when(F.col("longitud") < 50, "Corto (<50)")
               .when((F.col("longitud") >= 50) & (F.col("longitud") <= 150), "Medio (50-150)")
               .otherwise("Largo (>150)")
          )
          .groupBy("rango_longitud")
          .agg(
              F.count("*").alias("n_comentarios"),
              F.round(F.avg(F.col(col_metric)), 2).alias("promedio_interaccion"),
              F.sum(F.col(col_metric)).alias("suma_interaccion")
          )
          .withColumn(
              "total_interaccion_estimado",
              F.round(F.col("promedio_interaccion") * F.col("n_comentarios"), 2)
          )
          .withColumn("fuente", F.lit(fuente))
          .orderBy("rango_longitud")
    )
    return df_len

# PARTICIPACIÓN PROMEDIO GENERAL
def participacion_promedio(df: DataFrame, fuente: str, col_metric: str) -> DataFrame:
    df_avg = (
        df.groupBy()
          .agg(
              F.count("*").alias("n_total"),
              F.sum(F.col(col_metric)).alias("suma_interaccion"),
              F.avg(F.col(col_metric)).alias("promedio_interaccion")
          )
          .withColumn("promedio_interaccion", F.round(F.col("promedio_interaccion"), 2))
          .withColumn("suma_interaccion", F.round(F.col("suma_interaccion"), 2))
          .withColumn("fuente", F.lit(fuente))
    )
    return df_avg