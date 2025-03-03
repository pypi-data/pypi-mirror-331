import os
from abc import ABC, abstractmethod

class InstructionHandlerBase(ABC):
    def __init__(self, repository_folder : str, configs):
        self.configs = configs
        self.repository_folder : str = repository_folder
        
    @abstractmethod
    def handle(self):
        pass
    
    def get_repository_path(self, repository_name : str) -> str:
        return os.path.join(self.repository_folder, repository_name)
    
    def create_folder(self, base_folder, folder_name):
        folder_path = os.path.join(base_folder, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        
        return folder_path