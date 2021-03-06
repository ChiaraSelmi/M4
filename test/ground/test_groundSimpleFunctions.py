'''
Authors
  - C. Selmi: written in 2020
'''
import unittest
import numpy as np
from skimage.draw import circle
from m4.ground import geo
from m4.ground import find_directory
from m4.ground import smooth_function
from m4.ground.timestamp import Timestamp
from m4.ground import logger_set_up
from m4.ground.tracking_number_folder import TtFolder
from m4.ground import zernike


class Test(unittest.TestCase):


    @unittest.skip('Mettere dei file')
    def testFindDirectory(self):
        tt = '2021...'
        find_directory.findTtPath(tt)

    def testGeometry(self):
        img = np.random.rand(500, 500)
        masked_ima = geo.draw_mask(img, 250, 250, 50)
        geo.qpupil(masked_ima)
        geo.rotate(img, 30)

    def testGUI(self):
        pass

    @unittest.skip('Dove mettere il file')
    def testLogger(self):
        file_path = '?'
        logging_level = 0
        logger_set_up.set_up_logger(file_path, logging_level)

    def testReadData(self):
        pass

    def testSmoothFunction(self):
        data = np.arange(100)
        smooth_function.smooth(data, 4)

    def testTimestamp(self):
        t = Timestamp()
        t.asNowString()
        t.asTodayString()
        t.now()
        t.nowUSec()
        t.today()

    @unittest.skip('Dove mettere il file')
    def testTtFolder(self):
        store_in_folder = '?'
        t = TtFolder(store_in_folder)
        t._createFolderToStoreMeasurements()

    def testZernike(self):
        img = np.random.rand(500, 500)
        mask = np.ones((500, 500), dtype= bool)
        rr, cc = circle(250, 250, 100)
        mask[rr,cc] = 0
        masked_ima = np.ma.masked_array(img, mask=mask)

        coef, mat = zernike.zernikeFit(masked_ima, np.arange(10)+1)
        zernike.zernikeSurface(masked_ima, coef, mat)
