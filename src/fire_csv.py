import pandas as pd
import matplotlib.pyplot as plt                       # Plotting library
import cartopy, cartopy.crs as ccrs                   # Plot maps
import cartopy.io.shapereader as shpreader            # Import shapefiles
import requests

# https://queimadas.dgi.inpe.br/queimadas/dados-abertos/

def baixar_arquivo(url, endereco):
    resposta = requests.get(url)
    if resposta.status_code == requests.codes.OK:
        with open(endereco, 'wb') as novo_arquivo:
                novo_arquivo.write(resposta.content)

# Especificar o dia que você quer os focos de incêndio (tem do dia anterior ao atual até um mês atras mais ou menos)
data = '20220415' #formato AnoMesDia

#Define URL dos dados a serem baixados:
CSV_URL = 'https://queimadas.dgi.inpe.br/home/downloadfile?path=%2Fapp%2Fapi%2Fdata%2Fdados_abertos%2Ffocos%2FDiario%2Ffocos_abertos_24h_' + data + '.csv'

lonW = -73.99 # Longitude Oeste.
lonE = -33.86 # Longitude Leste.
latS = -28.63 # Latitude Sul.
latN = 5.29   # Latitude Norte.
extent = [lonW, latS, lonE, latN] # Min lon, Min lat, Max lon, Max lat

# Realizar o download e só então ler o arquivo:
baixar_arquivo(CSV_URL, f'Fire/dados_focos_{data}.csv')
df = pd.read_csv(f'Fire/dados_focos_{data}.csv')

# Filtra os dados que estão dentro da extensão desejada
df.query(f'{latN} >= lat >= {latS} \
            and {lonE} >= lon >= {lonW} ', inplace = True)

df.to_csv(f'Fire/dados_filtrados_{data}.csv', index=False) #salva os dados filtrados em um novo csv

# Choose the plot size (width x height, in inches)
dpi = 125
plt.figure(figsize=(10,10), dpi=dpi)

# Use the Geostationary projection in cartopy
ax = plt.axes(projection=ccrs.PlateCarree())

# Define the image extent
ax.set_extent([extent[0], extent[2], extent[1], extent[3]], ccrs.PlateCarree())

# Define the data extent
img_extent = [extent[0], extent[2], extent[1], extent[3]]

# Plot
img = ax.plot(df['lon'], df['lat'],'.r', markersize=3, transform=ccrs.PlateCarree(), alpha=1)

# Add a shapefile
# https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2019/Brasil/BR/br_unidades_da_federacao.zip
shapefile = list(shpreader.Reader('BR_UF_2019.shp').geometries())
ax.add_geometries(shapefile, ccrs.PlateCarree(), edgecolor='black',facecolor='none', linewidth=0.7)

# Add coastlines, borders and gridlines
ax.coastlines(resolution='10m', color='black', linewidth=0.8, zorder=3)
ax.add_feature(cartopy.feature.BORDERS, edgecolor='black', linewidth=0.5, zorder=4)

# Save the image
plt.savefig(f'Fire/fire_inpe_{data}.png', transparent=True, bbox_inches='tight')

plt.show()