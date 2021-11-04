# Copyright Feiler 2021

"""Plot EDA data"""

import os
import matplotlib.pyplot as plt
import numpy as np
import neurokit2 as nk
import eda_includes.subject as subject


###Adjustments
font_size = 14
fig_size = (12, 8)
dpi = 200
###Adjustments end


def plot(obj, path_to_result_directory):
    if not os.path.isdir(path_to_result_directory):
        os.makedirs(path_to_result_directory)

    path_to_figure = path_to_result_directory + '/' + obj.tag
    __plot_eda(obj, path_to_figure)

    if isinstance(obj, subject.Subject):
        path_to_result_directory += '/' + obj.tag + '_experiments'
        for exp in obj.experiments:
            plot(exp, path_to_result_directory)


def __plot_eda(obj, path_to_figure):
    path_to_figure += '_eda'
    fig = plt.figure(figsize=fig_size, dpi=dpi)

    plt.plot(obj.time_vector, obj.eda, label='raw eda', color='b')
    plt.plot(obj.time_vector, obj.eda_tonic, label='eda tonic', color='g')
    plt.plot(obj.time_vector, obj.eda_phasic, label='eda phasic', color='orange')
    plt.grid(True)

    if isinstance(obj, subject.Subject):
        __plot_experiment_borders(obj)
    else:
        plt.plot(obj.eda_peak_indices/obj.fs, obj.eda[obj.eda_peak_indices.astype(int)],
                 'rx', label='SCR')

    plt.ylabel(r"eda in $\mu S$", fontsize=font_size)
    plt.legend(loc=0, fontsize=font_size)
    plt.xlabel("time in s", fontsize=font_size)
    plt.xticks(fontsize=font_size)
    plt.yticks(fontsize=font_size)
    plt.xlim((0, obj.time_vector[-1]))
    plt.ylim((-2, 27))
    fig.savefig(path_to_figure)
    plt.close()


def __plot_experiment_borders(obj, min_value=0):
    height = min_value + 5
    for exp in obj.experiments:
        start = obj.times.index(exp.times[0])/obj.fs
        end = obj.times.index(exp.times[-1])/obj.fs
        plt.axvline(start, color='r')
        plt.axvline(end, color='r')
        plt.text(start, height, exp.tag, fontsize=font_size)
