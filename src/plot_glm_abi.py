# Required modules
from netCDF4 import Dataset                           # Read / Write NetCDF4 files
import matplotlib.pyplot as plt                       # Plotting library
import cartopy, cartopy.crs as ccrs                   # Plot maps
from datetime import datetime                         # Basic Dates and time types
import os                                             # Miscellaneous operating system interfaces
from osgeo import gdal                                # Python bindings for GDAL
from osgeo import osr                                 # Python bindings for GDAL
import numpy as np                                    # Scientific computing with Python
from matplotlib import cm                             # Colormap handling utilities
import cartopy.io.shapereader as shpreader            # Import shapefiles
import boto3                                          # Amazon Web Services (AWS) SDK for Python
from botocore import UNSIGNED                         # boto3 config
from botocore.config import Config                    # boto3 config
gdal.PushErrorHandler('CPLQuietErrorHandler')         # Ignore GDAL warnings

#-----------------------------------------------------------------------------------------------------------

def reproject(file_name, ncfile, array, extent, undef):

    # Read the original file projection and configure the output projection
    source_prj = osr.SpatialReference()
    source_prj.ImportFromProj4(ncfile.GetProjectionRef())
    target_prj = osr.SpatialReference()
    target_prj.ImportFromProj4("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs")
   
    # Reproject the data
    GeoT = ncfile.GetGeoTransform()
    driver = gdal.GetDriverByName('MEM')
    raw = driver.Create('raw', array.shape[0], array.shape[1], 1, gdal.GDT_Float32)
    raw.SetGeoTransform(GeoT)
    raw.GetRasterBand(1).WriteArray(array)

    # Define the parameters of the output file  
    kwargs = {'format': 'netCDF', \
            'srcSRS': source_prj, \
            'dstSRS': target_prj, \
            'outputBounds': (extent[0], extent[3], extent[2], extent[1]), \
            'outputBoundsSRS': target_prj, \
            'outputType': gdal.GDT_Float32, \
            'srcNodata': undef, \
            'dstNodata': 'nan', \
            'resampleAlg': gdal.GRA_NearestNeighbour}

    # Write the reprojected file on disk
    gdal.Warp(file_name, raw, **kwargs)

#-----------------------------------------------------------------------------------------------------------

def download_PROD(yyyymmddhhmn, product_name, path_dest, bucket_name):

  os.makedirs(path_dest, exist_ok=True)

  year = datetime.strptime(yyyymmddhhmn, '%Y%m%d%H%M').strftime('%Y')
  day_of_year = datetime.strptime(yyyymmddhhmn, '%Y%m%d%H%M').strftime('%j')
  hour = datetime.strptime(yyyymmddhhmn, '%Y%m%d%H%M').strftime('%H')
  min = datetime.strptime(yyyymmddhhmn, '%Y%m%d%H%M').strftime('%M')

  # Initializes the S3 client
  s3_client = boto3.client('s3', config=Config(signature_version=UNSIGNED))

  # File structure
  prefix = f'{product_name}/{year}/{day_of_year}/{hour}/OR_{product_name}-M6_G16_s{year}{day_of_year}{hour}{min}'

  # Seach for the file on the server
  s3_result = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix, Delimiter = "/")

  # Check if there are files available
  if 'Contents' not in s3_result: 
    print(f'No files found for the date: {yyyymmddhhmn}, Product-{product_name}')
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
#extent = [-75.0, -34, -34, 5.5] # Min lon, Min lat, Max lon, Max lat
extent = [-74.0, -33, -34, 0.5] # Min lon, Min lat, Max lon, Max lat
bucket_name = 'noaa-goes16'
product_name = 'ABI-L2-RRQPEF'
var = 'RRQPE'
rate_abi = "Rainfall Rate mm"
title = "G-16 Abi + GLM"

array = np.zeros((5424,5424))
minute = int(datetime.now().strftime('%M'))
yyyymmddhhmn = datetime.now().strftime('%Y%m%d%H' + str(minute - (minute % 10))) 

# Download and open the file
file_name = download_PROD(yyyymmddhhmn, product_name, input, bucket_name)
img = gdal.Open(f'NETCDF:{input}/{file_name}.nc:' + var)
dqf = gdal.Open(f'NETCDF:{input}/{file_name}.nc:DQF')

# Read the header metadata
metadata = img.GetMetadata()
scale = float(metadata.get(var + '#scale_factor'))
offset = float(metadata.get(var + '#add_offset'))
undef = float(metadata.get(var + '#_FillValue'))
dtime = metadata.get('NC_GLOBAL#time_coverage_start')
unit = metadata.get(var + '#units')

# Load the data
ds = img.ReadAsArray(0, 0, img.RasterXSize, img.RasterYSize).astype(float)
ds_dqf = dqf.ReadAsArray(0, 0, dqf.RasterXSize, dqf.RasterYSize).astype(float)

# Remove undef
ds[ds == undef] = np.nan

# Apply the scale and offset 
ds = (ds * scale + offset)

# Apply NaN's where the quality flag is greater than 1
ds[ds_dqf > 1] = np.nan

# Reproject the file
array = np.nansum(np.dstack((array, ds)),2)
filename = f'{output}/{product_name}_{yyyymmddhhmn}.nc'
reproject(filename, img, array, extent, undef)

# Open the reprojected GOES-R image
file = Dataset(filename)
abi = file.variables['Band1'][:]

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
plt.figure(figsize=(abi.shape[1]/float(dpi),abi.shape[0]/float(dpi)), dpi=dpi)

# Use the Geostationary projection in cartopy
ax = plt.axes(projection=ccrs.PlateCarree())

# Define the image extent
ax.set_extent([extent[0], extent[2], extent[1], extent[3]], ccrs.PlateCarree())

# Define the data extent
img_extent = [extent[0], extent[2], extent[1], extent[3]]

# Plot the image
#img = ax.imshow(abi, vmin=-50, vmax=80, cmap='PuBu', origin='upper', extent=img_extent)
img2 = ax.plot(e_lons,e_lats,'.r', markersize=0, transform=ccrs.PlateCarree(), alpha=1, label="events")
#img3 = ax.plot(g_lons,g_lats,'.y', markersize=5, transform=ccrs.PlateCarree(), alpha=1, label="groups")
#img4 = ax.plot(f_lons,f_lats,'.g', markersize=2.5, transform=ccrs.PlateCarree(), alpha=1, label="flashs")

# Add a shapefile
# https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2019/Brasil/BR/br_unidades_da_federacao.zip
shapefile = list(shpreader.Reader('BR_UF_2019.shp').geometries())
ax.add_geometries(shapefile, ccrs.PlateCarree(), edgecolor='black',facecolor='none', linewidth=0.7)

# Add coastlines, borders and gridlines
# ax.coastlines(resolution='10m', color='white', linewidth=0.8, zorder=3)
# ax.add_feature(cartopy.feature.BORDERS, edgecolor='white', linewidth=0.5, zorder=4)
# gl = ax.gridlines(crs=ccrs.PlateCarree(), color='gray', alpha=1.0, linestyle='--', linewidth=0.25, xlocs=np.arange(-180, 180, 5), ylocs=np.arange(-90, 90, 5), draw_labels=True)
# gl.top_labels = False
# gl.right_labels = False

# Add colorbar
#plt.colorbar(img, label=rate_abi, extend='max', orientation='horizontal', pad=0.05, fraction=0.05)
#plt.legend()

# Add a title
#plt.title(title, fontweight='bold', fontsize=10, loc='left')
#plt.title(datetime.strptime(yyyymmddhhmn, '%Y%m%d%H%M').strftime('%Y-%m-%d %H:%M'), fontsize=10, loc='right')

# Save the image
plt.savefig(f'{output}/{title}{yyyymmddhhmn}.png', transparent=True, bbox_inches='tight')

# Show the image
plt.show()