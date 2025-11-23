# pip install -r requirements.txt

# ABRE UNA TERMINAL FUERA DEL PROYECTO Y SIGUE ESTOS PASOS PAPETO LENDO, presiona cd ..

1. # 1. Le decimos a Airflow dónde guardar sus cosas 
export AIRFLOW_HOME=~/airflow

# 2. Inicializamos la base de datos interna 
airflow standalone

# 3. atento que al inicio apareceran tus crednciales 
standalone | Starting Airflow Standalone
Simple auth manager | Password for user 'admin': WQEACTAUfX8YrX8Q

# 4. En una terminal fuera de visual y en tu ruta home/user coloca
mkdir -p ~/airflow/dags

# 5. Luego pega
nano ~/airflow/dags/ripley_workflow.py

# dentro de esto pega todo este bloque de codigo

from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
from airflow.sensors.filesystem import FileSensor
from datetime import datetime, timedelta
import os

# ==============================================================================
# CONFIGURACIÓN
# ==============================================================================
PROJECT_PATH = "/home/clever/RIPLEY/BIG-DATA-CASO-RIPLEY-G9"
VENV_PYTHON = f"{PROJECT_PATH}/proyectoripley_env/bin/python"
MAIN_SCRIPT = "main.py"
TRIGGER_FILE = f"{PROJECT_PATH}/INICIAR_PIPELINE.txt"

default_args = {
    'owner': 'Grupo9_Ripley',
    'depends_on_past': False,
    'retries': 0, # No reintentar inmediatamente si falla por memoria
    # IMPORTANTE: Le damos 30 minutos de vida máxima antes de matarlo
    'execution_timeout': timedelta(minutes=30), 
}

with DAG(
    dag_id='ripley_pipeline_file_sensor_v10', # Versión 10
    default_args=default_args,
    description='Pipeline activado por archivo local',
    schedule='*/1 * * * *',
    start_date=datetime(2025, 1, 1),
    catchup=False,
    # Concurrency: Evita que corran 2 pipelines a la vez y explote la RAM
    max_active_runs=1, 
    tags=['big_data', 'evento', 'ripley'],
) as dag:

    # --------------------------------------------------------------------------
    # TAREA 1: EL SENSOR
    # --------------------------------------------------------------------------
    esperar_archivo = FileSensor(
        task_id='esperando_archivo_inicio',
        filepath=TRIGGER_FILE,
        poke_interval=20, # Revisa cada 20s (menos carga al CPU que 10s)
        timeout=600,
        mode='reschedule'
    )

    # --------------------------------------------------------------------------
    # TAREA 2: EL PIPELINE (Aquí es donde moría)
    # --------------------------------------------------------------------------
    ejecutar_pipeline = BashOperator(
        task_id='ejecutar_main_py',
        # Agregamos un comando antes para liberar caché de RAM si es posible
        bash_command=f"""
        sync; echo 3 > /proc/sys/vm/drop_caches || true && \
        cd {PROJECT_PATH} && \
        export PYSPARK_PYTHON={VENV_PYTHON} && \
        export PYSPARK_DRIVER_PYTHON={VENV_PYTHON} && \
        {VENV_PYTHON} {MAIN_SCRIPT}
        """
    )

    # --------------------------------------------------------------------------
    # TAREA 3: LIMPIEZA
    # --------------------------------------------------------------------------
    borrar_trigger = BashOperator(
        task_id='borrar_archivo_trigger',
        bash_command=f"rm {TRIGGER_FILE}"
    )

    esperar_archivo >> ejecutar_pipeline >> borrar_trigger

## Ve a Airflow Web: http://localhost:8080.

En el menú superior: Admin -> Connections .

Haz clic en el botón + (Create).

Llena estos datos EXACTAMENTE así:

Connection Id: fs_default

Connection Type: File (path)

(Nota: Si no encuentras "File (path)", busca "Generic" o "FS").

Description: Conexión local

Extra: (Copia y pega esto para asegurar que lea desde la raíz):

JSON

{"path": "/"}
Haz clic en Save.

# FINAL

touch ~/RIPLEY/BIG-DATA-CASO-RIPLEY-G9/INICIAR_PIPELINE.txt