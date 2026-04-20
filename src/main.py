from extract import extract_original_dataset, extract_meteostat
from clean import clean_meteostat
from transform import transform_datasets
from validate import validate_fact_climate_daily


def main():

    #extraccion
    extract_original_dataset()
    extract_meteostat()

    #limpieza
    clean_meteostat()

    #transformacion
    transform_datasets()

    #validacion
    validate_fact_climate_daily()

    

if __name__ == "__main__":
    main()