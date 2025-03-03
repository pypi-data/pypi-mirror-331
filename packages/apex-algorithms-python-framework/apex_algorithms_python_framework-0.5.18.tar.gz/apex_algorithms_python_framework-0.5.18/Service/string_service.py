class StringService:
    def transform_to_camel_case(self, input_string: str) -> str:
        words = input_string.split('-')

        return ''.join(word.capitalize() for word in words)
    
    def build_file_name(self, title : str) -> str:
        """
        Constructs a filename from the given title by replacing spaces with underscores
        and appending the .json extension.

        Args:
            title (str): The title to convert into a filename.

        Returns:
            str: The formatted filename.
        """
        formatted_title = title.replace(" ", "_")
        filename = f"{formatted_title}.json"
        return filename