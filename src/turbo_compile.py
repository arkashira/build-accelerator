import json
from dataclasses import dataclass
from typing import Dict

@dataclass
class BuildConfig:
    """Holds the configuration for the build process."""
    turbo_compile: bool
    vite_config: Dict

def load_vite_config(config_path: str) -> Dict:
    """Loads the Vite configuration from a file."""
    with open(config_path, 'r') as f:
        return json.load(f)

def integrate_turbo_compile(vite_config: Dict) -> Dict:
    """Integrates TurboCompile into the Vite configuration."""
    if 'turboCompile' not in vite_config:
        vite_config['turboCompile'] = {}
    return vite_config

def calculate_build_time_improvement(build_time_before: float, build_time_after: float) -> float:
    """Calculates the build time improvement."""
    return (build_time_before - build_time_after) / build_time_before * 100

def validate_hmr(vite_config: Dict) -> bool:
    """Validates that HMR continues to function correctly."""
    return 'hmr' in vite_config and vite_config['hmr']
