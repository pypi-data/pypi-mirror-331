from typing import List
from Configurations.git_profile import GitProfile
from Github.Enums.profile_type import ProfileType

class GitConfigurations:
    def __init__(self, repositories_base_path : str, token : str, profiles : List[GitProfile]):
        self.repositories_base_path : str = repositories_base_path
        self.profiles : List[GitProfile] = profiles
        self.token : str = token
        
        self.selected_profile : GitProfile = None
        pass
    
    def set_selected_profile(self, profile_name : str):
        self.selected_profile = GitProfile.find_profile_by_name(self.profiles, profile_name)
        pass

    @staticmethod
    def from_json(json_data: dict):
        repositories_base_path = json_data.get("repositories_base_path")
        token = json_data.get("token")
        
        profiles_data = json_data.get("profile")
        profiles = [GitProfile(profile["name"], ProfileType[profile["type"]]) for profile in profiles_data]
        
        return GitConfigurations(repositories_base_path, token, profiles)