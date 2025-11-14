from modulo_carga.loader import save_parquet
from modulo_carga.config import ANALYTICS_YT_PATH, ANALYTICS_RD_PATH

def load_sentiment(yt_sent, rd_sent):

    save_parquet(yt_sent, ANALYTICS_YT_PATH)
    save_parquet(rd_sent, ANALYTICS_RD_PATH)
