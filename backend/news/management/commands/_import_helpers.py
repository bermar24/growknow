import json
from pathlib import Path


class JsonImportFacade:
    def __init__(self, command):
        self.command = command

    def resolve_file_path(self, cli_path: str | None, filename: str) -> Path:
        if cli_path:
            return Path(cli_path)
        return Path(__file__).resolve().parent.parent.parent / "static" / "news_data" / filename

    def load_items(self, file_path: Path):
        if not file_path.exists():
            self.command.stderr.write(self.command.style.ERROR(f"File not found: {file_path}"))
            return None
        try:
            with open(file_path, "r", encoding="utf-8") as file_handle:
                payload = json.load(file_handle)
        except (OSError, json.JSONDecodeError) as exc:
            self.command.stderr.write(self.command.style.ERROR(f"Failed to parse JSON: {exc}"))
            return None

        # SOLID (SRP): file validation/parsing lives in one helper, not duplicated across commands.
        # Pattern (Facade): commands call one method instead of repeating low-level file/JSON handling.
        # Benefit: both import commands stay smaller and parsing fixes happen in one place.
        return payload if isinstance(payload, list) else []

