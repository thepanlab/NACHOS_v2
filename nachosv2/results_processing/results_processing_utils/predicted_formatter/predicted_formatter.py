from termcolor import colored
from src.file_processing import path_getter
import pandas as pd
import argparse
import json


def read_json():
    """ Reads in the JSON config file """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-j', '--json', '--load_json',
        help='Load settings from a JSON file.',
        required=False,
        default='./util/predicted_formatter/predicted_formatter_config.json'
    )
    args = parser.parse_args()
    with open(args.json) as config_file:
        return json.load(config_file)


def translate_file(file_path):
    """ Reads and translates a data-file """
    # Get the data in the CSV file
    data = pd.read_csv(file_path, header=None)

    # Loop through all the rows, note the largest probability-value's index
    formatted_data = []
    for i, values in data.iterrows():
        values = [v for v in values]
        index = values.index(max(values))
        formatted_data.append(index)

    # Return a list of max-indexes
    return formatted_data


def write_file(file_path, formatted_data):
    """ Writes the formatted data out to CSV """
    # Append "_index" to the input file name
    new_file_path = file_path[:len(file_path) - 4] + '_index.csv'

    # Open file and write the data to it
    with open(new_file_path, 'w') as file:
        for item in formatted_data:
            file.write(f"{item}\n")


def main(data_path=None, is_outer=None):
    """ The Main Program """
    # Read the JSON file's arguments
    if data_path is None:
        config = read_json()
        data_path = config["data_path"]
        is_outer = config['is_outer']

    # Get a list of all files to translate
    file_paths = path_getter.get_subfolder_files(data_path, "prediction", isIndex=False, isOuter=is_outer)
    
    # Translate each file
    for model in file_paths:
        for test_subject in file_paths[model]:
            for file_path in file_paths[model][test_subject]:
                # The translation
                translated_data = translate_file(file_path)

                # Write it to file
                write_file(file_path, translated_data)
    print(colored("Formatting is finished.", "green"))


if __name__ == "__main__":
    """ Executes the code """
    main()
