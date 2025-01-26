from typing import List
from termcolor import colored

from nachosv2.data_processing.check_unique_subjects import check_unique_subjects
from nachosv2.data_processing.read_metadata_csv import read_metadata_csv
# from nachosv2.log_processing.read_log import read_item_list_in_log
# from nachosv2.log_processing.write_log import write_log_to_file
from nachosv2.setup.verify_configuration_types import verify_configuration_types
from nachosv2.setup.define_dimensions import define_dimensions
from nachosv2.data_processing.get_list_of_epochs import get_list_of_epochs
from nachosv2.training.training_processing.training_loop import training_loop
from nachosv2.checkpoint_processing.log_utils import write_log_to_file


def sequential_processing(execution_device: str,
                          list_dict_configs: List[dict],
                          is_outer_loop: bool = False,
                          is_verbose_on: bool = False):
    """
    Runs the sequential training process for each configuration and test subject.

    Args:
        execution_device (str): The name of the device that will be use.
        list_of_configs (list of JSON): The list of configuration file.
        list_of_configs_paths (list of str): The list of configuration file's paths.
        
        is_outer_loop (bool): If this is of the outer loop. (Optional)
        is_verbose_on (bool): If the verbose mode is activated. Default is false. (Optional)
    
    Raises:
        Exception: When there are repeated test subjects or validation subjects
    """

    # Does the sequential training process for each configuration file
    for dict_config in list_dict_configs:
               
        # Defines if the images are 2D or 3D
        is_3d = define_dimensions(dict_config)

        # Creates the path to the data CSV files
        path_csv_metadata = dict_config["path_metadata_csv"]
        
        do_normalize_2d = dict_config["do_normalize_2d"]
        # Creates the normalization
        # normalizer = None
        # if not is_3d:
        #     normalizer = normalize(path_csv_metadata, dict_config)
        
        # Gets the data from the CSV files
        df_metadata = read_metadata_csv(path_csv_metadata)
        
        use_mixed_precision = dict_config["use_mixed_precision"]

        # # Reads in the log's subject list, if it exists
        # log_list = read_item_list_in_log(
        #     dict_config['output_path'],    # The directory containing the log files
        #     dict_config['job_name'],       # The prefix of the log
        #     dict_config['test_subjects'],  # The list of dictionary keys to read
        #     is_verbose_on                  # If the verbose mode is activated
        # )
        
        # # Creates the list of test subjects
        # if log_list and 'subject_list' in log_list: # From the log file if it exists
        #     test_subjects_list = log_list['test_subjects']
            
        # else: # From scratch if the log file doesn't exists
        #     test_subjects_list = dict_config['test_subjects']
            
        
        # Double-checks that the test subjects are unique
        # check_unique_subjects(test_subjects_list, "test")

        # Double-checks that the validation subjects are unique
        if not is_outer_loop:  # Only if we are in the inner loop
            check_unique_subjects(dict_config["validation_fold_list"], "validation")
        
        if is_verbose_on:  # If the verbose mode is activated
            print(colored("Double-checks of test and validation uniqueness successfully done.", 'cyan'))
        
        
        # Creates test_subjects_list as a list, regardless of its initial form
        if not dict_config['test_fold_list']: # If the test_subjects list is empty, uses all subjects
            test_fold_list = list(dict_config['fold_list'])
        else:
            test_fold_list = list(dict_config['test_fold_list'])
        
        # Gets the list of epochs
        list_of_epochs = get_list_of_epochs(dict_config["hyperparameters"]["epochs"], test_fold_list, is_outer_loop, is_verbose_on)
        
        # TODO: split directly to test and validation, not only test
        
        # Trains for each test subject
        for test_fold_name, number_of_epochs in zip(test_fold_list,
                                                    list_of_epochs):

            training_loop(
                execution_device=execution_device,
                configuration=dict_config,
                test_fold_name=test_fold_name,
                df_metadata=df_metadata,
                number_of_epochs=number_of_epochs,
                do_normalize_2d=do_normalize_2d,
                is_outer_loop=is_outer_loop,
                is_3d=is_3d,
                use_mixed_precision=use_mixed_precision,
                rank=None,
                is_verbose_on=False
            )
             
            # test_subjects_dictionary = {'test_subjects': [t for t in test_subjects_list if t != test_subject_name]}
            
            # write_log_to_file(
            #     dict_config['output_path'],   # The directory containing the log files
            #     dict_config['job_name'],      # The prefix of the log
            #     test_subjects_dictionary,               # A dictionary of the relevant status info
            #     False, # use_lock                       # whether to use a lock or not when writing results
            #     is_verbose_on                           # If the verbose mode is activated
            # )
    