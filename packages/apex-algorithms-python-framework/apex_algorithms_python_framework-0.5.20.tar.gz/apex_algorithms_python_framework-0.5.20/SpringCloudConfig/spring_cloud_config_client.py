import requests
from rich.console import Console
import os

class SpringCloudConfigClient:
    def __init__(self, console: Console, server_url, application_name):
        self.console: Console = console
        self.server_url = server_url
        self.application_name = application_name

    def fetch_config_by_profile(self, profile):
        config_url = f"{self.server_url}/{self.application_name}-{profile}.json"
        try:
            response = requests.get(config_url)
            response.raise_for_status()
            self.console.print(f"[bold green]Successfully fetched configuration for profile:[/] {profile}")
            return response.json()
        except requests.exceptions.RequestException as e:
            self.console.print(f"[bold red]Failed to fetch configuration:[/] {e}")
            raise

    def get_configurations_by_env(self):
        env = os.getenv("environment", "Dev")
        self.console.print(f"[bold blue]Loading configurations for environment:[/] {env}")
        
        try:
            config = self.fetch_config_by_profile(env)
            self.console.print("[bold green]Configurations loaded successfully.[/]")
            return config
        except Exception as e:
            self.console.print(f"[bold red]Error loading configurations:[/] {e}")
            return None
