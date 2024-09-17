import os
import sys
from types import ModuleType
from typing import Dict

import yaml

from zix.server.logging import get_logger

logger = get_logger(logger_name=__name__)


def is_local() -> bool:
    return os.environ.get("DOMAIN") in [None, "localhost"]


def str_to_bool(string:str,) -> str:
    if not string:
        return None
    return string.lower() in ["true", "t"]


def list_submodules(module: ModuleType) -> Dict:
    submodules = dict()
    objects = dir(module)
    path, _ = os.path.split(module.__file__)
    for name in objects:
        if name[0] == "_" or os.path.exists(os.path.join(path, name, ".zixignore")):
            continue

        obj = getattr(module, name)

        if not callable(obj):
           submodules[name] = obj
    return submodules


def _dynamic_import(
        path:str,
        module_name:str,
        module_globals=None,
        ) -> ModuleType:
    """ Dynamically import module """
    sys.path.insert(1, path)
    kwargs = dict(globals=module_globals) if module_globals else {}
    module = __import__(module_name, **kwargs)
    return module


def dynamic_import(
    path:str,
    module_name: str,
    root_package: bool = False,
    relative_globals=None,
    level: int = 0):
    """ We only import modules, functions can be looked up on the module.
    Taken from: https://stackoverflow.com/a/37308413
    Usage:

    from foo.bar import baz
    >>> baz = importer('foo.bar.baz')

    import foo.bar.baz
    >>> foo = importer('foo.bar.baz', root_package=True)
    >>> foo.bar.baz

    from .. import baz (level = number of dots)
    >>> baz = importer('baz', relative_globals=globals(), level=2)
    """
    sys.path.insert(1, path)
    kwargs = {}
    if relative_globals:
        kwargs["globals"] = relative_globals
    if level is not None:
        kwargs["level"] = level
    if root_package:
        kwargs["fromlist"] = []

    return __import__(module_name, **kwargs)


def import_submodules(
        path:str,
        parent_module: str,
        ) -> ModuleType:
    parent_path = os.path.join(path, "..")
    for submodule in os.listdir(os.path.join(path, parent_module)):
        if submodule == "__init__.py":
            continue
        if (os.path.isdir(os.path.join(path, parent_module, submodule)) and
            os.path.exists(os.path.join(path, parent_module, submodule, "__init__.py")) and
            not os.path.exists(os.path.join(path, parent_module, submodule, ".zixignore"))):
            logger.info("Importing " + submodule)
            module = dynamic_import(parent_path, parent_module + "." + submodule)
    return module


def is_plugin_active(plugin):
    path =  os.path.join(os.getcwd())
    parent_module = "plugins"
    logger.debug("Checking " + os.path.join(path, parent_module, plugin, "__init__.py"))
    return (
        os.path.exists(os.path.join(path, parent_module, plugin, "__init__.py")) and
        not os.path.exists(os.path.join(path, parent_module, plugin, ".zixignore"))
    )


def define_env_vars_from_yaml(
    yaml_file:str,
    stage: str="local",
    ) -> None:
    """
    Read a yaml file with the following format to define the environment variables

    ```
    prod:
        <ENV_VAR_KEY>: <string value>
    <stage_name>:
        <ENV_VAR_KEY>: <string value>
    local:
        <ENV_VAR_KEY>: <string value>
    ```

    Example:
    ```
    local:
        API_KEY: xxxyyy01234
    ```
    """
    with open(yaml_file, "r") as f:
        stages = yaml.load(f, Loader=yaml.FullLoader)
    envs = stages[stage]
    for key in envs.keys():
        os.environ[key] = str(envs[key])
