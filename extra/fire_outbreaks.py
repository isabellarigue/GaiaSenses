import pandas as pd
import requests
from datetime import datetime                   

lat = -10 
lon = -50 

day = int(datetime.now().strftime('%d')) - 1
if day < 10:
  data = datetime.now().strftime('%Y%m0' + str(day))
else:
  data = datetime.now().strftime('%Y%m' + str(day))  

# https://queimadas.dgi.inpe.br/queimadas/dados-abertos/
def baixar_arquivo_incendio(url, endereco):
    resposta = requests.get(url)
    if resposta.status_code == requests.codes.OK:
        with open(endereco, 'wb') as novo_arquivo:
                novo_arquivo.write(resposta.content)


CSV_URL = 'https://queimadas.dgi.inpe.br/home/downloadfile?path=%2Fapp%2Fapi%2Fdata%2Fdados_abertos%2Ffocos%2FDiario%2Ffocos_abertos_24h_' + data + '.csv'

# Download and read the data
baixar_arquivo_incendio(CSV_URL, f'Fire/dados_focos_{data}.csv')
df = pd.read_csv(f'Fire/dados_focos_{data}.csv')

# Looking for a fire outbreak on the region of the user
for i in range(len(df['lat'])):
  if (df['lat'][i] <= (lat + 0.5) and df['lat'][i] >= (lat - 0.5)) and (df['lon'][i] <= (lon + 0.5) and df['lon'][i] >= (lon - 0.5)):
    print("found fire")