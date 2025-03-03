from typing import List
from Github.Enums.profile_type import ProfileType

class GitProfile:
    def __init__(self, name : str, type : ProfileType):
        self.name = name
        self.type : ProfileType = type
        pass
        
    @staticmethod
    def find_profile_by_name(profiles : List['GitProfile'], name : str):
        for profile in profiles:
            if profile.name == name:
                return profile
            
        raise Exception(f"The git profile with name '{name}' in unknown.")