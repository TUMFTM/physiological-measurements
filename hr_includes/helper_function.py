# Copyright Feiler 2021

"""Outsourced functions for better readability in main script"""

import matplotlib.pyplot as plt
from hr_includes.hr_settings import HrSettings as hr

def delete_line_of_plotted_peaks():
    index_to_delete_line = None
    for line_index, line in enumerate(plt.gca().lines):
        if hr.ECG_PEAKS in str(line):
            index_to_delete_line = line_index
    if index_to_delete_line is not None:
        plt.gca().lines.pop(index_to_delete_line)
    plt.draw()

def get_min_y_val_of_current_axis():
    axis = plt.gca()
    return min([min(line.get_ydata()) for line in axis.lines])

def get_max_y_val_of_current_axis():
    axis = plt.gca()
    return max([max(line.get_ydata()) for line in axis.lines])

def get_lims():
    cur_axes = plt.gca()
    x_lim = cur_axes.get_xlim()
    y_lim = cur_axes.get_ylim()
    return (x_lim, y_lim)

def apply_lims(lim):
    """apply lims received from get_lims()"""
    cur_axes = plt.gca()
    cur_axes.set_xlim(lim[0])
    cur_axes.set_ylim(lim[1])

def something_is_chosen_from_toolbar():
    something_is_chosen = False
    tool_bar = plt.gcf().canvas.manager.toolbar
    if tool_bar.mode != '':
        something_is_chosen = True
    return something_is_chosen

if __name__ == "__main__":
    print("has no main")
