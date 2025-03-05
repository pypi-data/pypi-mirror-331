import subprocess
from pathlib import Path

import typer

from refactorio import file_manager, config_manager

app = typer.Typer(
    help="Утилита для обновления конфигурации Ruff/Black и запуска pre-commit."
)


@app.command(
    "status",
    help="Показать текущее состояние проекта (количество файлов, основные директории).",
)
def status(
    project_dir: Path = typer.Option(".", help="Корневой каталог проекта")
):
    """Команда CLI: выводит общее состояние файлов проекта."""
    project_dir = project_dir.resolve()
    info = file_manager.summarize_project_structure(project_dir)
    typer.echo(f"Проект: {project_dir}")
    typer.echo(f"Всего Python-файлов: {info['total_files']}")
    typer.echo("Директории верхнего уровня и количество файлов в них:")
    for top_dir, count in info["top_dirs"].items():
        typer.echo(f"  - {top_dir}: {count} .py файлов")


@app.command(
    "exclude", help="Добавить указанные файлы/папки в исключения Ruff и Black."
)
def add_exclude(
    paths: list[Path] = typer.Argument(
        ..., help="Список путей (файлов или директорий) для исключения"
    ),
    run_precommit: bool = typer.Option(
        False,
        "--run",
        help="Запустить pre-commit после обновления конфигурации",
    ),
):
    """Команда CLI: добавляет заданные пути в исключения и опционально запускает pre-commit."""
    project_dir = Path(".").resolve()
    cfg_manager = config_manager.ProjectConfigManager(project_dir)
    for path in paths:
        abs_path = path if path.is_absolute() else project_dir / path
        if not abs_path.exists():
            typer.echo(f"⚠️  Путь '{path}' не найден в проекте.", err=True)
            raise typer.Exit(1)
        # Добавляем в конфиги
        cfg_manager.add_to_excludes(abs_path)
        typer.echo(f"Добавлено в исключения: {path}")
    # После обновления конфигурации, при необходимости запускаем pre-commit
    if run_precommit:
        _run_precommit()

@app.command(
    "exclude", help="Добавить указанные файлы/папки в исключения Ruff и Black."
)
def remove_exclude(
        paths: list[Path] = typer.Argument(
            ..., help="Список путей (файлов или директорий) для исключения"
        ),
        run_precommit: bool = typer.Option(
            False,
            "--run",
            help="Запустить pre-commit после обновления конфигурации",
        ),
):
    """Команда CLI: удаляет заданные пути в исключения и опционально запускает pre-commit."""
    project_dir = Path(".").resolve()
    cfg_manager = config_manager.ProjectConfigManager(project_dir)
    for path in paths:
        abs_path = path if path.is_absolute() else project_dir / path
        if not abs_path.exists():
            typer.echo(f"⚠️  Путь '{path}' не найден в проекте.", err=True)
            raise typer.Exit(1)
        # Добавляем в конфиги
        cfg_manager.remove_from_excludes(abs_path)
        typer.echo(f"Удалено из исключения: {path}")
    # После обновления конфигурации, при необходимости запускаем pre-commit
    if run_precommit:
        _run_precommit()

@app.command("run", help="Запустить все хуки pre-commit для всего проекта.")
def run_precommit():
    """Команда CLI: запуск pre-commit hooks по всему проекту."""
    _run_precommit()


def _run_precommit():
    """Внутренняя функция для запуска pre-commit и обработки результата."""
    typer.echo("Запуск pre-commit hooks...")
    result = subprocess.run(
        ["pre-commit", "run", "--all-files"], capture_output=True, text=True
    )
    if result.returncode == 0:
        typer.echo("pre-commit успешно выполнен. ✅")
    else:
        typer.echo("pre-commit завершился с ошибками. ❌", err=True)
        # Выводим stdout/stderr pre-commit для подробностей
        typer.echo(result.stdout or result.stderr, err=True)
        raise typer.Exit(result.returncode)


# Точка входа
if __name__ == "__main__":
    app()
