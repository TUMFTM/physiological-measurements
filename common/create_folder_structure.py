# Copyright Feiler 2021

"""Reads path from data_directory.txt and creates in that folder the respective
folder structure"""

import os

def get_data_path():
    """Look for data_directory.txt. Its content is desired data path."""
    cur_path = os.path.dirname(os.path.join(os.getcwd(), __file__))
    file = "data_directory.txt"
    repo_main_dir = os.path.split(cur_path)[0]
    first_line = None
    with open(os.path.join(repo_main_dir, file), "r") as op_fi:
        first_line = op_fi.readline()
    return first_line

def create_folders(data_path):
    """Create respective folders for data storage and loading"""
    os.makedirs(data_path, exist_ok=True)
    os.makedirs(os.path.join(data_path, "01_measurements"), exist_ok=True)
    os.makedirs(os.path.join(data_path, "02_protocols_original"), exist_ok=True)
    try:
        os.makedirs(os.path.join(data_path, "03_eda_preprocessed"), exist_ok=False)
        os.makedirs(os.path.join(data_path, "04_eda_excluded_intervals"), exist_ok=False)
        os.makedirs(os.path.join(data_path, "05_eda_prot_with_exclusion"), exist_ok=False)
        os.makedirs(os.path.join(data_path, "06_eda_parameters"), exist_ok=False)
        os.makedirs(os.path.join(data_path, "07_hr_rpeaks"), exist_ok=False)
        os.makedirs(os.path.join(data_path, "08_hrv_sdnn"), exist_ok=False)
    except FileExistsError as err:
        print("WARNING: At least one of the folders from 03_ to 08_ already exists " +
              "in " + str(data_path) +
              ".\n\tBe sure to copy results from previous evaluations into other " + 
              "folders. Results could be overwritten otherwise.")

def main():
    data_directory = get_data_path()
    create_folders(data_directory)
    print("Directories successfully created. Script is finished.")

if __name__ == "__main__":
    main()
