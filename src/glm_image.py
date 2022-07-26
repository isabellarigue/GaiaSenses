# Required modules
from netCDF4 import Dataset                           # Read / Write NetCDF4 files
import matplotlib.pyplot as plt                       # Plotting library
import cartopy, cartopy.crs as ccrs                   # Plot maps
from datetime import datetime                         # Basic Dates and time types
import os                                             # Miscellaneous operating system interfaces
from osgeo import gdal                                # Python bindings for GDAL
import cartopy.io.shapereader as shpreader            # Import shapefiles
import boto3                                          # Amazon Web Services (AWS) SDK for Python
from botocore import UNSIGNED                         # boto3 config
from botocore.config import Config                    # boto3 config
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

# Input and output directories
input = "Samples"; os.makedirs(input, exist_ok=True)
output = "Output"; os.makedirs(output, exist_ok=True)

# Desired data:
extent = [-75.0, -34, -34, 5.5]
bucket_name = 'noaa-goes16'
title = "GLM"

#-----------------------------------------------------------------------------------------------------------
# Get the GLM Data
seconds = int(datetime.now().strftime('%S'))
yyyymmddhhmnss = datetime.now().strftime('%Y%m%d%H%M' + str(seconds - (seconds % 20))) 
fileGLM = download_GLM(yyyymmddhhmnss, input, bucket_name)
glm = Dataset(f'{input}/{fileGLM}.nc')

e_lats = glm.variables['event_lat'][:]
e_lons = glm.variables['event_lon'][:]

g_lats = glm.variables['group_lat'][:]
g_lons = glm.variables['group_lon'][:]

f_lats = glm.variables['flash_lat'][:]
f_lons = glm.variables['flash_lon'][:] 
#-----------------------------------------------------------------------------------------------------------

# Choose the plot size (width x height, in inches)
dpi = 125
plt.figure(figsize=(10,10), dpi=dpi)

# Use the Geostationary projection in cartopy
ax = plt.axes(projection=ccrs.PlateCarree())

# Define the image extent
ax.set_extent([extent[0], extent[2], extent[1], extent[3]], ccrs.PlateCarree())

# Define the data extent
img_extent = [extent[0], extent[2], extent[1], extent[3]]

# Plot the image
img2 = ax.plot(e_lons,e_lats,'.r', markersize=3, transform=ccrs.PlateCarree(), alpha=1, label="events")
img3 = ax.plot(g_lons,g_lats,'.y', markersize=6, transform=ccrs.PlateCarree(), alpha=1, label="groups")
img4 = ax.plot(f_lons,f_lats,'.g', markersize=3.5, transform=ccrs.PlateCarree(), alpha=1, label="flashs")

#shapefile1 = list(shpreader.Reader('Focos_2022-01-22_2022-01-22.shp').geometries())
#ax.add_geometries(shapefile1, ccrs.PlateCarree())

# Add a shapefile
# https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2019/Brasil/BR/br_unidades_da_federacao.zip
shapefile = list(shpreader.Reader('BR_UF_2019.shp').geometries())
ax.add_geometries(shapefile, ccrs.PlateCarree(), edgecolor='black',facecolor='none', linewidth=0.7)

# Add coastlines, borders and gridlines
ax.coastlines(resolution='10m', color='black', linewidth=0.8, zorder=3)
ax.add_feature(cartopy.feature.BORDERS, edgecolor='black', linewidth=0.5, zorder=4)
#gl = ax.gridlines(crs=ccrs.PlateCarree(), color='gray', alpha=1.0, linestyle='--', linewidth=0.25, xlocs=np.arange(-180, 180, 5), ylocs=np.arange(-90, 90, 5), draw_labels=True)
#gl.top_labels = False
#gl.right_labels = False

plt.legend()

# Add a title
#plt.title(title, fontweight='bold', fontsize=10, loc='left')
#plt.title(datetime.strptime(yyyymmddhhmnss, '%Y%m%d%H%M').strftime('%Y-%m-%d %H:%M'), fontsize=10, loc='right')

# Save the image
plt.savefig(f'{output}/{title}{yyyymmddhhmnss}.png', transparent=True, bbox_inches='tight')

# Show the image
plt.show()