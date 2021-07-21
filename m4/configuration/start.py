'''
Authors
  - C. Selmi: written in 2020
'''
from m4.configuration.create_ott import OTT
from m4.configuration import config
from m4.devices.opc_ua_controller import OpcUaController
from m4.ott_sim.fake_parabola_slider import FakeParabolaSlider
from m4.ott_sim.fake_reference_mirror_slider import FakeReferenceMirrorSlider
from m4.ott_sim.fake_angle_rotator import FakeAngleRotator
from m4.ott_sim.fake_parabola import FakeParabola
from m4.ott_sim.fake_reference_mirror import FakeReferenceMirror
from m4.ott_sim.fake_m4 import FakeM4
from m4.ott_sim.fake_temperature_sensors import FakeTemperatureSensors
from m4.ott_sim.fake_interferometer import FakeInterferometer
from m4.ott_sim.fake_accelerometers import FakeAccelerometers
from m4.devices.parabola_slider import OpcUaParabolaSlider
from m4.devices.reference_mirror_slider import OpcUaReferenceMirrorSlider
from m4.devices.angle_rotator import OpcUaAngleRotator
from m4.devices.parabola import OpcUaParabola
from m4.devices.reference_mirror import OpcUaReferenceMirror
from m4.devices.m4_controller import OpcUaM4
from m4.devices.temperature_sensors import OpcUaTemperatureSensors
from m4.devices.accelerometers import ZmqAccelerometes
from m4.devices.interferometer import I4dArcetri


def create_ott(config=config):
    ''' Function for the ott creation

    Returns
    -------
    ott: object
        tower
    interf: object
        interferometer
    '''
    if config.simulated == 1:
        parabola_slider = FakeParabolaSlider()
        reference_mirror_slider = FakeReferenceMirrorSlider()
        angle_rotator = FakeAngleRotator()
        parab = FakeParabola()
        reference_mirror = FakeReferenceMirror()
        m4 = FakeM4()
        temperature_sensor = FakeTemperatureSensors()
        accelerometers = FakeAccelerometers()
        interf = FakeInterferometer()
    else:
        opcUa = OpcUaController()
        parabola_slider = OpcUaParabolaSlider(opcUa)
        reference_mirror_slider = OpcUaReferenceMirrorSlider(opcUa)
        angle_rotator = OpcUaAngleRotator(opcUa)
        parab = OpcUaParabola(opcUa)
        reference_mirror = OpcUaReferenceMirror(opcUa)
        m4 = OpcUaM4(opcUa)
        temperature_sensor = OpcUaTemperatureSensors(opcUa)
        accelerometers = ZmqAccelerometes()
        interf = I4dArcetri()

    ott = OTT(parabola_slider, reference_mirror_slider, angle_rotator,
              parab, reference_mirror, m4, temperature_sensor, accelerometers)
    if config.simulated == 1:
        interf.set_ott(ott)

    return ott, interf
