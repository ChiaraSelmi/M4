'''
Authors
  - C. Selmi: written in 2021
'''
import os

mirror_conf = '20170430'
optical_conf = '20150730'

simulated = None

BASE_PATH = '/mnt/m4storage/Data'
CONFIGURATION_ROOT_FOLDER = os.path.join(BASE_PATH, 'SYSCONFData')
CALIBRATION_ROOT_FOLDER = os.path.join(BASE_PATH, 'M4Data')
OPT_DATA_FOLDER = os.path.join(CALIBRATION_ROOT_FOLDER, 'OPTData')
OUT_FOLDER = os.path.join(CALIBRATION_ROOT_FOLDER, 'Results')
MIRROR_FOLDER = os.path.join(BASE_PATH, 'MIRROR_System')
OPTICAL_FOLDER = os.path.join(BASE_PATH, 'OPTICAL_System')

OPD_IMAGES_ROOT_FOLDER = os.path.join(OPT_DATA_FOLDER, 'OPDImages')
PHASECAM_ROOT_FOLDER = '/home/m4/4d/Zcopy/'
LOG_ROOT_FOLDER = os.path.join(BASE_PATH,
                               'LOGData/mylog')
IFFUNCTIONS_ROOT_FOLDER = os.path.join(OPT_DATA_FOLDER,
                                       'IFFunctions')
FLAT_ROOT_FOLD = os.path.join(OPT_DATA_FOLDER, "Flattening")
CALIBRATION_ROOT_FOLDER = os.path.join(OPT_DATA_FOLDER,
                                       "Calibration")
ALIGNMENT_ROOT_FOLDER = os.path.join(OPT_DATA_FOLDER, "Alignment")
ZERNIKECOMMANDTEST_ROOT_FOLDER = os.path.join(OPT_DATA_FOLDER,
                                              "ZernikeCommandTest")
NOISE_ROOT_FOLDER = os.path.join(OPT_DATA_FOLDER, "Noise")
SPL_ROOT_FOLDER = os.path.join(OPT_DATA_FOLDER, "SPL")
CALIBALL_ROOT_FOLDER = os.path.join(OPT_DATA_FOLDER,
                                    "Caliball")
MODESVECTOR_ROOT_FOLDER = os.path.join(OPT_DATA_FOLDER,
                                       "ModesVector")
MODALBASE_ROOT_FOLDER = os.path.join(OPT_DATA_FOLDER,
                                     "ModalBase")
MODALAMPLITUDE_ROOT_FOLDER = os.path.join(OPT_DATA_FOLDER,
                                          "ModalAmplitude")
COMMANDHISTORY_ROOT_FOLDER = os.path.join(OPT_DATA_FOLDER,
                                          "CommandHistory")
GEOTRANSFORM_ROOT_FOLDER = os.path.join(OPT_DATA_FOLDER,
                                        "GeomTransf")
ROT_OPT_ALIGN_ROOT_FOLDER = os.path.join(OPT_DATA_FOLDER,
                                         "RotOptAlignment")

PT_ROOT_FOLDER = os.path.join(OPT_DATA_FOLDER,
                              "PTCalibration")
OPD_SERIES_ROOT_FOLDER = os.path.join(OPT_DATA_FOLDER,
                              "OPD_series")
REPEATABILITY_ROOT_FOLDER = os.path.join(OPT_DATA_FOLDER,
                              "Repeatability")
PISTON_TEST_ROOT_FOLDER = os.path.join(OPT_DATA_FOLDER,
                              "PistonTest")
MAPPING_TEST_ROOT_FOLDER = os.path.join(OPT_DATA_FOLDER,
                              "Mapping")
ACC_ROOT_FOLDER = os.path.join(OPT_DATA_FOLDER,
                              "AccelerometersData")