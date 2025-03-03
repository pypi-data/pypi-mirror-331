from Instruction.instruction_base import InstructionBase
from SpringCloudConfig.script_configurations import ScriptConfigurations
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from typing import List
from abc import ABC, abstractmethod

class MenuManagerBase(ABC):
    def __init__(self, console : Console, config: ScriptConfigurations, header_title : str = "Script"):
        self.instructions : List[InstructionBase] = []
        self.console = console
        self.config = config
        self.header_title = header_title
        pass

    def show_header(self):
        self.console.print(Panel(Text(f"{self.header_title.capitalize()} Information", justify="center", style="bold blue"), border_style="light_slate_blue"))
        self.console.print("[dim]Please enter the following details:[/]")
        pass

    def get_yes_or_no_response(self, message):
        response = None
        
        while response == None:
            response = Prompt.ask(f"[bold light_sky_blue1] {message} (yes/no)[/]").strip().lower()
            
            if response not in {"yes", "no"}:
                self.console.print("[bold red]Invalid input. Please enter 'yes' or 'no'.[/]")
                response = None
                continue

        return response
        
    @abstractmethod
    def get_instructions(self, project_name : str):
        pass
        
    @abstractmethod
    def display_menu(self):
        pass
