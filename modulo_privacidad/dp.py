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
    sensitivity = 1
    scale = sensitivity / epsilon

    noise_udf = F.udf(lambda x: float(x) + laplace_noise(scale), "double")

    return df.withColumn(col_name, noise_udf(F.col(col_name)))


# Aplica ruido a todas las columnas numéricas seleccionadas
def dp_protect(df: DataFrame, cols: list, epsilon: float = 1.0) -> DataFrame:
    """
    Aplica DP a múltiples columnas numéricas.
    Antes de aplicar el ruido, convierte la columna a double para evitar que Spark la mantenga como string.
    """
    for c in cols:
        # Convertir a doble ANTES de aplicar ruido
        df = df.withColumn(c, F.col(c).cast("double"))
        
        # Aplicar el ruido
        df = dp_add_noise(df, c, epsilon)
    
    return df
