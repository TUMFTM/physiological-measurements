# Copyright Feiler 2021

"""Class to process eda data of one subject"""

import os
import numpy as np
from tabulate import tabulate
import eda_includes.plot_functions as plot_functions
import eda_includes.protocol_file_functions as protocol_file_functions

class Subject:
    def __init__(self, tag, times, sampling_rate, eda, eda_tonic, eda_phasic):
        self.tag = tag
        self.times = times
        self.fs = sampling_rate
        self.time_vector = np.linspace(0, len(self.times)/self.fs, len(self.times))
        self.eda = eda
        self.eda_tonic = eda_tonic
        self.eda_phasic = eda_phasic
        self.experiments = []

    def evaluate_protocol_file_and_create_experiments(self, path_to_protocol_file=''):
        if os.path.isfile(path_to_protocol_file):
            protocol_file_functions.evaluate_protocol_file_and_add_experiment(self, path_to_protocol_file)
        else:
            print("Warning -- No protocolfile or incorrect path provided")

    def evaluate_experiments_and_print_parameters_txt(self, path_to_result_directory):
        for exp in self.experiments:
            exp.calculate_parameters()

        if not os.path.isdir(path_to_result_directory):
            os.makedirs(path_to_result_directory)

        path_to_parameter_file = path_to_result_directory + '/' + self.tag + '_parameters.txt'
        with open(path_to_parameter_file, 'w') as parameter_file:
            keys = self.experiments[0].parameters.keys()
            table = [["Parameters"]]

            for exp in self.experiments:
                table[0].append(exp.tag)

            for key in keys:
                table.append([])
                row = [key]

                for exp in self.experiments:
                    row.append(exp.parameters[key])

                row[1:] = np.around(row[1:], 3)
                table.append(row)
            parameter_file.write(tabulate(table, headers='firstrow'))

    def print_parameters_of_experiments(self, path_to_folder=os.getcwd(),
            filename=None, separator=","):
        if filename is None:
            filename = self.tag + "_parameters_of_experiments.txt"
        with open(path_to_folder + '/' + filename, 'w') as parameter_file:
            first = True
            for experiment in self.experiments:
                keys = experiment.parameters.keys()
                if first:
                    header = self.__get_header(keys)
                    parameter_file.write(header)
                    first = False
                line = self.__create_line(experiment, keys)
                parameter_file.write(line)

    def plot(self, path_to_result_directory):
        plot_functions.plot(self, path_to_result_directory)

    def __get_header(self, keys, separator=',') -> str:
        header = 'subject_tag' + separator + 'experiment_tag'
        for key in keys:
            header += separator + str(key)
        header += '\n'
        return header

    def __create_line(self, experiment, keys, separator=',') -> str:
        line = self.tag + separator + experiment.tag
        for key in keys:
            line += separator + str(experiment.parameters[key])
        line += '\n'
        return line
