'''
Authors
  - C. Selmi: written in 2020
'''
from m4.configuration.create_ott import OTT
from m4.ground.interface_4D import comm4d
from m4.configuration import config
from m4.ground.opc_ua_controller import OpcUaController
from m4.ott_sim.fake_parabola_slider import FakeParabolaSlider
from m4.ott_sim.fake_reference_mirror_slider import FakeReferenceMirrorSlider
from m4.ott_sim.fake_angle_rotator import FakeAngleRotator
from m4.ott_sim.fake_parabola import FakeParabola
from m4.ott_sim.fake_reference_mirror import FakeReferenceMirror
from m4.ott_sim.fake_m4 import FakeM4
from m4.ott_sim.fake_temperature_sensors import FakeTemperatureSensors
from m4.devices.parabola_slider import OpcUaParabolaSlider
from m4.devices.reference_mirror_slider import OpcUaReferenceMirrorSlider
from m4.devices.angle_rotator import OpcUaAngleRotator
from m4.devices.parabola import OpcUaParabola
from m4.devices.reference_mirror import OpcUaReferenceMirror
from m4.devices.m4 import OpcUaM4
from m4.devices.temperature_sensors import OpcUaTemperatureSensors

def create_ott():
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
        parabola = FakeParabola()
        reference_mirror = FakeReferenceMirror()
        m4 = FakeM4()
        temperature_sensor = FakeTemperatureSensors()
    else:
        opcUa = OpcUaController()
        parabola_slider = OpcUaParabolaSlider(opcUa)
        reference_mirror_slider = OpcUaReferenceMirrorSlider(opcUa)
        angle_rotator = OpcUaAngleRotator(opcUa)
        parabola = OpcUaParabola(opcUa)
        reference_mirror = OpcUaReferenceMirror(opcUa)
        m4 = OpcUaM4(opcUa)
        temperature_sensor = OpcUaTemperatureSensors(opcUa)

    ott = OTT(parabola_slider, reference_mirror_slider, angle_rotator,
              parabola, reference_mirror, m4, temperature_sensor)
    interf = comm4d()
    return ott, interf
