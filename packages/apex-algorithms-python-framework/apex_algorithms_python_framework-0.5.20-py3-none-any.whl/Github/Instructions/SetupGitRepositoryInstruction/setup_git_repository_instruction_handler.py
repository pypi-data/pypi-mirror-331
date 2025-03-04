from Instructions.SetupGitRepositoryInstruction.setup_git_repository_instruction import SetupGitRepositoryInstruction
from Instruction.instruction_handler_base import InstructionHandlerBase
from SpringCloudConfig.script_configurations import ScriptConfigurations
from Github.git_client import GitHubClient

class SetupGitRepositoryInstructionHandler(InstructionHandlerBase):
    def __init__(self, configs : ScriptConfigurations, instruction : SetupGitRepositoryInstruction):
        super().__init__(instruction.repo_folder, configs)
        self.instruction = instruction
        self.github_client = GitHubClient(self.configs.git_configs)
        pass

    def handle(self):
        self.github_client.create_repository(self.instruction.component_name)
        pass