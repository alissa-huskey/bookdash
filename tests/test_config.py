from pathlib import Path

import pytest

from bookdash.config import (DEFAULT_CONFIG_DIR, DEFAULT_CONFIG_FILE,
                             DEFAULT_CONFIG_FILENAME, DEFAULT_DATA_DIR, Config,
                             ConfigFile, GoodreadsConfig)

from tests import data_source


bp = breakpoint


def test_config_defaults():
    with Config.change_config_sources(data_source()):
        config = Config()

        assert config.config_file == DEFAULT_CONFIG_FILE
        assert config.config_dir == DEFAULT_CONFIG_DIR
        assert config.data_dir == DEFAULT_DATA_DIR


def test_config_config_dir_changed():
    """
    WHEN: config_file is the default
    AND: config_dir is different
    THEN: config_file should be config_dir/DEFAULT_CONFIG_FILENAME
    AND: config_dir should be the one that is set
    """
    with Config.change_config_sources(data_source(config_dir="/a/b/c")):
        config = Config()

        assert config.config_file == Path("/a/b/c") / DEFAULT_CONFIG_FILENAME
        assert config.config_dir == Path("/a/b/c")


def test_config_config_file_changed():
    """
    WHEN: config_file is different
    AND: config_dir is the default
    THEN: config_file should be the one that is set
    AND: config_dir should be config_file.parent
    """
    config_file = "/a/b/c/bookdash.toml"
    with ConfigFile.change_config_sources(data_source(config_file=config_file)):
        with Config.change_config_sources(data_source()):
            config = Config()

            assert config.config_file == Path("/a/b/c/bookdash.toml")
            assert config.config_dir == Path("/a/b/c")


def test_config_config_file_and_config_dir_changed():
    """
    WHEN: config_file is different
    AND: config_dir is different
    THEN: config_file should be the one that is set
    AND: config_dir should be config_file.parent
    """
    config_file = "/a/b/c/bookdash.toml"
    with ConfigFile.change_config_sources(data_source(config_file=config_file)):
        with Config.change_config_sources(data_source(config_dir="/d/e/f")):
            config = Config()

            assert config.config_file == Path(config_file)
            assert config.config_dir == Path(config_file).parent


@pytest.mark.parametrize(("config_file_params", "config_dir_params"), [
    ({"config_file": "~/some-dir/bookdash.toml"}, {}),
    ({}, {"config_dir": "~/some-dir"}),
])
def test_config_file_config_paths_expanded(config_file_params, config_dir_params):
    """
    GIVEN: a path string that starts includes "~"
    WHEN: Config is loaded
    THEN: .config_dir and .config_path should replace with path to home
    """
    with ConfigFile.change_config_sources(data_source(**config_file_params)):
        with Config.change_config_sources(data_source(**config_dir_params)):
            config = Config()

            assert config.config_file == Path.home() / "some-dir" / "bookdash.toml"
            assert config.config_dir == Path.home() / "some-dir"
