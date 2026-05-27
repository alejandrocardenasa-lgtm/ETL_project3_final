import time
import json
import pandas as pd
from sqlalchemy import create_engine
from kafka import KafkaProducer


DB_URL = "mysql+pymysql://root:root@localhost:3306/climate_dw"
TOPIC_NAME = "climate_temperature_metrics"


def get_metrics():
    engine = create_engine(DB_URL)

    query = """
    SELECT
        ROUND(AVG(temperatura_promedio), 2) AS avg_temperature,
        ROUND(MAX(temperatura_maxima), 2) AS max_temperature,
        SUM(evento_calor_extremo) AS extreme_heat_events
    FROM fact_climate_daily;
    """

    df = pd.read_sql(query, engine)
    return df.iloc[0].to_dict()


def main():
    producer = KafkaProducer(
        bootstrap_servers="localhost:9092",
        value_serializer=lambda value: json.dumps(value).encode("utf-8")
    )

    print("Producer iniciado...")

    while True:
        metrics = get_metrics()
        metrics["timestamp"] = pd.Timestamp.now().isoformat()

        producer.send(TOPIC_NAME, metrics)
        producer.flush()

        print("Metrica enviada:", metrics)

        time.sleep(5)


if __name__ == "__main__":
    main()