# **Training**

<ul> 
    This module contains many various scripts that help process data from the data and training results. This can help to determine various performance metrics of the model. It does not directly affect the training process whatsoever. 
    All of these submodules can be run manually, or by using the provided Makefile. View the makefile or its documentation for more details.

</ul> <hr> <br>


+ ## ***MPI Init***
    <ul> 
        This module, located with the MPI distributed modules, creates a command based on your given configuration input. For example, you can provide multiple IP addresses (as strings) in order to execute a remote, distributed training job. This program will take those addresses and create a command line arguement that will run the training program to your needs. 
    </ul> <br>
    
    * ***You need to have SSH keys established in order to use any IP addresses!*** 
      * You can find a helpful guide on this topic here: https://medium.com/@jakewies/accessing-remote-machines-using-ssh-55a0fdf5e9d8

    ***Example:*** 
    >python3 -m -m training.training_multiprocessing.mpi_init --file myfile.json 

    <details>

    * ***Input:*** The configuration file. *(Optional)*
    * ***Output:*** A command that is printed to the console.
    * ***example_config.json:***
        ```json
        {
            "cuda_devices": [0, 1],
            "gpu_addrs": ["10.10.10", "11.11.11"],
            "n_processes": 2,
            "is_outer": true
        }
        ```

        * ***cuda_devices:*** A list of GPU CUDA devices visible to the program. Should be a list of ints.
        * ***gpu_addrs:*** A list of IP addresses as strings. If the list is empty, *n_processes* is used instead.
        * ***n_processes:*** The number of worker processes to run. The program adds one extra master process to this number. Only used if no IP addresses are given.
        * ***is_outer:*** If the program should be run as the inner or outer loop.
  
    </details> </hr> <br> <br>
<hr>


+ ## ***Inner Loop***
    <ul> 
        This runs the inner loop of the k-fold cross validation process. This can be called using the Makefile and manually within the command line from within the scripts folder. Do to its modularization implementation, it will most likely break when called outside of this location. The default configuration folder is "training/training_config_files".
    </ul>

    ***Example:*** 
    >python3 -m training.training_sequential.loop_inner.training_loop_inner --file myfile.json ***OR*** --folder /myfolder
    
    <br>
    
    >mpirun -n 3 python3 -m training.training_multiprocessing.loop_inner.multiprocessed_training_loop_inner --file myfile.json ***OR*** --folder /myfolder

    <details>

    * ***Input:*** The configuration file or folder. *(Optional)*
    * ***Output:*** Trained models, prediction results, and other various metrics.
    * ***example_model_config.json:***
        ```json
        {
            "hyperparameters": {
                "batch_size": 24,
                "channels": 1,
                "cropping_position": [40, 10],
                "decay": 0.01,
                "do_cropping": true,
                "epochs": 6,
                "learning_rate": 0.01,
                "momentum": 0.9,
                "bool_nesterov": true,
                "patience": 10
            },

            "data_input_directory": "[path]/ep_intensity",
            "output_path": "[path]/training",
            "job_name": "InceptionV3_test_1",
            
            "k_epoch_checkpoint_frequency": 2,

            "shuffle_the_images": true,
            "shuffle_the_folds": false,
            "seed": 9,

            "class_names": ["fat", "ligament", "flavum", "epidural space", "spinal cord"],
            "selected_model_name": "InceptionV3",
            "subject_list": ["e1", "e2", "e3", "e4", "e5", "e6"],
            "test_subjects": ["e1", "e2"],
            "validation_subjects": ["e3", "e4"],

            "target_height": 241,
            "target_width": 181
        }

        ```
        * ***hyperparameters:*** These are the parameters needed for the training step.
          * ***batch_size:*** This will divide the input datasets into n training batches.
          * ***channels:*** The image channels in which the image will be processed on.
          * ***cropping_position:*** The position at which to crop the image.
          * ***decay:*** Decays the learning rate over time.
          * ***do_cropping:*** Whether to crop the input images.
          * ***epochs:*** The number of training epochs.
          * ***learning_rate:*** The learning speed.
          * ***momentum:*** Helps the learning rate's speed by speeding up the gradient descent search.
          * ***"bool_nesterov"***: Whether to apply Nesterov momentum
          * ***patience:*** How long to wait for improvement within early stopping.
        * ***data_input_directory:*** Where the input images are located. No specific structure is needed.
        * ***output_path:*** Where to write the results to.
        * ***job_name:*** The name of your job. Will mainly affect checkpointing file names.
        * ***k_epoch_checkpoint_frequency:*** How many epochs should checkpoints be saved.
        * ***shuffle_the_images:*** Whether to randomly shuffle the image paths.
        * ***shuffle_the_folds:*** Whether to randomly shuffle the training folds.
        * ***seed:*** The random seed.
        * ***class_names:*** The names of the image classes or labels.
        * ***selected_model_name:*** The model type to create. The choices are: resnet_50, resnet_VGG16, InceptionV3, ResNet50V2, and Xception.
        * ***subject_list:*** The list of all training subjects found in the data. 
        * ***test_subjects:*** The list of the particular testing subjects.
        * ***validation_subjects:*** The list of the particular validation subjects.
        * ***target_height:*** The target image height.
        * ***target_width:*** The target image width.
  
    </details> </hr> <br> <br>
<hr>


+ ## ***Outer Loop***
    <ul> 
        This runs the outer loop of the k-fold cross validation process. The only difference between running the inner and outer loop is its purpose, configuration, and names. They share most of their logic.
    </ul>

    ***Example:*** 
    >python3 -m training.training_sequential.loop_outer.training_outer_loop --file myfile.json ***OR*** --folder /myfolder
    
    <br>
    
    >mpirun -n 3 python3 -m training.training_multiprocessing.loop_outer.multiprocessed_training_outer_loop --file myfile.json ***OR*** --folder /myfolder

    <details>

    * ***Input:*** The configuration file or folder. *(Optional)*
    * ***Output:*** Trained models, prediction results, and other various metrics.
    * ***example_model_config.json:***
        ```json
        {
            "hyperparameters": {
                "batch_size": 24,
                "channels": 1,
                "cropping_position": [40, 10],
                "decay": 0.01,
                "do_cropping": true,
                "epochs": [4,6],
                "learning_rate": 0.01,
                "momentum": 0.9
            },

            "data_input_directory": "[path]/ep_intensity",
            "output_path": "[path]/training",
            "job_name": "InceptionV3_test_1",
            
            "k_epoch_checkpoint_frequency": 2,

            "shuffle_the_images": true,
            "shuffle_the_folds": false,
            "seed": 9,

            "class_names": ["fat", "ligament", "flavum", "epidural space", "spinal cord"],
            "selected_model_name": "InceptionV3",
            "subject_list": ["e1", "e2", "e3", "e4", "e5", "e6"],
            "test_subjects": ["e1", "e2"],

            "target_height": 241,
            "target_width": 181
        }

        ```
        * ***hyperparameters:*** These are the parameters needed for the training step.
          * ***batch_size:*** This will divide the input datasets into n training batches.
          * ***channels:*** The image channels in which the image will be processed on.
          * ***cropping_position:*** The position at which to crop the image.
          * ***decay:*** Decays the learning rate over time.
          * ***do_cropping:*** Whether to crop the input images.
          * ***epochs:*** The number of training epochs. You can specify a single value or a list of values according to each subject test.
          * ***learning_rate:*** The learning speed.
          * ***momentum:*** Helps the learning rate's speed by speeding up the gradient descent search.
        * ***data_input_directory:*** Where the input images are located. No specific structure is needed.
        * ***output_path:*** Where to write the results to.
        * ***job_name:*** The name of your job. Will mainly affect checkpointing file names.
        * ***k_epoch_checkpoint_frequency:*** How many epochs should checkpoints be saved.
        * ***shuffle_the_images:*** Whether to randomly shuffle the image paths.
        * ***shuffle_the_folds:*** Whether to randomly shuffle the training folds.
        * ***seed:*** The random seed.
        * ***class_names:*** The names of the image classes or labels.
        * ***selected_model_name:*** The model type to create. The choices are: resnet_50, resnet_VGG16, InceptionV3, ResNet50V2, and Xception.
        * ***subject_list:*** The list of all training subjects found in the data. 
        * ***test_subjects:*** The list of the particular testing subjects.
        * ***target_height:*** The target image height.
        * ***target_width:*** The target image width.
  
    </details> </hr> <br> <br>
<hr>


+ ## ***Checkpoint and Logging Modules***
    <ul> 
        This module contains various scripts that aid in checkpointing the model and continuing from previous training data.
    </ul> <br>
    <details>
    <summary>Show/Hide files</summary>

    1) ### ***checkpointer.py:***
        <ul> 
            This has the ability to write and load checkpoints. This allows the model to continue off from a previous training session. The checkpoints are saved in the same format as regular models, in h5 form.
        </ul>

    2) ### ***logger.py:***
        <ul> 
            This allows the training loop to log the most recent training state. This will allow the training loop to carry off from a cancelled job. Things like the testing subject, validation subject, and various training fold properties are stored using the functions within. It has the ability to read, write, and delete log files.
        </ul>

    </details> <br> <br>
<hr>



+ ## ***Training Modules***
    <ul> 
        This module contains most of the main training loop functions.
    </ul> <br>
    <details>
    <summary>Show/Hide files</summary>

    1) ### ***Data Processing: fold_generator.py:***
        <ul> 
            This will generate a list of training folds and the number of rotations for a given subject.
        </ul>

    2) ### ***Data Processing: index_getter.py:***
        <ul> 
            This will generate ordered lists for the labels, label-indexes, and subjects of the input images from their names.
        </ul>

    3) ### ***Data Processing: training_preparation.py:***
        <ul> 
            This is where basic training loop data is generated. Things like files, indexes, and folds are created here.
        </ul>

    4) ### ***Image Processing: image_getter.py:***
        <ul> 
            This retrieves every image from the given input file path.
        </ul>

    5) ### ***Image Processing: image_parser.py:***
        <ul> 
            This parses the input images as tensors.
        </ul>

    6) ### ***Image Processing: image_reader.py:***
        <ul> 
            A (currently unused) bit of code. Meant to implememt custom image reading classes.
        </ul>

    7) ### ***Model Processing:model_creator.py:***
        <ul> 
            This generates a model object, based on the given configuration.
        </ul>

    8) ### ***Output Processing: console_printing.py:***
        <ul> 
            This contains a basic printing function. It may be removed later.
        </ul>

    9) ### ***Output Processing: result_outputter.py:***
        <ul> 
            This outputs various training metrics after the process is done within each fold.
        </ul>

    10) ### ***Training Processing: training_fold.py:***
        <ul> 
            This is the main training function. Here is where the model is trained and its data is saved within a log and checkpoint.
        </ul>

    11) ### ***Training Processing: ttraining_loop.py:***
        <ul> 
            This module runs all of the training folds for a particular subject.
        </ul>

    </details> <br> <br>
<hr>


