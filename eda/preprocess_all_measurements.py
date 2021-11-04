# Copyright Feiler 2021

"""Script runs iteratively 'preprocess_measurements' over all
subjects in data path"""

from os import listdir
from os.path import isfile, join
import sys
import preprocess_measurement
import append_sys_paths
from common.create_folder_structure import get_data_path

length_of_codeword = 8

if __name__ == "__main__":
    path_to_main_directory = get_data_path()
    measurement_path = path_to_main_directory + '/' + "01_measurements/"
    onlyfiles = [f for f in listdir(measurement_path) if isfile(join(measurement_path, f))]

    for current_file in onlyfiles:
        split_file = current_file.split(sep="_")
        subject_tag = split_file[0]
        if len(subject_tag) is not length_of_codeword:
            print("skipping " + subject_tag + ", because codeword does not have 8 characters")
            continue
        print("starting preprocessing of subject " + subject_tag)
        preprocess_measurement.split_eda_phasic_tonic(subject_tag, path_to_main_directory)
        
    