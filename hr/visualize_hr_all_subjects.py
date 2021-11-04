# Copyright Feiler 2021

"""Calls one proband after another for visual ecg data inspection.
The GUI-manual is on the top of visualize_hr_one_subject.py"""

import os
import visualize_hr_one_subject as hrv_artifacts
import append_sys_paths
from common.create_folder_structure import get_data_path

if __name__ == "__main__":
    path_to_data_dir = get_data_path()
    PATH_TO_MEASUREMENTS = path_to_data_dir + '/01_measurements'
    list_of_filenames = [f for f in os.listdir(PATH_TO_MEASUREMENTS) if \
        os.path.isfile(os.path.join(PATH_TO_MEASUREMENTS, f))]
    codewords = set([f.split(sep="_")[0] for f in list_of_filenames])
    for index, codeword in enumerate(codewords):
        hrv_artifacts.visualize_one_subject(codeword)
