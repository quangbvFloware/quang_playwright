import pathlib

# Project directory
ROOT_DIR = pathlib.Path(__file__).parent.parent.parent

CONFIG_DIR = ROOT_DIR / "config"

RESOURCES_DIR = ROOT_DIR / "resources"
RESOURCES_CAPABILITIES_DIR = RESOURCES_DIR / "capabilities"
RESOURCES_YAML_DIR = RESOURCES_DIR / "yaml"
RESOURCES_PEM_DIR = RESOURCES_DIR / "pem"
RESOURCES_IMAGES_DIR = RESOURCES_DIR / "images"

# Project structure
PROJECT_NAME = str(ROOT_DIR).split("/")[-1]
PYTHON_CONFIG_LOG = "pythonConfig"
