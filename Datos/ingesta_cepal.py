import requests
import pandas as pd
import time

def obtener_datos_cepal(indicador_id, pais):
    url = f"https://api-cepalstat.cepal.org/cepalstat/api/v1/indicator/{indicador_id}/data"

    params = {
        "members": pais,
        "lang": "es",
        "format": "json"
    }

    try:
        print(f"Intentando indicador {indicador_id} para país {pais}...")
        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        registros = data['body']['data']

        df = pd.DataFrame(registros)
        
        return df

    except Exception as e:
        print(f"Error con indicador {indicador_id} y país {pais}: {e}")
        return None


# ---------------------------
# EJECUCIÓN
# ---------------------------

# Indicadores
id_desempleo = 4174
id_tic = 3251

# SOLO Bolivia (más estable)
pais = "216"

# Descargar datos uno por uno
df_desempleo = obtener_datos_cepal(id_desempleo, pais)
time.sleep(2)  # pequeña pausa

df_tic = obtener_datos_cepal(id_tic, pais)

# Guardar
if df_desempleo is not None:
    df_desempleo.to_csv("desempleo_bruto.csv", index=False)
    print("✔ desempleo guardado")

if df_tic is not None:
    df_tic.to_csv("tic_bruto.csv", index=False)
    print("✔ TIC guardado")

print("Proceso finalizado")