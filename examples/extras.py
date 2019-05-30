
import numpy as np

def LAB2RGB(L, a, b, radius, rgb = True):
    '''
    draws a circle in CIELab colour space with specified center (L, a, b)
    and radius then converts to RGB values, trimming nonsense values.
    Returns a list of 360 color values.
    '''
    colours = [] # proper spelling :)
    # create CIELab colours
    for ang in range(360):
        theta = ang * np.pi / 180.000 # converts angle to radian
        A = a + radius*np.cos(theta)
        B = b + radius*np.sin(theta)

        # Lab to XYZ
        var_Y = (L + 16) / 115.000
        var_X = A / 500.000 + var_Y
        var_Z = var_Y - B / 200.000

        # filter X, Y, Z with threshold 0.008856
        if  var_Y**3 > 0.008856: var_Y = var_Y**3
        else: var_Y = ( var_Y - 16 / 116.000 ) / 7.787
        if var_X**3 > 0.008856: var_X = var_X**3
        else: var_X = ( var_X - 16 / 116.000 ) / 7.787
        if var_Z**3 > 0.008856: var_Z = var_Z**3
        else: var_Z = ( var_Z - 16 / 116.000 ) / 7.787

        # reference points
        ref_X =  95.047
        ref_Y = 100.000
        ref_Z = 108.883

        X = ref_X * var_X / 100.000
        Y = ref_Y * var_Y / 100.000
        Z = ref_Z * var_Z / 100.000

        # covert XYZ to RGB
        var_R = X * 3.2406 + Y * -1.5372 + Z * -0.4986
        var_G = X * -0.9689 + Y * 1.8758 + Z * 0.0415
        var_B = X * 0.0557 + Y * -0.2040 + Z * 1.0570

        # gamma correction to IEC 61966-2-1 standard
        if var_R > 0.0031308: var_R = 1.055 * ( var_R ** ( 1 / 2.400 ) ) - 0.055
        else: var_R = 12.92 * var_R
        if var_G > 0.0031308: var_G = 1.055 * ( var_G ** ( 1 / 2.400 ) ) - 0.055
        else: var_G = 12.92 * var_G
        if var_B > 0.0031308: var_B = 1.055 * ( var_B ** ( 1 / 2.400 ) ) - 0.055
        else: var_B = 12.92 * var_B

        # trim
        if (var_R*255) > 255: R = 255
        elif (var_R*255) < 0: R = 0
        else: R = round(var_R*255)

        if (var_G*255) > 255: G = 255
        elif (var_G*255) < 0: G = 0
        else: G = round(var_G*255)

        if (var_B*255) > 255: B = 255
        elif (var_B*255) < 0: B = 0
        else: B = round(var_B*255)

        if rgb:
            x = 255.0/2.0
            R = (R - x)/x
            G = (G - x)/x
            B = (B - x)/x
        colours.append([R,G,B])
    return np.array(colours)

#colors = LAB2RGB(L = 50, a = 20, b = 20, radius = 60)
