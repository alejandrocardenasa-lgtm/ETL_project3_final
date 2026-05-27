import json
from kafka import KafkaConsumer


TOPIC_NAME = "climate_temperature_metrics"


def main():
    consumer = KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers="localhost:9092",
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="climate_monitor_group_2",
        value_deserializer=lambda value: json.loads(value.decode("utf-8"))
    )

    print("Consumer escuchando metricas...")

    for message in consumer:
        data = message.value

        print("\nNueva metrica recibida")
        print("Temperatura promedio:", data["avg_temperature"])
        print("Temperatura maxima:", data["max_temperature"])
        print("Eventos extremos:", data["extreme_heat_events"])
        print("Timestamp:", data["timestamp"])


if __name__ == "__main__":
    main()