'''
@author: cs
'''

import numpy as np
#import sklearn.feature_extraction as skf_e
#import sklearn.cluster as skc
import skimage.segmentation as sks
#from skimage.measure import label
from scipy import ndimage as ndi
from m4.ground import logger


class ROI():

    def __init__(self):
        pass

    def roiGenerator(self, ima):
        '''
        arg:
            ima= np.masked_array
        return:
            roiList= lista delle prime 7 roi trovate nell'immagine

        NOTA: roiList[3]= RM roi per allineamento
              roiList[3]= central roi per segmento

        '''
        logger.log('Creation', 'of', 'roi', 'list')
        labels = ndi.label(np.invert(ima.mask))[0]
        #import skimage.morphology as skm
        #pro= skm.watershed(ima, markers)
        roiList = []
        for i in range(1, 13):
            maski = np.zeros(labels.shape, dtype=np.bool)
            maski[np.where(labels == i)] = 1
            final_roi = np.ma.mask_or(np.invert(maski), ima.mask)
            roiList.append(final_roi)
        return roiList



    def _ROIonAlignmentImage(self, ima):

        markers = ima.mask.astype('int')*0
        markers[0, 0] = 1
        markers[170, 86] = 2
        markers[322, 166] = 3
        markers[223, 252] = 4
        markers[163, 442] = 5
        markers[73, 229] = 6

        roi_mask = sks.random_walker(ima.mask, markers)

        roiList = []
        for i in range(2, 7):
            maski = np.zeros(roi_mask.shape, dtype=np.bool)
            maski[np.where(roi_mask == i)] = 1
            final_roi = np.ma.mask_or(np.invert(maski), ima.mask)
            roiList.append(final_roi)

        self._DetectorROI = roiList
        return self._DetectorROI


    def _ROIonSegment(self, ima):
#graph = skf_e.image.img_to_graph(ima.data, mask=ima.mask)
#labels = skc.spectral_clustering(graph, n_clusters=4, eigen_solver='arpack')
#labels = label(ima.mask.astype(int))
#label_im = -np.ones(ima.mask.shape)
#label_im[ima.mask.astype(int)] = labels

        markers = ima.mask.astype('int')*0

        #per immagini 256x256
#         markers[0,0]=1
#         markers[73,39]=2
#         markers[115,116]=3
#         markers[79, 221]=4
#         markers[9,128]=5

        #per immagini 512x512
        markers[0, 0] = 1
        markers[170, 86] = 2
        markers[216, 266] = 3
        markers[177, 416] = 4
        markers[17, 258] = 5

        roi_mask = sks.random_walker(ima.mask, markers)


        roiList = []
        for i in range(2, 6):
            maski = np.zeros(roi_mask.shape, dtype=np.bool)
            maski[np.where(roi_mask == i)] = 1
            final_roi = np.ma.mask_or(np.invert(maski), ima.mask)
            roiList.append(final_roi)

        self._DetectorROI = roiList
        return self._DetectorROI


    def _ROIonM4(self, ima):
#graph = skf_e.image.img_to_graph(ima.data, mask=ima.mask)
#labels = skc.spectral_clustering(graph, n_clusters=7, eigen_solver='arpack')
#labels = label(ima.mask.astype(int))
#label_im = -np.ones(ima.mask.shape)
#label_im[ima.mask.astype(int)] = labels

        #per immagini 512x512
        markers = ima.mask.astype('int')*0
        markers[0, 0] = 1
        markers[164, 407] = 2
        markers[339, 409] = 3
        markers[433, 254] = 4
        markers[338, 103] = 5
        markers[157, 101] = 6
        markers[232, 270] = 8
        markers[83, 257] = 7
        roi_mask = sks.random_walker(ima.mask, markers)

        roiList = []
        for i in range(2, 9):
            maski = np.zeros(roi_mask.shape, dtype=np.bool)
            maski[np.where(roi_mask == i)] = 1
            final_roi = np.ma.mask_or(np.invert(maski), ima.mask)
            roiList.append(final_roi)

        self._DetectorROI = roiList
        return self._DetectorROI
