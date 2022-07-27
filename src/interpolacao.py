from PIL import Image

def bilinear():
    im = Image.open(f'C:\\Gaia Senses\\python_goes\\DMW\\14.png') 
    pix = im.load()
    width, height = im.size
    i = 0
    for pixel_x in range(width):
        for pixel_y in range(height):
            sum = 0
            peso = 7
            total = 0
            for k in range(1, 4):
                if (403 > (pixel_x + k) > 0) and (389 > (pixel_y + k) > 0):
                    sum += ((pix[(pixel_x + k), (pixel_y + k)][i]) * peso)
                    total += peso
                if (403 > (pixel_x - k) > 0) and (389 > (pixel_y - k) > 0):
                    sum += ((pix[(pixel_x - k), (pixel_y - k)][i]) * peso)
                    total += peso
                if (403 > (pixel_x - k) > 0) and (389 > (pixel_y + k) > 0):
                    sum += (pix[(pixel_x - k), (pixel_y + k)][i] * peso)
                    total += peso
                if (403 > (pixel_x + k) > 0) and (389 > (pixel_y - k) > 0):
                    sum += (pix[(pixel_x + k), (pixel_y - k)][i] * peso)
                    total += peso
                if (403 > (pixel_x + k) > 0) and (389 > (pixel_y) > 0):
                    sum += (pix[(pixel_x + k), (pixel_y)][i] * peso) 
                    total += peso
                if (403 > (pixel_x - k) > 0) and (389 > (pixel_y) > 0):
                    sum += (pix[(pixel_x - k), (pixel_y)][i] * peso)
                    total += peso
                if (403 > (pixel_x) > 0) and (389 > (pixel_y - k) > 0):
                    sum += (pix[(pixel_x), (pixel_y - k)][i] * peso)
                    total += peso
                if (403 > (pixel_x) > 0) and (389 > (pixel_y + k) > 0):
                    sum += (pix[(pixel_x), (pixel_y + k)][i] * peso)
                    total += peso
                peso -= 1
              
            if total != 0:
                pix[pixel_x, pixel_y] = (int(sum/total), pix[pixel_x, pixel_y][1], 0)

    i = 1
    for pixel_x in range(width):
        for pixel_y in range(height):
            sum = 0
            peso = 7
            total = 0
            for k in range(1, 4):
                if (403 > (pixel_x + k) > 0) and (389 > (pixel_y + k) > 0):
                    sum += ((pix[(pixel_x + k), (pixel_y + k)][i]) * peso)
                    total += peso
                if (403 > (pixel_x - k) > 0) and (389 > (pixel_y - k) > 0):
                    sum += ((pix[(pixel_x - k), (pixel_y - k)][i]) * peso)
                    total += peso
                if (403 > (pixel_x - k) > 0) and (389 > (pixel_y + k) > 0):
                    sum += (pix[(pixel_x - k), (pixel_y + k)][i] * peso)
                    total += peso
                if (403 > (pixel_x + k) > 0) and (389 > (pixel_y - k) > 0):
                    sum += (pix[(pixel_x + k), (pixel_y - k)][i] * peso)
                    total += peso
                if (403 > (pixel_x + k) > 0) and (389 > (pixel_y) > 0):
                    sum += (pix[(pixel_x + k), (pixel_y)][i] * peso) 
                    total += peso
                if (403 > (pixel_x - k) > 0) and (389 > (pixel_y) > 0):
                    sum += (pix[(pixel_x - k), (pixel_y)][i] * peso)
                    total += peso
                if (403 > (pixel_x) > 0) and (389 > (pixel_y - k) > 0):
                    sum += (pix[(pixel_x), (pixel_y - k)][i] * peso)
                    total += peso
                if (403 > (pixel_x) > 0) and (389 > (pixel_y + k) > 0):
                    sum += (pix[(pixel_x), (pixel_y + k)][i] * peso)
                    total += peso
                peso -= 1
              
            if total != 0:
                pix[pixel_x, pixel_y] = (pix[pixel_x, pixel_y][0], int(sum/total), 0)

    im.save(f'C:\\Gaia Senses\\python_goes\\DMW\\15.png', transparent=True, bbox_inches='tight')

bilinear()