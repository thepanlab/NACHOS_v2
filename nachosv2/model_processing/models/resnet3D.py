import torch.nn as nn
from torchvision.models.video import r3d_18

from nachosv2.model_processing.custom_softmax import custom_softmax


class ResNet3D(nn.Module):
    def __init__(self, configuration_file):
        super(ResNet3D, self).__init__()
        """
        Creates and prepares a model for training.
            
        Args:
            model_type (str): Name of the type of model to create.
            class_names (list of str): List of all classes. Use to know how many there are.
            
        Returns:
            model (nn.Module): The prepared torch.nn model.
        """

        # Sets the model definition
        self.model_type = configuration_file["architecture_name"]

        # Gets the model base
        self.base_model = r3d_18(pretrained = True)

        
        # Changes the last layer to have the right amount of classes
        num_ftrs = self.base_model.fc.in_features
        self.base_model.fc = nn.Linear(num_ftrs, len(configuration_file["class_names"]))
            
    

    def forward(self, x):
        '''
        Defines the forward function of the model.
        
        Args:
            x (PyTorch Tensor): The PyTorch tensor containing the model's input data.
        
        Returns:
            outputs (PyTorch Tensor): The PyTorch tensor containing the model's output data.
        '''
        
        # Passes the data through the model
        x = self.base_model(x)
        
        
        # Uses logits if available
        if hasattr(x, "logits"):
            logits = x.logits
        
        # Otherwise uses x directly
        else:
            logits = x  
        
        
        # Applies the custom softmax function to have probabilities
        outputs = custom_softmax(logits)
        
        return outputs
