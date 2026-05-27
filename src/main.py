from extract import extract_original_dataset, extract_meteostat
from clean import clean_meteostat
from transform import transform_datasets
from validate import validate_fact_climate_daily
from load import load_to_warehouse


def main():

    #extraccion
    extract_original_dataset()
    extract_meteostat()

    #limpieza
    clean_meteostat()

    #transformacion
    dim_city, dim_date, dim_source, fact_climate_daily = transform_datasets()

    #validacion
    validate_fact_climate_daily()

    #carga al warehouse
    load_to_warehouse(dim_city, dim_date, dim_source, fact_climate_daily)

    
if __name__ == "__main__":
    main()