from Menu.menu_manager_base import MenuManagerBase
from SpringCloudConfig.script_configurations import ScriptConfigurations
from rich.console import Console
from rich.prompt import Prompt
from abc import ABC, abstractmethod

class MenuManager(MenuManagerBase, ABC):
    component = "git-menu-manager"
    
    def __init__(self, console : Console, config: ScriptConfigurations):
        super().__init__(console, config, MenuManager.component)
        
        self.wants_automatically_create_repository : bool = False
        self.wants_automatic_repository_clone : bool = False
        self.git_profile_name : str = None
        pass
        
    @abstractmethod
    def get_instructions(self, project_name : str):
        pass
        
    @abstractmethod
    def display_menu(self):
        pass
    
    def ask_for_git_profile_name(self):
        git_profile_name = None
        profiles_names = [profile.name for profile in self.config.git_configs.profiles]
        
        while git_profile_name not in profiles_names:
            self.console.print(f"\n[bold cornflower_blue]Git Profiles:[/] [white]{profiles_names}[/]")
        
            git_profile_name = Prompt.ask("[bold light_sky_blue1]Git Profile Name[/]") 
            if git_profile_name not in profiles_names:
                self.console.print(f"\n[bold red]Git Profile Not Found![/]")
                
        self.git_profile_name = git_profile_name
        self.console.print(f"\n[bold cornflower_blue]Git Profile Name:[/] [white]{self.git_profile_name}[/]")
        return