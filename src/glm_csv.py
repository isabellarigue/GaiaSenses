# Required modules
from netCDF4 import Dataset                           # Read / Write NetCDF4 files
from datetime import timedelta, datetime              # Basic Dates and time types
import os                                             # Miscellaneous operating system interfaces
from osgeo import gdal                                # Python bindings for GDAL
import boto3                                          # Amazon Web Services (AWS) SDK for Python
from botocore import UNSIGNED                         # boto3 config
from botocore.config import Config                    # boto3 config
import pandas as pd
import pickle
gdal.PushErrorHandler('CPLQuietErrorHandler')         # Ignore GDAL warnings

#-----------------------------------------------------------------------------------------------------------
def download_GLM(yyyymmddhhmnss, path_dest, bucket_name):

  os.makedirs(path_dest, exist_ok=True)

  year = datetime.strptime(yyyymmddhhmnss, '%Y%m%d%H%M%S').strftime('%Y')
  day_of_year = datetime.strptime(yyyymmddhhmnss, '%Y%m%d%H%M%S').strftime('%j')
  hour = datetime.strptime(yyyymmddhhmnss, '%Y%m%d%H%M%S').strftime('%H')
  min = datetime.strptime(yyyymmddhhmnss, '%Y%m%d%H%M%S').strftime('%M')
  seg = datetime.strptime(yyyymmddhhmnss, '%Y%m%d%H%M%S').strftime('%S')

  # Initializes the S3 client
  s3_client = boto3.client('s3', config=Config(signature_version=UNSIGNED))

  # File structure
  product_name = "GLM-L2-LCFA"
  prefix = f'{product_name}/{year}/{day_of_year}/{hour}/OR_{product_name}_G16_s{year}{day_of_year}{hour}{min}{seg}'

  # Seach for the file on the server
  s3_result = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix, Delimiter = "/")

  # Check if there are files available
  if 'Contents' not in s3_result: 
    print(f'No files found for the date: {yyyymmddhhmnss}, Product-{product_name}')
    return -1
  else:
    for obj in s3_result['Contents']: 
      key = obj['Key']
      file_name = key.split('/')[-1].split('.')[0]
      if os.path.exists(f'{path_dest}/{file_name}.nc'):
        print(f'File {path_dest}/{file_name}.nc exists')
      else:
        print(f'Downloading file {path_dest}/{file_name}.nc')
        s3_client.download_file(bucket_name, key, f'{path_dest}/{file_name}.nc')
  return f'{file_name}'
#-----------------------------------------------------------------------------------------------------------

# Desired data:
input = "Samples"; os.makedirs(input, exist_ok=True)
output = "GLM"; os.makedirs(output, exist_ok=True)
inicial_day  = 16
final_day = 17
month = 12
year = 2021
bucket_name = 'noaa-goes16'

date_ini = str(datetime(year,month,inicial_day,0,0))
date_end = str(datetime(year,month,final_day,0,0))
primeiro = True

while (date_ini <= date_end):
    # Get the GLM Data
    yyyymmddhhmnss = datetime.strptime(date_ini, '%Y-%m-%d %H:%M:%S').strftime('%Y%m%d%H%M%S')
    fileGLM = download_GLM(yyyymmddhhmnss, input, bucket_name)
    glm = Dataset(f'{input}/{fileGLM}.nc')

    f_lats = glm.variables['flash_lat'][:]
    f_lons = glm.variables['flash_lon'][:] 

    if (primeiro):
        df_anterior = pd.DataFrame({"lat": f_lats, "lon": f_lons, "time": datetime.strptime(yyyymmddhhmnss, '%Y%m%d%H%M%S').strftime('%Y-%m-%d %H:%M:%S')})
        primeiro = False
    else:
        df_1 = pd.DataFrame({"lat": f_lats, "lon": f_lons, "time": datetime.strptime(yyyymmddhhmnss, '%Y%m%d%H%M%S').strftime('%Y-%m-%d %H:%M:%S')})
        df = df_anterior.append(df_1, ignore_index=True)
        df_anterior = df

    date_ini = str(datetime.strptime(date_ini, '%Y-%m-%d %H:%M:%S') + timedelta(seconds=20))

df.to_csv(f'{output}/flashs_{inicial_day}-{final_day}.csv')
