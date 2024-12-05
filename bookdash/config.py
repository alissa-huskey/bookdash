from os import environ
from pathlib import Path
from typing import Optional

import toml
from confz import BaseConfig, EnvSource, FileSource
from pydantic import (EmailStr, Field, computed_field, field_validator,
                      model_validator)
from pydantic.functional_validators import AfterValidator
from typing_extensions import Annotated
from xdg.BaseDirectory import xdg_config_home, xdg_data_home

DEFAULT_CONFIG_FILENAME = "bookdash.toml"
DEFAULT_CONFIG_DIR = Path(xdg_config_home) / "bookdash"
DEFAULT_DATA_DIR = Path(xdg_data_home) / "bookdash"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / DEFAULT_CONFIG_FILENAME

bp = breakpoint

DEFAULT_SOURCES = (
    FileSource(file=DEFAULT_CONFIG_FILE, optional=True),
    FileSource(file_from_env="BOOKDASH_CONFIG_FILE", optional=True),
)


class ConfigFile(BaseConfig):
    """Just handles the config file location."""
    config_file: Path = DEFAULT_CONFIG_FILE

    CONFIG_SOURCES = EnvSource(prefix="BOOKDASH_", allow="config_file")


class Config(BaseConfig):
    """Class for storing user config settings."""
    config_dir: Annotated[Path, Field(validate_default=True)] = ConfigFile().config_file.parent
    data_dir: Path = DEFAULT_DATA_DIR

    CONFIG_SOURCES = [
        *DEFAULT_SOURCES,
        EnvSource(prefix="BOOKDASH_", allow_all=True),
    ]

    @computed_field
    @property
    def config_file(self) -> Path:
        """Get config_file.

        Populate from ConfigFile(). If self.config_dir is set by the user and
        config_file is not, config_file should be realiteve to config_dir."""
        file = ConfigFile().config_file

        if file == DEFAULT_CONFIG_FILE and self.config_dir != DEFAULT_CONFIG_DIR:
            file = self.config_dir / DEFAULT_CONFIG_FILENAME

        return file

    @field_validator("config_dir")
    def validate_config_dir(cls, config_dir) -> Path:
        """Get config_dir.

        config_dir should be relative to config_file if config_file is set."""
        config_file = ConfigFile().config_file

        if config_file != DEFAULT_CONFIG_FILE:
            config_dir = config_file.parent

        return config_dir

    #  @model_validator(mode="after")
    #  @classmethod
    #  def config_dir_validator(self, v: Path) -> Path:
    #      """Overwrite the config_dir with the directory the config file is in if
    #      the config file has been set and """
    #      if self.config_file == DEfAULT_CONFIG_FILE:
    #          return

    #      return self.config_file.parent

class GoodreadsConfig(BaseConfig):
    """Class for storing goodreads credentials."""

    email: Optional[EmailStr] = None
    pwd: Optional[str] = None

    CONFIG_SOURCES = [
        *DEFAULT_SOURCES,
        EnvSource(prefix="GOODREADS_", allow_all=True),
    ]


def shorten_home(path):
    if not isinstance(path, Path):
        return path
    if not path.is_relative_to(Path.home()):
        return path
    return "~/" + str(path.relative_to(Path.home()))

def init_config(path):
    """Initialize config file."""
    config = Config().model_dump()
    config["goodreads_email"] = "YOUR-EMAIL"
    config["goodreads_pwd"] = "YOUR-PASSWORD"

    config.pop("config_dir")
    config.pop("config_file")

    config = {k: shorten_home(v) for k, v in config.items()}
    config = {k: str(v) for k, v in config.items()}

    config_text = toml.dumps(config)

    prefix = (
        "# bookdash config file",
        "# https://github.com/alissa-huskey/bookdash",
        "",
        "",
        "",
    )

    suffix = (
        "",
        "",
        "# Environment Variables",
        "# =====================",
        "# Configuation values can also be set using the following",
        "# environment variables. (In a .bashrc, .zshrc, or .env file,"
        "# for example.)"
        "#",
        "# Values set in environment variables supercede any duplicate values here.",
        "#",
        "# - BOOKDASH_CONFIG_FILE:  Path to bookdash config file.",
        "#                          (Supercedes all other config path settings.)",
        f"# - BOOKDASH_CONFIG_DIR:   {DEFAULT_CONFIG_FILENAME} directory.",
        "#                          (Supercedes XDG_CONFIG_HOME.)",
        "# - BOOKDASH_DATA_DIR:     Bookdash user data directory.",
        "#                          (Supercedes XDG_DATA_HOME.)",
        "# - XDG_CONFIG_HOME:       User config directory.",
        "# - XDG_DATA_HOME:         User data directory.",
        "# - GOODREADS_EMAIL:       Your goodreads email address.",
        "# - GOODREADS_PWD:         Your goodreads password.",
        "",
    )

    text = "\n".join(prefix) + config_text + "\n".join(suffix)
    path.write_text(text)
