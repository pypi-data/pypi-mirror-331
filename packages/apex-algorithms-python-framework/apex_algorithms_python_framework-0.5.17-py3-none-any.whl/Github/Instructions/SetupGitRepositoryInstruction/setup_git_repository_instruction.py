from Instruction.instruction_base import InstructionBase

class SetupGitRepositoryInstruction(InstructionBase):
    instruction = "setup-git-repository-instruction"
    
    def __init__(self, component_name: str, repo_folder : str):
        super().__init__(SetupGitRepositoryInstruction.instruction, component_name, repo_folder)