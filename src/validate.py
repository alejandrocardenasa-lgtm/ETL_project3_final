import pandas as pd
import great_expectations as gx
from great_expectations.core.batch import RuntimeBatchRequest

def run_fact_validation(context, batch_request):
    suite_name = "fact_climate_daily_suite"
    
    # 1. Crear o recuperar suite
    try:
        suite = context.get_expectation_suite(suite_name)
    except:
        suite = context.add_expectation_suite(expectation_suite_name=suite_name)

    # 2. Crear validador
    validator = context.get_validator(
        batch_request=batch_request,
        expectation_suite_name=suite_name
    )

    # 3. Aplicar expectativas (tus reglas originales)
    validator.expect_column_values_to_not_be_null("city_id")
    validator.expect_column_values_to_not_be_null("date_id")
    validator.expect_column_values_to_not_be_null("source_id")
    validator.expect_column_values_to_not_be_null("temperatura_promedio")
    validator.expect_column_values_to_not_be_null("temperatura_minima")
    validator.expect_column_values_to_not_be_null("temperatura_maxima")
    validator.expect_column_values_to_not_be_null("amplitud_termica")
    validator.expect_column_values_to_not_be_null("evento_calor_extremo")
    validator.expect_compound_columns_to_be_unique(column_list=["city_id", "date_id", "source_id"])
    validator.expect_column_values_to_be_in_set("source_id", [1, 2])
    validator.expect_column_values_to_be_in_set("evento_calor_extremo", [0, 1])
    validator.expect_column_pair_values_A_to_be_greater_than_B("temperatura_promedio", "temperatura_minima", or_equal=True)
    validator.expect_column_pair_values_A_to_be_greater_than_B("temperatura_maxima", "temperatura_promedio", or_equal=True)
    validator.expect_column_values_to_be_between("temperatura_promedio", min_value=-50, max_value=60, mostly=0.98)
    validator.expect_column_values_to_be_between("temperatura_minima", min_value=-50, max_value=60, mostly=0.98)
    validator.expect_column_values_to_be_between("temperatura_maxima", min_value=-50, max_value=60, mostly=0.98)
    validator.expect_column_values_to_be_between("amplitud_termica", min_value=0, max_value=70, mostly=0.98)

    # 4. VALIDACIÓN DIRECTA (Aquí está el cambio clave: no usamos Checkpoint)
    results = validator.validate()

    print("\n=== RESULTADOS VALIDACION FACT ===")
    print("Validation success:", results["success"])

    # 5. Lógica de detención
    if not results["success"]:
        raise ValueError("Fallaron las validaciones de calidad de Great Expectations")

    return results

def validate_fact_climate_daily():
    print("Iniciando validacion con GX 0.18.21 (Modo directo)")
    context = gx.get_context()
    df = pd.read_csv("data/processed/fact_climate_daily.csv")

    datasource_config = {
        "name": "fact_datasource",
        "class_name": "Datasource",
        "execution_engine": {"class_name": "PandasExecutionEngine"},
        "data_connectors": {
            "default_runtime_data_connector_name": {
                "class_name": "RuntimeDataConnector",
                "batch_identifiers": ["default_identifier_name"]
            }
        }
    }
    context.add_datasource(**datasource_config)

    batch_request = RuntimeBatchRequest(
        datasource_name="fact_datasource",
        data_connector_name="default_runtime_data_connector_name",
        data_asset_name="fact_climate_daily",
        runtime_parameters={"batch_data": df},
        batch_identifiers={"default_identifier_name": "default_id"}
    )

    return run_fact_validation(context, batch_request)