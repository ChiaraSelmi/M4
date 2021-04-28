'''
Authors
  - C. Selmi: written in 2020
'''

import os
import numpy as np
import zmq
import h5py
import time
from m4.ground import rebinner
from m4.configuration.config import fold_name
from m4.configuration.ott_parameters import OpcUaParameters
from matplotlib import pyplot as plt
from m4.ground.timestamp import Timestamp

class Accelerometers():

    def __init__(self):
        """The constructor """
        self._rebinnig_factor = OpcUaParameters.accelerometers_dt/OpcUaParameters.accelerometers_dt_plc
        self.dt = OpcUaParameters.accelerometers_dt
        self.id_vector = OpcUaParameters.accelerometers_plc_id
        self.directions = OpcUaParameters.accelerometrs_directions
        self._datah5 = None

    @staticmethod
    def _storageFolder():
        """ Creates the path where to save measurement data"""
        return fold_name.ACC_ROOT_FOLDER

    def acquisitionAndShow(self, recording_seconds=5):
        tt = self.acquire_acc_data(recording_seconds)
        #print(tt)
        data = self.read_data()
        spe, freq = self.power_spectrum(data)
        self.plot_power_spectrum(spe, freq)
        #plt.pause(plot_seconds)
        #plt.close()
        return tt

    def readAndShow(self, tt):
        acc = Accelerometers.reload_acc_info(tt)
        data = acc.read_data()
        spe, freq = acc.power_spectrum(data)
        acc.plot_power_spectrum(spe, freq)

    def acquire_acc_data(self, recording_seconds=5):
        '''
        Parameters
        ----------
        recording_seconds: int
            recording seconds for data acquisition

        Returns
        -------
        h5_file_name: string
            tracking number of measurement
        '''
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect(OpcUaParameters.accelerometers_server)
        time.sleep(0.2)
        socket.send_string("START %d" %recording_seconds)
        time.sleep(0.5)
        try:
            reply = socket.recv(1)
            print('Data from %s' %reply)
        except:
            raise OSError('No reply from socket')
        time.sleep(0.5)
        socket.disconnect(OpcUaParameters.accelerometers_server)
        time.sleep(0.5)
        #time.sleep(recording_seconds+2)

        list = os.listdir(OpcUaParameters.accelerometers_data_folder)
        list.sort()
        h5_file_name = list[len(list)-1]
        tt = Timestamp.now()
        name = tt + '.h5'
        final_destination = os.path.join(Accelerometers._storageFolder(), name)
        print( 'To %s' %final_destination)
        start = os.path.join(OpcUaParameters.accelerometers_data_folder, h5_file_name)

        t0 = os.path.getmtime(start)
        time.sleep(2)
        t1 = os.path.getmtime(start)
        diff = t1-t0
        while diff != 0:
            #print(diff)
            t0 = os.path.getmtime(start)
            time.sleep(2)
            t1 = os.path.getmtime(start)
            diff = t1-t0

        if self._rebinnig_factor == 1:
            os.system('cp %s %s' %(start, final_destination)) #popen
        else:
            self._rebinAndSaveData(start, final_destination)
        self._tt = name
        return name

    def _rebinAndSaveData(self, start, final_destination):    
        hf = h5py.File(start, 'r')
        data = hf.get('Accelerometers')

        vec = data[:, OpcUaParameters.accelerometers_plc_id]
        rebinning_size = np.int(vec.shape[0]/self._rebinnig_factor)
        v_list=[]
        for i in range(vec.shape[1]):
            v_list.append(rebinner.rebin(vec[:, i], rebinning_size)) #1050
        rebinned_vector = np.array(v_list)
        time = rebinner.rebin(data[:, 0], rebinning_size)

        hf = h5py.File(final_destination, 'w')
        hf.create_dataset('Accelerometers', data=rebinned_vector)
        hf.attrs['DT'] = OpcUaParameters.accelerometers_dt
        hf.attrs['ID'] = OpcUaParameters.accelerometers_plc_id
        hf.attrs['DIR'] = ['X', 'Z', 'Y', 'Z']
        hf.attrs['TIME'] = time
        hf.close()

    @staticmethod
    def reload_acc_info(h5_name):
        '''
        Parameters
        ----------
        h5_file_name: string
            tracking number of measurement

        Returns
        -------
        data:
        '''
        h5_file_path = os.path.join(Accelerometers._storageFolder(), h5_name)
        theObject = Accelerometers()
        theObject._tt = h5_name
        hf = h5py.File(h5_file_path, 'r')
        #hf.keys()
        #theObject.datah5 = hf.get('Accelerometers')
        #data = datah5[()]
        #hf.close()
        try:
            theObject.dt = hf.attrs['DT']
            theObject.id_vector = hf.attrs['ID']
            theObject.directions = hf.attrs['DIR']
            theObject.time = hf.attrs['TIME']
        except:
            theObject.dt = OpcUaParameters.accelerometers_dt_plc
            theObject.id_vector = OpcUaParameters.accelerometers_plc_id
            theObject.directions = ['X', 'Z', 'Y', 'Z']
        return theObject

    def read_data(self, tt=None):
        if tt is not None:
            self._tt = tt
        h5_file_path = os.path.join(Accelerometers._storageFolder(), self._tt)
        hf = h5py.File(h5_file_path, 'r')
        self.datah5 = hf.get('Accelerometers')[()]
        nacc = (self.datah5.shape)[0]
        for i in range(nacc):
            print(self.datah5[i,:].std())
        return self.datah5

    def get_dt(self):
        return self.dt

    def power_spectrum(self, vec):
        '''
        Parameters
        ----------
            vec: numpy array
                matrix containing the signal projections
                or signals to analyze
        Returns
        -------
            spe_list: list
                    list containing the spectrum of vectors composing
                    the matrix z
            freq_list: list
                    list containing the frequencies of vectors composing
                    the matrix z
        '''
        if self.dt == OpcUaParameters.accelerometers_dt_plc:
            vec_cut = vec[:, OpcUaParameters.accelerometers_plc_id]
            z = vec_cut.T
        else:
            z = vec
        #dt = OpcUaParameters.accelerometers_dt
        #z = vec.T
    #         #spe = np.fft.fftshift(np.fft.rfft(vector, norm='ortho'))
    #         #freq = np.fft.fftshift(np.fft.rfftfreq(vector.size, d=self._dt))
        spe  = np.fft.rfft(z, axis=1, norm='ortho')
        nn   = np.sqrt(spe.shape[1])   #modRB 
        spe  = (np.abs(spe)) / nn
        freq = np.fft.rfftfreq(z.shape[1], d=self.dt)
        return spe, freq
    #clf(); plot(freq[0], np.abs(spe[0]), label='proiezione1');
    #plot(freq[1], np.abs(spe[1]), label='proiezione2');
    #plot(freq[2], np.abs(spe[2]), label='proiezione3'); plt.xlabel('Freq[Hz]');
    #plt.ylabel('FFT|sig|'); plt.legend()

    def plot_power_spectrum(self, spe, freq):
        spe1 = spe[:, 1:]
        freq1 = freq[1:]
        plt.figure()
        label_list = ['acc05-X', 'acc06-Z', 'acc07-Y','acc08-Z']
        for i in range(spe1.shape[0]):
            plt.plot(freq1, np.abs(spe1[i,:]), '-', label=label_list[i])
        plt.xlabel('Freq[Hz]')
        plt.ylabel('FFT|sig|')
        plt.xlim([0,100])
        plt.title(self._tt)

        plt.ion()
        plt.show()
        plt.pause(0.01)
        plt.legend()
        plt.grid()
        
        
    def counts_to_g(self, vec):
        id = OpcUaParameters.accelerometers_plc_id -1
        sens = OpcUaParameters.accelerometers_sensitivity[id]
        plcfs = OpcUaParameters.accelerometers_plc_range[id]
        cal_list = []
        for i in range(vec.shape[1]):
            cal_vec = vec[:, i] /OpcUaParameters.accelerometers_plc_totcounts/(sens*plcfs)
            cal_list.append(cal_vec)
        cal_vec = np.array(cal_list)
        return cal_vec.T




### FUNZIONI NON USATE ###
def _create_test_signal(self):
    T = 10
    n = int(T/self._dt)
    t = np.linspace(0, T, n)
    freqSin = 2
    ampSin = 1
    vector = ampSin * np.sin(2*np.pi*freqSin*t)
#         spe = np.fft.fftshift(np.fft.fft(vector, norm='ortho'))
#         freq = np.fft.fftshift(np.fft.fftfreq(spe.size, d=dt))
    return vector, t

def _create_test_vector_sign(vector):
    vv = np.column_stack((vector, vector))
    vv_c = np.column_stack((vv, vector))
    return vv_c

def data_projection(vv_c):
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
    c60 = np.cos(60/180. * np.pi)

    a = np.ones(3)
    b = np.array([0, c30, -c30])
    c = np.array([-1, c60, c60])

    w = np.column_stack((a, b))
    w_c = np.column_stack((w, c)) #a,b,c sono colonne

    w1 = np.linalg.pinv(w_c.T)
    z = np.dot(w1, vv_c.T)
    return z
#clf(); plot(t, vec, '--', label='signal'); plot(t, z[0,:], label='proiezione1');
#plot(t, z[1,:], label='proizione2'); plot(t, z[2,:], label='proiezione3');
#plt.xlabel('Time[s]'); plt.legend()

### FINE FUNZIONI NON USATE ###


# def main(recording_seconds=5, plot_seconds=10):
#     tt = acquire_acc_data(recording_seconds)
#     print(tt)
#     data = read_acc_data(tt)
#     vec = data[:, 5:9]
#     spe, freq = power_spectrum(vec)
#     plot_power_spectrum(spe, freq)
#     plt.pause(plot_seconds)
#     plt.close()
#     return tt
# 
# if __name__ == '__main__':
#     tt = acquire_acc_data()
#     print(tt)
#     data = read_acc_data(tt)
#     vec = data[:, 5:9]
#     spe, freq = power_spectrum(vec)
#     plot_power_spectrum(spe, freq)
#     plt.pause(5)
#     plt.close()
