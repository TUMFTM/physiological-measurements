# Copyright Feiler 2021

"""Data recorded with BITalino can be loaded via these functions"""

import sys
import json
import numpy as np
import datetime

def load_metadata(path_to_data_file):
    with open(path_to_data_file, 'r') as data_file:
        if 'OpenSignals' not in str(data_file.readline()):
            print("Error -- " + path_to_data_file + " is not an opensignals file")
            sys.exit()

        meta_data = json.loads(data_file.readline().replace('#', ''))
        meta_data = meta_data[list(meta_data.keys())[0]]
        start_time = meta_data['time']
        start_time = datetime.datetime.strptime(start_time, '%H:%M:%S.%f')
        no_of_lines = 0

        for _ in data_file:
            no_of_lines += 1
        no_of_measurements = no_of_lines-1

        sampling_rate = meta_data['sampling rate']
        time_delta_in_micro_sec = 1e6/sampling_rate
        times = [start_time + datetime.timedelta(microseconds=i*time_delta_in_micro_sec) \
                 for i in range(no_of_measurements)]
        return sampling_rate, times


def load_eda_data(path_to_data_file):
    eda_signal = None
    sampling_rate = None

    with open(path_to_data_file, 'r') as data_file:
        if 'OpenSignals' in str(data_file.readline()):
            meta_data = json.loads(data_file.readline().replace('#', ''))
            meta_data = meta_data[list(meta_data.keys())[0]]
            sampling_rate = meta_data['sampling rate']

            data = np.loadtxt(data_file)
            eda_signal = data[:, -1]
            eda_signal = eda_transfer_function(eda_signal)

        else:
            print(path_to_data_file + " is not a BITalino file")
    return eda_signal, sampling_rate


def load_eda_ecg_data(path_to_data_file):
    ecg_signal = None
    eda_signal = None
    sampling_rate = None

    with open(path_to_data_file, 'r') as data_file:
        if 'OpenSignals' in str(data_file.readline()):
            meta_data = json.loads(data_file.readline().replace('#', ''))
            meta_data = meta_data[list(meta_data.keys())[0]]
            sampling_rate = meta_data['sampling rate']

            data = np.loadtxt(data_file)
            ecg_signal = data[:, -2]
            eda_signal = data[:, -1]

            ecg_signal = ecg_transfer_function(ecg_signal)
            eda_signal = eda_transfer_function(eda_signal)

        else:
            print(path_to_data_file + " is not a BITalino file")
    return ecg_signal, eda_signal, sampling_rate


def load_preprocessed_eda_data(path_to_eda_file):
    with open(path_to_eda_file) as eda_file:
        #check and load meta data
        eda_meta_data = json.loads(eda_file.readline())

        sampling_rate = eda_meta_data["sampling_rate"]
        preprocessed_data={}
        preprocessed_data["fs"] = sampling_rate

        # load_data()
        preprocessed_data["times"] = []
        preprocessed_data["eda"] = []
        preprocessed_data["eda_tonic"] = []
        preprocessed_data["eda_phasic"] = []

        eda_data = np.loadtxt(eda_file, dtype=np.str)
        eda = np.array(eda_data[:, 0], dtype=np.float)
        eda_tonic = np.array(eda_data[:, 1], dtype=np.float)
        eda_phasic = np.array(eda_data[:, 2], dtype=np.float)
        eda_times = list(eda_data[:, 3])

        for i in range(len(eda_times)):
            eda_times[i] = datetime.datetime.strptime(eda_times[i], "%H:%M:%S.%f")
        eda_start_time = eda_times[0]
        preprocessed_data["times"] = eda_times
        preprocessed_data["eda"] = eda
        preprocessed_data["eda_tonic"] = eda_tonic
        preprocessed_data["eda_phasic"] = eda_phasic

        return preprocessed_data



VCC = 3.3  # Operating voltage of ADC
n = 10  # sampling resolution of ADC
G_ECG = 1100  # gain of ecg sensor


# ecg transfer function from ecg-sensor-datasheet
# transfers raw ecg sensor values to mV values
def ecg_transfer_function(raw_ecg):
    return 1000 * ((raw_ecg / np.power(2, n) - 0.5) * VCC) / G_ECG


# eda transfer function from eda-sensor-datasheet
# transfers raw eda values to microsiemens values
def eda_transfer_function(raw_eda):
    return (raw_eda/np.power(2, n)*VCC)/0.132
