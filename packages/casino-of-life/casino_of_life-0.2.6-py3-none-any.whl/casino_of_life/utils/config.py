"""
Configuration settings for Casino of Life
"""
import os
from pathlib import Path

# Base configuration - all paths configurable through environment variables
PACKAGE_ROOT = Path(os.getenv('CASINO_OF_LIFE_ROOT', str(Path(__file__).parent.parent)))

# Data directories
DATA_DIR = Path(os.getenv('CASINO_OF_LIFE_DATA_DIR', str(PACKAGE_ROOT / "data")))
STABLE_DATA_DIR = Path(os.getenv('CASINO_OF_LIFE_STABLE_DIR', str(DATA_DIR / "stable")))
CONTRIB_DATA_DIR = Path(os.getenv('CASINO_OF_LIFE_CONTRIB_DIR', str(DATA_DIR / "contrib")))
EXPERIMENTAL_DATA_DIR = Path(os.getenv('CASINO_OF_LIFE_EXPERIMENTAL_DIR', str(DATA_DIR / "experimental")))

# Model, state, and scenario directories
MODELS_DIR = Path(os.getenv('CASINO_OF_LIFE_MODELS_DIR', str(PACKAGE_ROOT / "models")))
STATES_DIR = Path(os.getenv('CASINO_OF_LIFE_STATES_DIR', str(PACKAGE_ROOT / "states")))
SCENARIOS_DIR = Path(os.getenv('CASINO_OF_LIFE_SCENARIOS_DIR', str(PACKAGE_ROOT / "scenarios")))

# Game configuration
DEFAULT_GAME = "MortalKombatII-Genesis"
DEFAULT_STATE = "Level1.LiuKangVsJax.2P.state"

# API configuration
API_HOST = os.getenv("CASINO_OF_LIFE_API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("CASINO_OF_LIFE_API_PORT", "8001"))
CHAT_WS_URL = os.getenv("CASINO_OF_LIFE_WS_URL", f"ws://localhost:{API_PORT}/ws")

# Training defaults
DEFAULT_TRAINING_PARAMS = {
    "learning_rate": 3e-4,
    "batch_size": 32,
    "timesteps": 100000,
    "n_steps": 2048,
    "gamma": 0.99,
    "policy": "MlpPolicy"
}

__all__ = [
    'DATA_DIR',
    'STABLE_DATA_DIR',
    'CONTRIB_DATA_DIR',
    'EXPERIMENTAL_DATA_DIR',
    'MODELS_DIR',
    'STATES_DIR',
    'SCENARIOS_DIR',
    'DEFAULT_GAME',
    'DEFAULT_STATE',
    'API_HOST',
    'API_PORT',
    'CHAT_WS_URL',
    'DEFAULT_TRAINING_PARAMS'
]