from pyspark.sql import DataFrame

def save_parquet(df: DataFrame, out_path: str, mode: str = "overwrite"):
    df.write.mode(mode).parquet(out_path)
    print(f"Datos guardados en: {out_path}")

def load_json(spark, path: str):
    return spark.read.json(path, multiLine=True)
