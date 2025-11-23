import logging
import sys
from modulo_extraccion_datos.extraction import extraction
from modulo_limpieza_datos.transformation import transformation
from modulo_limpieza_datos.spark_client import get_spark
from modulo_machine_learning.sentiment_process import sentiment_process
from modulo_tend.process_tend import process_tend
from modulo_carga.load import load

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),                 
        logging.FileHandler("pipeline_run.log", mode='a')  
    ],
    force=True
)


logger = logging.getLogger("Main_Orquestador")

def main():

    logger.info("\n" + "="*50)
    logger.info(">>> NUEVA EJECUCIÓN DEL PIPELINE INICIADA <<<")
    logger.info("="*50)

    # --- Extracción ---
    # logger.info(">>> INICIANDO EXTRACCIÓN")
    # extraction()

    # --- TRANSFORMACIÓN ---
    logger.info(">>> INICIANDO TRANSFORMACIÓN")
    spark = get_spark()
    
    try:
        yt_clean, rd_clean = transformation(spark)
        logger.info("Transformación finalizada correctamente.")
    except Exception as e:
        logger.error(f"Error crítico en Transformación: {e}")
        spark.stop()
        sys.exit(1)
    
    # --- CARGA ---
    logger.info(">>> INICIANDO CARGA")
    load(yt_clean, rd_clean)

    # --- MACHINE LEARNING (Análisis de Sentimiento) ---
    logger.info(">>> INICIANDO ANÁLISIS DE SENTIMIENTO")
    sentiment_process(spark)

    # --- TENDENCIAS Y PARTICIPACIÓN ---
    logger.info(">>> INICIANDO ANÁLISIS DE TENDENCIAS Y PARTICIPACIÓN")
    process_tend(spark)

    spark.stop()
    logger.info(">>> PIPELINE COMPLETADO EXITOSAMENTE")

if __name__ == "__main__":
    main()