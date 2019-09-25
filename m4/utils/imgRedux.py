'''
@author: cs
'''

import numpy as np
from m4.ground.configuration import Configuration
from m4.utils.roi import ROI
from m4.ground.zernikeGenerator import ZernikeGenerator


class TipTiltDetrend():
    
    def __init__(self):
        self._pupilXYRadius= Configuration.ParabolaPupilXYRadius
        self._zg= ZernikeGenerator(2*self._pupilXYRadius[2])
    
    def tipTiltRemover(self, image, roi, finalIndex, analysisInd= None):   
        ''' 
            arg:
                image= immagine da analizzare
                roi= roi dell'immagine
                finalIndex= indice della roi finale
                analysisInd= indice delle roi da utilizzare per l'analisi
        '''
        coefList=[]
        for r in roi:
            imag= np.ma.masked_array(image.data, mask=r)
            ima= np.ma.MaskedArray.copy(imag)
            coef= self._zernikeFit(ima, np.array([2,3]))
            coefList.append(coef)
            
        if analysisInd is None:
            coef_List= coefList
            del coef_List[finalIndex]
        else:
            coef_List=[]
            for i in range(len(analysisInd)):
                coef_List.append(coefList[analysisInd[i]])
        tip, tilt= np.average(coef_List, axis=0)
        
        surfcoef= np.array([tip, tilt]) 
        surfaceMap=self._zernikeSurface(surfcoef)
        
        cx= self._pupilXYRadius[0]
        cy= self._pupilXYRadius[1]
        r= self._pupilXYRadius[2]
        imaCut=image[cy-r:cy+r, cx-r:cx+r]
        imageTTR= np.ma.masked_array(imaCut.data - surfaceMap, mask=roi[finalIndex])
            
        return coefList, imaCut, surfaceMap, imageTTR
  
       
    def _zernikeFit(self, img, zernikeMode):
        '''
        zernikeMode= vector of Zernike modes to remove
        '''
        z= self._zg.getZernike(2)
        mat= np.zeros((img.compressed().shape[0], zernikeMode.size)) 
        for i in range(0, zernikeMode.size):
            z=self._zg.getZernike(zernikeMode[i])
            aa= np.ma.masked_array(z, mask= img.mask)
            mat.T[i]= aa.compressed()
        
        self._mat= mat
        inv= np.linalg.pinv(mat)   
        a= np.dot(inv, img.compressed())  
        return a
    
    
    def _zernikeSurface(self, surfaceZernikeCoeffArray):
        surfaceMap= np.dot(self._mat, surfaceZernikeCoeffArray)
        #v= np.ma.masked_array(np.zeros((512,512)), mask=rois[0])               
        #v[rois[0]]= surfaceMap 
        return surfaceMap
  
    
        

class PhaseSolve():
    
    def __init__(self):
        self._r=ROI()
        self._lambda= Configuration.Lambda
        self._n= None
    
    
    def n_calculator(self, splValues): 
        n=np.zeros(splValues.shape[0])   
        for i in range(splValues.shape[0]):
            n[i]= (2.* splValues[i]) / self._lambda
        self._n= n
        return self._n
    
    
    def m4PhaseSolver(self, m4Ima, splValues): 
        self.n_calculator(splValues)
        roiList= self._r._ROIonM4(m4Ima)
        m4NewImage= None
        
        media=[]
        imgList=[]
        for roi in roiList:
            imgg= np.ma.masked_array(m4Ima.data, mask= roi)
            m= imgg.mean()
            media.append(m)
            imgList.append(imgg)
               
        aa= np.arange(self._n.shape[0])
        zipped= zip(aa, imgList)
        img_phaseSolveList=[]
        for i, imgg in zipped:
            img_phaseSolve= np.ma.masked_array(imgg.data - self._n[i], mask= imgg.mask)
            img_phaseSolveList.append(img_phaseSolve)
        
        img_phaseSolveList[len(img_phaseSolveList)-1]= np.ma.masked_array(imgList[len(imgList)-2].data, 
                                                                mask= imgList[len(imgList)-2].mask)
          
          
        for j in range(1, len(img_phaseSolveList)):
            if m4NewImage is None:
                m4NewImage= np.ma.array(img_phaseSolveList[0].filled(1)* img_phaseSolveList[j].filled(1), 
                                         mask=(img_phaseSolveList[0].mask * img_phaseSolveList[j].mask))
            else:
                m4NewImage = np.ma.array(m4NewImage.filled(1) * img_phaseSolveList[j].filled(1), 
                                         mask=(m4NewImage.mask * img_phaseSolveList[j].mask))
            
        return m4NewImage, img_phaseSolveList, imgList
    
    
        
        
    def masterRoiPhaseSolver(self, segIma, splValue):
        self.n_calculator(splValue)
        roiList= self._r._ROIonSegment(segIma)
    
        imgg= np.ma.masked_array(segIma.data, mask= roiList[1])
        
        img_phaseSolve= np.ma.masked_array(imgg.data - self._n, mask= imgg.mask)
        
        return img_phaseSolve
          
          
            
            
            