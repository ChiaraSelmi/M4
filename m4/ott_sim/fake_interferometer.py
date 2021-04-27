'''
Authors
  - C. Selmi: written in 2020
'''
import logging
import os
import numpy as np
from astropy.io import fits as pyfits
from m4.ott_sim.ott_images import OttImages
from m4.devices.base_interferometer import BaseInterferometer

class FakeInterferometer(BaseInterferometer):

    def __init__(self):
        """The constructor """
        self._logger = logging.getLogger('FakeInterferometer')

    def acquire_phasemap(self, ott, show=0):
        ottIma = OttImages(ott)
        opd, mask = ottIma.ott_smap(show=show)
        masked_ima = np.ma.masked_array(opd.T, mask=np.invert(mask.astype(bool)).T)
        return masked_ima

    def save_phasemap(self, dove, name, image):
        """
        Parameters
        ----------
        dove: string
            measurement file path
        name: string
            measuremnet fits file name
        image: numpy masked array
            data to save
        """
        fits_file_name = os.path.join(dove, name)
        pyfits.writeto(fits_file_name, image.data)
        pyfits.append(fits_file_name, image.mask.astype(int))
