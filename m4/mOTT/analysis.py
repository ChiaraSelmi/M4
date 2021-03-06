'''
Authors
  - C. Selmi: written in 2020
'''

import os
import numpy as np
from astropy.io import fits as pyfits
from matplotlib import pyplot as plt
from m4.configuration.config import fold_name

def testCalib():
    tts1 = np.array(['20201214_091212', '20201214_092528', '20201214_093842',
                    '20201214_095152', '20201214_100508', '20201214_101821',
                    '20201214_103128', '20201214_104441', '20201214_105754',
                    '20201214_111110', '20201214_112435', '20201214_113749'])
    tts2 = np.array(['20201214_115451', '20201214_120323', '20201214_121200',
                    '20201214_122040', '20201214_122922', '20201214_123807',
                    '20201214_124640', '20201214_125504', '20201214_130327',
                    '20201214_131134', '20201214_131950', '20201214_132822'])
    intMat1 = None
    intMat2 = None
    for i in range(tts1.size):
        mat1 = pippo(tts1[i])
        mat2 = pippo(tts2[i])
        if intMat1 is None:
            intMat1 = mat1
        else:
            intMat1 = np.stack((intMat1, mat1))
        if intMat2 is None:
            intMat2 = mat2
        else:
            intMat2 = np.stack((intMat2, mat2))
    return intMat1, intMat2

def _readRepData(tt):
    file_name = os.path.join(fold_name.REPEATABILITY_ROOT_FOLDER, tt)
    hduList = pyfits.open(os.path.join(file_name, 'par.fits'))
    par = hduList[0].data
    hduList = pyfits.open(os.path.join(file_name, 'rm.fits'))
    rm = hduList[0].data
    #hduList = pyfits.open(os.path.join(file_name, 'images.fits'))
    #cube = np.ma.masked_array(hduList[0].data, mask=hduList[1].data.astype(bool))
    return par, rm

#     def analyzeOptRep(tt):
#         par, rm, cube = ._readRepData(tt)
#         z_list=[]
#         for i in range(cube.shape[2]):
#             masked_ima = cube[:,:,i]
#             coef, mat = zernike.zernikeFit(masked_ima, np.arange(2, 7))
#             z_list.append(coef)
#         return np.array(z_list)

def actsRepeatability(tt):
    par, rm = _readRepData(tt)

    pos01_list_std = []
    pos02_list_std = []
    pos01_list_mean = []
    pos02_list_mean = []
    pos0_list = []
    for i in range(par.shape[2]):
        pos01 = par[:, 0, i] - par[:, 1, i]
        pos02 = par[:, 0, i] - par[:, 2, i]
        pos01_list_std.append(pos01.std())
        pos02_list_std.append(pos02.std())
        pos01_list_mean.append(pos01.mean())
        pos02_list_mean.append(pos02.mean())

        pos0 = par[:,0,i]
        pos0_list.append(pos0.std())

    pos01_std = np.array(pos01_list_std)
    pos02_std = np.array(pos02_list_std)
    pos01_mean = np.array(pos01_list_mean)
    pos02_mean = np.array(pos02_list_mean)
    pos0 = np.array(pos0_list)
    return pos01_std, pos02_std, pos01_mean, pos02_mean, pos0

def scanAstigComa(tn):
    dove = os.path.join(fold_name.CALIBRATION_ROOT_FOLDER, tn)
    name = os.path.join(dove, 'zernike.fits')
    hduList = pyfits.open(name)
    zer = hduList[0].data
    name = os.path.join(dove, 'PAR_positions.fits')
    hduList = pyfits.open(name)
    par_pos = hduList[0].data
    name = os.path.join(dove, 'RM_positions.fits')
    hduList = pyfits.open(name)
    rm_pos = hduList[0].data
    plt.plot(par_pos[0:20,3], zer[0:20,4],'o')
    plt.plot(par_pos[0:20,3], zer[0:20,5],'o')
    plt.xlabel('Par tilt [as]')
    plt.ylabel('Astigm. Coeff [m]')
    plt.title(tn)
    plt.plot(par_pos[0:20,3], zer[0:20,6],'o')
    plt.plot(par_pos[20:40,3], zer[20:40,7],'o')
    plt.xlabel('Par tilt [as]')
    plt.ylabel('Coma. Coeff [m]')
    plt.legend(['X','Y'])
    plt.title(tn)
    return zer, par_pos, rm_pos

def opticalMonitoring(self):
    pass

def parPistonTest(self):
    pass

def parTiltTest(self):
    pass


###ALTRO###
def pippo(tt):
    from m4.utils.optical_alignment import OpticalAlignment
    al = OpticalAlignment(tt)
    intMat, rec, mask = al._loadAlignmentInfo()
    return intMat