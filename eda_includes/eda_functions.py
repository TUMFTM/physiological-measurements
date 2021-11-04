import numpy as np
import scipy.signal


def evaluate_eda(exp):
    phasic = np.copy(exp.eda_phasic)

    dx = 1/exp.fs
    phasic_diff = np.diff(phasic)/dx

    # find relevant peaks in eda_signal
    if np.isnan(phasic).any():
        for i, value in enumerate(phasic):
            if np.isnan(value):
                phasic[i] = 0

    minimal_eda_peak_height = 0.01 # 0.01 - 0.05 Boucsein 2012, Publication recommendations
    minimal_seconds_between_peaks = 1 # https://github.com/shkurtagashi/EDArtifact/tree/master/EDArtifact_Dashboard
    min_prominence = 0.06
    exp.eda_peak_indices, _ = \
        scipy.signal.find_peaks(phasic, height=minimal_eda_peak_height,
                                distance=minimal_seconds_between_peaks*exp.fs,
                                prominence=min_prominence)

    exp.eda_peak_amplitudes = np.empty(len(exp.eda_peak_indices))
    exp.eda_peak_rise_times = np.empty(len(exp.eda_peak_indices))

    for i, peak_index in enumerate(exp.eda_peak_indices):
        exp.eda_peak_amplitudes[i] = exp.eda_phasic[peak_index]

        # calculate the risetime of each SCR
        start_onset = max(0, peak_index-4*exp.fs)
        max_diff = np.max(phasic_diff[start_onset:peak_index])
        max_diff_index = np.where(phasic_diff[start_onset:peak_index] == max_diff)
        if max_diff_index[0].size == 0 or np.isnan(max_diff):
            continue
        max_diff_index = max_diff_index[0][0]
        max_diff_index += start_onset
        onset = np.where(phasic_diff[:max_diff_index] <= 0.01 * max_diff)
        if onset[0].size != 0:
            onset = onset[0][-1]
        else:
            onset = start_onset

        exp.eda_peak_rise_times[i] = (peak_index-onset) / exp.fs

    exp.parameters["EDA_Std"] = np.nanstd(exp.eda)
    exp.parameters["EDA_Mean"] = np.nanmean(exp.eda)
    exp.parameters["SCL_Mean"] = np.nanmean(exp.eda_tonic)

    #length of the eda_signal that can be used (that is not excluded) in minutes
    eda_length_evaluated_in_min = np.sum(~ np.isnan(exp.eda)) / (60 * exp.fs)

    # calculate peaks per min
    exp.parameters["SCR_Frequency"] = len(exp.eda_peak_indices) / eda_length_evaluated_in_min
    # calculate area under eda phasic curve, set in relation to the calculation time -> unit=[1/min]
    exp.parameters["EDA_Phasic_AUC"] = np.trapz(phasic, dx=1/exp.fs)/ eda_length_evaluated_in_min

    if len(exp.eda_peak_indices) > 0:
        exp.parameters["SCR_Mean_Amplitude"] = np.mean(exp.eda_peak_amplitudes)
        exp.parameters["SCR_Median_Amplitude"] = np.median(exp.eda_peak_amplitudes)
        exp.parameters["SCR_Mean_Rise_Time"] = np.mean(exp.eda_peak_rise_times)
        exp.parameters["SCR_Median_Rise_time"] = np.median(exp.eda_peak_rise_times)
    else:
        exp.parameters["SCR_Mean_Amplitude"] = 0
        exp.parameters["SCR_Mean_Rise_Time"] = 0
        exp.parameters["SCR_Median_Rise_time"] = 0
