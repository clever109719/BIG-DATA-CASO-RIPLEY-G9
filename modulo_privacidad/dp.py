import pyspark.sql.functions as F
from pyspark.sql import DataFrame
import numpy as np

# ---------------------------
# MECANISMO LAPLACE (epsilon-DP)
# ---------------------------
def laplace_noise(scale: float):
    return np.random.laplace(loc=0.0, scale=scale)

# Aplica ruido a columnas numéricas
def dp_add_noise(df: DataFrame, col_name: str, epsilon: float) -> DataFrame:
    """
    Aplica Privacidad Diferencial a una columna numérica en un DataFrame Spark.
    Agrega ruido Laplace calibrado con epsilon.
    """

    # Sensibilidad para conteos y sumas (Δf = 1)
    sensitivity = 1  
    scale = sensitivity / epsilon

    # Registrar UDF de ruido
    noise_udf = F.udf(lambda x: float(x) + laplace_noise(scale))

    return df.withColumn(col_name, noise_udf(F.col(col_name)))

# Aplica ruido a todas las columnas numéricas seleccionadas
def dp_protect(df: DataFrame, cols: list, epsilon: float = 1.0) -> DataFrame:
    """
    Aplica DP a múltiples columnas numéricas.
    """
    for c in cols:
        df = dp_add_noise(df, c, epsilon)
    return df
