# Copyright Feiler 2021

"""Determines the EDA parameters of all codewords with files in prot_files_dir"""

import os
from concurrent import futures
import determine_params_of_one_subject as subj
import append_sys_paths
from common.create_folder_structure import get_data_path

def main():
    """main function"""
    path_to_main_directory = get_data_path()
    prot_files_dir = os.path.join(path_to_main_directory, "05_eda_prot_with_exclusion")
    filenames = [f for f in os.listdir(prot_files_dir) if \
                 os.path.isfile(os.path.join(prot_files_dir, f))]
    codewords = [f.split(sep="_")[0] for f in filenames]
    if len(codewords) == 0:
        print("No protocol files found in " +
              str(prot_files_dir) +
              ". Did you run add_eda_excludes_to_prot.py?")
    with futures.ProcessPoolExecutor(max_workers=5) as ex:
        for number, codeword in enumerate(codewords, 1):
            print("starting with " + str(number) + "/" + str(len(codewords)))
            ex.submit(subj.process_one_subject, codeword, path_to_main_directory)

if __name__ == "__main__":
    main()
