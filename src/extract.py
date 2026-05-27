import requests
import pandas as pd
import os

def extract_original_dataset():
    df_original = pd.read_csv("data/raw/temperature_observations_colombia_transformed.csv")
    print("Dataset original extraido")
    print(df_original.head(5))
    return df_original

def extract_meteostat():
    cities = [
        {"city": "Berlin", "lat": 52.5200, "lon": 13.4050},
        {"city": "Lima", "lat": -12.0464, "lon": -77.0428},
        {"city": "Mexico_City", "lat": 19.4326, "lon": -99.1332},
        {"city": "Buenos_Aires", "lat": -34.6037, "lon": -58.3816},
        {"city": "Santiago", "lat": -33.4489, "lon": -70.6693},
        {"city": "Madrid", "lat": 40.4168, "lon": -3.7038},
        {"city": "Paris", "lat": 48.8566, "lon": 2.3522},
        {"city": "London", "lat": 51.5074, "lon": -0.1278},
        {"city": "Tokyo", "lat": 35.6762, "lon": 139.6503},
        {"city": "Washington_DC", "lat": 38.9072, "lon": -77.0369}
    ]       

    periods = [
        ("2003-01-01", "2012-12-29"),
        ("2013-01-01", "2019-12-31")
    ]

    url = "https://meteostat.p.rapidapi.com/point/daily"
    headers = {
        "x-rapidapi-key": "fd44fbc69fmsh07d145fd64df469p134ca6jsn425ae4cad914",
        "x-rapidapi-host": "meteostat.p.rapidapi.com"
    }

    all_data = []

    for city in cities:
        for start, end in periods:
            params = {
                "lat": city["lat"],
                "lon": city["lon"],
                "start": start,
                "end": end
            }

            response = requests.get(url, headers=headers, params=params)
            data = response.json()

            print("Ciudad:", city["city"], "| Rango:", start, "a", end)
            print("Status:", response.status_code)

            if "data" in data:
                df = pd.DataFrame(data["data"])
                df["city"] = city["city"]
                all_data.append(df)
            else:
                print("No se pudo traer data para", city["city"], start, end)

    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        print("Extraccion de la API completada")
        print(final_df.head(5))

        os.makedirs("data/raw", exist_ok=True)
        final_df.to_csv("data/raw/meteostat_daily_globalv2.csv", index=False)
        return final_df
    else:
        return pd.DataFrame()