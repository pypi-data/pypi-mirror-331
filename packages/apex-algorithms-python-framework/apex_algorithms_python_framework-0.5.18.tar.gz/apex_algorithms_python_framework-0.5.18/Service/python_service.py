import os

class PythonService:
    def create_init_file(self, folder_path):
        init_file_path = os.path.join(folder_path, '__init__.py')
        
        with open(init_file_path, 'w') as init_file:
            init_file.write("")
        
        return init_file_path