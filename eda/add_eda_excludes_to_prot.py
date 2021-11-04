# Copyright Feiler 2021

"""This module copies all protocol files and 
appends the exclude intervals to the respective copied protocol files"""

import shutil
import os
import append_sys_paths
from common.create_folder_structure import get_data_path

def get_timestamp(line):
    """Line split for time stamp as string"""
    timestamp = line.split(sep=",")[0]
    return timestamp

def append_new_interval_to(exclusion_intervals, start_time, end_time):
    """Append start and end time to exclusion intervals"""
    exclusion_intervals.append(["exclude_eda", start_time, end_time])

def get_eda_excluded_intervals(current_codeword, eda_exclusion_dir):
    """Return list of exclude intervals"""
    path_to_exclusion_file = eda_exclusion_dir + str(current_codeword) + "_excluded.txt"
    exclusion_intervals = []
    start_time = []
    end_time = []
    with open(path_to_exclusion_file, "r") as exclude_file:
        for index, line in enumerate(exclude_file):
            line_number = index + 1
            if (line_number%2) == 1:
                start_time = get_timestamp(line)
            else:
                end_time = get_timestamp(line)
                append_new_interval_to(exclusion_intervals, start_time, end_time)
    return exclusion_intervals

def copy_file_to_target_position(current_codeword, prot_dir, target_dir):
    """Create new file in target directory by copying"""
    source_file = prot_dir + str(current_codeword) + "_protocol.txt"
    target_file = target_dir + str(current_codeword) + "_protocol.txt"
    shutil.copyfile(source_file, target_file)
    return target_file

def add_excludes_to_target_file(exclusion_intervals, target_file):
    """Write exclusion intervals into target file"""
    with open(target_file, "a") as file_to_append:
        for exclusion in exclusion_intervals:
            text = str(exclusion[0]) + ' ' + \
                   str(exclusion[1]) + ' ' + \
                   str(exclusion[2]) + '\n'
            file_to_append.write(text)

def process_one_codeword(current_codeword, prot_source_dir, eda_exclusion_dir, target_dir):
    """Main function"""
    exclusion_intervals = get_eda_excluded_intervals(current_codeword, eda_exclusion_dir)
    target_file = copy_file_to_target_position(current_codeword, prot_source_dir, target_dir)
    add_excludes_to_target_file(exclusion_intervals, target_file)

if __name__ == "__main__":
    main_data_dir = get_data_path()
    PROT_FILE_FOLDER = main_data_dir + "/02_protocols_original/"
    EDA_EXCLUDE_DIR = main_data_dir + "/04_eda_excluded_intervals/"
    PROT_TARGET_DIR = main_data_dir + "/05_eda_prot_with_exclusion/"
    list_of_filenames = [f for f in os.listdir(PROT_FILE_FOLDER) if \
        os.path.isfile(os.path.join(PROT_FILE_FOLDER, f))]
    codewords = [f.split(sep="_")[0] for f in list_of_filenames]
    for codeword in codewords:
        process_one_codeword(codeword, PROT_FILE_FOLDER, EDA_EXCLUDE_DIR, PROT_TARGET_DIR)
