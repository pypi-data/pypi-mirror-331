from Github.Configurations.git_configurations import GitConfigurations

class ScriptConfigurations:
    def __init__(self, git_configs : GitConfigurations):
        self.git_configs : GitConfigurations = git_configs 
        pass
    
    @staticmethod
    def decode_config(data: dict) -> 'ScriptConfigurations':
        git_configs = GitConfigurations.from_json(data.get("git_configs"))
        
        return ScriptConfigurations(git_configs)