import os
import sys
import clr
import yaml
import logging

class DWSIMEngine:
    """
    Manages the DWSIM .NET lifecycle on macOS with thread-safe initialization.
    Loads system and thermodynamic configuration from config.yaml.
    """
    def __init__(self, config_path="config.yaml"):
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config(config_path)
        
        bundle_path = self.config['system']['bundle_path']
        if not os.path.exists(bundle_path):
            self.logger.error(f"DWSIM bundle path not found: {bundle_path}")
            raise FileNotFoundError(f"DWSIM bundle path not found: {bundle_path}")

        if bundle_path not in sys.path:
            sys.path.append(bundle_path)
        
        self._initialize_assemblies()

    def _load_config(self, path):
        """Loads repository-wide configuration."""
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to load configuration from {path}: {e}")

    def _initialize_assemblies(self):
        """Bridge Python to .NET assemblies using clr."""
        assemblies = [
            "DWSIM.Automation",
            "DWSIM.Interfaces",
            "DWSIM.Thermodynamics",
            "DWSIM.SharedClasses",
            "DWSIM.UnitOperations"
        ]
        
        try:
            for assembly in assemblies:
                clr.AddReference(assembly)
            
            from DWSIM.Automation import Automation3
            self.automation = Automation3()
        except Exception as e:
            self.logger.critical(f"DWSIM .NET bridge initialization failed: {e}")
            raise ImportError(f"DWSIM .NET bridge initialization failed: {e}")

    def create_flowsheet(self):
        """Returns a new IFlowsheet instance for simulation."""
        return self.automation.CreateFlowsheet()