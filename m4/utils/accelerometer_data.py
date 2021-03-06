'''
Authors
  - C. Selmi: written in 2020
'''

import numpy as np

class AccData():

    def __init__(self):
        """The constructor """
        self._dt = 1e-3

    @staticmethod
    def _storageFolder():
        """ Creates the path where to save measurement data"""
        pass

    def create_test_signal(self):
        T = 10
        n = int(T/self._dt)
        t = np.linspace(0, T, n)
        freqSin = 30
        ampSin = 1
        vector = ampSin * np.sin(2*np.pi*freqSin*t)
#         spe = np.fft.fftshift(np.fft.fft(vector, norm='ortho'))
#         freq = np.fft.fftshift(np.fft.fftfreq(spe.size, d=dt))
        return vector, t

    def create_test_vector_sign(self, vector):
        vv = np.column_stack((vector, vector))
        vv_c = np.column_stack((vv, vector))
        return vv_c

    def data_projection(self, vv_c):
        '''
        Parameters
        ----------
            vv_c: numpy array
                    matrix containing the signal (1000x3)
        Returns
        -------
            z: numpy array
                matrix containing the signal projections
        '''
        c30 = np.cos(30/180. * np.pi)
        c60= np.cos(60/180. * np.pi)

        a = np.ones(3)
        b =np.array([0, c30,-c30])
        c = np.array([-1, c60, c60])

        w = np.column_stack((a,b))
        w_c = np.column_stack((w,c)) #a,b,c sono colonne

        w1 = np.linalg.pinv(w_c.T)
        z = np.dot(w1, vv_c.T)
        return z
#clf(); plot(t, vec, '--', label='signal'); plot(t, z[0,:], label='proiezione1');
#plot(t, z[1,:], label='proizione2'); plot(t, z[2,:], label='proiezione3');
#plt.xlabel('Time[s]'); plt.legend()

    def power_spectrum(self, z):
        '''
        Parameters
        ----------
            z: numpy array
                matrix containing the signal projections
        Returns
        -------
            spe_list: list 
                    list containing the spectrum of vectors composing
                    the matrix z
            freq_list: list
                    list containing the frequencies of vectors composing
                    the matrix z
        '''
        spe_list = []
        freq_list = []
        for i in range(z.shape[0]):
            vector = z[i, :]
            spe = np.fft.fftshift(np.fft.rfft(vector, norm='ortho'))
            freq = np.fft.fftshift(np.fft.rfftfreq(vector.size, d=self._dt))
            spe_list.append(spe)
            freq_list.append(freq)
        return spe_list, freq_list
#clf(); plot(freq[0], np.abs(spe[0]), label='proiezione1');
#plot(freq[1], np.abs(spe[1]), label='proiezione2');
#plot(freq[2], np.abs(spe[2]), label='proiezione3'); plt.xlabel('Freq[Hz]');
#plt.ylabel('FFT|sig|'); plt.legend()
