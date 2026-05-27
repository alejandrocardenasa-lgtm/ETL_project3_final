# ETL Project 3 - Pipeline Climatico con Airflow, Great Expectations y Kafka

## Descripcion General

Este proyecto implementa un pipeline completo de ingenieria de datos orientado al procesamiento y monitoreo de informacion climatica utilizando herramientas modernas de ETL, validacion, orquestacion y streaming en tiempo real.

El proyecto fue desarrollado con el objetivo de simular una arquitectura real de procesamiento analitico de datos climaticos, integrando:

* procesos ETL,
* validacion de calidad,
* modelo dimensional,
* orquestacion automatica,
* y streaming analytics.

Durante el desarrollo se trabajaron conceptos reales de ingenieria de datos como:

* integracion de multiples fuentes,
* limpieza y transformacion de datos,
* modelado dimensional,
* control de calidad,
* automatizacion de pipelines,
* y procesamiento en tiempo real.

---

# Objetivo del Proyecto

Construir un pipeline capaz de:

* extraer informacion climatica desde diferentes fuentes,
* transformar e integrar los datos,
* validar su calidad automaticamente,
* almacenarlos en un Data Warehouse,
* automatizar el flujo con Airflow,
* y transmitir metricas climaticas en tiempo real utilizando Kafka.

---

# Tecnologias Utilizadas

El proyecto fue desarrollado utilizando las siguientes tecnologias:

* Python
* Pandas
* NumPy
* MySQL
* Apache Airflow
* Apache Kafka
* Zookeeper
* Great Expectations
* Docker
* Docker Compose
* Requests
* SQLAlchemy

---

# Fuentes de Datos

## 1. Dataset IDEAM

Se utilizo un dataset historico de observaciones climaticas provenientes del IDEAM.

Este dataset contenia:

* temperaturas observadas,
* municipios,
* fechas de observacion,
* y diferentes registros climaticos diarios para ciudades de Colombia.

Los datos fueron almacenados inicialmente en archivos CSV.

---

## 2. API Meteostat

Como segunda fuente se utilizo la API Meteostat para obtener informacion climatica internacional.

La extraccion se realizo mediante solicitudes HTTP usando la libreria `requests` y una API Key obtenida desde RapidAPI.

La consulta utilizo:

* endpoint diario de Meteostat,
* coordenadas geograficas,
* rangos de fechas,
* y consultas iterativas por ciudad.

Esto permitio integrar informacion climatica global junto con los datos nacionales del IDEAM.

---

# Arquitectura del Proyecto

El flujo general del proyecto sigue la siguiente arquitectura:

```text id="fjlwmk"
Fuentes de Datos
       ↓
Extraccion
       ↓
Transformacion y Limpieza
       ↓
Validacion con Great Expectations
       ↓
Carga a MySQL (Data Warehouse)
       ↓
Orquestacion con Airflow
       ↓
Streaming de Metricas con Kafka
       ↓
Monitoreo en Tiempo Real
```

---

# Proceso ETL

## Extraccion

La etapa de extraccion obtiene informacion desde:

* archivos CSV locales,
* y la API Meteostat.

### Extraccion desde IDEAM

Los datos nacionales fueron cargados desde archivos CSV con informacion historica de temperaturas.

### Extraccion desde Meteostat

La API fue consultada iterativamente para:

* diferentes ciudades,
* diferentes coordenadas,
* y distintos rangos de fechas.

La informacion obtenida fue almacenada temporalmente para posteriormente integrarse al pipeline.

---

# Transformacion de Datos

La etapa de transformacion fue una de las partes mas importantes del proyecto.

Debido a que ambas fuentes tenian estructuras diferentes, fue necesario:

* limpiar,
* normalizar,
* transformar,
* e integrar los datos bajo un mismo esquema.

---

## Procesos de Limpieza Implementados

### Estandarizacion de columnas

Se normalizaron nombres de columnas utilizando:

* minusculas,
* eliminacion de espacios,
* y formatos consistentes.

### Conversion de tipos de datos

Las fechas y temperaturas fueron convertidas correctamente a:

* `datetime`,
* `float`,
* y formatos numericos adecuados.

### Limpieza de ciudades

Los nombres de ciudades fueron normalizados para evitar inconsistencias.

### Eliminacion de valores nulos

Se eliminaron registros incompletos en columnas criticas.

### Eliminacion de duplicados

Se eliminaron registros repetidos para mantener integridad en el Data Warehouse.

### Validacion de rangos climaticos

Se validaron temperaturas dentro de rangos climaticos realistas:

* entre -50 y 60 grados.

### Validacion de consistencia

Tambien se validaron relaciones logicas como:

* temperatura maxima >= temperatura promedio,
* temperatura promedio >= temperatura minima.

---

# Integracion de Datos

Como las fuentes no compartian exactamente la misma estructura, se realizo un proceso de integracion para unificar los datasets.

En el caso del IDEAM:

* existian multiples observaciones por ciudad y fecha,
* por lo tanto se agruparon registros diarios,
* calculando:

  * temperatura promedio,
  * temperatura minima,
  * temperatura maxima.

Luego ambos datasets fueron integrados en una sola estructura uniforme.

---

# Metricas Derivadas

Durante la transformacion tambien se calcularon nuevas metricas analiticas:

## Amplitud Termica

Diferencia entre:

* temperatura maxima
* y temperatura minima.

## Evento de Calor Extremo

Indicador binario para detectar temperaturas extremas.

Regla implementada:

* temperatura maxima >= 35 grados.

---

# Modelo Dimensional

El proyecto implementa un Data Warehouse basado en un modelo dimensional.

---

## Dimension Ciudad - dim_city

Contiene:

* identificador de ciudad,
* nombre de ciudad.

---

## Dimension Fecha - dim_date

Contiene:

* año,
* mes,
* dia,
* semana,
* trimestre,
* indicador de fin de semana.

---

## Dimension Fuente - dim_source

Permite identificar:

* IDEAM,
* Meteostat,
* tipo de fuente.

---

## Tabla de Hechos - fact_climate_daily

Tabla principal del modelo dimensional.

Contiene:

* temperaturas,
* amplitud termica,
* eventos extremos,
* y llaves hacia dimensiones.

---

# Validacion de Calidad con Great Expectations

Great Expectations fue utilizado para implementar validaciones automaticas de calidad de datos.

Las validaciones se ejecutan automaticamente dentro del pipeline antes de cargar informacion al Data Warehouse.

---

## Validaciones Implementadas

### Validacion de nulos

Se verifica que columnas criticas no contengan valores vacios.

Ejemplos:

* city_id
* date_id
* source_id
* temperaturas

---

### Validacion de grano unico

Se asegura que no existan duplicados en:

* city_id
* date_id
* source_id

---

### Validacion de rangos climaticos

Se verifican temperaturas dentro de rangos validos.

---

### Validacion de consistencia

Se valida:

* temperatura maxima >= promedio
* promedio >= minima

---

### Validacion de indicadores

Se validan:

* source_id validos,
* indicadores binarios correctos.

---

# Data Docs

Great Expectations tambien genera automaticamente Data Docs para visualizar:

* expectativas configuradas,
* reglas de calidad,
* y resultados de validacion.

Esto permite monitorear visualmente la calidad de los datos del pipeline.

---

# Orquestacion con Apache Airflow

Apache Airflow fue utilizado para automatizar todo el flujo ETL.

Se implemento un DAG encargado de ejecutar:

1. extraccion,
2. transformacion,
3. validacion,
4. carga de datos.

Esto permite controlar el pipeline completo de forma automatica y organizada.

---

# Streaming en Tiempo Real con Kafka

Kafka fue implementado para agregar un componente de streaming analytics.

---

## Kafka Producer

El producer consulta directamente metricas desde la tabla de hechos cargada en MySQL.

Las metricas enviadas incluyen:

* temperatura promedio por ciudad,
* temperatura maxima por ciudad,
* cantidad de eventos extremos.

Estas metricas son publicadas continuamente en un topico de Kafka.

La idea fue simular un escenario real de monitoreo climatico continuo.

---

## Kafka Consumer

El consumer se suscribe al topico y recibe las metricas en tiempo real.

Esto permite:

* monitoreo continuo,
* visualizacion de metricas,
* y simulacion de analitica en streaming.

---

# Infraestructura con Docker

Docker Compose fue utilizado para contenerizar:

* Airflow,
* Kafka,
* Zookeeper,
* MySQL.

Esto permite levantar todo el entorno facilmente y garantizar compatibilidad entre maquinas.

---

# Estructura del Proyecto

```text id="x4zh7l"
ETL_project3_final/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── dags/
│
├── kafka/
│   ├── producer.py
│   └── consumer.py
│
├── src/
│   ├── extract.py
│   ├── transform.py
│   ├── validate.py
│   ├── load.py
│   └── main.py
│
├── gx/
│
├── requirements.txt
├── docker-compose.yml
└── README.md
```

---

# Como Ejecutar el Proyecto

## 1. Clonar el Repositorio

```bash id="1vnn1r"
git clone https://github.com/alejandrocardenasa-lgtm/ETL_project3_final.git
cd ETL_project3_final
```

---

## 2. Crear Entorno Virtual

```bash id="gxdfdu"
python3 -m venv venv
```

### Activar entorno virtual

#### Mac/Linux

```bash id="1lymxv"
source venv/bin/activate
```

#### Windows

```bash id="x7f3rb"
venv\Scripts\activate
```

---

## 3. Instalar Dependencias

```bash id="s4lmhz"
pip install -r requirements.txt
```

---

# Ejecutar Docker

## Levantar Contenedores

```bash id="rz0pdg"
docker compose up -d
```

---

## Verificar Contenedores

```bash id="et81cc"
docker ps
```

Deben aparecer:

* airflow_orquestador
* kafka_climate
* zookeeper_climate
* mysql_dw

---

# Ejecutar Airflow

Abrir en navegador:

```text id="8j1isr"
http://localhost:8080
```

Credenciales:

```text id="bsuvdu"
usuario: admin
contraseña: admin
```

Activar el DAG y ejecutarlo manualmente.

---

# Ejecutar Kafka

## Crear Topic

```bash id="byydgb"
docker exec -it kafka_climate kafka-topics \
--create \
--topic climate_temperature_metrics \
--bootstrap-server localhost:9092 \
--partitions 1 \
--replication-factor 1
```

---

## Ejecutar Consumer

```bash id="ay7nbl"
python kafka/consumer.py
```

---

## Ejecutar Producer

En otra terminal:

```bash id="s16z5l"
python kafka/producer.py
```

---

# Visualizar Data Docs de Great Expectations

## Copiar Data Docs

```bash id="wvw9sj"
docker cp airflow_orquestador:/opt/airflow/gx/uncommitted/data_docs/local_site ./gx_data_docs
```

---

## Abrir Data Docs

```bash id="4m38j6"
open gx_data_docs/index.html
```

---

# Resultado Final

El proyecto implementa exitosamente un pipeline completo de ingenieria de datos capaz de:

* integrar multiples fuentes climaticas,
* validar calidad automaticamente,
* cargar informacion analitica,
* automatizar procesos ETL,
* y transmitir metricas climaticas en tiempo real utilizando Kafka.
