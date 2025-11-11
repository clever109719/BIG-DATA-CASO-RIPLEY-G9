from modulo_carga.loader import save_parquet
from modulo_carga.config import (
    TEND_YT_PATH,
    TEND_RD_PATH,
)

def load_tend(yt_palabras, yt_rangos, yt_eng, yt_avg,
              rd_palabras, rd_rangos, rd_eng, rd_avg):
    """
    Guarda los resultados analíticos de tendencias y participación en HDFS.
    Se almacenan 4 archivos por fuente: palabras, rangos, engagement y promedio.
    """

    print("Guardando resultados de YouTube en HDFS...")
    save_parquet(yt_palabras, TEND_YT_PATH.replace(".parquet", "_palabras.parquet"))
    save_parquet(yt_rangos,   TEND_YT_PATH.replace(".parquet", "_rangos.parquet"))
    save_parquet(yt_eng,      TEND_YT_PATH.replace(".parquet", "_engagement.parquet"))
    save_parquet(yt_avg,      TEND_YT_PATH.replace(".parquet", "_promedio.parquet"))

    print("Guardando resultados de Reddit en HDFS...")
    save_parquet(rd_palabras, TEND_RD_PATH.replace(".parquet", "_palabras.parquet"))
    save_parquet(rd_rangos,   TEND_RD_PATH.replace(".parquet", "_rangos.parquet"))
    save_parquet(rd_eng,      TEND_RD_PATH.replace(".parquet", "_engagement.parquet"))
    save_parquet(rd_avg,      TEND_RD_PATH.replace(".parquet", "_promedio.parquet"))

    print("Datos de tendencias y participación guardados correctamente en HDFS (/user/ripley/analytics).")