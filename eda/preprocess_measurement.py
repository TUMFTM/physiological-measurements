# Copyright Feiler 2021

"""
This program preprocesses data acquired with a BITalino (R)evolution:
1. loads the raw BITalino data
2. transfers eda to actual measurement values and cleans the data
3. separates tonic and phasic component of eda
4. writes the results to files

Note: With high sampling rates and long data comes high computation time.

Argument 1: subject tag
"""

import sys
import os
import json
import datetime
import numpy as np
import neurokit2 as nk
import append_sys_paths
from common import file_reader
from common.create_folder_structure import get_data_path

### adjustments
EDA_SEPARATION_METHOD = 'cvxEDA'  # use 'highpass' (quick) or
                                  # 'cvxEDA' (accurate but long)
### adjustments end

def write_eda_values_to_file(header, _eda, _eda_tonic, _eda_phasic, _times, _output_file):
    """store data into txt for later usage"""
    eda_header_dict = header
    columns = ["raw eda", "tonic eda component", "phasic eda component", "measurement time"]
    eda_header_dict["columns"] = columns
    with open(_output_file, 'w') as eda_file:
        eda_file.write(json.dumps(eda_header_dict) + '\n')
        for i_line, _ in enumerate(_eda):
            line = str(_eda[i_line]) + ' ' + str(_eda_tonic[i_line]) + ' '
            line += str(_eda_phasic[i_line]) + ' '
            line += datetime.datetime.strftime(_times[i_line], '%H:%M:%S.%f')[:-3]
            eda_file.write(line + '\n')

def split_eda_phasic_tonic(subject, main_directory):
    """process subject"""
    path_to_data_file = main_directory + '/' + "01_measurements/" +\
                        subject + "_data.txt"
    path_to_preprocessed_directory = main_directory +\
                                     '/03_eda_preprocessed'

    eda, _ = file_reader.load_eda_data(path_to_data_file)
    sampling_rate, times = file_reader.load_metadata(path_to_data_file)
    print(str(subject) + " is loaded")

    eda = nk.eda_clean(eda, sampling_rate=sampling_rate)
    print(str(subject) + ": splitting into phasic and tonic is started." + \
          " This may take some time (Demo: 20 sec, otherwise: 1 min measurement ~ 30 sec processing).")
    eda_sep = nk.eda_phasic(eda, sampling_rate, method=EDA_SEPARATION_METHOD)
    eda_phasic = eda_sep['EDA_Phasic'].values
    eda_tonic = eda_sep['EDA_Tonic'].values
    print(str(subject) + " is split into phasic and tonic")
    del eda_sep

    eda = np.around(eda, 4)
    eda_tonic = np.around(eda_tonic, 4)
    eda_phasic = np.around(eda_phasic, 4)

    header_dict={"subject_tag" : subject,
                "sampling_rate" : sampling_rate,
                "start_time" : datetime.datetime.strftime(times[0], "%H:%M:%S.%f")[:-3]}
    output_file = path_to_preprocessed_directory + '/' + subject + '_eda.txt'
    write_eda_values_to_file(header_dict, eda, eda_tonic, eda_phasic, times, output_file)

    del eda
    del eda_tonic
    del eda_phasic

if __name__ == "__main__":
    if (len(sys.argv)) < 2:
        print("Usage: Pass subject tag as argument 1")
        sys.exit()

    subject_tag = sys.argv[1]
    path_to_main_directory = get_data_path()
    split_eda_phasic_tonic(subject_tag, path_to_main_directory)
