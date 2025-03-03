import os
import subprocess
import requests
from Configurations.git_configurations import GitConfigurations
from Configurations.git_profile import GitProfile
from Github.Enums.profile_type import ProfileType

class GitHubClient:
    def __init__(self, config : GitConfigurations):
        self.config : GitConfigurations = config
        self.base_url : str = "https://api.github.com"
        self.repo_sufix : str = "/repos"
        self.user_sufix : str = "/user"
        self.org_sufix : str = f"/orgs"
        self.clone_base_url : str = "https://github.com/"
        pass

    def get_repository_url(self):        
        if (self.config.selected_profile.type == ProfileType.USER):
            return self.base_url + self.user_sufix + self.repo_sufix
        
        return self.base_url + self.org_sufix + f"/{self.config.selected_profile.name}" +  self.repo_sufix
    
    def get_clone_url(self, repository_name : str):        
        return self.clone_base_url + f"/{self.config.selected_profile.name}/{repository_name}"

    def create_repository(self, repository_name : str , is_private : bool = True, license_template : str = 'mit'):
        url = self.get_repository_url()
        
        headers = {
            "Authorization": f"token {self.config.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        data = {
            "name": repository_name,
            "auto_init": True,
            "private": is_private,
            "license_template": license_template
        }
        
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 201:
            print(f"Repository '{repository_name}' created successfully!")
        else:
            print(f"Failed to create repository '{repository_name}'.")
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")

        pass
    
    def clone_repository(self, repository_name : str):
        clone_url = self.get_clone_url(repository_name)

        target_dir = self.config.repositories_base_path + "/" + repository_name
        
        if os.path.exists(target_dir):
            print(f"The directory '{target_dir}' already exists. Please choose a different directory or remove it to proceed.")
            return False

        print(f"Cloning '{repository_name}' into '{target_dir}'...")
        
        try:
            subprocess.run(['git', 'clone', clone_url, target_dir], check=True)
            print("Repository cloned successfully.")
            return True
        
        except subprocess.CalledProcessError as e:
            print(f"Failed to clone repository: {e}")
            return False
        
    def push_changes(self, component_name: str, commit_message : str):
        component_repository_folder_path = self.config.repositories_base_path + "/" + component_name
        
        os.chdir(component_repository_folder_path)
        subprocess.run(['git', 'init'])
        subprocess.run(['git', 'add', '.'])
        subprocess.run(['git', 'commit', '-m', commit_message])
        subprocess.run(['git', 'push'])
        pass