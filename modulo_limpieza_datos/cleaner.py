import re
import unicodedata
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, trim, length, regexp_replace

spam_words = [
    "suscribete", "suscríbete", "siguenos", "sígueme",
    "whatsapp", "gana dinero", "haz clic", "curso online", "gratis",
    "accede a nuestro curso", "link en la bio", "dale like y comparte",
    "promocion exclusiva", "visita mi canal", "invierte ya", "oferta limitada",
    "haz tu pedido aqui", "llama ya", "descuento especial", "envio gratis",
    "trabaja desde casa", "gana dinero rapido", "ingresos pasivos", "hazte rico",
    "multiplica tu dinero", "inversion segura", "entra a este link", "visita mi pagina",
    "sigue el enlace", "pagina oficial", "suscribete ahora", "dale follow", "comparte con tus amigos",
    "ventas por whatsapp", "contáctame al inbox", "telegram", "crypto", "bitcoin", "usdt", "ahahahahhahahahaha"
]

pattern = "|".join([re.escape(w) for w in spam_words])

def normalize_text(text: str) -> str:
    if text is None:
        return ""
    text = text.lower().strip()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"@\w+", "", text)
    text = re.sub(r"#\w+", "", text)
    text = re.sub(r"[^\w\sáéíóúñ]", "", text)
    text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    return text.strip()

from pyspark.sql.functions import udf
from pyspark.sql.types import StringType

normalize_udf = udf(normalize_text, StringType())

def clean_comments_youtube(df: DataFrame) -> DataFrame:
    df = df.withColumn("comment", normalize_udf(col("comment")))
    df = df.filter(length(trim(col("comment"))) > 2)
    df = df.filter(~col("comment").rlike(pattern))
    df = df.dropDuplicates(["content_id","comment"])
    return df.select("content_id","comment","published_date","likes")

def clean_comments_reddit(df: DataFrame) -> DataFrame:
    df = df.withColumn("comment", normalize_udf(col("comment")))
    df = df.filter(length(trim(col("comment"))) > 2)
    df = df.filter(~col("comment").rlike(pattern))
    df = df.dropDuplicates(["content_id","comment"])
    return df.select("content_id","comment","published_date","score")
