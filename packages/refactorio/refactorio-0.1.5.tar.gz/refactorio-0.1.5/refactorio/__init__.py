"""
CLI для управления Ruff, Black и pre-commit.
"""

__version__ = "0.1.0"

from .cli import app
# Импортируем основные классы и функции для удобства
from .config_manager import (
    RuffConfigManager,
    BlackConfigManager,
    ProjectConfigManager,
)
from .file_manager import get_python_files, summarize_project_structure

# Определяем публичные API пакета
__all__ = [
    "RuffConfigManager",
    "BlackConfigManager",
    "ProjectConfigManager",
    "app",
    "__version__",
]
