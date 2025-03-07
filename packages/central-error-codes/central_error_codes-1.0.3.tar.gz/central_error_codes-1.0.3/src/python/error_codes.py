import json
import os

class ErrorCode:
    errors = {}

    @staticmethod
    def initialize():
        # Get the directory path where this file is located
        base_dir = os.path.dirname(__file__)

        # Path to the 'errors' folder that is in the root directory of the package
        errors_folder = os.path.join(base_dir, '../../errors')

        # Load the primary 'error-code.json' file that lists other error files
        file_path = os.path.join(errors_folder, 'error-code.json')
        with open(file_path, 'r') as file:
            error_paths = json.load(file)

        # Load the other error JSON files from the paths listed in 'error-code.json'
        for error_key, error_file in error_paths.items():
            full_path = os.path.join(errors_folder, error_file)  # Full path for each error file
            with open(full_path, 'r') as err_file:
                ErrorCode.errors[error_key] = json.load(err_file)  # Load into the dictionary

    @staticmethod
    def get_error():
        return ErrorCode.errors

    @staticmethod
    def get_generic_error():
        return ErrorCode.errors.get("GENERIC_ERROR")

    @staticmethod
    def get_llm_gateway_error():
        return ErrorCode.errors.get("LLM_GW_ERROR")
