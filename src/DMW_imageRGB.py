# Required modules
from netCDF4 import Dataset                           # Read / Write NetCDF4 files
import matplotlib.pyplot as plt                       # Plotting library
from datetime import datetime                         # Basic Dates and time types
import os                                             # Miscellaneous operating system interfaces
from osgeo import gdal                                # Python bindings for GDAL
import numpy as np                                    # Scientific computing with Python
#from mpl_toolkits.basemap import Basemap              # Import the Basemap toolkit 
import math                                           # Import the Math package
from PIL import Image
import cv2
gdal.PushErrorHandler('CPLQuietErrorHandler')         # Ignore GDAL warnings
#-----------------------------------------------------------------------------------------------------------

# Input and output directories
input = "Samples"; os.makedirs(input, exist_ok=True)
output = "Output_DMW"; os.makedirs(output, exist_ok=True)

# Desired data:
extent = [-75.0, -34, -34, 5.5] # Min lon, Min lat, Max lon, Max lat
title = "Derivated_Motion_Winds"
minute = int(datetime.now().strftime('%M'))
yyyymmddhhmn = datetime.now().strftime('%Y%m%d%H' + str(minute - (minute % 10))) 

# Opening the NetCDF Derivated Motion Winds
#print(arquivo)
nc = Dataset('C:\\Gaia Senses\\python_goes\\Samples_DMW\\OR_ABI-L2-DMWF-M6C07_G16_s20212810500206_e20212810509516_c20212810523319.nc')

# Read the required variables: ================================================ 
pressure = nc.variables['pressure'][:]
temperature = nc.variables['temperature'][:]
wind_direction = nc.variables['wind_direction'][:]
wind_speed = nc.variables['wind_speed'][:]
lats = nc.variables['lat'][:]
lons = nc.variables['lon'][:]

# Selecting data only from the region of interest: ============================
# Detect Latitude lower and upper index, according to the selected extent: 
latli = np.argmin( np.abs( lats - extent[1] ) ) # Lower index
latui = np.argmin( np.abs( lats - extent[3] ) ) # Upper index

# Detect the Longitude index:
# Store the indexes where the lons are between the selected extent:
lon_ind = np.where(( lons >= extent[0]) & (lons <= extent[2] ))[0]
# Eliminate the lon indexes where we don't have the lat indexes:
lon_ind = lon_ind[(lon_ind >= latui) & (lon_ind <= latli)]

# Create the variables lists ==================================================
pressure_a = []
temperature_a = []
wind_direction_a = []
wind_speed_a = []
lats_a = []
lons_a = []

# For each item, append the values to the respective variables ================
for item in lon_ind:
    lons_a.append(lons[item])
    lats_a.append(lats[item])
    pressure_a.append(pressure[item])
    temperature_a.append(temperature[item])
    wind_direction_a.append(wind_direction[item])
    wind_speed_a.append(wind_speed[item])

# Read the variables as numpy arrays
temperature = np.asarray(temperature_a)
wind_direction = np.asarray(wind_direction_a)
wind_speed = np.asarray(wind_speed_a)
lons = np.asarray(lons_a)
lats = np.asarray(lats_a)
        
pressure = np.asarray(pressure_a)
pressure_index = np.where(( pressure >= 100 ) & ( pressure <= 1000 ))[0]
color = '#0000FF' # Blue 
    
# Create the variables lists (considerign only the given pressure range)
pressure_b = []
temperature_b = []
wind_direction_b = []
wind_speed_b = []
lats_b = []
lons_b = []

# For each item, append the values to the respective variables 
for item in pressure_index:
    lons_b.append(lons_a[item])
    lats_b.append(lats_a[item])
    pressure_b.append(pressure_a[item])
    temperature_b.append(temperature_a[item])
    wind_direction_b.append(wind_direction_a[item])
    wind_speed_b.append(wind_speed_a[item])
    
# Final variables for the given pressure range
# Read the variables as numpy arrays
pressure = np.asarray(pressure_b)
temperature = np.asarray(temperature_b)
wind_direction = np.asarray(wind_direction_b)
wind_speed = np.asarray(wind_speed_b)
lons = np.asarray(lons_b)
lats = np.asarray(lats_b)
    
# Calculating the u and v components using the wind_speed and wind direction
u = []
v = []

componente_x = []
componente_y = []
for item in range(lons.shape[0]):
    u.append(-(wind_speed[item]) * math.sin((math.pi / 180) * wind_direction[item])) #conta original do código, para fazer as flechinhas (nesse codigo n esta sendo utilizado, acho q da pra tirar)
    v.append(-(wind_speed[item]) * math.cos((math.pi / 180) * wind_direction[item]))
    if str(wind_speed[item]) != 'nan':
        aux_x = wind_speed[item] * math.cos(wind_direction[item]) #coordenadas polares para retangulares
        comp_x = (255 * aux_x + 155)/310 #normalizando valores entre -127 e 127
        componente_x.append(int(comp_x + 128))
        aux_y = wind_speed[item] * math.sin(wind_direction[item])
        comp_y = (255 * aux_y + 155)/310
        componente_y.append(int(comp_y + 128)) #aplicando offset, para que so tenham valores positivos, ja que o output é uma imagem rgb
    else:
        componente_x.append(int(128.5)) #equivalente ao 0
        componente_y.append(int(128.5))

# im = Image.open(f'C:\\Gaia Senses\\python_goes\\DMW\\base2.png') # Can be many different formats.
# pix = im.load()
# for i in range(lons.size):
#     pixel_x = int(((lons[i] + 75) * 403)/41)
#     if 5.5 >= lats[i] >= -34:
#         pixel_y = 389 - int(((lats[i] + 34) * 389)/39.5)
#         for k in range(10):
#             if (403 > (pixel_x + k) > 0) and (389 > (pixel_y + k) > 0):
#                 pix[(pixel_x + k), (pixel_y + k)] = (componente_x[i], componente_y[i], 0)
#             if (403 > (pixel_x - k) > 0) and (389 > (pixel_y - k) > 0):
#                 pix[(pixel_x - k), (pixel_y - k)] = (componente_x[i], componente_y[i], 0)
#             if (403 > (pixel_x - k) > 0) and (389 > (pixel_y + k) > 0):
#                 pix[(pixel_x - k), (pixel_y + k)] = (componente_x[i], componente_y[i], 0)
#             if (403 > (pixel_x + k) > 0) and (389 > (pixel_y - k) > 0):
#                 pix[(pixel_x + k), (pixel_y - k)] = (componente_x[i], componente_y[i], 0)
#             if (403 > (pixel_x + k) > 0) and (389 > (pixel_y) > 0):
#                 pix[(pixel_x + k), (pixel_y)] = (componente_x[i], componente_y[i], 0)
#             if (403 > (pixel_x - k) > 0) and (389 > (pixel_y) > 0):
#                 pix[(pixel_x - k), (pixel_y)] = (componente_x[i], componente_y[i], 0)
#             if (403 > (pixel_x) > 0) and (389 > (pixel_y - k) > 0):
#                 pix[(pixel_x), (pixel_y - k)] = (componente_x[i], componente_y[i], 0)
#             if (403 > (pixel_x) > 0) and (389 > (pixel_y + k) > 0):
#                 pix[(pixel_x), (pixel_y + k)] = (componente_x[i], componente_y[i], 0)

# im.save(f'C:\\Gaia Senses\\python_goes\\DMW\\DMW_norm10.png', transparent=True, bbox_inches='tight')  # Save the modified pixels as .png

im = cv2.imread(f'C:\\Gaia Senses\\python_goes\\DMW\\base.png') #a base é uma imagem rgb com todos os pixels nos valores (int(128.5), int(128.5), 0)
#pix = im.load()
for i in range(lons.size):
    pixel_x = int(((lons[i] + 75) * 403)/41) #posicao do pixel refrente a tal longitude (aquela conta de escala, semelhante a de conversao de escala de temperatura)
    if 5.5 >= lats[i] >= -34: #se esta dentro do recorte de latitude
        pixel_y = 389 - int(((lats[i] + 34) * 389)/39.5) #posicao do pixel refrente a tal latitude
        raio = 3 #raio do tamanho do circulo a ser plotado (eh pra ser pequeno, tipo um ponto, coloquei isso pra ficar mais visivel)
        cv2.circle(im, (pixel_x, pixel_y), raio, (0, componente_y[i], componente_x[i]), -1) #formato BGR

cv2.imshow('teste',im) 
cv2.imwrite(f'C:\\Gaia Senses\\python_goes\\DMW\\norm2_size10.png', im)              
#im.save(f'C:\\Gaia Senses\\python_goes\\DMW\\DMW_circle.png', transparent=True, bbox_inches='tight')  # Save the modified pixels as .png

# Read the u and v components as numpy arrays
u_comp = np.asarray(u) #acho q da pra tirar
v_comp = np.asarray(v)
#bmap = Basemap(llcrnrlon=extent[0], llcrnrlat=extent[1], urcrnrlon=extent[2], urcrnrlat=extent[3], epsg=4326)
#x,y = bmap(lons, lats)
#bmap.barbs(x, y, u_comp, v_comp, length=2, pivot='middle', barbcolor=color)

plt.axis('off')

# Save the image
plt.savefig(f'C:\\Gaia Senses\\python_goes\\{output}\\{title}{i}.png', transparent=True, bbox_inches='tight')

# Show the image
plt.show()