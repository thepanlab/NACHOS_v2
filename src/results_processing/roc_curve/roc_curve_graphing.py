from . import roc_curve
from src.file_processing import path_getter
from src.results_processing.results_processing_utils.get_config import parse_json


def run_program(args):
    """
    Run the program for each item.
    """
    
    # Gets the needed input paths, as well as the proper file names for output
    pred_paths, true_paths = find_directories(args["data_path"])
    json = {
        label: args[label] for label in (
            'line_width', 'label_types', 'line_colors',
            'font_family', 'label_font_size', 'title_font_size',
            'save_resolution', 'save_format', 'output_path'
        )
    }

    # For each item, run the program
    for model in pred_paths:
        for subject in pred_paths[model]:
            for item in range(len(pred_paths[model][subject])):
                # Get the program's arguments
                json = generate_json(pred_paths, true_paths, model, subject, item, json)
                roc_curve.main(json)



def find_directories(data_path):
    """
    Finds the directories for every input needed to make graphs.
    """
    
    # Gets the paths of every prediction and true CSV, as well as the fold-names
    true_paths = path_getter.get_subfolder_files(data_path, "true_label", isIndex=True, getValidation=True)
    pred_paths = path_getter.get_subfolder_files(data_path, "prediction", isIndex=False, getValidation=True)
    
    return pred_paths, true_paths



def generate_json(pred_paths, true_paths, model, subject, item, json):
    """
    Creates a dictionary of would-be JSON arguments
    """
    
    # The current expected suffix format for true labels
    true_label_suffix = " true label index.csv"

    # Create dictionary for every item
    json["pred_path"] = pred_paths[model][subject][item]
    json["true_path"] = true_paths[model][subject][item]
    json["output_file_prefix"] = true_paths[model][subject][item].split('/')[-1].replace(true_label_suffix, "")
    
    return json



def main():
    """
    The Main Program.
    """
    
    # Gets program configuration and run using its contents
    config = parse_json('./results_processing/roc_curve/roc_curve_graphing_config.json')
    run_program(config)



if __name__ == "__main__":
    """
    Executes Program.
    """
    
    main()
