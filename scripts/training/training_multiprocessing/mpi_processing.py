import argparse
import datetime
from mpi4py import MPI
import os
from termcolor import colored
import time
import sys

import tensorflow as tf

from scripts.training.training_processing import training_loop
from scripts.training.training_processing.training_variables import TrainingVariables
from src.data_processing.fold_generator import generate_pairs
from src.log_processing.read_log import read_item_list_in_log
from src.log_processing.write_log import write_log_to_file
from src.file_processing.parse_mpi_training_configs import parse_mpi_training_configs


# Location of the configurations
CONFIG_LOC = './training/training_config_files'

def parse_n_gpus():
    parser = argparse.ArgumentParser()

    parser.add_argument("-ng", "--ngpus",
                        help=" Number of gpus per server",
                        required=False)
    
    # This functions allows to not produce an error when extra arguments are present
    args = parser.parse_known_args()
    # print("args =", args)
    n_gpus = int(args[0].ngpus)
    # print("n_gpus =", n_gpus)
    
    return n_gpus


def parse_dummy_node():
    parser = argparse.ArgumentParser()

    parser.add_argument('--dummy', action="store_true")
        
    args = parser.parse_known_args()
    
    b_dummy = args[0].dummy
    
    print("b_dummy =", b_dummy)
    
    return b_dummy
 

def split_tasks(configs, is_outer):
    """ Generates config-fold tuples for training.

    Args:
        configs (list of dict): List of configurations.
        is_outer (bool): If this is of the outer loop or not.
        
    Returns:
        (list tuples): A list of config-fold tuples.
    """
    # Create a list of (config, test subject, validation subject) tuples
    tasks = []
    for config in configs:
        
        # Generate all fold-pairs
        test_subjects = list(config['test_subjects'])
        validation_subjects = None if is_outer else config['validation_subjects']
        folds = generate_pairs(test_subject_list = test_subjects,
                                              validation_subject_list = validation_subjects,
                                              do_shuffle = config['shuffle_the_folds'],
                                              param_epoch = config["hyperparameters"]['epochs'],
                                              is_outer = is_outer)
        print(folds)
        # Add folds to task list
        tasks.extend([(config, n_epochs, test_subject, validation_subject) for n_epochs, test_subject, validation_subject in folds])
    return tasks
        
            
def run_training(rank, config, n_epochs, test_subject, validation_subject, is_outer):
    """ Run the training loop for some task.
    Args:
        rank (int): The rank of the process.
        config (dict): The given training configuration for the task.
        test_subject (str): The task's testing subject name.
        validation_subject (str): The task's training/validation subject name. May be None.
        is_outer (bool): If this task is of the outer loop.
    """    
    # Read in the log, if it exists
    job_name = f"{config['job_name']}_test_{test_subject}" if is_outer else f"{config['job_name']}_test_{test_subject}_sub_{validation_subject}"
    log = read_item_list_in_log(
        config['output_path'], 
        job_name, 
        ['is_finished']
    )
    
    # If this fold has finished training, return
    if log and log['is_finished']:
        return
    
    # Run the subject pair
    if is_outer:
        print(colored(f"Rank {rank} is starting training for {test_subject}.", 'green'))
    else:
        print(colored(f"Rank {rank} is starting training for {test_subject} and validation subject {validation_subject}.", 'green'))
        
    subject_loop(rank, config, is_outer, n_epochs, test_subject, validation_subject=validation_subject)
    write_log_to_file(
        config['output_path'], 
        job_name, 
        {'is_finished': True},
        use_lock=True
    )
        
        
def subject_loop(rank, config, is_outer, n_epochs, test_subject, validation_subject=None):
    """ Executes the training loop for the given test subject.

    Args:
        rank (int): The rank of the process.
        config (dict): The training configuration.
        is_outer (bool): If this task is of the outer loop.
        test_subject (str): The task's test subject name.
        validation_subject (str): The task's training/validation subject name. May be None. (Optional)
    """
    print(colored(
        f"\n===========================================================\n" + 
        f"Rank {rank} is starting training for {test_subject} in {config['selected_model_name']}\n"
        , 'magenta'
    ))
    training_vars = TrainingVariables(config, is_outer, test_subject, validation_subject=validation_subject)
    # training_loop(config, testing_subject, files, folds, rotations, indexes, label_position, n_epochs, is_outer, rank=None)
    training_loop.training_loop(
        config=config, 
        testing_subject=test_subject, 
        files=training_vars.files, 
        folds=training_vars.folds, 
        rotations=training_vars.n_folds, 
        indexes=training_vars.indexes, 
        label_position=training_vars.label_position,
        n_epochs=n_epochs,
        is_outer=is_outer,
        rank=rank
    )


def main(config_loc, is_outer):
    """ Runs the training process for each configuration and test subject. Process 0 DOES NOT train. 
    Args:
        config_loc (str): The location of the configuration.
        is_outer (bool): Whether this is of the outer loop. 
    """
       
    # Initialize MPI
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    n_proc = comm.Get_size()
    
    n_gpus = parse_n_gpus()
    b_dummy = parse_dummy_node()
    print("python location", os.path.dirname(sys.executable))
    
    # Initalize TF, set the visible GPU to rank%2 for rank > 0
    if rank == 0:
        tf.config.set_visible_devices([], 'GPU')
    else:
        physical_devices = tf.config.list_physical_devices('GPU')

        print(colored(f'Rank {rank}', 'cyan'))
        print("Num GPUs Available: ", len(physical_devices))
        print("GPUs Available: ", physical_devices)        
       
        index_gpu = -100
       
        if b_dummy:
           
            # Assuming we discard one process
            # Assunming # gpus 2
            # mod number is (# gpus +1)
            # Rank 0 Rank 1  Rank 2
            #        0       1  
            # Rank 3 Rank 4  Rank 5
            # 2      0       1
            # Rank 6 Rank 7  Rank 8 
            # 2      0       1      
            
            # The value 2 will do nothing 
            index_gpu = (rank-1) % (n_gpus+1)
            print("index_gpu =", index_gpu)
        else:
            index_gpu = (rank-1) % n_gpus
        
    # Rank 0 initializes the program and runs the configuration loops
    if rank == 0:  
        
        # Get start time
        start_time_name = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        start_time = time.time()
        start_perf = time.perf_counter()
        
        # Get the configurations
        configs = parse_mpi_training_configs(config_loc)
        n_configs = len(configs)
        next_task_index = 0
        
        # No configs, no run
        if n_configs == 0:
            print(colored("No configurations given.", 'yellow'))
            for subrank in range(1, n_proc):
                comm.send(False, dest=subrank)
            exit(-1)
        
        # Get the tasks for each process
        tasks = split_tasks(configs, is_outer)
        # tasks is a list of tuples
        # where tuple has 4 elements
        # 0: dictionary of configuration of hyperparameters
        # 1: number of epochs
        # 2: test_fold
        # 3: validation_fold
        print("len(tasks(top3)) = ", len(tasks[:3]))
        print("tasks(top3) = ", tasks[:3])

        n_tasks = len(tasks)
        
        # Listen for process messages while running
        exited = []
        # add manually when b_dummy is used 
        # to avoid problems later
        if b_dummy:
            
            # r: rank
            # 2 GPUs
            #       | r0 r1 r2 | r3 r4 r5 | r6 r7 r8 | r9 r10 r11 |
            # index_gpu   0  1 |  2  0  1 |  2  0  1 |  2   0   1 |
            #                     ^          ^          ^           
            # ranks with index_gpu are not used
            # r3, r6, r9 
            
            n_not_used_ranks = n_proc/(n_gpus+1) - 1
            
            exited.extend([(n_gpus+1)*i for i in range(1, n_not_used_ranks+1)])
            
        print("exited =", exited)

        while True:
            # it received rank from other processes
            subrank = comm.recv(source=MPI.ANY_SOURCE)
            
            # Send task if the process is ready
            if tasks:
                print(colored(f"Rank 0 is sending rank {subrank} its task {len(tasks)}/{n_tasks}.", 'green'))
                comm.send(tasks.pop(), dest=subrank)
                next_task_index += 1
                    
            # If no task remains, terminate process
            else:
                print(colored(f"Rank 0 is terminating rank {subrank}, no tasks to give.", 'red'))
                comm.send(False, dest=subrank)
                exited += [subrank]
                
                # Check if any processes are left, end this process if so
                if all(subrank in exited for subrank in range(1, n_proc)):
                    
                    # Get end time and print
                    print(colored(f"Rank 0 is printing the processing time.", 'red'))
                    elapsed_time = time.perf_counter() - start_perf

                    if not os.path.exists("../results/training_timings"):
                        os.makedirs("../results/training_timings")
                    outfile = f'_TIME_MPI_OUTER_{start_time_name}.txt' if is_outer else f'_TIME_MPI_INNER_{start_time_name}.txt'
                    with open(os.path.join("../results/training_timings", outfile), 'w') as fp:
                        fp.write(f"{elapsed_time}")
                    print(colored(f'Rank {rank} terminated. All other processes are finished.', 'yellow'))
                    break
            
    # The other ranks will listen for rank 0's messages and run the training loop
    else: 
        
        # Listen for the first task
        print("n_gpus:", n_gpus)
        print(f"rank: {rank}, index_gpu: {index_gpu}")
        print("b_dummy:", b_dummy)
        
        if not b_dummy or ( b_dummy and index_gpu != n_gpus):

            print(f"physical_devices[{index_gpu}]=", physical_devices[index_gpu])
            tf.config.set_visible_devices(physical_devices[index_gpu], 'GPU')
            tf.config.experimental.set_memory_growth(physical_devices[index_gpu], True)

            comm.send(rank, dest=0)
        
            print(colored(f'Rank {rank} is listening for process 0.', 'cyan'))
            task = comm.recv(source=0)
            
            # While there are tasks to run, train
            while task:
                        
                # Training loop
                config, n_epochs, test_subject, validation_subject = task
                print(colored(f"rank {rank}: test {test_subject}, validation {validation_subject}", 'cyan'))         
                
                run_training(rank, config, n_epochs, test_subject, validation_subject, is_outer)
                comm.send(rank, dest=0)
                task = comm.recv(source=0)
                
            # Nothing more to run.
            print(colored(f'Rank {rank} terminated. All jobs finished for this process.', 'yellow'))
            