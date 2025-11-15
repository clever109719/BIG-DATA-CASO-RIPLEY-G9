# Rutas para guardado de datos en HDFS

# Procesados (limpios)
PROCESSED_YT_PATH = "hdfs://localhost:9000/user/ripley/processed/ripley_youtube_clean.parquet"
PROCESSED_RD_PATH = "hdfs://localhost:9000/user/ripley/processed/ripley_reddit_clean.parquet"

# Analíticos (con sentimiento)
ANALYTICS_YT_PATH = "hdfs://localhost:9000/user/ripley/analytics/ripley_youtube_sentiment.parquet"
ANALYTICS_RD_PATH = "hdfs://localhost:9000/user/ripley/analytics/ripley_reddit_sentiment.parquet"

# Analíticos (tendencias y participación)
TEND_YT_PATH = "hdfs://localhost:9000/user/ripley/analytics/ripley_youtube_tendencias.parquet"
TEND_RD_PATH = "hdfs://localhost:9000/user/ripley/analytics/ripley_reddit_tendencias.parquet"