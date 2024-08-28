from src.results_processing.results_processing_utils.get_configuration_file import parse_json
from termcolor import colored
import subprocess
import socket
import sys
import os


# This exists as a method of creating a command for running some MPI job given some conditions.
# The command can be put manually into the terminal or makefile to run some job.


def main(config=None):
    """ The main program. """
    # Read in the program configuration
    if config is None:
        config = parse_json("./training/training_multiprocessing/mpi_config.json")
        
    # We will create a command line argument
    arg = ""
    
    # If the devices are specified, add them to the beginning
    if config['cuda_devices']:
        devices = ','.join(map(str, config['cuda_devices']))
        print(colored(f"Specified CUDA devices: {devices}.", 'cyan'))
        arg += f"CUDA_VISIBLE_DEVICES={devices} "
    
    # Get the worker (process) addresses, if they exist
    if config['gpu_addrs']:
        print(colored(f"Specified IP addresses: {','.join(config['gpu_addrs'])}", 'cyan'))
        
        # Try to make sure every address is reachable
        for addr in config['gpu_addrs']:
            print(colored(f"\nAttempting to ping {addr}...", 'blue'))
            if os.system("ping -c 1 " + addr) != 0:
                raise Exception(colored(f'Error: Host {addr} could not be reached. Remember to generate SSH keys if you haven\'t. You can find a guide in the training markdown documentation.', 'red'))
            
        # One process is added to the host machine for the master (non-training) process
        ip_address = socket.gethostbyname(socket.gethostname())
        addrs = [ip_address] + config['gpu_addrs']
        arg += f"mpirun -H {','.join(addrs)} "
        
    # If not, just run n processes on the same machine
    else:
        print(colored(f"Specified processes: {config['n_processes']}.", 'cyan'))
        
        # One process is added to the host machine for the master (non-training) process
        arg += f"mpirun -n {int(config['n_processes']) + 1} " 
        
    # Add the final location of the program
    if config['is_outer']:
        arg += "python3 -m training.training_multiprocessing.loop_outer.multiprocessed_training_outer_loop"
    else:
        arg += "python3 -m training.training_multiprocessing.loop_inner.multiprocessed_training_inner_loop"
    print(colored(f"Use this argument:", 'green'))
    print(colored(f"\t{arg}", 'yellow'))
    print(colored(f"Note: An extra host CPU process is added automatically to what is given.", 'cyan'))
    

if __name__ == '__main__':
    """ Executes the main function """
    main()
