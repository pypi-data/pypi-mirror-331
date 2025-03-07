import json
import os

class ErrorCode:
    errors = {}

    @staticmethod
    def initialize():
        file_path = os.path.join(os.path.dirname(__file__), '../error-code.json')  # Path to error-code.json
        with open(file_path, 'r') as file:
            error_paths = json.load(file)
        
        for error_key, error_file in error_paths.items():
            full_path = os.path.join(os.path.dirname(__file__), error_file)  # Construct full path for each error file
            with open(full_path, 'r') as err_file:
                ErrorCode.errors[error_key] = json.load(err_file)  # Load the error details into the errors dictionary

    @staticmethod
    def get_error():
        return ErrorCode.errors

    @staticmethod
    def get_generic_error():
        return ErrorCode.errors.get("GENERIC_ERROR")

    @staticmethod
    def get_llm_gateway_error():
        return ErrorCode.errors.get("LLM_GW_ERROR")

# Initialize the error codes
ErrorCode.initialize()
