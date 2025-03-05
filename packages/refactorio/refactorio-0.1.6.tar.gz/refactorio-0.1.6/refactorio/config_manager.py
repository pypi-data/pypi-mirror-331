import re
from pathlib import Path

import tomlkit


class RuffConfigManager:
    """Класс для управления конфигурацией Ruff (ruff.toml)."""

    def __init__(self, config_path: Path):
        self.config_path = config_path
        # Парсим существующий TOML-документ Ruff
        config_text = config_path.read_text(encoding="utf-8")
        self.toml_doc = tomlkit.parse(config_text)
        # Ожидаем, что в конфиге Ruff есть ключ 'exclude'
        if "exclude" not in self.toml_doc:
            # Если раздел exclude отсутствует, создадим пустой список
            self.toml_doc["exclude"] = tomlkit.array()

    def add_exclude(self, pattern: str) -> bool:
        """Добавляет шаблон в список исключений Ruff. Возвращает True, если добавлено."""
        exclude_list = self.toml_doc["exclude"]
        # Проверяем, нет ли уже такого паттерна в списке
        if pattern in exclude_list:
            return False  # уже исключено
        exclude_list.append(pattern)
        return True

    def remove_exclude(self, path: Path) -> bool:
        """Удаляет путь из списка исключений Ruff. Возвращает True, если удалено."""
        exclude_list = self.toml_doc["exclude"]
        if path in exclude_list:
            exclude_list.remove(path)
            return True
        return False

    def save(self):
        """Сохраняет обновленный Ruff TOML обратно в файл, сохраняя форматирование."""
        self.config_path.write_text(
            tomlkit.dumps(self.toml_doc), encoding="utf-8"
        )


class BlackConfigManager:
    """Класс для управления конфигурацией Black (секции [tool.black] в pyproject.toml)."""

    def __init__(self, pyproject_path: Path):
        self.pyproject_path = pyproject_path
        pyproject_text = pyproject_path.read_text(encoding="utf-8")
        self.toml_doc = tomlkit.parse(pyproject_text)
        # Переходим к секции [tool.black] (создаем, если нет)
        tool_section = self.toml_doc.get("tool", {})
        if "black" not in tool_section:
            # Если конфиг Black отсутствует, создаем таблицу
            tool_section["black"] = tomlkit.table()
            self.toml_doc["tool"] = tool_section
        self.black_section = self.toml_doc["tool"]["black"]
        # Убедимся, что ключи exclude/extend-exclude существуют для дальнейшего использования
        if "force-exclude" not in self.black_section:
            # Если force-exclude отсутствует, создаем его как пустой шаблон в скобках
            self.black_section["force-exclude"] = "()"

    def add_exclude(self, path: str) -> bool:
        """Добавляет путь в шаблон исключений Black (force-exclude).
        Возвращает True, если добавлено новое исключение."""
        # Получаем текущее значение force-exclude (многострочная строка с регулярным выражением)
        force_exclude_val = self.black_section.get("force-exclude")
        if force_exclude_val is None:
            current_pattern = "()"
        else:
            current_pattern = str(force_exclude_val)
        # Убираем тройные кавычки, если tomlkit вернул с ними (tomlkit обычно возвращает только содержимое)
        # Приводим текущее выражение к строке (например, '(\n    src/old_module\n)').
        pattern_text = current_pattern

        # Проверяем, не включён ли уже данный путь в шаблон (чтобы избежать дубликатов).
        # Для надёжности экранируем специальные символы пути в контексте regex.
        regex_pattern = re.escape(path)
        if regex_pattern in pattern_text:
            return False  # уже есть в исключениях

        # Разбиваем многострочное выражение на строки для вставки нового пути перед ')'
        lines = pattern_text.splitlines()
        if not lines:
            # Если вдруг шаблон пустой, создаём с нашими скобками
            lines = ["(", ")"]
        # Определяем отступ (индентацию) для новых линий – берем отступ второй строки, если есть
        indent = ""
        if len(lines) > 1:
            # Количество пробелов в начале второй строки (где перечисляются пути)
            indent_match = re.match(r"\s*", lines[1])
            indent = indent_match.group(0) if indent_match else ""
        if indent == "":
            indent = "    "  # по умолчанию 4 пробела, если отступ не определён

        # Вставляем новый путь с вертикальной чертой '|' в предпоследнюю позицию (перед строкой с ')')
        lines.insert(-1, f"{indent}| {path}".replace("\\", "/"))
        # Формируем новое содержимое многострочного шаблона
        new_pattern_text = "\n".join(lines)
        # Обновляем значение force-exclude в конфигурации
        self.black_section["force-exclude"] = tomlkit.string(new_pattern_text, literal=True)
        return True

    def remove_exclude(self, path: Path) -> bool:
        """Удаляет путь из force-exclude Black. Возвращает True, если удалено."""
        force_exclude_val = str(self.black_section.get("force-exclude", ".*"))

        # Разбиваем по строкам и удаляем путь, если он есть
        lines = force_exclude_val.splitlines()
        new_lines = [line for line in lines if path not in line]

        # Если изменилось, записываем обратно
        if len(new_lines) != len(lines):
            self.black_section["force-exclude"] = tomlkit.string("\n".join(new_lines))
            return True
        return False

    def save(self):
        """Сохраняет обновленный pyproject.toml обратно в файл."""
        self.pyproject_path.write_text(
            tomlkit.dumps(self.toml_doc), encoding="utf-8"
        )


class ProjectConfigManager:
    """Фасад для управления конфигурациями Ruff и Black одновременно."""

    def __init__(self, project_path: Path):
        self.project_path = project_path
        # Пути к файлам конфигурации (ruff.toml и pyproject.toml)
        self.ruff_cfg = RuffConfigManager(project_path / "ruff.toml")
        self.black_cfg = BlackConfigManager(project_path / "pyproject.toml")

    def add_to_excludes(self, path: Path) -> None:
        """Добавляет указанный путь (файл или директорию) в исключения Ruff и Black."""
        # Преобразуем путь к относительному (относительно корня проекта) в POSIX формате
        rel_path = (
            path
            if path.is_absolute() is False
            else path.relative_to(self.project_path)
        )
        rel_str = rel_path.as_posix()
        # Для Ruff: если это директория, исключаем всю её содержимое
        ruff_pattern = rel_str + ("/**" if path.is_dir() else "")
        ruff = self.ruff_cfg.add_exclude(ruff_pattern)
        # Для Black: формируем паттерн (в regex) аналогично (директории и файлы добавляются как есть в regex)
        black = self.black_cfg.add_exclude(
            rel_str if not path.is_dir() else rel_str
        )
        # Сохраняем файлы конфигурации, если были внесены новые изменения
        if ruff:
            self.ruff_cfg.save()
        if black:
            self.black_cfg.save()

    def remove_from_excludes(self, path: Path) -> None:
        """Удаляет указанный путь из исключений Ruff и Black."""
        rel_path = Path(path.relative_to(self.project_path).as_posix())
        ruff_pattern = Path(str(rel_path) + ("/**" if path.is_dir() else ""))

        ruff = self.ruff_cfg.remove_exclude(ruff_pattern)
        black = self.black_cfg.remove_exclude(rel_path)

        if ruff:
            self.ruff_cfg.save()
        if black:
            self.black_cfg.save()