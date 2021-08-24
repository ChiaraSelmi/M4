'''
Authors
  - C. Selmi: written in 2021
'''
from m4.configuration import config_folder_names as config

class config_rewriter():

    def __init__(self, conf_obj):
        self.cc = conf_obj

    def upload(self):
        config.simulated = self.cc.simulated
        config.BASE_PATH = self.cc.BASE_PATH
        config.CONFIGURATION_ROOT_FOLDER = self.cc.CONFIGURATION_ROOT_FOLDER
        config.CALIBRATION_ROOT_FOLDER = self.cc.CALIBRATION_ROOT_FOLDER
        config.OPT_DATA_FOLDER = self.cc.OPT_DATA_FOLDER
        config.OUT_FOLDER = self.cc.OUT_FOLDER
        config.MIRROR_FOLDER = self.cc.MIRROR_FOLDER
        config.OPTICAL_FOLDER = self.cc.OPTICAL_FOLDER

        config.OPD_IMAGES_ROOT_FOLDER = self.cc.OPD_IMAGES_ROOT_FOLDER
        config.PHASECAM_ROOT_FOLDER = self.cc.PHASECAM_ROOT_FOLDER
        config.LOG_ROOT_FOLDER = self.cc.LOG_ROOT_FOLDER
        config.IFFUNCTIONS_ROOT_FOLDER = self.cc.IFFUNCTIONS_ROOT_FOLDER
        config.FLAT_ROOT_FOLD = self.cc.FLAT_ROOT_FOLD
        config.CALIBRATION_ROOT_FOLDER = self.cc.CALIBRATION_ROOT_FOLDER
        config.ALIGNMENT_ROOT_FOLDER = self.cc.ALIGNMENT_ROOT_FOLDER
        config.ZERNIKECOMMANDTEST_ROOT_FOLDER = self.cc.ZERNIKECOMMANDTEST_ROOT_FOLDER
        config.NOISE_ROOT_FOLDER = self.cc.NOISE_ROOT_FOLDER
        config.SPL_ROOT_FOLDER = self.cc.SPL_ROOT_FOLDER
        config.CALIBALL_ROOT_FOLDER = self.cc.CALIBALL_ROOT_FOLDER
        config.MODESVECTOR_ROOT_FOLDER = self.cc.MODESVECTOR_ROOT_FOLDER
        config.MODALBASE_ROOT_FOLDER = self.cc.MODALBASE_ROOT_FOLDER
        config.MODALAMPLITUDE_ROOT_FOLDER = self.cc.MODALAMPLITUDE_ROOT_FOLDER
        config.COMMANDHISTORY_ROOT_FOLDER = self.cc.COMMANDHISTORY_ROOT_FOLDER
        config.GEOTRANSFORM_ROOT_FOLDER = self.cc.GEOTRANSFORM_ROOT_FOLDER
        config.ROT_OPT_ALIGN_ROOT_FOLDER = self.cc.ROT_OPT_ALIGN_ROOT_FOLDER
        config.PT_ROOT_FOLDER = self.cc.PT_ROOT_FOLDER
        config.OPD_SERIES_ROOT_FOLDER = self.cc.OPD_SERIES_ROOT_FOLDER
        config.REPEATABILITY_ROOT_FOLDER = self.cc.REPEATABILITY_ROOT_FOLDER
        config.PISTON_TEST_ROOT_FOLDER = self.cc.PISTON_TEST_ROOT_FOLDER
        config.MAPPING_TEST_ROOT_FOLDER = self.cc.MAPPING_TEST_ROOT_FOLDER
        config.ACC_ROOT_FOLDER = self.cc.ACC_ROOT_FOLDER
