'''
@author: cs
'''


import numpy as np
import os
import copy
import pyfits
from matplotlib import pyplot as plt


def main1908_createFileInfo():
    from m4.utils import createDevice 
    device= createDevice.myDevice("segment") 
    from m4.influenceFunctionsMaker import IFFunctionsMaker 
    IF= IFFunctionsMaker(device) 
    cmdMatrix=np.ones([892,700]) 
    cmdMatrix.T[30]=np.zeros(892) 
    indexing=np.array([10,11,12,13,14,15,16,17,18,19,30,31,32,33,34]) 
    amplitude= np.ones(15)
    save="/Users/rm/Desktop/Arcetri/M4/ProvaCodice/IFFunctions" 
    #dove= IF.acq_IFFunctions(save,indexing,3, amplitude,cmdMatrix)
    dove= IF.acq_IFFunctions(save,indexing,3,amplitude)
    
    return dove

def main1908_analyzer(tt):
    from m4.analyzerIFFunctions import AnalyzerIFF
    save=os.path.join("/Users/rm/Desktop/Arcetri/M4/ProvaCodice/IFFunctions", tt)
    an= AnalyzerIFF.loadInfoFromh5Folder(save)
    
    return an

def main2108_amplitudeReaorgTEST():
    from m4.type.commandHistory import CmdHistory
    from m4.utils import createDevice 
    from m4.influenceFunctionsMaker import IFFunctionsMaker
    device= createDevice.myDevice("segment")
    IF= IFFunctionsMaker(device)
    cmdH= CmdHistory(device)
    
    indexing= np.array([11,12,13,14,15])
    cmdMatrix=np.ones([892,700]) 
    cmdMatrix.T[30]=np.zeros(892)
    amplitude=np.array([1,2,3,4,5])
    indexingImput= copy.copy(indexing)
    matrixToApply, indexingList= cmdH.createShuffleCmdHistory(
                                            indexing, 3, cmdMatrix)
    
    vect= IF._amplitudeReorganization(indexingImput, indexingList, amplitude, 3) 
    
    return indexingList, vect


def main2808_commandHistoryTest():
    from m4.utils import createDevice 
    from m4.type.commandHistory import CmdHistory 
    device= createDevice.myDevice("segment") 
    cmdH= CmdHistory(device)
    modeVector=np.array([11,12,13,14,15])
    cmdMatrix=np.ones([892,700]) 
    cmdMatrix.T[30]=np.zeros(892)
    amplitude=np.array([1,2,3,4,5])
    matrixToApply= cmdH.shuffleCommandHistoryMaker(modeVector, 
                                                   amplitude, cmdMatrix, 3)
    #matrixToApply2= cmdH.tidyCommandHistoryMaker(modeVector, 
                                                    #amplitude, cmdMatrix, 3)
    
    return matrixToApply

def main2908_provaIFF():
    from m4.utils import createDevice 
    device= createDevice.myDevice("segment") 
    from m4.influenceFunctionsMaker import IFFunctionsMaker
    IF= IFFunctionsMaker(device) 
    
    cmdMatrix=np.ones([892,800]) 
    cmdMatrix.T[30]=np.zeros(892) 
    #cmdMatrix=np.zeros((892,800))  
    #for i in range(800):
    #    cmdMatrix[i][i]=1
    modeVect=np.array([10,11,12,13,14,15,16,17,18,19,30,31,32,33,34]) 
    amp= np.array([0,1,2,3,4,5,6,7,8,9,0.30,0.31,0.32,0.33,0.34])
    
    IF.acq_IFFunctions(modeVect, 3, amp, cmdMatrix, 1)
    
    
def main0409_imageM4():
    fitsRoot= "/Users/rm/Desktop/Arcetri/M4/ProvaCodice/Immagini_prova"
    fitsFileName= os.path.join(fitsRoot, 'mode_0005.fits')
    hduList= pyfits.open(fitsFileName)
    ima= hduList[0].data
    m4= ima[1]
    fitsFileName= os.path.join(fitsRoot, 'mode_0006.fits')
    hduList= pyfits.open(fitsFileName)
    ima= hduList[0].data
    segment= ima[1]
    
    mask=np.zeros(segment.shape, dtype=np.bool) 
    mask[np.where(segment==segment.max())]=1  
    ima=np.ma.masked_array(segment * 632.8e-9, mask=mask)
    
    return m4, segment, ima


def main0409_ROI(ima):
    import sklearn.feature_extraction as skf_e
    import sklearn.cluster as skc
    import skimage.segmentation as sks
    graph = skf_e.image.img_to_graph(ima.data, mask=ima.mask)
    labels = skc.spectral_clustering(graph, n_clusters=4, eigen_solver='arpack')
    label_im = -np.ones(ima.mask.shape)
    label_im[ima.mask] = labels
    
    markers = ima.mask.astype('int')*0
    markers[0,0]=1
    markers[180,79]=2
    markers[296,258]=3 
    markers[170,436]=4
    markers[34,258]=5
    roi_mask = sks.random_walker(ima.mask, markers)  
    
    return label_im, markers, roi_mask
    
    
    
    
    
    
    

    
    

    
    
    
    
    
    