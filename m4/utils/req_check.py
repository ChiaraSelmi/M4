'''
Authors
  - C. Selmi:  written in October 2020
'''

import numpy as np
import os
import glob
from m4.ground import geo
from m4.configuration.ott_parameters import OttParameters
from astropy.io import fits as pyfits
from skimage.draw import circle as draw_circle
from m4.ground import zernike
from scipy.ndimage.interpolation import shift
from m4.ground import read_data
from m4.configuration import config

def patches_analysis(image, radius_m, pixelscale=None, step=None, n_patches=None):
    '''
    Parameters
    ----------
        image: masked array
            image for the analysis
        radius_m: int
            radius of circular patch in meters
        fit: int
            0 to remove tip e tilt
            other values to not remove it
    Other Parameters
    ----------
        pixelscale: int
            value of image's pixel scale [px/m]
        step: int
            distance between patches
        n_patches: int
        number of patches for the second cut
        (if it is None sw creates a single crop in the center of the image)
    Returns
    -------
        rms: numpy array
            std of every patches
        ord_rms: numpy array
            tidy std of every patches
    '''
    if pixelscale is None:
        ps = 1/OttParameters.pscale
    else:
        ps = 1/pixelscale

    raggio_px = radius_m/ps

    nn = image.compressed().shape[0]
    idx = np.where(image.mask==0)
    x = idx[0]
    y = idx[1]

    if step is None:
        n_point = nn
        step = 1
    else:
        n_point = np.int(nn/step)+1

    result_list = []
    list_ima = []
    list_big = []
    for i in range(n_point):
        p = i + i * (step - 1)
        print('%d' %p)
        print('%d %d' %(x[p], y[p]))
        if radius_m == 0.04:
            thresh = 0.05
            ima = _circleImage(image, x[p], y[p], raggio_px)
            if ima is not None:
                list_ima.append(ima)
                alpha, beta = curv_fit(ima, 2*radius_m)
                raggio = roc(2*radius_m, alpha, beta)
                print(raggio)
                result_list.append(raggio)
        if radius_m == 0.015:
            thresh = 0.95
            r1 = 0.1/2
            r_px1 = r1/ps
            ima = _circleImage(image, x[p], y[p], r_px1)
            if ima is not None:
                new_ima = tiptilt_fit(ima)
                list_big.append(new_ima)
                if n_patches is None:
                    final_ima = _circleImage(new_ima, x[p], y[p], raggio_px)
                    if final_ima is not None:
                        list_ima.append(final_ima)
                        result_list.append(np.std(final_ima))
                else:
                    list_circleima = _circleImageList(new_ima, x[p], y[p], n_patches, raggio_px)
                    if list_circleima is not None:
                        for ima in list_circleima:
                            list_ima.append(ima)
                            result_list.append(np.std(ima))

    result_vect = np.array(result_list)
    result_sort = np.copy(result_vect)
    result_sort.sort()
    dim = result_sort.size
    req = result_sort[np.int(thresh*dim)]
    return req, list_ima, result_vect, list_big


def _circleImageList(new_ima, x, y, n_point, r_px):
    '''
    Parameters
    ----------
        image: masked array
            image for the analysis
        radius_m: int
            radius of circular patch in meters
        x: int
            coordinate x
        y: int
            coordinate y
        n_point: int
            number of images for second cut
        pixelscale: int
            value of image's pixel scale
    Returns
    -------
        final_ima_list: list
            list of circle cropped image
    '''
    if new_ima is not None:
        nn = new_ima.compressed().shape[0]
        idx = np.where(new_ima.mask==0)
        x = idx[0]
        y = idx[1]
        step = np.int(nn/(n_point-1))
        final_ima_list = []
        for i in range(n_point):
            p = i + i * (step - 2)
            final_ima = _circleImage(new_ima, x[p], y[p], r_px)
            if final_ima is not None:
                final_ima_list.append(final_ima)
        return final_ima_list

def _circleImage(image, x, y, raggio_px):
    ''' Function to create circular cuts of the image.
    The function excludes cuts that come out of the edges of the image
    and check the threshold for valid point
    NOTE: if image is out of conditions return None type

    Parameters
    ----------
        image: masked array
            image for the analysis
        x: int
            coordinate x
        y: int
            coordinate y
        radius_px: int
            radius of circular patch in pixels

    Returns
    -------
        ima: numpy masked array
            cut image
    '''
    th_validPoint = np.pi * raggio_px**2 * 30 / 100
    if image is not None:
        circle = np.ones((image.shape[0],image.shape[1])).astype(int)
        rr, cc = draw_circle(x, y, raggio_px)
        test_r = (len(list(filter (lambda x : x >= image.shape[0], rr))) > 0)
        test_r2 = (len(list(filter (lambda x : x <= 0, rr))) > 0)
        test_c = (len(list(filter (lambda x : x >= image.shape[0], cc))) > 0)
        if test_r == True:
            pass
        elif test_r2 == True:
            pass
        elif test_c == True:
            pass
        else:
            circle[rr, cc] = 0
            mask_prod = np.ma.mask_or(circle.astype(bool), image.mask)
            ima = np.ma.masked_array(image, mask=mask_prod)
            valid_point = ima.compressed().shape[0]
            if valid_point >= th_validPoint:
                return ima

def tiptilt_fit(ima):
    '''
    Parameters
    ----------
        image: masked array

    Returns
    -------
        ima_ttr: numpy masked array
            image without tip and tilt
    '''
    if ima is not None:
        coef, mat = zernike.zernikeFit(ima,
                                    np.array([2, 3]))
        surf = zernike.zernikeSurface(ima, coef, mat)
        new_image = ima - surf
        ima_ttr = np.ma.masked_array(new_image, mask=ima.mask)
        return ima_ttr

def curv_fit(image, test_diameter):
    '''
    Parameters
    ----------
        image: masked array
            image for the analysis
        test_diameter: int
            diameter for xy coordinates

    Returns
    -------
        alpha: float
            analytical coefficient of scalloping
        beta: float
            analytical coefficient of scalloping
    '''
    size = np.array([image.shape[0], image.shape[1]])
    ima_x = np.arange(size[0], dtype = float)
    ima_y = np.arange(size[1], dtype = float)
    xx = np.tile(ima_x, (size[0], 1))
    yy = np.tile(ima_y, (size[1], 1)).T

    idx = np.where(image.mask==0)
    xx = xx*(test_diameter/2)
    yy = yy*(test_diameter/2)

    nn = image.compressed().shape[0]
    zmat = np.zeros((nn, 6))
    zmat[:,0] = xx[idx]**2
    zmat[:,1] = yy[idx]**2
    zmat[:,2] = xx[idx]*yy[idx]
    zmat[:,3] = xx[idx]
    zmat[:,4] = yy[idx]
    zmat[:,5] = np.ones(nn)

    inv = np.linalg.pinv(zmat)
    coeff = np.dot(inv, image.compressed())

    alpha = 0.5*( coeff[1]+ coeff[2]+ np.sqrt((coeff[1]-coeff[2])**2 + coeff[3]**2) )
    beta  = 0.5*( coeff[1]+ coeff[2]- np.sqrt((coeff[1]-coeff[2])**2 + coeff[3]**2) )
    return alpha, beta

def roc(test_diameter, alpha, beta):
    '''
    Parameters
    ----------
        test_diameter: int
            diameter for xy coordinates
        alpha: float
            analytical coefficient of scalloping
        beta: float
            analytical coefficient of scalloping

    Returns
    -------
        raggio: float
            radius of curvature
    '''
    wfe = test_diameter**2 /(8*np.sqrt(3)) * np.sqrt(2*(alpha-beta)**2 - (alpha+beta)**2)
    rho = test_diameter/2
    raggio = (rho**2 + wfe**2)/(2*wfe)
    return raggio

def slope(image, pscale):
    '''
    Parameters
    ----------
        image: masked array
            image for the analysis
        pscale: float
            pixel scale of image [m/px]
    Returns
    -------
        slope: numpy masked array
    '''
    ax = ((image - shift(image, [1,0]))*pscale)
    ay = ((image - shift(image, [0,1]))*pscale)
    mask = np.ma.mask_or(image.mask, shift(image.mask, [1,0]))
    sp = np.sqrt(((ax))**2+((ay))**2)
    #s = np.sqrt((np.arctan(ax))**2+(np.arctan(ay))**2)
    masked_slope = np.ma.masked_array(sp, mask=mask)
    return masked_slope


### REQ ###

def test242(image):
    ''' Return slop in arcsec '''
    mask = np.invert(image.mask).astype(int)
    x, y, r, xx, yy = geo.qpupil(mask)
    pscale = r * (1/0.17)

    sp = slope(image, pscale)
    # sp in pixel * fattore di conversione da rad ad arcsec
    slope_arcsec = sp * 206265
    rms = slope_arcsec.std()
    return rms

def test243(image, step, n_patches):
    mask = np.invert(image.mask).astype(int)
    x, y, r, xx, yy = geo.qpupil(mask)
    pscale = r * (1/0.17)
    req, list_ima, result_vect, list_big = patches_analysis(image, 0.015, pscale, step, n_patches)
    return req

def test283(image, step):
    mask = np.invert(image.mask).astype(int)
    x, y, r, xx, yy = geo.qpupil(mask)
    pscale = r * (1/0.17)
    req, list_ima, result_vect, list_big = patches_analysis(image, 0.04, pscale, step)
    return req

def diffPiston(image):
    '''
    Parameters
    ----------
        image: masked array
            image for the analysis

    Returns
    -------
        diff_piston: numpy masked array
    '''
    dimx = image.shape[0]
    dimy = image.shape[1]
    imas = image[:, 0:np.int(dimy/2)]
    imad = image[np.int(dimx/2):, :]

    coefs, mat = zernike.zernikeFit(imas, np.arange(3)+1)
    coefd, mat = zernike.zernikeFit(imad, np.arange(3)+1)
    diff_piston = coefs[0]-coefd[1]
    return diff_piston


### ROBUST IMAGE ###
def imageOpticOffset(data_file_path, start, stop):
    '''
    Parameters
    ----------
    data_file_path: string
        data file path for measurement to analyze
    start: int
        number of first image to use for the data analysis
    stop: int
        last number of measurement to use

    Returns
    -------
    image: numpy  masked array
        mean image of the selected data
    '''
    list = glob.glob(os.path.join(data_file_path, '*.fits'))
    list.sort()
    list = list[start:stop]

    cube = None
    print('Creating cube for offset image:')
    for name in list:
        nn = name.split('/')[-1]
        print(nn)
        image = read_data.readFits_maskedImage(name)
        if cube is None:
            cube = image
        else:
            cube = np.ma.dstack((cube, image))

    image = np.mean(cube, axis=2)
    #coef, mat = zernike.zernikeFit(image, np.array([1,2,3,4,5,6]))
    #surf = zernike.zernikeSurface(image, coef, mat)
    #image_ttr = image - surf

    results_path = os.path.join(config.path_name.OUT_FOLDER, 'Req')
    fits_file_name = os.path.join(results_path, 'OptOffset.fits')
    pyfits.writeto(fits_file_name, image.data)
    pyfits.append(fits_file_name, image.mask.astype(int))
    return image

def robustImageFromH5DataSet(n_images, path):
    ''' From h5 files
    Parameters
    ----------
    n_images: int
        number of images to analyze
    path: string
        total path for data analysis

    Returns
    -------
    robust_image: numpy masked array
        robust image from data set
    '''
    list_tot = glob.glob(os.path.join(path, '*.h5'))
    list_tot.sort()
    list = list_tot[0: n_images]
    half = np.int(len(list)/2)
    list1 = list[0:half]
    list2 = list[half:]

    cube1 = None
    print('Creating cube 1:')
    for name in list1:
        print(name)
        image = read_data.InterferometerConverter.from4D(name)
        if cube1 is None:
            cube1 = image
        else:
            cube1 = np.ma.dstack((cube1, image))

    cube2 = None
    print('Creating cube 2:')
    for name in list2:
        print(name)
        image = read_data.InterferometerConverter.from4D(name)
        if cube2 is None:
            cube2 = image
        else:
            cube2 = np.ma.dstack((cube1, image))

    mean1 = np.ma.mean(cube1, axis=2)
    mean2 = np.ma.mean(cube2, axis=2)

    image = mean2 -mean1
    return image

def robustImageFromFitsDataSet(n_images, path, offset=None):
    ''' From fits files and whit offset subtraction

    Parameters
    ----------
    n_images: int
        number of images to analyze
    path: string
        total path for data analysis

    Other Parameters
    ----------------
    offset: if it is None data analysis is made by split n_images in two

    Returns
    -------
    robust_image: numpy masked array
        robust image from data set
    '''
    list_tot = glob.glob(os.path.join(path, '*.fits'))
    list_tot.sort()
    list = list_tot[0: n_images]
    if offset is None:
        half = np.int(len(list)/2)
        list1 = list[0:half]
        list2 = list[half:]

        cube1 = None
        print('Creating cube 1')
        for name in list1:
            #print(name)
            image = read_data.readFits_maskedImage(name)
            if cube1 is None:
                cube1 = image
            else:
                cube1 = np.ma.dstack((cube1, image))

        cube2 = None
        print('Creating cube 2')
        for name in list2:
            #print(name)
            image = read_data.readFits_maskedImage(name)
            if cube2 is None:
                cube2 = image
            else:
                cube2 = np.ma.dstack((cube1, image))

        mean1 = np.ma.mean(cube1, axis=2)
        mean2 = np.ma.mean(cube2, axis=2)

        final_image = mean2 -mean1

    else:
        fits_file_name = os.path.join(config.path_name.OUT_FOLDER, 'Req',
                                      'OptOffset-20210204_233630.fits')
        image_optOffset = read_data.readFits_maskedImage(fits_file_name)

        cube = None
        print('Creating cube')
        for name in list:
            #print(name)
            ima = read_data.readFits_maskedImage(name)
            image = ima - image_optOffset
            if cube is None:
                cube = image
            else:
                cube = np.ma.dstack((cube, image))
        final_image = np.ma.mean(cube, axis=2)
    return final_image





###TEST###
def _imaTest():
    ff = '/Users/rm/Desktop/Arcetri/M4/ProvaCodice/ZernikeCommandTest/20191210_110019/mode0002_measure_segment00_neg.fits'
    hduList=pyfits.open(ff)
    image = np.ma.masked_array(hduList[0].data, mask=hduList[1].data.astype(bool))
    return image

#    path_rm = '/Users/rm/Desktop/Arcetri/M4/RM_20201020.fits'
#    path_par = '/Users/rm/Desktop/Arcetri/M4/PM_20191113.fits'
def _readTestData(path):
    hduList = pyfits.open(path)
    ogg = hduList[0].data
    dim = int(np.sqrt(ogg[:,0].size))
#     image = np.zeros((dim, dim))
#     xx = np.reshape(ogg[:,1], [dim,dim])
#     yy = np.reshape(ogg[:,0], [dim,dim])
#     z = ogg[:,2]
    zz = np.reshape(ogg[:,2], [dim,dim])
    mask = np.isnan(zz)
    prova = np.ma.masked_array(zz, mask=mask)
    ps = ogg[:,1][1] - ogg[:,1][0]
    return prova, ps

### Per l'immagine 591X591
# vv = np.ma.masked_array(np.zeros((1,image.shape[0])), mask=np.ones((1,image.shape[0])).astype(bool))
# vv2 =np.ma.masked_array(np.zeros((image.shape[0]+1,1)), mask=np.ones((image.shape[0]+1, 1)).astype(bool)) 
# pp = np.ma.append(image, vv, axis=0)
# new = np.ma.append(pp, vv2, axis=1)
