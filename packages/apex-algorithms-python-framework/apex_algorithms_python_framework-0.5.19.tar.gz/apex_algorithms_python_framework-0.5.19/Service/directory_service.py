import os

class DirectoryService:
    def __init__(self):
        """
        Initialize the DirectoryService.
        """
        pass

    def get_all_files(self, directory_path, file_extension=None):
        """
        Retrieve all files from the specified directory. Optionally filter by file extension.
        :param directory_path: Path to the directory to be managed.
        :param file_extension: File extension to filter by (e.g., '.txt'). Default is None (no filtering).
        :return: List of file names in the directory.
        """
        if not os.path.isdir(directory_path):
            raise ValueError(f"The provided path '{directory_path}' is not a valid directory.")
        
        try:
            files = []
            for item in os.listdir(directory_path):
                item_path = os.path.join(directory_path, item)
                if os.path.isfile(item_path):
                    if file_extension:
                        if item.endswith(file_extension):
                            files.append(item)
                    else:
                        files.append(item)
            return files
        except Exception as e:
            raise RuntimeError(f"An error occurred while retrieving files: {e}")