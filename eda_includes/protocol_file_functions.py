import datetime
import numpy as np
from eda_includes.experiment import Experiment


def evaluate_protocol_file_and_add_experiment(subject, path_to_protocol_file):
    __evaluate_protocol_file_for_excludes(subject, path_to_protocol_file)
    __evaluate_protocol_file_to_add_experiments(subject, path_to_protocol_file)


def __evaluate_protocol_file_for_excludes(subject, path_to_protocol_file):
    protocol_file = open(path_to_protocol_file, 'r')
    for line in protocol_file:
        if 'exclude' in line:
            split_protocol_line = line.split()
            if not (len(split_protocol_line) < 3):
                # see protocol_experiments.py for structure of protocol_file
                start_time = datetime.datetime.strptime(split_protocol_line[1], '%H:%M:%S.%f')
                end_time = datetime.datetime.strptime(split_protocol_line[2], '%H:%M:%S.%f')
                
                if start_time < subject.times[0]:
                    start_time = subject.times[0]
                # find the indexes corresponding to start and end time of the period described
                # in the line
                start_index = subject.times.index(start_time)
                # list[:end_index] cuts of before end_index --> + 1
                end_index = subject.times.index(end_time) + 1
                measure = ''
                if ('eda' in line or 'EDA' in line) and 'ecg' not in line and 'ECG' not in line:
                    measure = 'eda'
                __exclude_data(subject, start_index, end_index, measure)
    protocol_file.close()


def __exclude_data(subject, start_index, end_index, measure):
    nans = np.empty(end_index-start_index)
    nans[:] = np.nan

    # replace the values in the excluded period with nans
    if measure == 'eda' or measure == '':
        subject.eda[start_index:end_index] = nans
        subject.eda_tonic[start_index:end_index] = nans
        subject.eda_phasic[start_index:end_index] = nans


def __evaluate_protocol_file_to_add_experiments(subject, path_to_protocol_file):
    protocol_file = open(path_to_protocol_file, 'r')
    for line in protocol_file:
        if 'exclude' not in line:
            split_protocol_line = line.split()
            if not (len(split_protocol_line) < 3):
                # see protocol_experiments.py for structure of protocol_file
                exp_tag = split_protocol_line[0]
                start_time = datetime.datetime.strptime(split_protocol_line[1], '%H:%M:%S.%f')
                end_time = datetime.datetime.strptime(split_protocol_line[2], '%H:%M:%S.%f')

                # find the indexes corresponding to start and end time of the period discribed
                # in the line
                start_index = subject.times.index(start_time)
                # list[:end_index] cuts of before end_index --> +=1
                end_index = subject.times.index(end_time) + 1
                __add_experiment(subject, exp_tag, start_index, end_index)
    protocol_file.close()


def __add_experiment(subject, exp_tag, start_index, end_index):
    # find the measurements for the experiment
    exp_eda = subject.eda[start_index:end_index]
    exp_eda_tonic = subject.eda_tonic[start_index:end_index]
    exp_eda_phasic = subject.eda_phasic[start_index:end_index]
    exp_times = subject.times[start_index:end_index]

    # create an experiment object and add it to the experiments property of subject
    subject.experiments.append(Experiment(
            exp_tag, exp_times, subject.fs, subject.tag, 
            exp_eda, exp_eda_tonic, exp_eda_phasic))
