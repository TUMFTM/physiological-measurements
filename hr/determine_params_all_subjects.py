# Copyright Feiler 2021

'''
SDNN-value for each subject for each task range provided by protocol file.
SDNN is measured over complete task interval and stored into sdnn.csv
'''

import os
import datetime as dt
import json
import numpy as np
import pandas as pd
from neurokit2.hrv.hrv_utils import _hrv_get_rri, _hrv_sanitize_input
import append_sys_paths
from common.create_folder_structure import get_data_path

def str_to_datetime(dt_as_string):
    """convert str to datetime"""
    return dt.datetime.strptime(dt_as_string, "%H:%M:%S.%f")

def calc_sdnn(prot_data_as_series, peaks, start, sampling, code):
    """calc sdnn over complete task interval"""
    task_beg = str_to_datetime(prot_data_as_series[1])
    task_end = str_to_datetime(prot_data_as_series[2])

    start_ind = int((task_beg - start).total_seconds() * sampling)
    end_ind = int((task_end - start).total_seconds() * sampling)

    ecg_rpeaks_indices = peaks[np.where(peaks >= start_ind)[0][0]:np.where(peaks >= end_ind)[0][0]]
    if np.isnan(np.sum(ecg_rpeaks_indices)):
        print(str(code) + " has NaN")

    ecg_rpeaks_indices = _hrv_sanitize_input(ecg_rpeaks_indices)
    rri = _hrv_get_rri(ecg_rpeaks_indices, sampling_rate=sampling, interpolate=False)
    sdnn = np.nanstd(rri, ddof=1)

    dic = {"mode": prot_data_as_series[0][0], "task_number": prot_data_as_series[0][-1], \
           "sdnn": sdnn}
    return pd.DataFrame(dic, index=[code])

def get_meta_infos(cur_rpeaks_file_path):
    """return meta-data"""
    first_line = None
    with open(cur_rpeaks_file_path, "r") as prot:
        first_line = json.loads(prot.readline())
    start_time = str_to_datetime(first_line["start_time"])
    sampling_rate = first_line["sampling_rate"]
    return start_time, sampling_rate

def get_sdnn_of_prob(rpeaks_path, r_file, prot_path):
    """return sdnn values for all intervals of one proband"""
    codeword = r_file.split(sep="_")[0]
    protocol = pd.read_csv(os.path.join(prot_path, codeword+"_protocol.txt"), sep=" ", header=None)

    rpeaks_file_path = os.path.join(rpeaks_path, r_file)
    peaks_np = np.genfromtxt(rpeaks_file_path, dtype=np.float64, skip_header=1)

    start_time, sampling_rate = get_meta_infos(rpeaks_file_path)

    intervals = protocol.iloc[0:9,:]
    sdnn_series = intervals.apply(calc_sdnn, axis=1, peaks=peaks_np, start=start_time,\
                           sampling=sampling_rate, code=codeword)
    sdnn_df = pd.concat([f for f in sdnn_series], axis=0)
    return sdnn_df

def write_to_file(total_sdnn, output_file):
    """store it into csv"""
    total_sdnn.to_csv(output_file, sep=";", float_format='%.4f')

def main():
    """process all probands"""
    main_data_path = get_data_path()
    path_to_rpeaks = main_data_path + "/07_hr_rpeaks"
    list_of_filenames = [f for f in os.listdir(path_to_rpeaks) if \
        os.path.isfile(os.path.join(path_to_rpeaks, f))]
    print("Found " + str(len(list_of_filenames)) + " subjects in " +
          str(path_to_rpeaks))
    path_to_prot = main_data_path + "/02_protocols_original"

    first_time = True
    total_sdnn = None
    for number, rpeak_filename in enumerate(list_of_filenames):
        print("Processing " + str(number + 1) + "/" + str(len(list_of_filenames)))
        sdnn_of_proband = get_sdnn_of_prob(path_to_rpeaks, rpeak_filename, path_to_prot)
        if first_time:
            first_time = False
            total_sdnn = sdnn_of_proband
        else:
            total_sdnn = total_sdnn.append(sdnn_of_proband)

    output_file = main_data_path + "/08_hrv_sdnn/" + "sdnn.csv"
    write_to_file(total_sdnn, output_file)


if __name__ == "__main__":
    main()
