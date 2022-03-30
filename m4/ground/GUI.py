'''
Authors
  - C. Selmi: written in 2021
'''

import sys
import numpy as np

from guietta import Gui, G, MA, _, ___, III
#from guietta import Empty, Exceptions



class Runner():
    '''
    Class for creating interactive GUI

    HOW TO USE IT::

        conf = 'myConfGlobalPath.yaml'
        from m4.configuration import start
        ott, interf = start.create_ott(conf)
        from m4.ground import GUI
        g = GUI.Runner(ott, interf)
        g.run()
    '''

    def __init__(self, ott, interf):
        '''The constructor
        ott: object
            tower object
        interf: object
            interferometer object
        '''
        self.ott = ott
        self.interf = interf

    def _setUp(self):

        def setPlot(gui, image):
            '''
            image: masked numpy array
                image from the calibration tower
            '''
            gui.plot = image
            gui.plot.set_clim(vmin=image.min(), vmax=image.max())

        def getstatus(gui):
            ''' Function to reload tower data and image
            '''
            if self.ott:
                gui.parpos = self.ott.parabola.getPosition()
                gui.rmpos = self.ott.referenceMirror.getPosition()
                gui.m4pos = self.ott.m4.getPosition()
                gui.pslider = self.ott.parabolaSlider.getPosition()
                gui.anglepos = self.ott.angleRotator.getPosition()
                gui.rslider = self.ott.referenceMirrorSlider.getPosition()
            image = self.interf.acquire_phasemap()
            setPlot(gui, image)

        def movepar(gui, *args):
            ''' Function to move the parabola'''
            vec = self.ott.parabola.getPosition()
            vec[2] = np.float(gui.parpist or vec[2])
            vec[3] = np.float(gui.partip or vec[3])
            vec[4] = np.float(gui.partilt or vec[4])
            if self.ott:
                self.ott.parabola.setPosition(vec)

        def moverm(gui, *args):
            ''' Function to move the reference mirror '''
            vec = self.ott.referenceMirror.getPosition()
            vec[2] = np.float(gui.rmpist or vec[2])
            vec[3] = np.float(gui.rmtip or vec[3])
            vec[4] = np.float(gui.rmtilt or vec[4])
            if self.ott:
                self.ott.referenceMirror.setPosition(vec)

        def movem4(gui, *args):
            ''' Function to move the exapode '''
            vec = self.ott.m4.getPosition()
            vec[2] = np.float(gui.m4pist or vec[2])
            vec[3] = np.float(gui.m4tip or vec[3])
            vec[4] = np.float(gui.m4tilt or vec[4])
            if self.ott:
                self.ott.m4.setPosition(vec)

        def moverslider(gui, *args):
            ''' Function to move the reference mirror slider '''
            pos = self.ott.referenceMirrorSlider.getPosition() or np.int(gui.rmslider)
            if self.ott:
                self.ott.referenceMirrorSlider.setPosition(pos)

        def moveangle(gui, *args):
            ''' Function to rotate the tower angle'''
            pos = self.ott.angleRotator.getPosition() or np.int(gui.angle)
            if self.ott:
                self.ott.angleRotator.setPosition(pos)

        def movepslider(gui, *args):
            ''' Function to move the parabola slider '''
            pos = self.ott.parabolaSlider.getPosition() or np.int(gui.parslider)
            if self.ott:
                self.ott.parabolaSlider.setPosition(pos)


        image = self.interf.acquire_phasemap()
        gui_image = Gui([ MA('plot'), ___, ___, ___, ___, ___, ___, ___ ],
                        [ III, III, III, III, III, III, III, III ],
                        [ III, III, III, III, III, III, III, III ],
                        [ III, III, III, III, III, III, III, III ],
                        [ III, III, III, III, III, III, III, III ],
                        [ III, III, III, III, III, III, III, III ],
                        ['Par position:','parpos', ___, ___, ___, ___, ___, 'mm'],
                        ['Rm position:', 'rmpos', ___, ___, ___, ___, ___, 'mm'],
                        ['M4 position:', 'm4pos', ___, ___, ___, ___, ___, 'mm'],
                        ['Par slider position:', 'pslider', ___, ___, ___, ___, ___,'mm'],
                        ['Rm slider position:', 'rslider', ___, ___, ___, ___, ___,'mm'],
                        ['Ang rot position:', 'anglepos', ___, ___, ___, ___, ___, 'deg'])
        control_gui = Gui(['New Par position', '0', '0', '__parpist__', '__partip__', '__partilt__', '0', 'mm'],
                          [['Set_Parabola'], ___, ___, ___, ___, ___, ___, ___],
                          ['New Rm position', '0', '0', '__rmpist__', '__rmtip__', '__rmtilt__', '0', 'mm'],
                          [['Set_RefMirror'], ___, ___, ___, ___, ___, ___, ___],
                          ['New M4 position', '0', '0', '__m4pist__', '__m4tip__', '__m4tilt__', '0', 'mm'],
                          [['Set_M4'], ___, ___, ___, ___, ___, ___, ___],
                          ['New Par Slider position', '__parslider__', _, _, _, _, _, 'mm'],
                          [['Set_ParabolaSlider'], ___, ___, ___, ___, ___, ___, ___],
                          ['New Rm Slider position', '__rmslider__', _, _, _, _, _, 'mm'],
                          [['Set_ReferenceMirrorSlider'], ___, ___, ___, ___, ___, ___, ___],
                          ['New Angle Rot position', '__angle__', _, _, _, _, _, 'deg'],
                          [['Set_AngleRotator'], ___, ___, ___, ___, ___, ___, ___]) #exceptions=Exceptions.OFF)

        gui_image.plot = image
        gui_image.plot.set_title('Un bel titolo')
        gui_image.plot.colorbar()


        control_gui.Set_Parabola = movepar
        control_gui.Set_RefMirror = moverm
        control_gui.Set_M4 = movem4
        control_gui.Set_ParabolaSlider = movepslider
        control_gui.Set_ReferenceMirrorSlider = moverslider
        control_gui.Set_AngleRotator = moveangle

        gui_image.timer_start(getstatus, 1)

        self.gui = Gui(
             [ G('OTT') , G('Control') ]
             )

        self.gui_control = control_gui
        self.gui_image = gui_image

#         while 0:
#             try:
#                 name, event = gui_image.get(timeout=1)
# 
#             except Empty:
#                 oi = OttImages(self.ott)
#                 smap1, smask = oi.ott_smap()
#                 setPlot(gui_image, image)
#                 continue
# 
#             if name is None:
#                 break
#             if name in ['viridis', 'hot']:
#                 cmap = name

    def runImage(self):
        self._setUp()
        self.gui_image.run()

    def run(self):
        ''' Run the GUI '''
        self._setUp()
        self.gui.run()


if __name__ == '__main__':
    from m4.configuration import start
    conf = '/Users/rm/eclipse-workspace/M4/m4/configuration/myConfig.yaml' #modificare all'occorrenza
    ott, interf = start.create_ott(conf)

    runner = Runner(ott, interf)
    sys.exit(runner.run())

