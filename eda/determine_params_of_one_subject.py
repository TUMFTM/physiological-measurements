# Copyright Feiler 2021

"""
This program extracts the EDA parameters of a subject and its experiments.
Please see the Readme for further details.

Argument 1: subject tag
"""

import sys
import os
import append_sys_paths
from common import file_reader
from common.create_folder_structure import get_data_path
from eda_includes.subject import Subject

def process_one_subject(subject, main_directory):
    """Determine params of specified subject"""
    protocol_filename = subject + "_protocol.txt"
    path_to_protocol_file = main_directory + "/05_eda_prot_with_exclusion/" + \
                            protocol_filename
    tell_and_exit_if_path_does_not_exist(path_to_protocol_file)

    path_to_eda_results = main_directory + '/06_eda_parameters'
    path_to_preprocessed_directory = main_directory + '/03_eda_preprocessed'

    path_to_eda_file = path_to_preprocessed_directory + '/' + subject + '_eda.txt'
    tell_and_exit_if_path_does_not_exist(path_to_eda_file)

    print("Started to load preprocessed data for proband " + str(subject))
    preprocessed_eda_data = file_reader.load_preprocessed_eda_data(path_to_eda_file)
    print("Data is loaded")

    _, times = file_reader.load_metadata(main_directory + "/01_measurements/" + \
                                         subject + "_data.txt")
    sampling_rate = preprocessed_eda_data["fs"]
    eda = preprocessed_eda_data["eda"]
    eda_tonic = preprocessed_eda_data["eda_tonic"]
    eda_phasic = preprocessed_eda_data["eda_phasic"]

    # create_subject()
    subject = Subject(subject, times, sampling_rate,
                      eda, eda_tonic, eda_phasic)
    print("Subject is created")
    subject.evaluate_protocol_file_and_create_experiments(path_to_protocol_file)
    print("Experiments are created")
    subject.evaluate_experiments_and_print_parameters_txt(path_to_eda_results)
    print("Proband is evaluated")
    subject.print_parameters_of_experiments(path_to_folder=path_to_eda_results,
        filename=subject.tag + "_parameters_of_experiments.txt")
    # plot eda:
#    subject.plot(path_to_result_directory)


def tell_and_exit_if_path_does_not_exist(path):
    """Print message and leave if path does not exist"""
    if not os.path.isfile(path):
        error_string = "Error -- file " + path + " does not exist. \n"
        error_string += "Make sure to passed the right path and ran the scripts "
        error_string += "in the correct order as mentioned in the README.md."
        print(error_string)
        sys.exit()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: Pass subject tag as argument 1")
        sys.exit()

    subject_tag = sys.argv[1]
    path_to_main_directory = get_data_path()
    process_one_subject(subject_tag, path_to_main_directory)
