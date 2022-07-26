from PIL import Image

#colocar limite de max/min valor do pixel

def bilinear():
    im = Image.open(f'C:\\Gaia Senses\\python_goes\\DMW\\35.png') # Can be many different formats.
    pix = im.load()
    width, height = im.size
    i = 0
    for pixel_x in range(width):
        for pixel_y in range(height):
            if  pix[pixel_x, pixel_y][i] != 128:
                sum = 0
                peso = 20000
                total = 0
                for k in range(1, 4):
                    if (403 > (pixel_x + k) > 0) and (389 > (pixel_y + k) > 0) and pix[(pixel_x + k), (pixel_y + k)][i] != 128:
                        sum += ((pix[(pixel_x + k), (pixel_y + k)][i]) * peso)
                        total += peso
                    if (403 > (pixel_x - k) > 0) and (389 > (pixel_y - k) > 0) and pix[(pixel_x - k), (pixel_y - k)][i] != 128:
                        sum += ((pix[(pixel_x - k), (pixel_y - k)][i]) * peso)
                        total += peso
                    if (403 > (pixel_x - k) > 0) and (389 > (pixel_y + k) > 0) and pix[(pixel_x - k), (pixel_y + k)][i] != 128:
                        sum += (pix[(pixel_x - k), (pixel_y + k)][i] * peso)
                        total += peso
                    if (403 > (pixel_x + k) > 0) and (389 > (pixel_y - k) > 0) and pix[(pixel_x + k), (pixel_y - k)][i] != 128:
                        sum += (pix[(pixel_x + k), (pixel_y - k)][i] * peso)
                        total += peso
                    if (403 > (pixel_x + k) > 0) and (389 > (pixel_y) > 0) and pix[(pixel_x + k), (pixel_y)][i] != 128:
                        sum += (pix[(pixel_x + k), (pixel_y)][i] * peso) 
                        total += peso
                    if (403 > (pixel_x - k) > 0) and (389 > (pixel_y) > 0) and pix[(pixel_x - k), (pixel_y)][i] != 128:
                        sum += (pix[(pixel_x - k), (pixel_y)][i] * peso)
                        total += peso
                    if (403 > (pixel_x) > 0) and (389 > (pixel_y - k) > 0) and pix[(pixel_x), (pixel_y - k)][i] != 128:
                        sum += (pix[(pixel_x), (pixel_y - k)][i] * peso)
                        total += peso
                    if (403 > (pixel_x) > 0) and (389 > (pixel_y + k) > 0) and pix[(pixel_x), (pixel_y + k)][i] != 128:
                        sum += (pix[(pixel_x), (pixel_y + k)][i] * peso)
                        total += peso
                    peso -= 4000
                
                if i == 1:
                    if total != 0:
                        pix[pixel_x, pixel_y] = (pix[pixel_x, pixel_y][0], int(sum/total), 0)
                    # else:
                    #     pix[pixel_x, pixel_y] = (pix[pixel_x, pixel_y][0], 130, 0)
                else:
                    if total != 0:
                        pix[pixel_x, pixel_y] = (int(sum/total), pix[pixel_x, pixel_y][1], 0)
                    # else:
                    #     pix[pixel_x, pixel_y] = (130, pix[pixel_x, pixel_y][1], 0)

    i = 1
    for pixel_x in range(width):
        for pixel_y in range(height):
            if pix[pixel_x, pixel_y][i] != 128:
                sum = 0
                peso = 20000
                total = 0
                for k in range(1, 4):
                    if (403 > (pixel_x + k) > 0) and (389 > (pixel_y + k) > 0) and pix[(pixel_x + k), (pixel_y + k)][i] != 128:
                        sum += ((pix[(pixel_x + k), (pixel_y + k)][i]) * peso)
                        total += peso
                    if (403 > (pixel_x - k) > 0) and (389 > (pixel_y - k) > 0) and pix[(pixel_x - k), (pixel_y - k)][i] != 128:
                        sum += ((pix[(pixel_x - k), (pixel_y - k)][i]) * peso)
                        total += peso
                    if (403 > (pixel_x - k) > 0) and (389 > (pixel_y + k) > 0) and pix[(pixel_x - k), (pixel_y + k)][i] != 128:
                        sum += (pix[(pixel_x - k), (pixel_y + k)][i] * peso)
                        total += peso
                    if (403 > (pixel_x + k) > 0) and (389 > (pixel_y - k) > 0) and pix[(pixel_x + k), (pixel_y - k)][i] != 128:
                        sum += (pix[(pixel_x + k), (pixel_y - k)][i] * peso)
                        total += peso
                    if (403 > (pixel_x + k) > 0) and (389 > (pixel_y) > 0) and pix[(pixel_x + k), (pixel_y)][i] != 128:
                        sum += (pix[(pixel_x + k), (pixel_y)][i] * peso) 
                        total += peso
                    if (403 > (pixel_x - k) > 0) and (389 > (pixel_y) > 0) and pix[(pixel_x - k), (pixel_y)][i] != 128:
                        sum += (pix[(pixel_x - k), (pixel_y)][i] * peso)
                        total += peso
                    if (403 > (pixel_x) > 0) and (389 > (pixel_y - k) > 0) and pix[(pixel_x), (pixel_y - k)][i] != 128:
                        sum += (pix[(pixel_x), (pixel_y - k)][i] * peso)
                        total += peso
                    if (403 > (pixel_x) > 0) and (389 > (pixel_y + k) > 0) and pix[(pixel_x), (pixel_y + k)][i] != 128:
                        sum += (pix[(pixel_x), (pixel_y + k)][i] * peso)
                        total += peso
                    peso -= 4000
                
                if i == 1:
                    if total != 0:
                        pix[pixel_x, pixel_y] = (pix[pixel_x, pixel_y][0], int(sum/total), 0)
                    # else:
                    #     pix[pixel_x, pixel_y] = (pix[pixel_x, pixel_y][0], 130, 0)
                else:
                    if total != 0:
                        pix[pixel_x, pixel_y] = (int(sum/total), pix[pixel_x, pixel_y][1], 0)
                    # else:
                    #     pix[pixel_x, pixel_y] = (130, pix[pixel_x, pixel_y][1], 0)

    im.save(f'C:\\Gaia Senses\\python_goes\\DMW\\36.png', transparent=True, bbox_inches='tight')

bilinear()