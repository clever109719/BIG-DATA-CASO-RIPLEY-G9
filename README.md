# BIG-DATA-CASO-RIPLEY-G9

# Sistema Big Data para Ripley Perú - Análisis de Sentimiento en Redes Sociales

##  Descripción del Proyecto
Este proyecto propone un **Sistema Big Data** orientado al **análisis de sentimiento en redes sociales** para **Ripley Perú**.  

El flujo de datos contempla:

1. **Recolección de comentarios** desde APIs de:
   - YouTube  
   - Reddit     

2. **Almacenamiento en HDFS**  
   - Datos en crudo (`/data/raw`)  
   - Datos procesados (`/data/processed`)  
   - Datos analíticos (`/data/analytics`)  

3. **Procesamiento con Apache Spark / PySpark**  
   - Limpieza y transformación de datos  
   - Análisis de sentimiento y tendencias  
   - Orquestación de recursos mediante **Hadoop YARN**  

4. **Visualización en Power BI**  
   - Dashboards interactivos  
   - Indicadores de sentimiento (positivo, negativo, neutral)  
   - Alertas de posibles crisis de imagen  
   - Métricas sobre campañas digitales  

---

## Objetivos
- Transformar **datos no estructurados** en **información estratégica**.  
- Detectar **tendencias** y **crisis de reputación** en tiempo real.  
- Optimizar campañas de **marketing digital** mediante insights.  
- Comprender mejor las **percepciones y preferencias** de los clientes.  

---

## Stack Tecnológico
- **Hadoop HDFS** → almacenamiento distribuido.  
- **Hadoop YARN** → gestión de recursos del clúster.  
- **Apache Spark / PySpark** → procesamiento masivo de datos.  
- **APIs (YouTube, Reddit, Google, Facebook)** → extracción de comentarios.  
- **Apache Superset** → visualización e inteligencia de negocio.  

---

# Primeros Pasos - Sistema Big Data Ripley Perú

Este documento describe la **configuración inicial** necesaria para levantar el entorno de trabajo en Debian 12 para el proyecto Big Data de análisis de sentimiento en redes sociales.

---

## Requisitos previos
Antes de comenzar asegúrate de tener instalado:
- **Python 3.10+**
- **Hadoop** (con HDFS y YARN)
- **Apache Spark**
- **Java JDK 8 o superior**
- **Git**

---

## PASO A PASO

```bash
## 1. Inicializar hadoop
/opt/hadoop-3.3.6/sbin/start-all.sh

```bash
## 2. CLonar el repositorio
git clone https://github.com/clever109719/BIG-DATA-CASO-RIPLEY-G9.git
cd BIG-DATA-CASO-RIPLEY-G9

```bash
## 3. Crear entorno virtual de Python
python3 -m venv proyectoripley_env

```bash
## 4. Activar el entorno virtual
source proyectoripley_env/bin/activate

```bash
## 5. Instalar dependencias iniciales
pip install -r requirements.txt

```bash
## 6. Para desactivarlo más adelante
deactivate

## 7. Configuración inicial en HDFS

Ejecuta los siguientes comandos para crear la estructura de carpetas en HDFS que usará el proyecto:

```bash
# Crear directorio raíz para el proyecto
hdfs dfs -mkdir -p /user/ripley/raw
hdfs dfs -mkdir -p /user/ripley/processed
hdfs dfs -mkdir -p /user/ripley/analytics

# Permisos (opcional)
hdfs dfs -chmod -R 755 /user/ripley
hdfs dfs -chmod -R 777 /user/ripley/processed

## COMANDOS EXTRAS:
mkdir -p /home/matias/hadoopdata/hdfs/namenode
mkdir -p /home/matias/hadoopdata/hdfs/datanode
chmod -R 700 /home/matias/hadoopdata


## HDFS
hdfs dfs -chmod -R 777 /user/ripley/raw

## Para ir y ver qué hay en /user/ripley/raw:
hdfs dfs -ls /user/ripley/raw

## Para ver el contenido del JSON:
hdfs dfs -cat /user/ripley/raw/ripley_youtube_comments.json | less

## Para copiarlo a tu máquina local 
hdfs dfs -get /user/ripley/raw/ripley_youtube_comments.json .
hdfs dfs -get /user/ripley/raw/ripley_reddit_comments.json .

####
#Importante antes de ejecutar el modulo de limpieza, correr lo siguiente en la consola, tienes que estar en la carpeta raiz
####
echo "export PYTHONPATH=\$PYTHONPATH:\$(pwd)/modulo_limpieza_datos" >> ~/.bashrc
source ~/.bashrc



# Para visualizar los datos ya transformados
## En consola ingresar:
pyspark
## Luego esto para visualizar los comentarios de youtube
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("VerDatosLimpios").getOrCreate()

df_youtube = spark.read.parquet("hdfs://localhost:9000/user/ripley/processed/ripley_youtube_clean.parquet")

print("Total registros YouTube:", df_youtube.count())
df_youtube.printSchema()
df_youtube.show(10, truncate=False)


#Para ver los de reddit
df_reddit = spark.read.parquet("hdfs://localhost:9000/user/ripley/processed/ripley_reddit_clean.parquet")

print("Total registros Reddit:", df_reddit.count())
df_reddit.printSchema()
df_reddit.show(10, truncate=False)



# Con eso veras los datos mas legibles, al ser parquet, esto recalcando unicamente para visualizar los datos

# Para visualizar el analisis de sientimiento
## En consola ingresar:
pyspark
## Luego esto para visualizar los comentarios de youtube
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("VerAnalisisSentimientoYT").getOrCreate()

df_youtube_sent = spark.read.parquet("hdfs://localhost:9000/user/ripley/analytics/ripley_youtube_sentiment.parquet")

df_youtube_sent.printSchema()
df_youtube_sent.show(10, truncate=False)


#Para ver los de reddit
df_reddit_sent = spark.read.parquet("hdfs://localhost:9000/user/ripley/analytics/ripley_reddit_sentiment.parquet")

df_reddit_sent.printSchema()
df_reddit_sent.show(10, truncate=False)

###########################
#### Para presentacion ####
###########################
# 1 inicializar servicios
/opt/hadoop-3.3.6/sbin/start-all.sh

# 2 inicializar entorno
source proyectoripley_env/bin/activate

# 3 ver carpetas hdfs
hdfs dfs -ls /user/ripley

# 4 ver datos crudos
hdfs dfs -ls /user/ripley/raw

# 5 ver contenido de youtube crudo
hdfs dfs -cat /user/ripley/raw/ripley_youtube_comments.json | head -n 20

# 6 ver contenido de reddit crudo
hdfs dfs -cat /user/ripley/raw/ripley_reddit_comments.json | head -n 20

# 7 ver datos procesados
hdfs dfs -ls /user/ripley/processed

#INGRESAR en consola antes de los 2 siguientes comandos
pyspark
# 8 ver contenido de youtube procesado
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("VerDatosLimpios").getOrCreate()

df_youtube = spark.read.parquet("hdfs://localhost:9000/user/ripley/processed/ripley_youtube_clean.parquet")

print("Total registros YouTube:", df_youtube.count())
df_youtube.printSchema()
df_youtube.show(30, truncate=False)

# 9 ver contenido de reddit procesado
df_reddit = spark.read.parquet("hdfs://localhost:9000/user/ripley/processed/ripley_reddit_clean.parquet")

print("Total registros Reddit:", df_reddit.count())
df_reddit.printSchema()
df_reddit.show(10, truncate=False)



# Tendencias y Participación

# En consola ingresar:
pyspark

# Luego esto para visualizar los resultados de YouTube
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("VerAnalisisTendenciasYT").getOrCreate()

# Frecuencia de palabras
df_youtube_pal = spark.read.parquet("hdfs://localhost:9000/user/ripley/analytics/ripley_youtube_tendencias_palabras.parquet")
df_youtube_pal.printSchema()
df_youtube_pal.show(10, truncate=False)

# Distribución de likes por rango
df_youtube_rangos = spark.read.parquet("hdfs://localhost:9000/user/ripley/analytics/ripley_youtube_tendencias_rangos.parquet")
df_youtube_rangos.printSchema()
df_youtube_rangos.show()

# Engagement (likes) promedio por longitud del comentario
df_youtube_eng = spark.read.parquet("hdfs://localhost:9000/user/ripley/analytics/ripley_youtube_tendencias_engagement.parquet")
df_youtube_eng.printSchema()
df_youtube_eng.show()

# Promedio de likes por fuente
df_youtube_prom = spark.read.parquet("hdfs://localhost:9000/user/ripley/analytics/ripley_youtube_tendencias_promedio.parquet")
df_youtube_prom.printSchema()
df_youtube_prom.show()


# Luego esto para visualizar los resultados de Reddit
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("VerAnalisisTendenciasReddit").getOrCreate()

# Frecuencia de palabras
df_reddit_pal = spark.read.parquet("hdfs://localhost:9000/user/ripley/analytics/ripley_reddit_tendencias_palabras.parquet")
df_reddit_pal.printSchema()
df_reddit_pal.show(10, truncate=False)

# Distribución de score por rango
df_reddit_rangos = spark.read.parquet("hdfs://localhost:9000/user/ripley/analytics/ripley_reddit_tendencias_rangos.parquet")
df_reddit_rangos.printSchema()
df_reddit_rangos.show()

# Engagement (score) promedio por longitud del comentario
df_reddit_eng = spark.read.parquet("hdfs://localhost:9000/user/ripley/analytics/ripley_reddit_tendencias_engagement.parquet")
df_reddit_eng.printSchema()
df_reddit_eng.show()

# Promedio de score por fuente
df_reddit_prom = spark.read.parquet("hdfs://localhost:9000/user/ripley/analytics/ripley_reddit_tendencias_promedio.parquet")
df_reddit_prom.printSchema()
df_reddit_prom.show()

# Cada conjunto Parquet refleja:
# *_palabras.parquet → Tendencias temáticas. Palabras más frecuentes, sentimiento predominante y periodo en que fueron mencionadas.
# *_promedio.parquet → Participación general. Incluye número total de comentarios (n_total), suma de interacciones (suma_interaccion) y el promedio de participación (promedio_interaccion).
# *_rangos.parquet → Participación estructurada. Distribuye los comentarios por niveles de interacción (0–1, 2–5, 6–10, 10+).
# *_engagement.parquet → Relación longitud–interacción. Mide el promedio de interacción por tipo de comentario (Corto, Medio, Largo), con el total de comentarios (n_comentarios) y el total estimado de interacciones (total_interaccion_estimado).
