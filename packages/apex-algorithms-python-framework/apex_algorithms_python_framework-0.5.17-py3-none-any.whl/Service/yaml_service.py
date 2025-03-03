import os
import yaml

class YamlFileService:
    def load_yaml_file(self, folder_path, file_name):
        file_path = os.path.join(folder_path, file_name)
        if not os.path.exists(file_path):
            print(f"File {file_path} does not exist. Initializing empty data.")
            return {}

        try:
            with open(file_path, 'r') as file:
                data = yaml.safe_load(file)
                return data if data is not None else {}
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return {}
        
    def save_yaml_file(self, folder_path, file_name, data):
        file_path = os.path.join(folder_path, file_name)
        try:
            with open(file_path, 'w') as file:
                yaml.dump(data, file, default_flow_style=False)
                print(f"Successfully saved data to {file_path}")
        except Exception as e:
            print(f"Error writing to file {file_path}: {e}")