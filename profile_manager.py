# profile_manager.py
import os
import random
from pathlib import Path

class ProfileManager:
    def __init__(self, base_profile_dir=None):
        if base_profile_dir is None:
            # Default to project directory
            project_dir = Path(__file__).parent
            base_profile_dir = project_dir / "chrome_profiles"
        
        self.base_dir = Path(base_profile_dir)
        self.profiles = []
        
        # Create profiles if they don't exist
        self._setup_profiles()
    
    def _setup_profiles(self):
        """Create profile directories"""
        for i in range(1, 4):  # Create 3 profiles
            profile_path = self.base_dir / f"profile_{i}"
            profile_path.mkdir(parents=True, exist_ok=True)
            self.profiles.append(str(profile_path))
        
        #print(f"✅ {len(self.profiles)} profiles ready at {self.base_dir}")
    
    def get_random_profile(self):
        """Get a random profile path"""
        return random.choice(self.profiles)
    
    def get_profile(self, index=0):
        """Get specific profile by index (0-2)"""
        return self.profiles[index % len(self.profiles)]
