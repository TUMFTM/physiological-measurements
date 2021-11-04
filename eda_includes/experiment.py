import numpy as np
import eda_includes.eda_functions as eda_functions


class Experiment:
    def __init__(self, tag, times, sampling_rate, subject_tag,
                 eda, eda_tonic, eda_phasic):
        self.tag = tag
        self.times = times
        self.fs = sampling_rate
        self.subject_tag=subject_tag
        self.time_vector = np.linspace(0, len(self.times)/self.fs, len(self.times))

        self.eda = eda
        self.eda_tonic = eda_tonic
        self.eda_phasic = eda_phasic

        self.parameters = {}
        self.parameters['EDA_Mean'] = np.nan
        self.parameters['EDA_Std'] = np.nan
        self.parameters['SCL_Mean'] = np.nan
        self.parameters['EDA_Phasic_AUC'] = np.nan
        self.parameters['SCR_Frequency'] = np.nan
        self.parameters['SCR_Mean_Amplitude'] = np.nan
        self.parameters["SCR_Median_Amplitude"] = np.nan
        self.parameters['SCR_Mean_Rise_Time'] = np.nan
        self.parameters['SCR_Median_Rise_time'] = np.nan

    def calculate_parameters(self):
        eda_functions.evaluate_eda(self)
