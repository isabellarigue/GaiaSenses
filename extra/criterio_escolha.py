# Código do critério de escolha da animação, conforme diagrama nesta mesma pasta 

# Valores de exemplo:
lat = -10 # latitude do usuario
lon = -50 # longitude do usuario

#-----------------------------------------------------------------------------------------------------------
# Composição incêndios
#-----------------------------------------------------------------------------------------------------------

import pandas as pd
import requests
from datetime import datetime                   

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


#Define URL dos dados a serem baixados:
CSV_URL = 'https://queimadas.dgi.inpe.br/home/downloadfile?path=%2Fapp%2Fapi%2Fdata%2Fdados_abertos%2Ffocos%2FDiario%2Ffocos_abertos_24h_' + data + '.csv'

# Realizar o download e só então ler o arquivo:
baixar_arquivo_incendio(CSV_URL, f'Fire/dados_focos_{data}.csv')
df = pd.read_csv(f'Fire/dados_focos_{data}.csv')

# Busca por um foco de incendio nas redondezas da região do usuário
for i in range(len(df['lat'])):
  if (df['lat'][i] <= (lat + 0.5) and df['lat'][i] >= (lat - 0.5)) and (df['lon'][i] <= (lon + 0.5) and df['lon'][i] >= (lon - 0.5)):
    print("animação incendios")
    exit()


#-----------------------------------------------------------------------------------------------------------
# Composição tempestade
#-----------------------------------------------------------------------------------------------------------

import os                                       # Miscellaneous operating system interfaces
from osgeo import osr                           # Python bindings for GDAL
from osgeo import gdal                          # Python bindings for GDAL
import boto3                                    # Amazon Web Services (AWS) SDK for Python
from botocore import UNSIGNED                   # boto3 config
from botocore.config import Config              # boto3 config
gdal.PushErrorHandler('CPLQuietErrorHandler')   # Ignore GDAL warnings


def download_CMI(yyyymmddhhmn, band, path_dest):

  os.makedirs(path_dest, exist_ok=True)

  year = datetime.strptime(yyyymmddhhmn, '%Y%m%d%H%M').strftime('%Y')
  day_of_year = datetime.strptime(yyyymmddhhmn, '%Y%m%d%H%M').strftime('%j')
  hour = datetime.strptime(yyyymmddhhmn, '%Y%m%d%H%M').strftime('%H')
  min = datetime.strptime(yyyymmddhhmn, '%Y%m%d%H%M').strftime('%M')

  # AMAZON repository information 
  # https://noaa-goes16.s3.amazonaws.com/index.html
  bucket_name = 'noaa-goes16'
  product_name = 'ABI-L2-CMIPF'

  # Initializes the S3 client
  s3_client = boto3.client('s3', config=Config(signature_version=UNSIGNED))
  #-----------------------------------------------------------------------------------------------------------
  # File structure
  prefix = f'{product_name}/{year}/{day_of_year}/{hour}/OR_{product_name}-M6C{int(band):02.0f}_G16_s{year}{day_of_year}{hour}{min}'

  # Seach for the file on the server
  s3_result = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix, Delimiter = "/")

  #-----------------------------------------------------------------------------------------------------------
  # Check if there are files available
  if 'Contents' not in s3_result: 
    # There are no files
    print(f'No files found for the date: {yyyymmddhhmn}, Band-{band}')
    return -1
  else:
    # There are files
    for obj in s3_result['Contents']: 
      key = obj['Key']
      # Print the file name
      file_name = key.split('/')[-1].split('.')[0]

      # Download the file
      if os.path.exists(f'{path_dest}/{file_name}.nc'):
        print(f'File {path_dest}/{file_name}.nc exists')
      else:
        print(f'Downloading file {path_dest}/{file_name}.nc')
        s3_client.download_file(bucket_name, key, f'{path_dest}/{file_name}.nc')
  return f'{file_name}'


# Directories
output = "Output"; os.makedirs(output, exist_ok=True)

# Desired data:
extent = [-74.0, -33, -34, 0.5] # Min lon, Min lat, Max lon, Max lat (values for Brazil)
var = 'CMI'
band = 13

# Get the date and time
minute = int(datetime.now().strftime('%M'))
yyyymmddhhmn = datetime.now().strftime('%Y%m%d%H' + str(minute - (minute % 10))) 

# Download and open the file
file_name = download_CMI(yyyymmddhhmn, band, output)

# Open the file
img = gdal.Open(f'NETCDF:{output}/{file_name}.nc:' + var)

# Read the header metadata
metadata = img.GetMetadata()
scale = float(metadata.get(var + '#scale_factor'))
offset = float(metadata.get(var + '#add_offset'))
undef = float(metadata.get(var + '#_FillValue'))
dtime = metadata.get('NC_GLOBAL#time_coverage_start')

# Load the data
ds = img.ReadAsArray(0, 0, img.RasterXSize, img.RasterYSize).astype(float)

# Apply the scale, offset and convert to celsius
ds = (ds * scale + offset) - 273.15

# Read the original file projection and configure the output projection
source_prj = osr.SpatialReference()
source_prj.ImportFromProj4(img.GetProjectionRef())

target_prj = osr.SpatialReference()
target_prj.ImportFromProj4("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs")

# Reproject the data
GeoT = img.GetGeoTransform()
driver = gdal.GetDriverByName('MEM')
raw = driver.Create('raw', ds.shape[0], ds.shape[1], 1, gdal.GDT_Float32)
raw.SetGeoTransform(GeoT)
raw.GetRasterBand(1).WriteArray(ds)

# Define the parameters of the output file  
kwargs = {'format': 'netCDF', \
          'srcSRS': source_prj, \
          'dstSRS': target_prj, \
          'outputBounds': (extent[0], extent[3], extent[2], extent[1]), \
          'outputBoundsSRS': target_prj, \
          'outputType': gdal.GDT_Float32, \
          'srcNodata': undef, \
          'dstNodata': 'nan', \
          'xRes': 0.02, \
          'yRes': 0.02, \
          'resampleAlg': gdal.GRA_NearestNeighbour}

# Write the reprojected file on disk
gdal.Warp(f'{output}/{file_name}_ret.nc', raw, **kwargs)

# Read number of cols and rows
sat_data = gdal.Open(f'{output}/{file_name}_ret.nc')
ncol = sat_data.RasterXSize
nrow = sat_data.RasterYSize

# Load the data
sat_array = sat_data.ReadAsArray(0, 0, ncol, nrow).astype(float)

# Get geotransform
transform = sat_data.GetGeoTransform()
x = int((lon - transform[0]) / transform[1])
y = int((transform[3] - lat) / -transform[5]) 
sat = sat_array[y,x]

print("o valor eh: ", sat)
if int(sat) <= -50: # verificando se é um caso de tempestade
    print("composição tempestade")
    exit()


#-----------------------------------------------------------------------------------------------------------
# Composição NDVI
#-----------------------------------------------------------------------------------------------------------

import math
import numpy as np

# Functions to convert lat / lon extent to array indices 
def geo2grid(lat, lon):

    # Values scale and offset for NDVI 
    xscale, xoffset = 1.4e-02, -0.151865
    yscale, yoffset = -1.4e-02, 0.151865
    
    x, y = latlon2xy(lat, lon)
    col = (x - xoffset)/xscale
    lin = (y - yoffset)/yscale
    return int(lin), int(col)

def latlon2xy(lat, lon):
    # goes_imagery_projection:semi_major_axis
    req = 6378137 # meters
    #  goes_imagery_projection:inverse_flattening
    invf = 298.257222096
    # goes_imagery_projection:semi_minor_axis
    rpol = 6356752.31414 # meters
    e = 0.0818191910435
    # goes_imagery_projection:perspective_point_height + goes_imagery_projection:semi_major_axis
    H = 42164160 # meters
    # goes_imagery_projection: longitude_of_projection_origin
    lambda0 = -1.308996939

    # Convert to radians
    latRad = lat * (math.pi/180)
    lonRad = lon * (math.pi/180)

    # (1) geocentric latitude
    Phi_c = math.atan(((rpol * rpol)/(req * req)) * math.tan(latRad))
    # (2) geocentric distance to the point on the ellipsoid
    rc = rpol/(math.sqrt(1 - ((e * e) * (math.cos(Phi_c) * math.cos(Phi_c)))))
    # (3) sx
    sx = H - (rc * math.cos(Phi_c) * math.cos(lonRad - lambda0))
    # (4) sy
    sy = -rc * math.cos(Phi_c) * math.sin(lonRad - lambda0)
    # (5)
    sz = rc * math.sin(Phi_c)

    # x,y
    x = math.asin((-sy)/math.sqrt((sx*sx) + (sy*sy) + (sz*sz)))
    y = math.atan(sz/sx)

    return x, y


x, y = geo2grid(lat, lon)

# Open the file
matrix = np.load('ndvi_20210102_br_max.npy', allow_pickle=True) # Esse é um arquivo de teste fornecido pelo CEPAGRI 
ndvi = matrix[x][y]
if ndvi < 0.33:
    print("composição ndvi")
    exit()


#-----------------------------------------------------------------------------------------------------------
# Composição agradável
#-----------------------------------------------------------------------------------------------------------

import random

agradaveis = ["chuvas", "ventos", "ndvi"] # lista de composições agradáveis, caso não haja nenhuma alarmante

composicao = random.choice(agradaveis) # escolhe uma aleatoriamente
print("composição " + composicao + " agradavel")


