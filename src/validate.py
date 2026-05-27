import great_expectations as gx
from great_expectations.core.batch import RuntimeBatchRequest


def run_fact_validation(context, batch_request):

    suite_name = "fact_climate_daily_suite"

    # creacion de suite
    try:
        context.get_expectation_suite(suite_name)
    except Exception:
        context.add_expectation_suite(
            expectation_suite_name=suite_name
        )

    # creacion de validator
    validator = context.get_validator(
        batch_request=batch_request,
        expectation_suite_name=suite_name
    )

    # limpieza de expectativas anteriores
    validator.expectation_suite.expectations = []

    # validacion de claves
    validator.expect_column_values_to_not_be_null("city_id")
    validator.expect_column_values_to_not_be_null("date_id")
    validator.expect_column_values_to_not_be_null("source_id")

    # validacion de medidas
    validator.expect_column_values_to_not_be_null("temperatura_promedio")
    validator.expect_column_values_to_not_be_null("temperatura_minima")
    validator.expect_column_values_to_not_be_null("temperatura_maxima")
    validator.expect_column_values_to_not_be_null("amplitud_termica")
    validator.expect_column_values_to_not_be_null("evento_calor_extremo")

    # validacion de grano
    validator.expect_compound_columns_to_be_unique(
        column_list=["city_id", "date_id", "source_id"]
    )

    # validacion de fuente
    validator.expect_column_values_to_be_in_set(
        "source_id",
        [1, 2]
    )

    # validacion de indicador
    validator.expect_column_values_to_be_in_set(
        "evento_calor_extremo",
        [0, 1]
    )

    # consistencia de temperaturas
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

    # rango de temperatura promedio
    validator.expect_column_values_to_be_between(
        "temperatura_promedio",
        min_value=-50,
        max_value=60,
        mostly=0.98
    )

    # rango de temperatura minima
    validator.expect_column_values_to_be_between(
        "temperatura_minima",
        min_value=-50,
        max_value=60,
        mostly=0.98
    )

    # rango de temperatura maxima
    validator.expect_column_values_to_be_between(
        "temperatura_maxima",
        min_value=-50,
        max_value=60,
        mostly=0.98
    )

    # rango de amplitud termica
    validator.expect_column_values_to_be_between(
        "amplitud_termica",
        min_value=0,
        max_value=70,
        mostly=0.98
    )

    # guardado de suite
    validator.save_expectation_suite(
        discard_failed_expectations=False
    )

    # ejecucion de validacion
    validation_results = validator.validate()

    # creacion de checkpoint
    context.add_or_update_checkpoint(
        name="fact_climate_daily_checkpoint",
        validations=[
            {
                "batch_request": batch_request,
                "expectation_suite_name": suite_name
            }
        ]
    )

    # ejecucion de checkpoint
    context.run_checkpoint(
        checkpoint_name="fact_climate_daily_checkpoint"
    )

    # generacion de data docs
    context.build_data_docs()

    print("\n=== RESULTADOS VALIDACION FACT ===")
    print("Validation success:", validation_results["success"])
    print("Data Docs generados")
    print("Validacion completada")

    critical_failed = []

    # columnas criticas
    critical_not_null_columns = [
        "city_id",
        "date_id",
        "source_id",
        "temperatura_promedio",
        "temperatura_minima",
        "temperatura_maxima",
        "amplitud_termica",
        "evento_calor_extremo"
    ]

    # revision de validaciones criticas
    for result in validation_results["results"]:

        expectation = result["expectation_config"]["expectation_type"]
        kwargs = result["expectation_config"]["kwargs"]

        if expectation == "expect_column_values_to_not_be_null":

            if (
                kwargs.get("column") in critical_not_null_columns
                and not result["success"]
            ):
                critical_failed.append(
                    f"{expectation} - {kwargs.get('column')}"
                )

        elif expectation == "expect_compound_columns_to_be_unique":

            if not result["success"]:
                critical_failed.append(
                    "grano_unico_city_id_date_id_source_id"
                )

        elif expectation == "expect_column_values_to_be_in_set":

            if (
                kwargs.get("column")
                in ["source_id", "evento_calor_extremo"]
                and not result["success"]
            ):
                critical_failed.append(
                    f"{kwargs.get('column')}_valido"
                )

        elif expectation == "expect_column_pair_values_A_to_be_greater_than_B":

            if not result["success"]:
                critical_failed.append(
                    f"{kwargs.get('column_A')} >= {kwargs.get('column_B')}"
                )

    # detencion del pipeline
    if len(critical_failed) > 0:
        raise ValueError(
            f"Fallaron validaciones criticas: {critical_failed}"
        )

    return validation_results


def validate_fact_climate_daily():

    print("Iniciando validacion con Great Expectations")

    # contexto GX dentro de airflow
    context = gx.get_context(
        context_root_dir="/opt/airflow/gx"
    )

    # configuracion de datasource
    context.add_or_update_datasource(
        name="fact_datasource",
        class_name="Datasource",
        execution_engine={
            "class_name": "PandasExecutionEngine"
        },
        data_connectors={
            "default_runtime_data_connector_name": {
                "class_name": "RuntimeDataConnector",
                "batch_identifiers": [
                    "default_identifier_name"
                ]
            }
        }
    )

    # batch de validacion
    batch_request = RuntimeBatchRequest(
        datasource_name="fact_datasource",
        data_connector_name="default_runtime_data_connector_name",
        data_asset_name="fact_climate_daily",
        runtime_parameters={
            "path": "/opt/airflow/data/processed/fact_climate_daily.csv"
        },
        batch_identifiers={
            "default_identifier_name": "default_id"
        }
    )

    return run_fact_validation(
        context,
        batch_request
    )
