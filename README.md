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
- **Power BI** → visualización e inteligencia de negocio.  

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
df_reddit.show(30, truncate=False)

#=========================================#
# Limpieza de datos del proyecto Ripley   #
#=========================================#

El pipeline de limpieza de datos procesa comentarios de **YouTube** y **Reddit** para obtener datos confiables y listos para análisis.

### Flujo general
1. **Extracción**  
   - Lectura de los JSON crudos de HDFS con comentarios y metadatos.

2. **Transformación y limpieza**  
   - **Normalización:**  
     - Texto en minúsculas  
     - Eliminación de saltos de línea dobles (`\n\n`)  
     - Eliminación de símbolos y caracteres especiales  
     - Normalización de espacios múltiples
   - **Filtrado de spam:** se eliminan comentarios con palabras o frases típicas de spam  
   - **Filtrado por idioma:** solo se conservan comentarios en español  
   - **Eliminación de duplicados:** se consideran `content_id` y `comment`  
   - **Conversión de fechas:** a formato `YYYY-MM-DD`

3. **Carga**  
   - Guardado de los datos limpios en HDFS para análisis posterior.

