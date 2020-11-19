'''
Autors
  - C. Selmi:  written in 2019
'''

import os
import copy
import logging
import h5py
import numpy as np
from astropy.io import fits as pyfits
from m4.ground import tracking_number_folder
from m4.configuration.config import fold_name
from m4.type.commandHistory import CmdHistory
from m4.ground import object_from_fits_file_name


class IFFunctionsMaker():
    '''
    This class is responsible for the application of zonal or global commands
    to the deformable mirror in order to collect the functions of influence.
    Data are saving in the folder corresponding to
    the tracking number generated

    HOW TO USE IT::

        from m4.utils import create_device
        device = create_device.myDevice("segment")         #or "m4"
        from m4.influence_functions_maker import IFFunctionsMaker
        IFF = IFFunctionsMaker(device)
        tt = IFF.acq_IFFunctions(modesVectorFitsFileName, nPushPull,
                                amplitudeFitsFileName, cmdMatrixFitsFileName,
                                shuffle=None)
    '''

    def __init__(self, device):
        """The constructor """
        self._device = device
        self._who = self._device._who
        self._nActs = self._device.nActs()
        self._logger = logging.getLogger('IFF_MAKER:')

        self._nPushPull = None
        self._template = None
        self._modesVectorTag = None
        self._amplitudeTag = None
        self._cmdMatrixTag = None
        self._tt_cmdH = None
        self._indexingList = None

    @staticmethod
    def _storageFolder():
        """ Creates the path where to save measurement data"""
        return fold_name.IFFUNCTIONS_ROOT_FOLDER


    def acq_IFFunctions(self, modes_vector_fits_file_name, n_push_pull,
                        amplitude_fits_file_name, cmd_matrix_fits_file_name,
                        shuffle=None, template=None):
        '''
        Performs the process of acquiring interferograms

        Parameters
        ----------
             modes_vector_fits_file_name: string
                                          fits file name
                                          (Example = modes.fits)
             n_push_pull: int
                          number of push pull on the actuator
             amplitude_fits_file_name: string
                                       fits file name
                                       (Example = amp.fits)
             cmd_matrix_fits_file_name: int
                                        fits file name
                                        (Example = modalBase.fits)
        Other Parameters
        ----------------
             shuffle: optional
                      if not indicated, the function create the tidy command
                      history matrix
             template: numpy array, optional
                       vector composed by 1 and -1
                       if not indicated, the function create the vector [1, -1, 1]

        Returns
        -------
                tt: string
                    tracking number of measurements made
        '''
        amplitude, modes_vector, cmd_matrix = \
        object_from_fits_file_name.readObjectFitsFileName(amplitude_fits_file_name,
                                                          modes_vector_fits_file_name,
                                                          cmd_matrix_fits_file_name)
        self._nPushPull = n_push_pull
        if template is None:
            self._template = np.array([1, -1])
        else:
            self._template = template

        self._modesVectorTag = modes_vector_fits_file_name
        self._amplitudeTag = amplitude_fits_file_name
        self._cmdMatrixTag = cmd_matrix_fits_file_name

        store_in_folder = self._storageFolder()
        indexing_input = copy.copy(modes_vector)
        save = tracking_number_folder.TtFolder(store_in_folder)
        dove, tt = save._createFolderToStoreMeasurements()

        diagonal_mat = self._diagonalControll(cmd_matrix)
        if np.count_nonzero(diagonal_mat -
                            np.diag(np.diagonal(diagonal_mat))) == 0:
            print('Measure of zonal IF')
            self._logger.info("Measurement of zonal influence functions for %s. Location: %s",
                              self._who, tt)
        else:
            print('Measure of global IF')
            self._logger.info("Measurement of modal influence functions for %s. Location: %s",
                              self._who, tt)


        cmdH = CmdHistory(self._device)

        if shuffle is None:
            command_history_matrix_to_apply, self._tt_cmdH = \
                    cmdH.tidyCommandHistoryMaker(modes_vector,
                                                 amplitude,
                                                 cmd_matrix,
                                                 n_push_pull,
                                                 template)
        else:
            command_history_matrix_to_apply, self._tt_cmdH = \
                    cmdH.shuffleCommandHistoryMaker(modes_vector,
                                                    amplitude,
                                                    cmd_matrix,
                                                    n_push_pull,
                                                    template)
        self._indexingList = cmdH.getIndexingList()
        self._saveInfoAsFits(dove)
        self._saveInfoSeparately(dove)

        for i in range(command_history_matrix_to_apply.shape[1]):
            self._applyToDM(command_history_matrix_to_apply[:, i])
            #acquisizione immagine con 4d
            #salvataggio immagine

        return tt


    def _diagonalControll(self, matrix):
        """ Prepares the matrix for the diagonal control """
        v = np.zeros((self._nActs, 1))
        reps = matrix.shape[0] - matrix.shape[1]
        vects = np.tile(v, reps)
        new_matrix = np.hstack((matrix, vects))

        return new_matrix


    def _applyToDM(self, vector_to_apply):
        ''' Deve applicare i comandi della command history matrix allo specchio
        '''
        pass

    def _testIFFunctions_createCube25fromFileFitsMeasure(self):
        """ Test function: create a measurement cube using data
        generate whit m4 idl software"""
        fold_my_pc = '/Users/rm/Desktop/Arcetri/M4/ProvaCodice/Immagini_prova/OIM_25modes.fits'
        #fold_m4_pc = os.path.join(Configuration.OPD_DATA_FOLDER, 'TestData', 'OIM_25modes.fits')
        hduList = pyfits.open(fold_my_pc)
        cube_50 = hduList[0].data

        imaList = []
        maskList = []
        for i in range(cube_50.shape[0]):
            if i%2 == 0:
                imaList.append(cube_50[i])
            else:
                maskList.append(cube_50[i])

        cube_25 = None
        zipped = zip(imaList, maskList)
        for ima, mask in zipped:
            immagine = np.ma.masked_array(ima, mask=mask)
            if cube_25 is None:
                cube_25 = immagine
            else:
                cube_25 = np.ma.dstack((cube_25, immagine))
        return cube_25


    def _saveInfoAsFits(self, folder):
        """ Save the fits info file containing the input data for
        the creation of iff

        Args:
            folder = path that indicates where to save the info file
        """
        fits_file_name = os.path.join(folder, 'info.fits')
        header = pyfits.Header()
        header['NPUSHPUL'] = self._nPushPull
        header['WHO'] = self._who
        header['TT_CMDH'] = self._tt_cmdH
        header['MODEVECT'] = self._modesVectorTag
        header['CMDMAT'] = self._cmdMatrixTag
        header['AMP'] = self._amplitudeTag
        pyfits.writeto(fits_file_name, self._indexingList, header)
        pyfits.append(fits_file_name, self._template)

    def _saveInfoSeparately(self, folder):
        """ Save the input data for the creation of iff

        Args:
            folder = path that indicates where to save
        """
        fits_file_name = os.path.join(folder, 'indexingList.fits')
        pyfits.writeto(fits_file_name, self._indexingList)
        fits_file_name = os.path.join(folder, 'template.fits')
        pyfits.writeto(fits_file_name, self._template)
        fits_file_name = os.path.join(folder, 'more_info.txt')
        file = open(fits_file_name, 'w+')
        file.write('Who = %s, tt_cmdH = %s' %(self._who, self._tt_cmdH))
        file.close()
        fits_file_name = os.path.join(folder, 'tag_info.txt')
        file = open(fits_file_name, 'w+')
        file.write('Modes_vector_tag = %s, Cmd_matrix_tag = %s, Amplitude_tag = %s' \
                   %(self._modesVectorTag, self._cmdMatrixTag, self._amplitudeTag))
        file.close()
        fits_file_name = os.path.join(folder, 'n_push_pull.txt')
        file = open(fits_file_name, 'w+')
        file.write('N_push_pull = %e' %(self._nPushPull))
        file.close()

    def _saveInfoAsH5(self, folder):
        """ Save the h5 info file containing the input data for
        the creation of iff

        Args:
            folder = path that indicates where to save the info file
        """
        fits_file_name = os.path.join(folder, 'info.h5')
        hf = h5py.File(fits_file_name, 'w')
        hf.create_dataset('dataset_1', data=self._indexingList)
        hf.attrs['MODEVECT'] = self._modesVectorTag
        hf.attrs['CMDMAT'] = self._cmdMatrixTag
        hf.attrs['AMP'] = self._amplitudeTag
        hf.attrs['NPUSHPUL'] = self._nPushPull
        hf.attrs['WHO'] = self._who
        hf.attrs['TT_CMDH'] = self._tt_cmdH
        hf.close()


    @staticmethod
    def loadInfoFromFits(folder):
        """ Reload information contained in fits Info file

        Parameters
        ----------
        fits_file_name: string
                        info file path

        Returns
        -------
        who: string
            which segment
        tt_cmdH: string
                CommandHistory tracking number
        acts_vector: numpy array
                    vector of actuators
        cmd_matrix: matrix
                    modal base
        cmd_ampl: numpy array
                amplitude vector
        n_push_pull: int
                    number of push pull
        indexingList: list
                    list of index order using in command history
        """
        additional_info_fits_file_name = os.path.join(folder, 'info.fits')
        header = pyfits.getheader(additional_info_fits_file_name)
        hduList = pyfits.open(additional_info_fits_file_name)
        acts_vector_tag = header['MODEVECT']
        cmd_matrix_tag = header['CMDMAT']
        cmd_ampl_tag = header['AMP']
        indexingList = hduList[0].data
        template = hduList[1].data
        who = header['WHO']
        tt_cmdH = header['TT_CMDH']
        try:
            n_push_pull = header['NPUSHPUL']
        except KeyError:
            n_push_pull = 1

        cmd_ampl, acts_vector, cmd_matrix = \
        object_from_fits_file_name.readObjectFitsFileName(cmd_ampl_tag,
                                                          acts_vector_tag,
                                                          cmd_matrix_tag)
        return (who, tt_cmdH, acts_vector, cmd_matrix, cmd_ampl,
                n_push_pull, indexingList, template)

    @staticmethod
    def loadInfoFromH5(tt):
        """ Reload information contained in h5 Info file

        Parameters
        ----------
        fits_file_name: string
                        info file path

        Returns
        -------
        who: string
            which segment
        tt_cmdH: string
                CommandHistory tracking number
        acts_vector: numpy array
                    vector of actuators
        cmd_matrix: matrix
                    modal base
        cmd_ampl: numpy array
                amplitude vector
        n_push_pull: int
                    number of push pull
        indexingList: list
                    list of index order using in command history
        """
        store_in_folder = IFFunctionsMaker._storageFolder()
        folder = os.path.join(store_in_folder, tt)
        file_name = os.path.join(folder, 'info.h5')
        hf = h5py.File(file_name, 'r')
        hf.keys()
        data_1 = hf.get('dataset_1')
        acts_vector_tag = hf.attrs['MODEVECT']
        cmd_matrix_tag = hf.attrs['CMDMAT']
        cmd_ampl_tag = hf.attrs['AMP']
        indexingList = np.array(data_1)
        n_push_pull = hf.attrs['NPUSHPUL']
        who = hf.attrs['WHO']
        tt_cmdH = hf.attrs['TT_CMDH']

        cmd_ampl, acts_vector, cmd_matrix = \
        object_from_fits_file_name.readObjectFitsFileName(cmd_ampl_tag,
                                                          acts_vector_tag,
                                                          cmd_matrix_tag)
        return (who, tt_cmdH, acts_vector, cmd_matrix, cmd_ampl,
                n_push_pull, indexingList)
