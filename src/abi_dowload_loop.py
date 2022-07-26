# Required modules
from netCDF4 import Dataset                     # Read / Write NetCDF4 files
from datetime import datetime                   # Basic Dates and time types
import os                                       # Miscellaneous operating system interfaces
from osgeo import gdal                          # Python bindings for GDAL
from osgeo import osr                           # Python bindings for GDAL
import numpy as np                              # Scientific computing with Python
from matplotlib import cm                       # Colormap handling utilities
import boto3                                    # Amazon Web Services (AWS) SDK for Python
from botocore import UNSIGNED                   # boto3 config
from botocore.config import Config              # boto3 config
from PIL import Image
gdal.PushErrorHandler('CPLQuietErrorHandler')   # Ignore GDAL warnings

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
    # There are no files
    print(f'No files found for the date: {yyyymmddhhmn}, Product-{product_name}')
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

#-----------------------------------------------------------------------------------------------------------

# Input and output directories
input = "Samples"; os.makedirs(input, exist_ok=True)
output = "Rainfall"; os.makedirs(output, exist_ok=True)

# Desired data:
extent = [-75.0, -34, -34, 5.5] # Min lon, Min lat, Max lon, Max lat
bucket_name = 'noaa-goes16'
product_name = "ABI-L2-RRQPEF"
var = 'RRQPE'

hour = 0 # First hour
day = '18' 
year = '2021'
month = '12'
while (hour < 24):
    array = np.zeros((5424,5424))
    if hour < 10:
        hour_str = "0" + str(hour)
    else:
        hour_str = str(hour)
    yyyymmddhhmn = datetime.now().strftime(year + month + day + hour_str + "00") # Concatenating the date string that will be fetched from the server

    # Download and open the file
    file_name = download_PROD(yyyymmddhhmn, product_name, input, bucket_name)
    img = gdal.Open(f'NETCDF:{input}/{file_name}.nc:' + var)
    dqf = gdal.Open(f'NETCDF:{input}/{file_name}.nc:DQF')

    # Read the header metadata
    metadata = img.GetMetadata()
    scale = float(metadata.get(var + '#scale_factor'))
    offset = float(metadata.get(var + '#add_offset'))
    undef = float(metadata.get(var + '#_FillValue'))

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
    filename = f'{output}/{product_name}_{yyyymmddhhmn}_reprojected.nc'
    reproject(filename, img, array, extent, undef)

    # Open the reprojected GOES-R image
    file = Dataset(filename)
    data = file.variables['Band1'][:]
    
    # Modify the colormap to zero values are white
    colormap = cm.get_cmap('binary', 240)
    newcolormap = colormap(np.linspace(0, 1, 240))
    newcolormap[:1, :] = np.array([1, 1, 1, 1])
    cmap = cm.colors.ListedColormap(newcolormap)

    scaled = cmap(data)
    scaled = np.uint8(scaled) * 255
    im = Image.fromarray(scaled)
    im.save(f'{output}/{product_name}_{year}-{month}-{day}_{hour_str}.png')

    hour += 1

