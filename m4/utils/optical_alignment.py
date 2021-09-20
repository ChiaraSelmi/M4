'''
Authors
  - C. Selmi:  written in 2019
'''

import os
import logging
import numpy as np
from astropy.io import fits as pyfits
from matplotlib import pyplot as plt
from m4.configuration import config_folder_names as fold_name
from m4.configuration import config_folder_names as conf
from m4.utils.optical_calibration import OpticalCalibration
from m4.ground import zernike
from m4.configuration.ott_parameters import OttParameters, OtherParameters
from m4.ground.timestamp import Timestamp
from m4.utils.roi import ROI


class OpticalAlignment():
    """
    Class for the optical alignment

    HOW TO USE IT::

        from m4.utils.optical_alignment import opt_alignment
        al = OpticalAlignment(tt)
        command = al.opt_align(ott, piston=None)
    """

    def __init__(self, tt_cal, ott, interf):
        """The constructor """
        self._logger = logging.getLogger('OPT_ALIGN:')
        self.tt_cal = tt_cal
        self.cal = OpticalCalibration.loadCalibrationObjectFromFits(tt_cal)
        self._who = self.cal.getWho()
        self._mask = self.cal.getMask()
        self._interf = interf
        self._ott = ott
        #post selection
        self._intMatModesVector = None
        self._commandId = None
        self._rec = None
        self._intMat = None
        self._cmat = None
        self._zernikeVectorSelected = None
        #output
        self.par_command = None
        self.rm_command = None

    @staticmethod
    def _storageFolder():
        """ Creates the path where to save data"""
        return fold_name.ALIGNMENT_ROOT_FOLDER


    def opt_align(self, n_images, intMatModesVector=None, commandId=None):
        """
        Parameters
        ----------
        n_images: int
            number of interferometers frames

        Other Parameters
        ----------
            intMatModesVecor: numpy array
                        None is equal to np.array([0,1,2,3,4,5])
                        for tip, tilt, fuoco, coma, coma
            commandId: numpy array
                    array containing the number of degrees of freedom to be commanded

        Returns
        -------
                cmd: numpy array
                    final delta command for the optical alignment
        """
        par_position = self._ott.parabola.getPosition()
        rm_position = self._ott.referenceMirror.getPosition()
        m4_position = self._ott.m4.getPosition()
        self._logger.info('Calculation of the alignment command for %s',
                          self.tt_cal)
        self._intMatModesVector = intMatModesVector
        self._commandId = commandId
        self._intMat, self._rec, self._cmat = self._selectModesInIntMatAndRecConstruction(intMatModesVector, commandId)

        img = self._interf.acquire_phasemap(n_images)
        name = 'StartImage.fits'
        self.tt_al = Timestamp.now()
        dove = os.path.join(self._storageFolder(), self.tt_cal + '--' + self.tt_al)
        os.makedirs(dove)
        self._interf.save_phasemap(dove, name, img)

        if self._who=='PAR + RM':
            cmd, self._zernikeVectorSelected, total_zernike_vector = self._commandGenerator(img)
            self.par_command, self.rm_command = self._reorgCmdForParAndRm(cmd, commandId)
            self._saveData(dove, par_position, rm_position)
            self._alignmentLog(total_zernike_vector, self.tt_al)
            return self.par_command, self.rm_command, dove
        elif self._who=='M4':
            pass
            #cmd, zernike_vector = self._commandGenerator(img)
            #m4_command, zernike_vector_selected, total_zernike_vector = self._reorgCmdForM4(cmd)
            #self._saveAllDataM4(dove, m4_position, m4_command)
            #self._saveZernikeVector(dove, zernike_vector_selected)
            #return m4_command, dove

    def _alignmentLog(self, start_total_coef, tt):
        fits_file_name = os.path.join(self._storageFolder(), 'AlignmentLog.txt')
        file = open(fits_file_name, 'a+')
        file.write('%s ' %self.tt_al)
        for i in range(start_total_coef.size):
            file.write('%9.3e ' %start_total_coef[i])
        file.write('\n')
        file.write('%s ' %tt)
#         for i in range(total_coef.size):
#             file.write('%9.3e ' %total_coef[i])
#         file.write('\n')
#         file.write('%s \n ************\n' %commandId)
        file.close()

    def _selectModesInIntMatAndRecConstruction(self, zernike2control=None,
                                               commandId=None):
        '''
        Other Parameters
        ----------
        zernike2control: numpy array
                    None is equal to np.array([0,1,2,3,4,5])
                    for tip, tilt, fuoco, coma, coma
        commandId: numpy array
                array containing the number of degrees of freedom to be commanded
        '''
        intMat = self.cal.getInteractionMatrix()
        cmat = self.cal.getCommandMatrix()
        if zernike2control is None:
            new_intMat = intMat
            new_cmat = cmat
        else:
            new_intMat = intMat[zernike2control, :]

        if commandId is not None:
            new_intMat = new_intMat[:, commandId]
            new_cmat = cmat[commandId, :]
            new_cmat = new_cmat[:, commandId]

        rec = np.linalg.pinv(new_intMat)
        #self._plotIntMat()
        return new_intMat, rec, new_cmat

    def _plotIntMat(self):
        """ """
        #y = ['PAR_PIST', 'PAR_TIP', 'PAR_TILT', 'RM_TIP', 'RM_TILT']
        plt.clf()
        plt.imshow(self._intMat, origin='lower')
        plt.colorbar()
        plt.xlabel('Commands')
        plt.ylabel('Zernike Modes')
        return

    def _reorgCmdForParAndRm(self, cmd, commandId=None):
        '''reorganizes the delta command in the
        right positions for par and rm '''
        dofIndex = np.append(OttParameters.PARABOLA_DOF, OttParameters.RM_DOF)
        par_command = np.zeros(6)
        rm_command = np.zeros(6)

        if commandId is not None:
            mycomm = np.zeros(5)
            mycomm[commandId] = cmd
            cmd = mycomm

        for i in range(cmd.size):
            if i < OttParameters.PARABOLA_DOF.size:
                par_command[dofIndex[i]] = cmd[i]
            else:
                rm_command[dofIndex[i]] = cmd[i]

        return par_command, rm_command

    def _commandGenerator(self, img):
        """
        args:
            img = image

        returns:
            cmd = command for the dof
        """
        total_zernike_vector, zernike_vector_selected = self._zernikeCoeffCalculator(img)
        print('zernike:')
        print(zernike_vector_selected)
        M = np.dot(self._cmat, self._rec) #non serve la trasposta
        cmd = - np.dot(M, zernike_vector_selected) #serve il meno
        print('mix command:')
        print(cmd)
        return cmd, zernike_vector_selected, total_zernike_vector


    def _zernikeCoeffCalculator(self, img):
        """
        Returns:
                final_coef = zernike coeff on the image
                            (zernike modes 2,3,4,7,8)
                final_coef_selected = zernike selected using intMatModesVector (zernike2control)
        """
        if  conf.simulated ==1:
            mask_index = OtherParameters.MASK_INDEX_SIMULATORE
        else:
            mask_index = OtherParameters.MASK_INDEX_TOWER
        r = ROI()
        roi = r.roiGenerator(img)
        mask = roi[mask_index]
        mm = np.ma.mask_or(img.mask, mask)

        new_image = np.ma.masked_array(img, mask=mm)
        coef, mat = zernike.zernikeFit(new_image, np.arange(10)+1)
        z = np.array([1, 2, 3, 6, 7])
        all_final_coef = coef[z]

        if self._intMatModesVector is None:
            final_coef_selected = all_final_coef
        else:
            final_coef_selected = np.zeros(self._intMatModesVector.size)
            for i in range(self._intMatModesVector.size):
                final_coef_selected[i] = all_final_coef[self._intMatModesVector[i]]
        return all_final_coef, final_coef_selected

    def _saveData(self, dove, par_position, rm_position):
        fits_file_name = os.path.join(dove, 'AlignmentInfo.fits')
        header = pyfits.Header()
        header['WHO'] = self._who
        pyfits.writeto(fits_file_name, self._intMat, header)
        pyfits.append(fits_file_name, self._rec, header)
        pyfits.append(fits_file_name, self._cmat, header)
        if self._intMatModesVector is None:
            self._intMatModesVector = np.array([0,1,2,3,4,5])
        pyfits.append(fits_file_name, self._intMatModesVector, header)
        if self._commandId is None:
            self._commandId = np.array([0,1,2,3,4,5])
        pyfits.append(fits_file_name, self._commandId, header)
        pyfits.append(fits_file_name, self._zernikeVectorSelected, header)

        #salvataggi espliciti
        name = 'PositionAndDeltaCommand.fits'
        vector = np.array([par_position, rm_position, self.par_command, self.rm_command])
        fits_file_name = os.path.join(dove, name)
        pyfits.writeto(fits_file_name, vector)
        if self._intMatModesVector is not None:
            fits_file_name = os.path.join(dove, 'intMatModesVector')
            pyfits.writeto(fits_file_name, self._intMatModesVector)
        if self._commandId is not None:
            fits_file_name = os.path.join(dove, 'commandId')
            pyfits.writeto(fits_file_name, self._commandId)
        name = 'Zernike.fits'
        fits_file_name = os.path.join(dove, name)
        pyfits.writeto(fits_file_name, self._zernikeVectorSelected)

    @staticmethod
    def loadAlignmentObjectFromFits(tt):
        """ Creates the object using information contained in calibration fits file

        Parameters
        ----------
        tt: string
            tracking number

        Returns
        -------
        theObject: ibjecct
                 opt_alignment class object
        """
        ott = None
        interf = None
        tt_cal = tt.split('--')[0]
        theObject = OpticalAlignment(tt_cal, ott, interf)
        theObject.tt_cal = tt_cal
        theObject.tt_al = tt.split('--')[1]
        dove = os.path.join(theObject._storageFolder(), tt)
        file = os.path.join(dove, 'AlignmentInfo.fits')
        header = pyfits.getheader(file)
        hduList = pyfits.open(file)
        theObject._who = header['WHO']
        theObject._intMat = hduList[0].data
        theObject._rec = hduList[1].data
        theObject._cmat = hduList[2].data
        theObject._intMatModesVector = hduList[3].data
        theObject._commandId = hduList[4].data
        theObject._zernikeVectorSelected = hduList[5].data
        return theObject


### M4 ###
    #va riscritta
    def _reorgCmdForM4(self, cmd):
        dofIndex = OttParameters.M4_DOF
        m4_command = np.zeros(6)
        for i in range(cmd.size):
            m4_command[dofIndex[i]] = cmd[i]
        return m4_command

    def _saveAllDataM4(self, dove, m4_position, m4_command):
        name = 'PositionAndDeltaCommand.fits'
        vector = np.array([m4_position, m4_command])
        fits_file_name = os.path.join(dove, name)
        pyfits.writeto(fits_file_name, vector)
