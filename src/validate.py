import pandas as pd
import great_expectations as gx
from great_expectations.core.batch import RuntimeBatchRequest


def run_fact_validation(context, batch_request):

    suite_name = "fact_climate_daily_suite"

    # Crear la suite si no existe
    try:
        context.get_expectation_suite(suite_name)
    except Exception:
        context.add_expectation_suite(expectation_suite_name=suite_name)

    # Crear validator
    validator = context.get_validator(
        batch_request=batch_request,
        expectation_suite_name=suite_name
    )

    # Limpiar expectativas anteriores
    validator.expectation_suite.expectations = []

    # EXPECTATIVAS CRITICAS

    # Null checks en claves
    validator.expect_column_values_to_not_be_null("city_id")
    validator.expect_column_values_to_not_be_null("date_id")
    validator.expect_column_values_to_not_be_null("source_id")

    # Unicidad del grano
    validator.expect_compound_columns_to_be_unique(
        column_list=["city_id", "date_id", "source_id"]
    )

    # source_id válido
    validator.expect_column_values_to_be_in_set(
        "source_id",
        [1, 2]
    )

    # Null checks en temperaturas clave
    validator.expect_column_values_to_not_be_null("temperatura_promedio")
    validator.expect_column_values_to_not_be_null("temperatura_minima")
    validator.expect_column_values_to_not_be_null("temperatura_maxima")

    # Consistencia lógica
    validator.expect_column_pair_values_A_to_be_greater_than_B(
        "temperatura_promedio",
        "temperatura_minima",
        or_equal=True
    )

    validator.expect_column_pair_values_A_to_be_greater_than_B(
        "temperatura_maxima",
        "temperatura_promedio",
        or_equal=True
    )

    # EXPECTATIVAS NO CRITICAS

    validator.expect_column_values_to_be_between(
        "temperatura_promedio",
        min_value=-50,
        max_value=60,
        mostly=0.98
    )

    validator.expect_column_values_to_be_between(
        "temperatura_minima",
        min_value=-60,
        max_value=50,
        mostly=0.98
    )

    validator.expect_column_values_to_be_between(
        "temperatura_maxima",
        min_value=-50,
        max_value=70,
        mostly=0.98
    )

    validator.expect_column_values_to_be_between(
        "precipitacion",
        min_value=0,
        mostly=0.95
    )

    validator.expect_column_values_to_be_between(
        "velocidad_viento",
        min_value=0,
        mostly=0.95
    )

    validator.expect_column_values_to_be_between(
        "presion",
        min_value=800,
        max_value=1100,
        mostly=0.90
    )

    # Guardar suite
    validator.save_expectation_suite(discard_failed_expectations=False)

    # Ejecutar validación
    validation_results = validator.validate()

    # Crear o actualizar checkpoint
    context.add_or_update_checkpoint(
        name="fact_climate_daily_checkpoint",
        validations=[
            {
                "batch_request": batch_request,
                "expectation_suite_name": suite_name
            }
        ]
    )

    # Ejecutar checkpoint para Data Docs
    context.run_checkpoint(checkpoint_name="fact_climate_daily_checkpoint")

    # Construir Data Docs
    context.build_data_docs()

    print("\n=== RESULTADOS VALIDACION FACT ===")
    print("Validation success:", validation_results["success"])
    print("Data Docs generados")
    print("Validación completada")

    # CONTROL DE CRITICAS

    critical_failed = []

    for result in validation_results["results"]:
        expectation = result["expectation_config"]["expectation_type"]
        kwargs = result["expectation_config"]["kwargs"]

        if expectation == "expect_column_values_to_not_be_null":
            if kwargs.get("column") in [
                "city_id",
                "date_id",
                "source_id",
                "temperatura_promedio",
                "temperatura_minima",
                "temperatura_maxima"
            ] and not result["success"]:
                critical_failed.append(f"{expectation} - {kwargs.get('column')}")

        elif expectation == "expect_compound_columns_to_be_unique":
            if not result["success"]:
                critical_failed.append("grano_unico_city_id_date_id_source_id")

        elif expectation == "expect_column_values_to_be_in_set":
            if kwargs.get("column") == "source_id" and not result["success"]:
                critical_failed.append("source_id_valido")

        elif expectation == "expect_column_pair_values_A_to_be_greater_than_B":
            if not result["success"]:
                critical_failed.append(
                    f"{kwargs.get('column_A')} >= {kwargs.get('column_B')}"
                )

    # Si falla algo crítico, detener pipeline
    if len(critical_failed) > 0:
        raise ValueError(f"Fallaron validaciones críticas: {critical_failed}")

    return validation_results


def validate_fact_climate_daily():
    print("Iniciando validación con Great Expectations...")

    context = gx.get_context()

    # Crear o actualizar datasource
    context.add_or_update_datasource(
        name="fact_datasource",
        class_name="Datasource",
        execution_engine={
            "class_name": "PandasExecutionEngine"
        },
        data_connectors={
            "default_runtime_data_connector_name": {
                "class_name": "RuntimeDataConnector",
                "batch_identifiers": ["default_identifier_name"]
            }
        }
    )

    batch_request = RuntimeBatchRequest(
        datasource_name="fact_datasource",
        data_connector_name="default_runtime_data_connector_name",
        data_asset_name="fact_climate_daily",
        runtime_parameters={
            "path": "data/processed/fact_climate_daily.csv"
        },
        batch_identifiers={
            "default_identifier_name": "default_id"
        }
    )

    return run_fact_validation(context, batch_request)


if __name__ == "__main__":
    validate_fact_climate_daily()