# Copyright Feiler 2021

"""This program visualizes the preprocessed EDA data (<codeword>_eda.txt,
EDA, EDA-phasic and EDA-tonic). Click two lines with the mouse,
to mark an area in the plot. It can be used for manual labeling as well as
the exclusion of artifacts. The intervals are stored to a
log-file automatically after the complete data was inspected ([timestamp, index]).

- Use DELETE (german: ENTF) to remove lastly added line.
- Use ESCAPE to deactivate/activate clicking of line.
- Use SPACE to shut down the program (and store previous markers).

Close the plot and the next window opens automatically.
"""

import math
import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import append_sys_paths
from common.create_folder_structure import get_data_path

DETAILED_INTERVAL_IN_SEC = 60
Y_TICKS_INTERVAL = 0.1 # in micro_siemens
FREQUENCY_IN_HZ = 1000
NO_OF_INDICES_IN_DETAILED_INTERVAL = FREQUENCY_IN_HZ * DETAILED_INTERVAL_IN_SEC
MIN_OF_MIKRO_SIEMENS = 0.1

def get_data(path_to_file):
    """Return preprocessed EDA data"""
    data_frame = pd.read_csv(path_to_file, sep=" ", header=None, skiprows=[0])
    header = ["EDA", "EDA-Tonic", "EDA-Phasic", "Time"]
    data_frame.columns = pd.Index(header)
    return data_frame

def get_current_interval(interval_index, data_frame):
    """Returns the data of the current interval based on its index number"""
    start_ind = interval_index*NO_OF_INDICES_IN_DETAILED_INTERVAL
    end_ind = (interval_index+1)*NO_OF_INDICES_IN_DETAILED_INTERVAL
    current_interval_data = data_frame.iloc[start_ind:end_ind, 0:3]
    indices = pd.Index(data_frame.iloc[start_ind:end_ind, 3:4])
    current_interval_data.index = indices
    return current_interval_data

def make_indices_of_data_readable(pd_data_frame):
    """Changes the indices of the DataFrame to more readable format in plot"""
    new_indices = []
    for index in pd_data_frame.index:
        new_indices.append(index[0])
    pd_data_frame.index = new_indices

def plot_eda_data(input_data_frame, axes):
    """Plots the provided data"""
    plt.sca(axes[0])
    input_data_frame.iloc[:, 0].plot()
    input_data_frame.iloc[:, 1].plot()
    plt.gca().get_lines()[-1].set_color("green")
    plt.sca(axes[1])
    input_data_frame.iloc[:, 2].plot()
    plt.gca().get_lines()[-1].set_color("brown")

def set_y_ticks(current_axes):
    """Add background y ticks"""
    y_range = current_axes.get_ylim()
    y_ticks_micro_siemens = list(np.arange(y_range[0], y_range[1],\
                                           Y_TICKS_INTERVAL))
    current_axes.set_yticks(y_ticks_micro_siemens, minor=True)
    current_axes.grid(which="minor", alpha=0.3)

def set_x_ticks_per_min(current_axes):
    """Add background x ticks"""
    x_ticks_seconds = list(range(0,NO_OF_INDICES_IN_DETAILED_INTERVAL,FREQUENCY_IN_HZ))
    current_axes.set_xticks(x_ticks_seconds,minor=True)
    current_axes.grid(which="minor",alpha=0.3)

INTERVALS = []
intervals_readable = []
def store_x_click_in_interval(event):
    """Store clicked x-data into global variable"""
    INTERVALS.append(event.xdata)

def len_is_even(input_list):
    """Check if list has even length"""
    return_bool = False
    if (len(input_list)%2) == 0:
        return_bool = True
    return return_bool

def create_line_and_filled_area(event, axis):
    """Visualize clicks as lines and filled area"""
    minimum_value = 0
    first_time = True
    for line in axis.lines:
        current_min = min(line.get_ydata())
        if current_min < minimum_value:
            minimum_value = current_min
        if first_time:
            minimum_value = current_min
            first_time = False
    maximum_value = 0
    first_time = True
    for line in axis.lines:
        current_max = max(line.get_ydata())
        if current_max > maximum_value:
            maximum_value = current_max
        if first_time:
            maximum_value = current_max
            first_time = False

    axis.vlines(event.xdata, minimum_value, maximum_value, colors='orange')
    if len_is_even(INTERVALS):
        axis.fill_betweenx([minimum_value, maximum_value], INTERVALS[-2], \
                           INTERVALS[-1], facecolor='orange', alpha=0.1)
    plt.draw()

def second_click_is_not_right_from_previous(event):
    """Check if second click is later in time than previous"""
    second_click_is_smaller_than_first = False
    global INTERVALS
    if not len_is_even(INTERVALS):
        # new click is the second one
        if INTERVALS[-1]>=event.xdata:
            second_click_is_smaller_than_first = True
    return second_click_is_smaller_than_first

CLICK_CALLBACK_TURNED_OFF = False
def onclick(event):
    """Handle user click"""
    if CLICK_CALLBACK_TURNED_OFF:
        return
    if event.name == "button_press_event":
        if second_click_is_not_right_from_previous(event):
            print("Intervals must start at start time. Click is not processed.")
            return
        store_x_click_in_interval(event)
        axes = plt.gcf().axes
        for current_axes in axes:
            create_line_and_filled_area(event, current_axes)

def delete_last_line_added():
    """Delete lastly added line from plot"""
    current_axes = plt.gcf().axes
    for current_axes in current_axes:
        all_collections = current_axes.collections
        last = all_collections.pop()
        typ = type(last)
        print("Removed element " + str(typ))
        if "PolyCollection" in typ.__name__:
            again = all_collections.pop()
            print("Removed element " + str(type(again)))
    plt.draw()

SHUT_DOWN_PROGRAM = False
def on_key(event):
    """Handle user keypress"""
    global CLICK_CALLBACK_TURNED_OFF
    if event.key == 'escape':
        CLICK_CALLBACK_TURNED_OFF = not CLICK_CALLBACK_TURNED_OFF
        if CLICK_CALLBACK_TURNED_OFF:
            print("Custom onclick callback deactivated")
        else:
            print("Custom onclick callback activated")
    if event.key == 'delete':
        global INTERVALS
        if len(INTERVALS) == 0:
            return
        del INTERVALS[-1]
        delete_last_line_added()
    if event.key == ' ':
        global SHUT_DOWN_PROGRAM
        SHUT_DOWN_PROGRAM = True

def correct_index_to_current_interval(index, input_data_frame):
    """"Trim clicks next to interval to currently visualized interval"""
    corrected_index = index
    corrected_index = min(len(input_data_frame.index)-1, corrected_index)
    corrected_index = max(corrected_index, 0)
    return corrected_index

def transfer_intervals_into_readable_format_and_reset_intervals(data_frame, no_of_interval):
    """Read the function name"""
    for current_interval in INTERVALS:
        no_index = int(current_interval)
        corr_index = correct_index_to_current_interval(no_index, data_frame)
        time_stamp = data_frame.index[corr_index]
        overall_index = no_of_interval*NO_OF_INDICES_IN_DETAILED_INTERVAL + corr_index
        print("time stamp " + str(time_stamp) + " added")
        appended = [time_stamp, overall_index]
        intervals_readable.append(appended)
    del INTERVALS[:]

def add_plot_description(current_axes_array, subject):
    """Read the function name"""
    current_axes_array[1].set_xlabel("Time in hh:mm:ss.ms")
    current_axes_array[0].set_ylabel("Skin conductance in \u03BCS")
    current_axes_array[1].set_ylabel("Skin conductance in \u03BCS")
    current_axes_array[0].set_title("Skin conductance of subject " + \
                                    str(subject))
    for axes in current_axes_array:
        axes.legend()

def turn_grids_on(axes):
    """Read the function name"""
    for current_axes in axes:
        current_axes.grid()

def maximize_window():
    """Read the function name"""
    manager = plt.get_current_fig_manager()
    manager.window.showMaximized()

def visualize_detailed_view(data_frame, current_subject):
    """Read the function name"""
    make_indices_of_data_readable(data_frame)
    fig, axes = plt.subplots(2, 1)
    plot_eda_data(data_frame, axes)
    for current_axes in axes:
        set_y_ticks(current_axes)
        set_x_ticks_per_min(current_axes)
    add_plot_description(axes, current_subject)
    turn_grids_on(axes)
    fig.canvas.mpl_connect('button_press_event', onclick)
    fig.canvas.mpl_connect('key_press_event', on_key)
    maximize_window()
    plt.show()

def visualize_segment_per_segment(complete_data_as_pd, cur_subject):
    """Show plot for user interaction"""
    no_of_detailed_intervals = math.ceil(complete_data_as_pd.shape[0]/
                                         NO_OF_INDICES_IN_DETAILED_INTERVAL)
    for int_number in range(no_of_detailed_intervals):
        skip_first_number_of_plots = 0
        if int_number < skip_first_number_of_plots:
            continue
        global SHUT_DOWN_PROGRAM
        if SHUT_DOWN_PROGRAM:
            continue
        data = get_current_interval(int_number, complete_data_as_pd)
        visualize_detailed_view(data, cur_subject)
        transfer_intervals_into_readable_format_and_reset_intervals(data, int_number)

def write_data_to_file(path_to_file):
    """Store the work into file"""
    with open(path_to_file, "w") as write_file:
        for elem in intervals_readable:
            write_file.write(str(elem[0]) + "," + str(elem[1]) + "\n")


def main(subject):
    """Main function"""
    main_data_path = get_data_path()
    preprocessed_eda_file = main_data_path + '/03_eda_preprocessed/' + subject + \
                            "_eda.txt"
    loaded_data = get_data(preprocessed_eda_file)
    visualize_segment_per_segment(loaded_data, subject)

    excluded_interv_storage = main_data_path + '/04_eda_excluded_intervals/' + subject + \
                           "_excluded.txt"
    write_data_to_file(excluded_interv_storage)

if __name__ == "__main__":
    if (len(sys.argv)) < 2:
        print("Usage: Pass subject tag as argument 1")
        sys.exit()
    subject_tag = sys.argv[1]
    main(subject_tag)
