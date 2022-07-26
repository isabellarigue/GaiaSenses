import boto3                                    # Amazon Web Services (AWS) SDK for Python
from botocore import UNSIGNED                   # boto3 config
from botocore.config import Config              # boto3 config
import os
from datetime import datetime                   # Basic Dates and time types

path_dest = 'Samples'
yyyymmddhhmn = '202201021000'
bucket_name = 'noaa-goes16'
product_name = 'ABI-L2-DMWF'

os.makedirs(path_dest, exist_ok=True)

year = datetime.strptime(yyyymmddhhmn, '%Y%m%d%H%M').strftime('%Y')
day_of_year = datetime.strptime(yyyymmddhhmn, '%Y%m%d%H%M').strftime('%j')
hour = datetime.strptime(yyyymmddhhmn, '%Y%m%d%H%M').strftime('%H')
min = datetime.strptime(yyyymmddhhmn, '%Y%m%d%H%M').strftime('%M')

# Initializes the S3 client
s3_client = boto3.client('s3', config=Config(signature_version=UNSIGNED))

# File structure
prefix = f'{product_name}/{year}/{day_of_year}/{hour}/OR_{product_name}-M6C02_G16_s{year}{day_of_year}{hour}{min}' #tem outros prefixos que da pra usar

# Seach for the file on the server
s3_result = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix, Delimiter = "/")

# Check if there are files available
if 'Contents' not in s3_result: 
    # There are no files
    print(f'No files found for the date: {yyyymmddhhmn}, Product-{product_name}')
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