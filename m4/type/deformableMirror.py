'''
@author: cs
'''
from m4.ground.configuration import Configuration


class m4():
    def __init__(self):
        self._nActsTot = Configuration.N_ACTS_TOT
        self._who = 'All segments'

    def nActs(self):
        return self._nActsTot


class segment(m4):
    def __init__(self, segment_index):
        super().__init__()

        if segment_index < 6:
            self._segmentIndex = segment_index
        else:
            raise OSError('Segment number %s doesnt exists' % segment_index)

        self._nActSeg = Configuration.N_ACT_SEG
        self._nSeg = Configuration.N_SEG
        self._who = 'Segment number %s' % segment_index

    def nActs(self):
        return self._nActSeg
