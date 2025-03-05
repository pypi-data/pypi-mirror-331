from pathlib import Path


def get_python_files(base_dir: Path) -> list[Path]:
    """Возвращает список всех Python-файлов в проекте (рекурсивно)."""
    return list(base_dir.rglob("*.py"))


def summarize_project_structure(base_dir: Path) -> dict:
    """Собирает сводную информацию о структуре проекта:
    количество Python-файлов и список пакетов верхнего уровня."""
    python_files = get_python_files(base_dir)
    top_dirs = {}
    # Рассматриваем директории верхнего уровня внутри base_dir (например, 'src/')
    for py_file in python_files:
        # Определяем папку верхнего уровня для каждого файла
        parts = py_file.relative_to(base_dir).parts
        if parts:
            top_dir = parts[0]
            top_dirs.setdefault(top_dir, 0)
            top_dirs[top_dir] += 1
    return {"total_files": len(python_files), "top_dirs": top_dirs}
