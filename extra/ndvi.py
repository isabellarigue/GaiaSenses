lat = -10 # lat
lon = -50 # lon

import os                                # Miscellaneous operating system interfaces
import numpy as np                       # Import the Numpy package
import boto3                             # Amazon Web Services (AWS) SDK for Python
from botocore import UNSIGNED            # boto3 config
from botocore.config import Config       # boto3 config
import math
from datetime import datetime            # Basic Dates and time types


def download_CMI(yyyymmddhhmn, band, path_dest):

  os.makedirs(path_dest, exist_ok=True)

  year = datetime.strptime(yyyymmddhhmn, '%Y%m%d%H%M').strftime('%Y')
  day_of_year = datetime.strptime(yyyymmddhhmn, '%Y%m%d%H%M').strftime('%j')
  hour = datetime.strptime(yyyymmddhhmn, '%Y%m%d%H%M').strftime('%H')
  min = datetime.strptime(yyyymmddhhmn, '%Y%m%d%H%M').strftime('%M')

  # AMAZON repository information 
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

# Functions to convert lat / lon extent to array indices 
def geo2grid(lat, lon, nc):

    # Apply scale and offset 
    xscale, xoffset = nc.variables['x'].scale_factor, nc.variables['x'].add_offset
    yscale, yoffset = nc.variables['y'].scale_factor, nc.variables['y'].add_offset
    
    x, y = latlon2xy(lat, lon)
    col = (x - xoffset)/xscale
    lin = (y - yoffset)/yscale
    return int(lin), int(col)



# Required modules
from netCDF4 import Dataset                    # Read / Write NetCDF4 files
from datetime import timedelta, datetime # Basic Dates and time types
#-----------------------------------------------------------------------------------------------------------

# Input and output directories
output = "Samples"; os.makedirs(output, exist_ok=True)

# Desired extent
extent = [-74.0, -33, -34, 0.5] # Min lon, Min lat, Max lon, Max lat (values for Brazil)

# Initial date and time to process
date_ini = '202201011800'

# Number of days to accumulate
ndays = 1

# Convert to datetime
date_ini = datetime(int(date_ini[0:4]), int(date_ini[4:6]), int(date_ini[6:8]), int(date_ini[8:10]), int(date_ini[10:12]))
date_end = date_ini + timedelta(days=ndays)

# Create our references for the loop
date_loop = date_ini

# Variable to check if is the first iteration
first = True

# Create our references for the loop
date_loop = date_ini

ndvi_accumulative = 0

while (date_loop <= date_end):

    # Date structure
    yyyymmddhhmn = date_loop.strftime('%Y%m%d%H%M') 
    print(yyyymmddhhmn)

    # Download the file for Band 02
    file_name_ch02 = download_CMI(yyyymmddhhmn, '2', output)

    # Download the file for Band 03
    file_name_ch03 = download_CMI(yyyymmddhhmn, '3', output)
    
    #-----------------------------------------------------------------------------------------------------------
    
    # If one the files hasn't been downloaded for some reason, skip the current iteration
    if not (os.path.exists(f'{output}/{file_name_ch02}.nc')) or not (os.path.exists(f'{output}/{file_name_ch03}.nc')):
      # Increment the date_loop
      date_loop = date_loop + timedelta(days=1)
      print("The file is not available, skipping this iteration.")
      continue

    # Open the GOES-R image (Band 02)
    file = Dataset(f'{output}/{file_name_ch02}.nc')
                      
    # Convert lat/lon to grid-coordinates
    lly, llx = geo2grid(extent[1], extent[0], file)
    ury, urx = geo2grid(extent[3], extent[2], file)

    # Get the pixel values
    data_ch02 = file.variables['CMI'][ury:lly, llx:urx][::2 ,::2]   
    
    #-----------------------------------------------------------------------------------------------------------
    
    # Open the GOES-R image (Band 03)
    file = Dataset(f'{output}/{file_name_ch03}.nc')
                      
    # Convert lat/lon to grid-coordinates
    lly, llx = geo2grid(extent[1], extent[0], file)
    ury, urx = geo2grid(extent[3], extent[2], file)
            
    # Get the pixel values
    data_ch03 = file.variables['CMI'][ury:lly, llx:urx]      
    
    #-----------------------------------------------------------------------------------------------------------
    
    # Make the arrays equal size
    cordX = np.shape(data_ch02)[0], np.shape(data_ch03)[0]
    cordY = np.shape(data_ch02)[1], np.shape(data_ch03)[1]

    minvalX = np.array(cordX).min()
    minvalY = np.array(cordY).min()

    data_ch02 = data_ch02[0:minvalX, 0:minvalY]
    data_ch03 = data_ch03[0:minvalX, 0:minvalY]
    
    #-----------------------------------------------------------------------------------------------------------
    
    # Calculate the NDVI
    data = (data_ch03 - data_ch02) / (data_ch03 + data_ch02)
    
    #-----------------------------------------------------------------------------------------------------------
    
    # If it's the first iteration, create the array that will store the max values
    if (first == True):
      first = False
      ndvi_max = np.full((data_ch02.shape[0],data_ch02.shape[1]),-9999)
    
    # Keep the maximuns, ignoring the nans
    ndvi_max = np.fmax(data,ndvi_max)
    # Remove low values from the accumulation
    ndvi_max[ndvi_max < 0.1] = np.nan            #TESTARRRRR

    #-----------------------------------------------------------------------------------------------------------
    # Define the coordinates to extract the data (lat,lon) <- pairs
    coordinates = [('P1', lat, lon)]

    for label, lat1, lon1 in coordinates:
      # Reading the data from a coordinate
      lat_point = lat1
      lon_point = lon1
      
      # Convert lat/lon to grid-coordinates
      lat_ind, lon_ind = geo2grid(lat_point, lon_point, file)    
      NDVI_point = (ndvi_max[lat_ind - ury, lon_ind - llx]).round(2)  
      ndvi_accumulative = ndvi_accumulative + NDVI_point
    #-----------------------------------------------------------------------------------------------------------

    # Increment the date_loop
    date_loop = date_loop + timedelta(days=1)

ndvi_average = ndvi_accumulative/ndays
print(ndvi_average)