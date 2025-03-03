
class InstructionBase:
    def __init__(self, instruction : str, component_name : str, repo_folder : str):
        self.instruction = instruction
        self.component_name = component_name
        self.repo_folder = repo_folder