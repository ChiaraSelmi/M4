#!/usr/bin/env python
import unittest
from m4.devices.parabola_slider import OpcUaParabolaSlider
import mock
from m4.configuration.ott_parameters import OpcUaParameters


class TestOpcUaParabolaSlider(unittest.TestCase):

    def setUp(self):
        self.opc = mock.MagicMock()
        self.slider = OpcUaParabolaSlider(self.opc)

    def testCallsOpcOnGetPosition(self):
        self.opc.get_position = mock.Mock(return_value=123.4)
        pos = self.slider.getPosition()
        self.opc.get_position.assert_called_once_with(OpcUaParameters.ST)
        self.assertAlmostEqual(pos, 123.4)

    def testCallsOpcOnSetPosition(self):
        self.opc.get_position = mock.Mock(return_value=3.14)
        pos = self.slider.setPosition(3.14)
        self.opc.set_target_position.assert_called_once_with(
            OpcUaParameters.ST, 3.14)
        self.opc.move_object.assert_called_once_with(OpcUaParameters.ST)
        self.opc.wait_for_stop.assert_called_once_with(OpcUaParameters.ST)
        self.assertAlmostEqual(pos, 3.14)

    # @lb 210503
    @unittest.skip("Too complex to mock. FIX ME")
    def testMoveRelativeToCurrentPosition(self):
        init_pos = 42
        self.opc.get_position = mock.Mock(return_value=init_pos)

        off = 19.3
        curr_pos = self.slider.getPosition()
        fin_pos = self.slider.setPosition(curr_pos + off)

        self.assertAlmostEqual(init_pos + off, fin_pos)
