'''
Authors
  - C. Selmi:  written in 2020
'''

import os
import logging
import glob
import numpy as np
from astropy.io import fits as pyfits
from m4.ground import tracking_number_folder
from m4.configuration.config import fold_name
from m4.ground.read_data import InterferometerConverter
from m4.analyzer_iffunctions import AnalyzerIFF
from m4.ground import zernike


class Noise():
    '''
    Class for noise evaluation

    HOW TO USE IT::

        from m4.noise_functions import Noise
        n = Noise()
        #acquisizione dati e analisi dalla cartella hdf5
        tt = n.noise_analysis_from_hdf5_folder(tidy_or_shuffle, template)
        #analisi di pi cartelle di dati
        rms_medio, tip, tilt, n_temp = n.different_template_analyzer(tt_list)
    '''

    def __init__(self):
        """The constructor """
        self._logger = logging.getLogger('NOISE:')
        self._ic = InterferometerConverter()
        self._numberOfNoiseIma = None
        self._cubeFromAnalysis = None

    @staticmethod
    def _storageFolder():
        """ Creates the path where to save measurement data"""
        return fold_name.NOISE_ROOT_FOLDER

    def _defAnalyzer(self, data_file_path, tidy_or_shuffle, template, n_push_pull=None, actsVector=None):
        '''
        arg:
            tidy_or_shuffle = (int) 0 per tidy, 1 per shuffle
            template = np.array composed by 1 and -1
            actsVector = vector of actuators or modes
            n_push_pull = (int) number of push pull

        returns:
            an = analyzer object
        '''
        an = AnalyzerIFF()
        if n_push_pull is None:
            an._nPushPull = 3
        else:
            an._nPushPull = n_push_pull
        an._template = template
        if actsVector is None:
            list = glob.glob(os.path.join(data_file_path,'*.h5'))
            n_tot = len(list)
            n_acts = np.int(n_tot / (an._template.size * an._nPushPull))
            an._actsVector = np.arange(n_acts)
            an._modeVector = np.copy(an._actsVector)
        else:
            an._actsVector = actsVector
            an._modeVector = np.copy(an._actsVector)
        an._cmdAmplitude = np.ones(an._actsVector.shape[0])

        indexingList = []
        if tidy_or_shuffle == 0:
            for i in range(an._nPushPull):
                indexingList.append(an._modeVector)
        elif tidy_or_shuffle == 1:
            for j in range(an._nPushPull):
                np.random.shuffle(an._modeVector)
                indexingList.append(an._modeVector)
        an._indexingList = np.array(indexingList)
        return an


    def noise_analysis_from_hdf5_folder(self, data_file_path, tidy_or_shuffle, template,
                                        n_push_pull=None, actsVector=None):
        '''
        Parameters
        ----------
            data_file_path: string
                            measurement data folder
            tidy_or_shuffle: int
                            0 for tidy, 1 for shuffle
            template: numpy array
                    vector composed by 1 and -1
        Other Parameters
        ----------------
            actsVector: numpy array, optional
                        vector of actuators or modes
            n_push_pull: int
                        number of push pull

        Returns
        -------
                tt: string
                    tracking number of measurements made
        '''
        an = self._defAnalyzer(data_file_path, tidy_or_shuffle, template, actsVector, n_push_pull)

        save = tracking_number_folder.TtFolder(self._storageFolder())
        dove, tt = save._createFolderToStoreMeasurements()

        self._logger.info('Creating analysis in %s', tt)
        self._cubeFromAnalysis = an.createCubeFromImageFolder(data_file_path)
        fits_file_name = os.path.join(dove, 'Cube.fits')
        pyfits.writeto(fits_file_name, self._cubeFromAnalysis.data)
        pyfits.append(fits_file_name, self._cubeFromAnalysis.mask.astype(int))

        self._saveInfo(dove, tidy_or_shuffle, an._template, an._actsVector, an._nPushPull)

        rms_mean, quad_mean = self.rmsFromCube(self._cubeFromAnalysis)
        self._saveResults(rms_mean, quad_mean, dove)
        return tt

    def rmsFromCube(self, cube_to_process):
        '''
        Parameters
        ----------
            cube_to_process: [pixel, pixel, number of imagescube]
                            cube generated by the analyzer_iffunctions

        Returns
        -------
            rms_mean: numpy array
                    rms averaged on the number of modes used in the iff's acquisition
            tip: numpy array
                tip averaged on the number of modes used in the iff's acquisition
            tilt: numpy array
                tilt averaged on the number of modes used in the iff's acquisition
        '''
        self._logger.debug('Calculation of rms, tip and tilt')
        rms_list = []
        coef_tilt_list = []
        coef_tip_list = []
        quad_list = []
        for i in range(cube_to_process.shape[2]):
            image = cube_to_process[:, :, i]
            coef, mat = zernike.zernikeFit(image, np.array([2, 3]))
            sur = zernike.zernikeSurface(image, coef, mat)
            image_ttr = image - sur
            rms = image_ttr.std()
            rms_list.append(rms)
            coef_tip_list.append(coef[0])
            coef_tilt_list.append(coef[1])
            quad = np.sqrt(coef[0]**2 + coef[1]**2)
            quad_list.append(quad)
        rms_vector = np.array(rms_list)
        tip = np.array(coef_tip_list).mean()
        tilt = np.array(coef_tilt_list).mean()
        quad_tt = np.array(quad_list).mean()
        rms_mean = np.mean(rms_vector)
        return rms_mean, quad_tt

    def _spectrumAllData(self, data_file_path):
        list = glob.glob(os.path.join(data_file_path, '*.h5'))
        coef_tilt_list = []
        coef_tip_list = []
        for i in range(len(list)):
            name = 'img_%04d.h5' %i
            print(name)
            file_name = os.path.join(data_file_path, name)
            start_image = self._ic.from4D(file_name)
            coef, mat = zernike.zernikeFit(start_image, np.array([2, 3]))
            coef_tip_list.append(coef[0])
            coef_tilt_list.append(coef[1])
        tip = np.array(coef_tip_list)
        tilt = np.array(coef_tilt_list)
        return tip, tilt

    def _fft(self, vector):
        dt = 35e-3
        n = vector.size
        T = n*dt

        spe = np.fft.fftshift(np.fft.rfft(vector, norm='ortho'))
        freq = np.fft.fftshift(np.fft.rfftfreq(vector.size, d=dt))
        #freq = np.fft.fftshift(np.fft.rfftfreq(spe.size, d=dt))
#         res = np.fft.fft(rms_vector)
#         qq = res.real**2+res.imag**2
        return spe, freq


    def _saveResults(self, rms_mean, quad_mean, destination_file_path):
        ''' Save results as text file
        '''
        fits_file_name = os.path.join(destination_file_path, 'results.txt')
        file = open(fits_file_name, 'w+')
        file.write('%e %e' %(rms_mean, quad_mean))
        file.close()

    def _saveInfo(self, dove, tidy_or_shuffle, template, actsVector, n_push_pull):
        ''' Save measurement data as file fits
        '''
        fits_file_name = os.path.join(dove, 'Info.fits')
        header = pyfits.Header()
        header['NPUSHPUL'] = n_push_pull
        header['TIDYSHUF'] = tidy_or_shuffle
        pyfits.writeto(fits_file_name, template)
        pyfits.append(fits_file_name, actsVector)
        return

    def _readCube(self, tt):
        '''
        args:
            tt = tracking number of measurement

        return:
            _cubeFromAnalysis = cube obtained after iff analysis
        '''
        store_in_folder = Noise._storageFolder()
        file_path = os.path.join(store_in_folder, tt)
        fits_file_name = os.path.join(file_path, 'Cube.fits')
        hduList = pyfits.open(fits_file_name)
        self._cubeFromAnalysis = np.ma.masked_array(hduList[0].data,
                                                    hduList[1].data.astype(bool))
        return self._cubeFromAnalysis

    def _readTempFromInfoFile(self, tt):
        '''
        args:
            tt = tracking number of measurement

        return:
            n_temp = (int) length of template vector
        '''
        store_in_folder = Noise._storageFolder()
        file_path = os.path.join(store_in_folder, tt)
        fits_file_name = os.path.join(file_path, 'Info.fits')
        hduList = pyfits.open(fits_file_name)
        n_temp = hduList[0].data.shape[0]
        return n_temp

    def different_template_analyzer(self, tt_list):
        '''
        Parameters
        ----------
            tt_list: list
                    list of tracking number to analyze

        Returns
        -------
            rms_medio: numpy array
                     vector of mean rms (one for each data folder)
            n_tempo: numpy array
                    vector of the length of the templates used
        '''
        self._logger.info('Analysis whit different template')
        self._logger.debug('tt_list used: %s', tt_list)
        rms_list = []
        quad_list = []
        n_temp_list = []
        for tt in tt_list:
            cube = self._readCube(tt)
            n_temp = self._readTempFromInfoFile(tt)
            rms, quad = self.rmsFromCube(cube)
            rms_list.append(rms)
            quad_list.append(quad)
            n_temp_list.append(n_temp)

        rms_medio = np.array(rms_list)
        quad = np.array(quad_list)
        n_temp = np.array(n_temp_list)
        return rms_medio, quad, n_temp
    ### tt_list ###
    # measurementFolder ='/Users/rm/Desktop/Arcetri/M4/ProvaCodice/Noise'
    # list= os.listdir(measurementFolder); list.sort()
    # tt_list = list[1:len(list)-2]
    ### PLOT ###
    # plot(n_temp, rms, '-o'); plt.xlabel('n_temp'); plt.ylabel('rms_medio')

    ### FUNZIONE DI STRUTTURA ###
    def analysis_whit_structure_function(self, data_file_path, tau_vector):
        '''
        .. 4000 = total number of image in hdf5

        Parameters
        ----------
            data_file_path: string
                            measurement data folder
            tau_vector: numpy array
                        vector of tau to use

        Returns
        -------
            rms_medio: numpy array
                    calculated on the difference of the images (distant tau)
            quad_med: numpy array
                     squaring sum of tip and tilt calculated on the difference
                    of the images
        '''
        list = glob.glob(os.path.join(data_file_path, '*.h5'))
        image_number = len(list)
        i_max = np.int((image_number - tau_vector[tau_vector.shape[0]-1]) /
                       (tau_vector[tau_vector.shape[0]-1] * 2))
        if i_max <= 20:
            raise OSError('tau = %s too large' %tau_vector[tau_vector.shape[0]-1])
        rms_medio_list = []
        quad_med_list = []
        for j in range(tau_vector.shape[0]):
            dist = tau_vector[j]
            rms_list = []
            quad_list = []
            for i in range(i_max):
                k = i * dist * 2
                name = 'img_%04d.h5' %k
                file_name = os.path.join(data_file_path, name)
                image_k = self._ic.from4D(file_name)
                name = 'img_%04d.h5' %(k+dist)
                file_name = os.path.join(data_file_path, name)
                image_dist = self._ic.from4D(file_name)

                image_diff = image_k - image_dist
                zernike_coeff_array, mat = zernike.zernikeFit(image_diff, np.array([2, 3]))
                sur = zernike.zernikeSurface(image_diff, zernike_coeff_array, mat)
                image_ttr = image_diff - sur
                quad = np.sqrt(zernike_coeff_array[0]**2 + zernike_coeff_array[1]**2)

                rms = image_ttr.std()
                rms_list.append(rms)
                quad_list.append(quad)
            rms_vector = np.array(rms_list)
            aa = rms_vector.mean()
            rms_medio_list.append(aa)
            quad_med_list.append(np.array(quad_list).mean())
        rms_medio = np.array(rms_medio_list)
        quad_med = np.array(quad_med_list)

        # per calcolo statistical amplitude of convention
        n_meas = rms_vector.shape[0] * 2 * tau_vector.shape[0]

        return rms_medio, quad_med, n_meas
    # plot(tau_vector, rms, '-o'); plt.xlabel('tau'); plt.ylabel('rms_medio')

    def piston_noise(self, data_file_path):
        ''' Remove tip and tilt from image and average the results
        .. dovrei vedere una variazione nel tempo

        Parameters
        ----------
            data_file_path: string
                            measurement data folder

        Returns
        -------
            mean: numpy array
                vector containing images's mean
            time: numpy array
                vector of the time at which the image were taken
        '''
        list = glob.glob(os.path.join(data_file_path, '*.h5'))
        image_number = len(list)
        time = np.arange(image_number) * (1/27.58)

        mean_list = []
        for j in range(image_number):
            name = 'img_%04d.h5' %j
            file_name = os.path.join(data_file_path, name)
            image = self._ic.from4D(file_name)
            zernike_coeff_array, mat = zernike.zernikeFit(image,
                                                              np.array([2, 3]))
            sur = zernike.zernikeSurface(image, zernike_coeff_array, mat)
            image_ttr = image - sur
            mean = image_ttr.mean()
            mean_list.append(mean)
        return np.array(mean_list), time
