import tomllib
from functools import cached_property
from pathlib import Path


class Config:
    def __init__(
        self, filename: str = "config.toml", filepath: Path | None = None
    ) -> None:
        self.__filename = filename
        self.__filepath: Path | None = None
        if filepath is not None:
            if filepath.is_dir():
                self.__filepath = filepath / filename
            else:
                self.__filepath = filepath.name
        else:
            self.__filepath = Path(filename)

        assert self.__filepath.exists()

    def __str__(self) -> str:
        return f"Config(filename={self.__filename}, filepath={self.__filepath})"

    @property
    def filepath(self) -> Path:
        return self.__filepath

    @property
    def value(self) -> dict:
        """Get config value"""
        with open(self.filepath, "r") as f:
            return tomllib.loads(f.read())
        return {}

    def get(self, keys: tuple[str, ...], default=None):
        """Get the value from config"""
        data = self.value
        for key in keys[:-1]:
            data = data.get(key, {})
        return data.get(keys[-1], default)
