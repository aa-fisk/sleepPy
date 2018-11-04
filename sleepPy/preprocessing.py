# Script for preprocessing EEG data
# that has been scored and outputed
# as time series with labels and fourier
# transform power in columns
# single file for each animal/day to analyse

import re
import sys
import pandas as pd
import numpy as np
sys.path.insert(0, "/Users/angusfisk/Documents/01_PhD_files/07_python_package/"
                "actigraphy_analysis")
from actigraphy_analysis.preprocessing \
    import SaveObjectPipeline, create_file_name_path, create_subdir, \
        remove_object_col

def remove_header_and_save(file,**kwargs):
    """
    Function to scan through file name, remove
    the header and save the rest of the file
    to a new file in another directory
    :return:
    """
    file_contents = scan_sliceoff_header(file)
    new_file_name = create_file_name_path(directory=kwargs["save_dir_path"],
                                          file=file,
                                          save_suffix=kwargs[
                                              "save_suffix_file"])
    save_filecontents(file_contents=file_contents,
                      save_path=new_file_name)
    
def scan_sliceoff_header(file_path,
                         header="Signal"):
    """
    Function to read file from file
    path and scan for the start of the
    header (start of the actual data)
    Returns the file contents
    :param file_path: string
    :param header: string - default "Signal"
    :return: file contents cut from
        header start
    """
    # read the file
    # scan for the start
    # slice from the start
    with open(file_path, 'r', encoding='utf-8') as current_file:
        file_contents = current_file.read()
        start_of_table = re.search(header, file_contents).start()
        file_contents_modified = file_contents[start_of_table:]
    return file_contents_modified
    
def save_filecontents(file_contents,
                      save_path):
    """
    function to save the given file contents
    in the save path
    :param file_contents:
    :param save_path:
    :return:
    """
    with open(save_path, 'w', encoding='utf-8') as new_file:
        new_file.write(file_contents)
    
def read_file_to_df(file_path,
                    check_cols=True):
    """
    Function to read in fourier transformed data
    :param file_path:
    :return:
    """
    data = pd.read_csv(file_path,
                       header=1,
                       index_col=[0,2],
                       parse_dates=True)
    data = data.drop(data.columns[-1], axis=1)
    name = file_path.stem
    data.name = name
    if check_cols:
        check_data_columns(data)
    return data
    
def check_data_columns(data):
        """
        checks data has been imported correctly by checking the value
        of the first column
        
        """
        hz_column = data.iloc[:,3].name
        if not hz_column == "0.500000Hz"
            raise ValueError("Incorrect column name")
        return None

def artefacts_null(data,
                   stage_column="Stage",
                   stages_list=["W","NR","R","M"]):
    """
    Function to set all values which aren't in
     stages_list to np.nan, aimed to remove artefact values
    :param data:
    :param stage_column:
    :param stages_list:
    :return:
    """
    # create a mask of where the Stage is in the whitelist
    # remove object column
    # set all the values outside the mask to be nan
    # reset the object column
    # return the new data
    artefact_mask = data.loc[:,stage_column].isin(stages_list)
    df_nocol, cols = remove_object_col(data, return_cols=True)
    masked_data = df_nocol.where(artefact_mask, other=np.nan)
    for col in cols:
        col_name = col.name
        masked_data[col_name] = col
    return masked_data

def sum_power(data,
              range_to_sum):
    """
    Function to sum over the range given as a string for column names
    :param data:
    :param range_to_sum:
    :return:
    """
    