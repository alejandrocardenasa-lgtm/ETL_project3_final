import pandas as pd
from sqlalchemy import create_engine

def load_to_warehouse(dim_city, dim_date, dim_source, fact_climate):
    print("Iniciando carga al Data Warehouse...")
    
    
    db_url = "mysql+pymysql://root:root@mysql_dw:3306/climate_dw"
    engine = create_engine(db_url)
    
   
    
    print("Cargando dim_city...")
    dim_city.to_sql('dim_city', con=engine, if_exists='replace', index=False)
    
    print("Cargando dim_date...")
    dim_date.to_sql('dim_date', con=engine, if_exists='replace', index=False)
    
    print("Cargando dim_source...")
    dim_source.to_sql('dim_source', con=engine, if_exists='replace', index=False)
    
    print("Cargando fact_climate_daily...")
    fact_climate.to_sql('fact_climate_daily', con=engine, if_exists='replace', index=False)
    
    print("¡Carga exitosa en MySQL! El Data Warehouse está listo.")