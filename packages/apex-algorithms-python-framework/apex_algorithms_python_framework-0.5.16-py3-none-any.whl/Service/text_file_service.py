import os
import shutil
import hashlib
import gc

class TextFileService:
    def save_file(self, source_path: str, content: str, file_name: str = None):
        '''
        source_path = folder or file path where the content is stored;
        content = content to be saved in file;
        file_name = in case source_path is a folder, the file name can be specified here;
        '''
        file_path = source_path
        
        if file_name is not None:
            file_path = os.path.join(source_path, file_name)
        
        with open(file_path, "w") as file:
            file.write(content)
            
        return file_path
    
    def delete_file(self, source_path: str, file_name: str = None):
        '''
        source_path = folder or file path where the content is stored;
        file_name = in case source_path is a folder, the file name can be specified here;
        '''
        file_path = source_path
        
        if file_name is not None:
            file_path = os.path.join(source_path, file_name)
        
        if os.path.isfile(file_path):
            os.remove(file_path)
            return True
        else:
            return False
        
    def get_file_content(self, source_path: str, file_name: str = None):
        """
        Reads the content of a file.

        Parameters:
            source_path (str): Folder or file path where the content is stored.
            file_name (str, optional): If source_path is a folder, specify the file name.

        Returns:
            str: Content of the file if it exists, None otherwise.
        """
        file_path = source_path

        if file_name is not None:
            file_path = os.path.join(source_path, file_name)

        try:
            fd = os.open(file_path, os.O_RDONLY | os.O_BINARY)
            
            with open(fd, "r") as file:
                content = file.read()
                file.close()
                return content
        except FileNotFoundError:
            return None
    
    def move_file(self, source_path: str, destination_folder: str, file_name: str = None, new_name: str = None):
        '''
        Moves a file from the source path to the destination folder.
        
        source_path: Path to the file or folder where the file is located.
        destination_folder: Path to the folder where the file should be moved.
        file_name: If source_path is a folder, specify the file name to be moved.
        new_name: New name for the file in the destination folder (optional).
        '''
        file_path = source_path
        
        if file_name is not None:
            file_path = os.path.join(source_path, file_name)
        
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"The file '{file_path}' does not exist.")
        
        if not os.path.isdir(destination_folder):
            raise NotADirectoryError(f"The destination folder '{destination_folder}' does not exist.")
        
        destination_path = os.path.join(destination_folder, new_name if new_name else os.path.basename(file_path))
        
        shutil.move(file_path, destination_path)
        
        return destination_path
    
    def calculate_file_hash(self, file_path : str):
        """Calculate the hash of a file to detect content changes."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            # Read the full content of the file at once
            hash_md5.update(f.read())
            
        hash = hash_md5.hexdigest()
        
        del hash_md5
        gc.collect()
        
        return hash