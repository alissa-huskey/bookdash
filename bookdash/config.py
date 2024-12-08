from os import environ
from pathlib import Path
from typing import Optional, Union

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

PathLike = Union[Path, str]


def expand_path(path: Path) -> Path:
    """Expand the '~' and make the path absolute."""
    return path.expanduser().absolute()


def init_config(path: Path) -> None:
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


class ConfigFile(BaseConfig):
    """Just handles the config file location.

    Seperate from Config class as this value cannot be in the config file and
    comes only from the environment variable (for obvious reasons), and the
    Config class is dependent on the value if set.

    Sources include:
        * indirectly the XDG_CONFIG_HOME and XDG_DATA_HOME environment
          variables, obtained via xdg module.

    Precedent:
        * BOOKDASH_CONFIG_FILE env var supersedes XDG_CONFIG_HOME env var
    """
    config_file: Path = Field(
        validate_default=True,
        default=DEFAULT_CONFIG_FILE,
    )

    _config_file_validator = field_validator("config_file")(expand_path)

    CONFIG_SOURCES = EnvSource(prefix="BOOKDASH_", allow="config_file")


class Config(BaseConfig):
    """Class for storing user config settings.

    Sources include:
        * the config file at its default location if present
        * the config file set by the enviornment variable BOOKDASH_CONFIG_FILE
          if set and present
        * envionment variables with the prefix BOOKDASH_ if set
        * indirectly the XDG_CONFIG_HOME and XDG_DATA_HOME environment
          variables, obtained via xdg module.
        * value of ConfigFile().config_file

    Precedent:
        * Environment variables supersede config file settings.
        * bookdash_* settings supersede XDG_* env vars
        * config_file supersede config_dir
    """
    config_dir: Annotated[
        Path, Field(validate_default=True)
    ] = ConfigFile().config_file.parent
    data_dir: Path = Field(DEFAULT_DATA_DIR, validate_default=True)

    _data_dir_fixer = field_validator("data_dir")(expand_path)

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
    def validate_config_dir(cls, config_dir: PathLike) -> Path:
        """Get config_dir.

        config_dir should be relative to config_file if config_file is set."""
        config_file = ConfigFile().config_file

        if config_file != DEFAULT_CONFIG_FILE:
            config_dir = config_file.parent

        return expand_path(config_dir)


class GoodreadsConfig(BaseConfig):
    """Class for storing goodreads credentials."""

    email: Optional[EmailStr] = None
    pwd: Optional[str] = None

    CONFIG_SOURCES = [
        *DEFAULT_SOURCES,
        EnvSource(prefix="GOODREADS_", allow_all=True),
    ]


def shorten_home(path: PathLike) -> str:
    """Replace /home/USER with ~ symbol."""
    if not isinstance(path, Path):
        return path
    if not path.is_relative_to(Path.home()):
        return str(path)
    home = Path("~/").expanduser()
    return str(home) + str(path.relative_to(Path.home()))
