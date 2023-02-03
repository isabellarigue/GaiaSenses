import os                                       # Miscellaneous operating system interfaces
from osgeo import osr                           # Python bindings for GDAL
from osgeo import gdal                          # Python bindings for GDAL
import boto3                                    # Amazon Web Services (AWS) SDK for Python
from botocore import UNSIGNED                   # boto3 config
from botocore.config import Config              # boto3 config
from datetime import datetime                   
gdal.PushErrorHandler('CPLQuietErrorHandler')   # Ignore GDAL warnings

# Exemple:
lat = -10 
lon = -50 


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

print("the value is: ", sat)
if int(sat) <= -50: # verifying if it is a storm
    print("it is a storm")
