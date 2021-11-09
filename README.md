# Physiological Measurements

The package enables you to visually inspect your physiological measurements taken with a [BITalino
(r)evolution toolkit](https://bitalino.com/products/board-kit-ble-bt).
The measurements under consideration include the electrodermal activity (EDA) and
the electrocardiogram (ECG) or heart rate (HR).
Furthermore, key parameters can be
determined such as `EDA_Mean`, `SCL_Mean`, `SCR_Frequency`, `HRV_SDNN`, and so on. \

A user example is provided at the section [Demonstration](#demonstration).

This package is written in Python and is used under Windows or Ubuntu 18.04 or Ubuntu 20.04.

## Initial Preparation

1. Create appropriate conda env from `environment_*.yml`
(section [Dependencies](#dependencies))
2. Specify main storage path into `data_directory.txt`
3. Run `create_folder_structure.py` to create the folder structure for the data.

    ```Python
    python common/create_folder_structure.py
    ```

    Copy the raw BITalino measurements into the thereby created 01_measurements folder.

## Acquiring of Measurements

Acquire measurements with the BITalino (r)evolution toolkit and the respective OpenSignals firmware and document the
measurements with the protocol_experiments.py script meanwhile.\
Output: Data-file and protocol-file. Please follow the naming [Conventions](#conventions).

Example files (data and protocol) are provided for the demonstration.

## EDA (Electrodermal Activity)

The EDA data can be visually inspected and its key parameters can be determined by the following steps.
Please, carry out the [initial preparation](#initial-preparation) beforehand.

1. Split EDA measurements into phasic and tonic parts:

    ```Python
    python eda/preprocess_all_measurements.py
    ```

2. Inspect subject's eda data visually and mark the exclusions.
    The subject's raw data file should be named as described here [Conventions](#conventions). The user manual is at `doc/_build/html/index.html`.

    ```Python
    python eda/visualize_eda.py <subject_tag>
    ```

3. Append exclusion intervals to protocol files by running:

    ```Python
    python eda/add_eda_excludes_to_prot.py
    ```

4. Run determination of EDA parameters. The parameters are stored in `/06_eda_parameters`

    ```Python
    python eda/determine_params_all_subjects.py
    ```

## HRV (Heart Rate Variability)

The heart rate data can be visually inspected and its key parameters can be determined by the following steps.
Please, carry out the [initial preparation](#initial-preparation) beforehand.

1. Inspect subject's hr data for artifacts visually. After completion, an `rpeaks` file and a `hr_excluded_intervals`
   file in stored into the respective folders.

    ```Python
    python hr/visualize_hr_all_subjects.py
    ```

2. Calc SDNN (Standard Deviation of the NN Interval) of all subjects. The output is stored into `sdnn.csv`.

    ```Python
    python hr/determine_params_all_subjects.py
    ```

## Conventions

- Data-files are named `<subject_tag>_data.txt`
- Protocol-files are named `<subject_tag>_protocol.txt`

## Demonstration

In this section, the data can be analysed that are provided in the folder
`demonstration`. The provided, exemplary data was recorded with the BITalino (r)evolution toolkit
([Link](https://bitalino.com/products/board-kit-ble-bt)) and consists of:

- a data file containing EDA and ECG data
`01_measurements/XY12AB34_data.txt`
- a protocol file containing the timestamps of two example tasks T1 and T2
`02_protocols_original/XY12AB34_protocol.txt`

To execute the demonstration, copy the absolute path of the demonstration folder into the
`data_directory.txt`. Then, run the remaining step(s) from
[initial preparation](#initial-preparation) and execute the steps from section EDA and HRV afterwards.

> CAUTION: The script 'eda/preprocess_all_measurements.py' takes around 0:20 min to complete.

## Dependencies

Anaconda is highly recommended ([Conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html)).\
Tested with Python 3.8.\
Installation of dependencies can be done via the respective environment_*.yml file or manually.

### Windows

```Bash
conda env create -f environment_windows.yml
```

### Ubuntu

```Bash
conda env create -f environment_ubuntu.yml
```

### Manual installation (alternative)

If the installation via the `environment_*.yml` file does not work, the installation can be performed manually using the following commands.

- python 3.8 (`conda create -n <name> python=3.8`)
- numpy (`conda install numpy`)
- neurokit2 (`conda install -c conda-forge neurokit2`)
- cvxopt (`conda install cvxopt`)
- matplotlib (`conda install matplotlib`)
- tabulate (`conda install tabulate`)

## References

This package is citable via  
[![DOI](https://zenodo.org/badge/421737812.svg)](https://zenodo.org/badge/latestdoi/421737812)

This package uses some functionality provided by

- Makowski, D., Pham, T., Lau, Z. J., Brammer, J. C., Lespinasse, F., Pham, H., Schölzel, C., & Chen, S. A. (2021).
  NeuroKit2: A Python toolbox for neurophysiological signal processing. Behavior Research Methods, 53(4), 1689–1696.
  <https://doi.org/10.3758/s13428-020-01516-y>

The BITalino software 'OpenSignals (r)evolution' can be downloaded [here](https://bitalino.com/downloads/software)
