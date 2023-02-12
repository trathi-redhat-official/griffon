import logging
import os
from functools import partial, wraps

import corgi_bindings
import osidb_bindings
from rich.logging import RichHandler

from griffon.output import console

__version__ = "0.1.0"

CORGI_API_URL = os.environ["CORGI_API_URL"]
OSIDB_API_URL = os.environ["OSIDB_API_URL"]

logger = logging.getLogger("rich")


def get_logging(level="INFO"):
    FORMAT = "%(message)s"
    logging.basicConfig(level=level, format=FORMAT, datefmt="[%X]", handlers=[RichHandler()])
    return logging.getLogger("rich")


class CorgiService:
    name = "component-registry"
    description = "Red Hat component registry"
    has_binding = True

    @staticmethod
    def create_session():
        """init corgi session"""
        try:
            return corgi_bindings.new_session(corgi_server_uri=CORGI_API_URL)
        except:  # noqa
            console.log(f"{CORGI_API_URL} is not accessible.")
            exit(1)

    @staticmethod
    def get_component_types():
        """get component type enum"""
        return corgi_bindings.bindings.python_client.models.component_type_enum.ComponentTypeEnum

    @staticmethod
    def get_component_namespaces():
        """get component namespaces enum"""
        return corgi_bindings.bindings.python_client.models.namespace_enum.NamespaceEnum

    @staticmethod
    def get_component_arches():
        """get component arch enum"""
        return [
            "src",
            "noarch",
            "i386",
            "ia64",
            "s390",
            "x86_64",
            "s390x",
            "ppc",
            "ppc64",
            "aarch64",
            "ppc64le",
        ]


class OSIDBService:
    name = "osidb"
    description = "Open Source Incident database"
    has_binding = True

    @staticmethod
    def create_session():
        """init osidb session"""
        try:
            return osidb_bindings.new_session(osidb_server_uri=OSIDB_API_URL)
        except:  # noqa
            console.log(f"{OSIDB_API_URL} is not accessible (or krb ticket has expired).")
            exit(1)

    @staticmethod
    def get_flaw_states():
        """get flaw states enum"""
        return osidb_bindings.bindings.python_client.models.FlawClassificationState

    @staticmethod
    def get_flaw_resolutions():
        """get flaw resolution enum"""
        return osidb_bindings.bindings.python_client.models.FlawResolutionEnum

    @staticmethod
    def get_flaw_impacts():
        """get flaw impacts enum"""
        return osidb_bindings.bindings.python_client.models.ImpactEnum

    @staticmethod
    def get_affect_affectedness():
        """get affect affectedness enum"""
        return osidb_bindings.bindings.python_client.models.AffectednessEnum

    @staticmethod
    def get_affect_resolution():
        """get affect affectedness enum"""
        return osidb_bindings.bindings.python_client.models.AffectResolutionEnum

    @staticmethod
    def get_affect_impact():
        """get affect impact enum"""
        return osidb_bindings.bindings.python_client.models.ImpactEnum


def progress_bar(
    func=None,
):
    """progress bar decorator"""
    if not func:
        return partial(progress_bar)

    @wraps(func)
    def wrapper(*args, **kwargs):
        with console.status("griffoning...", spinner="line"):
            func(*args, **kwargs)

    return wrapper
