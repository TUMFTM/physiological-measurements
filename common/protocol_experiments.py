# Copyright Feiler 2021

"""
This program enables you to document your measurements.
Console outputs are provided to guide you.
"""

import os
import datetime
from create_folder_structure import get_data_path

def main():
    data_directory = get_data_path()
    protocol_path = os.path.join(data_directory, "02_protocols_original")

    print("Insert a tag or name of subject ")
    subject_name = input()
    with open(protocol_path + '/' + subject_name +'_protocol.txt', 'w') as protFile:
        user_input = ''
        while user_input != 'q':
            print("Enter a name for the next experiment (no spaces): ")
            user_input = input()
            protFile.write(user_input+' ')

            print("Press enter to start the experiment")
            user_input = input()
            timestamp = datetime.datetime.now()
            protFile.write(timestamp.strftime('%H:%M:%S.%f')[:-3] + ' ')

            print("Press enter to stop the experiment")
            user_input = input()
            timestamp = datetime.datetime.now()
            protFile.write(timestamp.strftime('%H:%M:%S.%f')[:-3])

            print("insert comment (optional, spaces are allowed): ")
            user_input = input()
            if user_input != '':
                protFile.write(' ' + user_input)
            protFile.write('\n')

            print("Press enter to continue and start a new experiment or press q + enter to quit")
            user_input = input()

if __name__ == "__main__":
    main()