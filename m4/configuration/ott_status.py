import numpy as np
import configparser
import json
from m4.mini_OTT import timehistory as th
basepath = th.foldname.OPT_DATA_FOLDER

def read(tn):
    fold = th.findTracknum(tn)
    f2read = basepath+'/'+fold+'/'+tn+'/OTTStatus.ini'
    config=configparser.ConfigParser()
    print(f2read)
    config.read(f2read)
    #OTT
    pp = config['OTT']
    par = np.array(json.loads(pp['PAR']))
    rm = np.array(json.loads(pp['RM']))
    m4 = np.array(json.loads(pp['M4']))
    ps = pp['PAR_SLIDER']  
    rs = pp['RM_SLIDER']  
    ang= pp['ROT_ANGLE']
    return ps, rs, ang, par, rm, m4


def save(basepath, ott):
    name = 'OTTStatus.ini'
    f=open(basepath+'/'+name,'w')
    f.write('[OTT]\n')
    par = ott.parabola.getPosition()
    rm = ott.referenceMirror.getPosition()
    m4 = ott.m4Exapode.getPosition()
    ps = ott.parabolaSlider.getPosition()
    rs = ott.referenceMirrorSlider.getPosition()
    ang = ott.angleRotator.getPosition()
    f.write('PAR_SLIDER = '+str(ps)+'\n')
    f.write('RM_SLIDER  = '+str(rs)+'\n')
    f.write('ROT_ANGLE  = '+str(ang)+'\n')
    f.write('PAR        = '+np.array2string(par,separator=',',formatter={'float_kind':lambda x: "%.2f" % x})+'\n')
    f.write('RM         = '+np.array2string(rm,separator=',',formatter={'float_kind':lambda x: "%.2f" % x})+'\n')
    f.write('M4         = '+np.array2string(m4,separator=',',formatter={'float_kind':lambda x: "%.2f" % x})+'\n')
    f.close()

