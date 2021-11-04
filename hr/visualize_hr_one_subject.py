# Copyright Feiler 2021

"""
Visualize ECG-data of proband.
The goal is to produce one _ecg_rpeaks.txt file, in which

- nan stands for: artifact area --> exclusion of intervals for sdnn analysis
- wrongly detected peaks are deleted
- peaks, missed by detection, are added

Manual:

- D activates the 'delete mode' --> a mouse click deletes the next rpeak
- A activates the 'add mode' --> a mouse click defines the next rpeak
    (highest point close to mouse click)
- E activates the 'exclude mode' --> two mouse clicks define an exclusion interval
- I activates the 'exact add mode' --> a mouse click defines exactly the next rpeak

- SPACE: current plot is closed and next interval is loaded

"""

import json
import math
import sys
import datetime
import matplotlib.pyplot as plt
import numpy as np
from numpy.core.defchararray import index
import pandas as pd
import neurokit2 as nk
from scipy.signal import argrelextrema
import append_sys_paths
from hr_includes import helper_function
from hr_includes.hr_settings import HrSettings as hr
from hr_includes.exclusion_tracker import ExclusionTracker, SecondIndexIsSmallerThanFirst
from common import file_reader
from common.create_folder_structure import get_data_path

class Proband:
    """A proband can be plotted and its automatically detected peaks can be
    corrected"""
    def __init__(self, raw_data_path, window_size_s):
        self.__data_path = raw_data_path
        self.__sampling_rate = []
        self.__ecg = None
        self.__ecg_rpeak_indices = None
        self.__current_st_ind = 0
        self.__window_size_s = window_size_s
        self.__current_mode = hr.DEL_PEAK
        self.__exclusion_tracker = ExclusionTracker()

    def load_data(self):
        """load the ecg data"""
        print(f"Started to load data for {self.__data_path.split('/')[-1]}")
        self.__sampling_rate = self.__get_from_file_header('sampling rate')
        self.__ecg = self.__get_transformed_ecg_data()
        self.__ecg = nk.ecg_clean(self.__ecg, sampling_rate=self.__sampling_rate)
        self.__ecg_rpeak_indices = \
            nk.ecg_findpeaks(self.__ecg,
                             sampling_rate=self.__sampling_rate)['ECG_R_Peaks']

    def __get_from_file_header(self, key):
        """"return something found in the file's header"""
        found_value = 0
        with open(self.__data_path, 'r') as data_file:
            if 'OpenSignals' not in str(data_file.readline()):
                print(f"wrong file at {self.__data_path}")
                sys.exit(1)
            meta_data = json.loads(data_file.readline().replace('#', ''))
            meta_data = meta_data[list(meta_data.keys())[0]]
            found_value = meta_data[key]
        return found_value

    def __get_transformed_ecg_data(self):
        """returns transformed but unmodified ecg data as pd.Series"""
        data = pd.read_csv(self.__data_path, skiprows=3, sep="\t", usecols=[5,6],
                           header=None)
        ecg = data.iloc[:,0]
        ecg = file_reader.ecg_transfer_function(ecg)
        return ecg

    def visualize_iteratively(self):
        """iterate over data to be visualized"""
        samples_per_window = self.__window_size_s * self.__sampling_rate
        number_of_windows = math.ceil(self.__ecg.shape[0] / samples_per_window)
        print("Plotting")
        for number in range(number_of_windows):
            title = f"ECG interval {number + 1}/{number_of_windows} of " +\
                    f"{self.__data_path.split('/')[-1]}"
            self.__plot_data(number, title, samples_per_window)

    def __plot_data(self, number, title, samples_per_window):
        """Plot everything"""
        self.__current_mode = hr.DEL_PEAK # reset to del mode, less error prone
#        fig, axes = plt.suplots(3, 1)
#        plt.sca(axes[0])
        fig = plt.figure()
        axes = fig.add_subplot(1, 1, 1)
        plt.sca(axes)
        plt.gca().set_title(title)
        self.__current_st_ind = number*samples_per_window
        end_ind = self.__current_st_ind + samples_per_window
        plt.plot(self.__ecg[self.__current_st_ind:end_ind], label=hr.ECG_SIGNAL, picker=True)
        plt.get_current_fig_manager().window.showMaximized()
        self.__plot_peaks()

        fig.canvas.mpl_connect('key_press_event', self.__on_key)
        fig.canvas.mpl_connect('button_press_event', self.__on_click)
        fig.canvas.mpl_connect('pick_event', self.__on_pick)
        plt.show()

    def __on_key(self, event):
        """Callback on key press"""
        if event.key == hr.DEL_KEY:
            self.__current_mode = hr.DEL_PEAK
        if event.key == hr.ADD_KEY:
            self.__current_mode = hr.ADD_PEAK
        if event.key == hr.EXCLUDE_KEY:
            self.__current_mode = hr.EXCLUDE_INTERVAL
        if event.key == hr.EXACT_PICKING_KEY:
            self.__current_mode = hr.EXACT_PICKING
        if event.key == " ": # SPACE
            plt.close(plt.gcf())
        print(f"Current mode is {self.__current_mode}")

    def __on_click(self, event):
        """Callback on any simple mouseclick"""
        if helper_function.something_is_chosen_from_toolbar():
            print("nothing further happens when toolbar is clicked")
            return
        if self.__current_mode == hr.EXCLUDE_INTERVAL:
            clicked_index = self.__current_st_ind + int(event.xdata)
            try:
                self.__exclusion_tracker.process_index(clicked_index)
            except SecondIndexIsSmallerThanFirst as err:
                print(f'SecondIndexIsSmallerThanFirst Error: {err}\nRETURNING')
                return
            self.__visualize_exclusion_line(clicked_index)
            if self.__exclusion_tracker.current_interval_pair_is_finished():
                self.__visualize_area()

    def __visualize_exclusion_line(self, index):
        axis = plt.gca()
        plot_index = index - self.__current_st_ind
        limits = helper_function.get_lims()
        axis.vlines(plot_index, helper_function.get_min_y_val_of_current_axis(),
                    helper_function.get_max_y_val_of_current_axis(), colors='orange')
        plt.draw()
        helper_function.apply_lims(limits)

    def __visualize_area(self):
        start_index = self.__exclusion_tracker.get_last_exclusion_pair()[0] - \
                        self.__current_st_ind
        plot_index = self.__exclusion_tracker.get_last_exclusion_pair()[1] - \
                        self.__current_st_ind
        plt.gca().fill_betweenx(
                    [helper_function.get_min_y_val_of_current_axis(),
                     helper_function.get_max_y_val_of_current_axis()],
                    start_index, plot_index, facecolor='orange', alpha=0.1)
        plt.draw()

    # if close to multiple objects, on_pick is called multiple times with different artist
    def __on_pick(self, event):
        """Callback on picker"""
        if helper_function.something_is_chosen_from_toolbar():
            print("nothing further happens when toolbar is clicked")
            return
        if self.__current_mode == hr.DEL_PEAK and hr.ECG_PEAKS in str(event.artist):
            x_axis_value = event.mouseevent.xdata
            print(f"now i delete {x_axis_value}")
            self.__delete_index_from_ecg_rpeak_indices(x_axis_value)
            self.__redraw_ecg_peaks()
        if self.__current_mode == hr.ADD_PEAK and hr.ECG_SIGNAL in str(event.artist):
            self.__add_maximum_value_in_adjacency_to_ecg_peaks(event)
        if self.__current_mode == hr.EXACT_PICKING and hr.ECG_SIGNAL in str(event.artist):
            self.__add_this_xval_to_ecg_peaks(event)

    def __delete_index_from_ecg_rpeak_indices(self, x_axis_val):
        clicked_index = self.__current_st_ind + x_axis_val
        index_del_item = (np.abs(self.__ecg_rpeak_indices - clicked_index)).argmin()
        self.__ecg_rpeak_indices = np.delete(self.__ecg_rpeak_indices, index_del_item)

    def __redraw_ecg_peaks(self):
        limits = helper_function.get_lims()
        helper_function.delete_line_of_plotted_peaks()
        self.__plot_peaks()
        helper_function.apply_lims(limits)

    def __plot_peaks(self):
        """plot the peaks"""
        end_ind = self.__current_st_ind + self.__sampling_rate * self.__window_size_s
        cur_peaks = self.__ecg_rpeak_indices[np.where(
                            np.logical_and(self.__ecg_rpeak_indices>self.__current_st_ind,
                                           self.__ecg_rpeak_indices<end_ind))]
        plt.plot(cur_peaks-self.__current_st_ind, self.__ecg[cur_peaks], "xr",
                 label=hr.ECG_PEAKS, picker=True, mew=2, ms=12)

    def __add_maximum_value_in_adjacency_to_ecg_peaks(self, event):
        all_local_maxima = argrelextrema(self.__ecg, np.greater)[0]
        clicked_abs_index = self.__current_st_ind + int(event.mouseevent.xdata)
        index_to_be_added = all_local_maxima[np.abs(all_local_maxima - clicked_abs_index).argmin()]
        position_of_new_index = np.argmax(self.__ecg_rpeak_indices>index_to_be_added)
        self.__ecg_rpeak_indices = np.insert(self.__ecg_rpeak_indices, position_of_new_index,\
                                             index_to_be_added)
        self.__redraw_ecg_peaks()

    def __add_this_xval_to_ecg_peaks(self, event):
        clicked_abs_index = self.__current_st_ind + round(event.mouseevent.xdata)
        # WARNING: this line does not work with click after last peak
        position_for_insertion = np.argmax(self.__ecg_rpeak_indices>clicked_abs_index)
        self.__ecg_rpeak_indices = np.insert(self.__ecg_rpeak_indices, position_for_insertion,\
                                             clicked_abs_index)
        self.__redraw_ecg_peaks()

    def process_exclusions_and_save_rpeaks_file(self, output_directory):
        """store metadata and indices of rpeaks into file"""
        subject = self.__data_path.split("/")[-1].split("_")[0]
        ecg_header_dict = self.__create_ecg_header(subject)

        ecg_peaks_as_float = self.__get_ecg_peaks_with_exclusions()
        output_file = output_directory + '/' + subject + '_ecg_rpeaks.txt'
        with open(output_file, 'w') as ecg_file:
            ecg_file.write(json.dumps(ecg_header_dict) + '\n')
            for rpeak in ecg_peaks_as_float:
                if np.isnan(rpeak):
                    ecg_file.write('nan\n')
                else:
                    ecg_file.write(str(int(rpeak)) + '\n')

    def __create_ecg_header(self, subject):
        _, times = file_reader.load_metadata(self.__data_path)
        ecg_header_dict = {"subject_tag": subject,
                       "sampling_rate": self.__sampling_rate,
                       "start_time": datetime.datetime.strftime(times[0],"%H:%M:%S.%f")[:-3]}
        ecg_header_dict["columns"] = ["index of rpeak in data_file"]
        return ecg_header_dict

    def __get_ecg_peaks_with_exclusions(self):
        ecg_peaks_as_float = np.array(self.__ecg_rpeak_indices, dtype=float)
        exclusion_data = self.__exclusion_tracker.get_all_exclusions()
        exclusion_data = [float(i) for i in exclusion_data]
        for even_index in range(0, len(exclusion_data), 2):
            cur_start_excl = exclusion_data[even_index]
            cur_end_excl = exclusion_data[even_index + 1]
            peaks_to_exclude = ecg_peaks_as_float[np.where(
                            np.logical_and(ecg_peaks_as_float>cur_start_excl,
                                           ecg_peaks_as_float<cur_end_excl))]
            if len(peaks_to_exclude) != 0:
                for peak in peaks_to_exclude.tolist():
                    ecg_peaks_as_float[np.where(ecg_peaks_as_float==peak)] = np.nan
            if len(peaks_to_exclude) == 0:
                position = np.argmax(ecg_peaks_as_float>cur_end_excl)
                ecg_peaks_as_float = np.insert(ecg_peaks_as_float, position, np.nan)
        return ecg_peaks_as_float

    def save_exclude_file(self, output_path):
        """save the exclusion area to separate file"""
        subject = self.__data_path.split("/")[-1].split("_")[0]
        file_name = output_path + "/" + str(subject) + "_exclusions.txt"
        with open(file_name, "w") as exclusion_file:
            exclusions = self.__exclusion_tracker.get_all_exclusions()
            for excl in exclusions:
                exclusion_file.write(f'{excl}\n')

def visualize_one_subject(subject, window_in_s=30):
    """Main function"""
    main_data_dir = get_data_path()
    path_to_data_file = main_data_dir + "/01_measurements/" + subject + "_data.txt"
    path_rpeaks_output = main_data_dir + "/07_hr_rpeaks/"
    prob = Proband(path_to_data_file, window_in_s)
    prob.load_data()
    prob.visualize_iteratively()
    prob.process_exclusions_and_save_rpeaks_file(path_rpeaks_output)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: Pass subject tag as argument 1")
        sys.exit()

    subject_tag = sys.argv[1]
    visualize_one_subject(subject_tag)
