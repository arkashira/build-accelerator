import pytest
import json
from turbo_compile import BuildConfig, load_vite_config, integrate_turbo_compile, calculate_build_time_improvement, validate_hmr

def test_load_vite_config():
    """Tests loading the Vite configuration from a file."""
    config_path = 'vite.config.json'
    with open(config_path, 'w') as f:
        json.dump({'build': {}}, f)
    config = load_vite_config(config_path)
    assert config == {'build': {}}

def test_integrate_turbo_compile():
    """Tests integrating TurboCompile into the Vite configuration."""
    vite_config = {'build': {}}
    integrated_config = integrate_turbo_compile(vite_config)
    assert 'turboCompile' in integrated_config

def test_calculate_build_time_improvement():
    """Tests calculating the build time improvement."""
    build_time_before = 100
    build_time_after = 50
    improvement = calculate_build_time_improvement(build_time_before, build_time_after)
    assert improvement == 50

def test_validate_hmr():
    """Tests validating that HMR continues to function correctly."""
    vite_config = {'hmr': True}
    is_hmr_valid = validate_hmr(vite_config)
    assert is_hmr_valid

def test_validate_hmr_false():
    """Tests validating that HMR continues to function correctly when it's not enabled."""
    vite_config = {'hmr': False}
    is_hmr_valid = validate_hmr(vite_config)
    assert not is_hmr_valid
